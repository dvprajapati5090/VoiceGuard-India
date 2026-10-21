"""
Global Configuration & System Thresholds for Agentis.
Supports AWS Bearer Token (AWS_BEARER_TOKEN_BEDROCK) and Standard IAM Access Keys.
"""

import os

# Risk & Transfer Thresholds
HITL_RISK_THRESHOLD_USD = 500000.0  # Transfers >= $500,000 USD require voice approval gate

# ML Spoof Detection Ensemble Thresholds
SPOOF_PASS_THRESHOLD = 0.65       # Score >= 0.65 -> Verified Authentic Human Voice
SPOOF_BLOCK_THRESHOLD = 0.35      # Score < 0.35  -> AI Voice Clone Detected (Block)
# Range [0.35, 0.65] is AMBIGUOUS -> Triggers Self-Correction Metadata Pass

# AWS Configuration & Bearer Token Support
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
AWS_BEARER_TOKEN_BEDROCK = os.getenv("AWS_BEARER_TOKEN_BEDROCK", None)
SAGEMAKER_ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME", "agentis-voice-spoof-detector-endpoint")

# DynamoDB Table Names
DYNAMODB_TABLE_BALANCES = "Agentis_TreasuryBalances"
DYNAMODB_TABLE_CASES = "Agentis_TransferCases"
DYNAMODB_TABLE_AUDIT = "Agentis_ComplianceAuditLogs"

# DPDP Privacy Enforcement
DPDP_HASH_ALGORITHM = "sha256"
STORE_RAW_AUDIO = False  # DPDP Act 2023 Compliance: Never store raw voice biometric audio
