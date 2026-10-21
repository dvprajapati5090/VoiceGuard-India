"""
Treasury Execution Agent (Bedrock Powered).
Monitors synthetic currency exposure data, proposes FX hedge transfers, and enforces the HITL gate limit ($500,000 USD).
"""

import uuid
import time
from backend.config import HITL_RISK_THRESHOLD_USD
from backend.db.models import TransferCaseRecord, TreasuryBalanceRecord
from backend.db.db_client import db_client
from backend.agents.prompts import TREASURY_EXECUTION_AGENT_PROMPT

class TreasuryExecutionAgent:
    """
    Autonomous Treasury Execution Agent.
    Evaluates multi-currency risk and initiates hedge transactions with HITL guardrail gating.
    """
    
    def __init__(self, db=db_client):
        self.db = db
        self.system_prompt = TREASURY_EXECUTION_AGENT_PROMPT

    def evaluate_exposure_and_propose_hedge(self, entity_id: str, currency_pair: str, exposure_amount: float, volatility_index: float):
        """
        Analyzes currency exposure and determines if an FX hedge is required.
        Enforces HITL gate when transaction value >= $500,000 USD.
        """
        # Save balance state
        risk_level = "HIGH" if volatility_index > 0.045 or exposure_amount >= HITL_RISK_THRESHOLD_USD else "MEDIUM" if volatility_index > 0.02 else "LOW"
        balance_record = TreasuryBalanceRecord(
            entity_id=entity_id,
            currency_pair=currency_pair,
            exposure_amount=exposure_amount,
            volatility_index=volatility_index,
            risk_level=risk_level
        )
        self.db.save_balance(balance_record)
        
        # Calculate hedge amount (e.g. 75% coverage for high risk exposures)
        hedge_amount_usd = round(exposure_amount * 0.75, 2)
        
        # Check HITL Gate requirement
        hitl_required = hedge_amount_usd >= HITL_RISK_THRESHOLD_USD
        
        case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        
        if hitl_required:
            status = "PENDING_HITL_VERIFICATION"
            recommendation = (
                f"HIGH RISK EXPOSURE ({currency_pair} ${exposure_amount:,.2f} USD equiv). "
                f"Proposed FX forward hedge of ${hedge_amount_usd:,.2f}. "
                f"PAUSED AT HITL GATE: Requires CFO voice sign-off verification."
            )
        else:
            status = "AUTO_EXECUTED_LOW_RISK"
            recommendation = (
                f"LOW/MEDIUM EXPOSURE ({currency_pair} ${exposure_amount:,.2f} USD equiv). "
                f"Executed automated spot hedge of ${hedge_amount_usd:,.2f}."
            )
            
        case_record = TransferCaseRecord(
            case_id=case_id,
            entity_id=entity_id,
            currency_pair=currency_pair,
            amount_usd=hedge_amount_usd,
            hedge_recommendation=recommendation,
            status=status,
            hitl_required=hitl_required
        )
        
        saved_case = self.db.create_case(case_record)
        
        return {
            "agent": "TreasuryExecutionAgent",
            "case_id": case_id,
            "entity_id": entity_id,
            "currency_pair": currency_pair,
            "hedge_amount_usd": hedge_amount_usd,
            "hitl_required": hitl_required,
            "status": status,
            "recommendation": recommendation,
            "case_record": saved_case
        }
