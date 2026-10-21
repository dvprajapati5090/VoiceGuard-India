"""
Database Client Interface for Agentis.
Supports local in-memory storage and AWS DynamoDB integration.
"""

import os
import time
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError

from backend.config import (
    AWS_REGION,
    DYNAMODB_TABLE_BALANCES,
    DYNAMODB_TABLE_CASES,
    DYNAMODB_TABLE_AUDIT
)
from backend.db.models import (
    TreasuryBalanceRecord,
    TransferCaseRecord,
    ComplianceAuditLogRecord
)

class AgentisDBClient:
    """Database client managing Treasury Balances, Transfer Cases, and Compliance Audit Logs."""
    
    def __init__(self, use_dynamodb=False):
        self.use_dynamodb = use_dynamodb
        
        # In-memory stores
        self._balances = {}
        self._cases = {}
        self._audit_logs = []
        
        if self.use_dynamodb:
            try:
                self.dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)
                self.tbl_balances = self.dynamodb.Table(DYNAMODB_TABLE_BALANCES)
                self.tbl_cases = self.dynamodb.Table(DYNAMODB_TABLE_CASES)
                self.tbl_audit = self.dynamodb.Table(DYNAMODB_TABLE_AUDIT)
            except Exception as e:
                print(f"[DBClient-Warning] Could not initialize DynamoDB ({e}). Falling back to local store.")
                self.use_dynamodb = False

    # --- Balance Operations ---
    def save_balance(self, record: TreasuryBalanceRecord):
        data = record.to_dict()
        key = f"{record.entity_id}#{record.currency_pair}"
        self._balances[key] = data
        
        if self.use_dynamodb:
            try:
                self.tbl_balances.put_item(Item=data)
            except Exception as e:
                print(f"[DynamoDB-Error] Put balance failed: {e}")
        return data

    def get_balance(self, entity_id: str, currency_pair: str):
        key = f"{entity_id}#{currency_pair}"
        if key in self._balances:
            return self._balances[key]
        return None

    # --- Case Operations ---
    def create_case(self, case_record: TransferCaseRecord):
        data = case_record.to_dict()
        self._cases[case_record.case_id] = data
        
        if self.use_dynamodb:
            try:
                self.tbl_cases.put_item(Item=data)
            except Exception as e:
                print(f"[DynamoDB-Error] Put case failed: {e}")
        return data

    def update_case_status(self, case_id: str, new_status: str, ensemble_score: float = None, self_corrected: bool = False):
        if case_id in self._cases:
            self._cases[case_id]["status"] = new_status
            self._cases[case_id]["updated_at"] = time.time()
            if ensemble_score is not None:
                self._cases[case_id]["ensemble_score"] = ensemble_score
            self._cases[case_id]["self_correction_applied"] = self_corrected
            
            if self.use_dynamodb:
                try:
                    self.tbl_cases.update_item(
                        Key={"case_id": case_id},
                        UpdateExpression="SET #st = :s, updated_at = :u, ensemble_score = :es, self_correction_applied = :sc",
                        ExpressionAttributeNames={"#st": "status"},
                        ExpressionAttributeValues={
                            ":s": new_status,
                            ":u": time.time(),
                            ":es": ensemble_score or 0.0,
                            ":sc": self_corrected
                        }
                    )
                except Exception as e:
                    print(f"[DynamoDB-Error] Update case failed: {e}")
            return self._cases[case_id]
        return None

    def get_case(self, case_id: str):
        return self._cases.get(case_id, None)

    def list_pending_cases(self):
        return [c for c in self._cases.values() if c["status"] == "PENDING_HITL_VERIFICATION"]

    # --- Compliance Audit Log Operations ---
    def log_audit(self, audit_record: ComplianceAuditLogRecord):
        data = audit_record.to_dict()
        self._audit_logs.append(data)
        
        if self.use_dynamodb:
            try:
                self.tbl_audit.put_item(Item=data)
            except Exception as e:
                print(f"[DynamoDB-Error] Put audit log failed: {e}")
        return data

    def get_all_audit_logs(self):
        return self._audit_logs

# Shared global instance
db_client = AgentisDBClient()
