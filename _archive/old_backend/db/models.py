"""
Database Models for Agentis Treasury & Compliance Store.
Defines schemas for TreasuryBalances, TransferCases, and ComplianceAuditLogs.

DPDP ACT 2023 COMPLIANCE:
Audit logs store cryptographic metadata hashes (SHA256 of caller ID/IMEI) and confidence metrics.
Raw audio biometric data is NEVER retained.
"""

import time
import hashlib
import json
from dataclasses import dataclass, field, asdict

def hash_dpdp_identifier(raw_identifier: str) -> str:
    """Hashes sensitive PII/biometric identifier to comply with DPDP Act 2023."""
    if not raw_identifier:
        return "ANONYMOUS_DPDP_HASH"
    return hashlib.sha256(raw_identifier.encode('utf-8')).hexdigest()[:16]

@dataclass
class TreasuryBalanceRecord:
    entity_id: str
    currency_pair: str
    exposure_amount: float
    volatility_index: float
    risk_level: str  # 'LOW', 'MEDIUM', 'HIGH'
    last_updated: float = field(default_factory=time.time)

    def to_dict(self):
        return asdict(self)

@dataclass
class TransferCaseRecord:
    case_id: str
    entity_id: str
    currency_pair: str
    amount_usd: float
    hedge_recommendation: str
    status: str  # 'PENDING_HITL_VERIFICATION', 'RELEASED_PASS', 'BLOCKED_AI_CLONE', 'SELF_CORRECTED_RELEASE'
    hitl_required: bool
    ensemble_score: float = 0.0
    self_correction_applied: bool = False
    caller_metadata: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def to_dict(self):
        return asdict(self)

@dataclass
class ComplianceAuditLogRecord:
    audit_id: str
    case_id: str
    timestamp: float
    caller_hash: str  # DPDP-anonymized SHA256 hash
    ensemble_score: float
    submodel_breakdown: dict
    decision: str     # 'PASS', 'BLOCK', 'SELF_CORRECTED_PASS'
    decision_reason: str
    dpdp_compliance_flag: bool = True

    def to_dict(self):
        return asdict(self)
