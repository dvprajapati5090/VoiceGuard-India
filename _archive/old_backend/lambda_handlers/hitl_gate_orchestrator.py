"""
AWS Lambda Orchestrator Handler for Agentis Multi-Lingual System.
Coordinates Treasury Execution Agent, Voice Verification Agent (EN/HI/GU), HITL Gate, SNS Escalation, and DynamoDB storage.
"""

import json
import time
from backend.agents.execution_agent import TreasuryExecutionAgent
from backend.agents.verification_agent import VoiceVerificationAuditAgent
from backend.db.db_client import db_client

def sns_publish_fraud_alert(case_id: str, amount_usd: float, reason: str):
    """Simulates Amazon SNS fraud escalation notification alert."""
    alert_msg = {
        "event": "FRAUD_ESCALATION_ALERT",
        "topic": "arn:aws:sns:us-east-1:123456789012:Agentis_FraudEscalationAlerts",
        "case_id": case_id,
        "amount_usd": amount_usd,
        "reason": reason,
        "timestamp": time.time()
    }
    print(f"[SNS-Alert] *** FRAUD ESCALATION ALERT FIRED *** -> {json.dumps(alert_msg)}")
    return alert_msg

def lambda_handler(event, context=None):
    """
    AWS Lambda entry point for end-to-end Treasury Execution & HITL Voice Gate flow.
    
    Expected Event Payload:
    {
       "entity_id": "ENTITY-GLOBAL-01",
       "currency_pair": "USD/INR",
       "exposure_amount": 750000.0,
       "volatility_index": 0.052,
       "language": "en" | "hi" | "gu",
       "audio_sample_type": "authentic" | "cloned" | "ambiguous",
       "caller_telemetry": { ... }
    }
    """
    entity_id = event.get("entity_id", "CORP-GIFT-CITY-01")
    currency_pair = event.get("currency_pair", "USD/INR")
    exposure_amount = float(event.get("exposure_amount", 750000.0))
    volatility_index = float(event.get("volatility_index", 0.048))
    language = event.get("language", "en")
    audio_sample_type = event.get("audio_sample_type", "authentic")
    caller_telemetry = event.get("caller_telemetry", None)
    
    exec_agent = TreasuryExecutionAgent(db=db_client)
    verif_agent = VoiceVerificationAuditAgent(db=db_client)
    
    proposal = exec_agent.evaluate_exposure_and_propose_hedge(
        entity_id=entity_id,
        currency_pair=currency_pair,
        exposure_amount=exposure_amount,
        volatility_index=volatility_index
    )
    
    case_id = proposal["case_id"]
    
    if proposal["hitl_required"]:
        verification_result = verif_agent.verify_transfer_call(
            case_id=case_id,
            sample_type=audio_sample_type,
            language=language,
            caller_metadata=caller_telemetry
        )
        
        final_decision = verification_result["final_decision"]
        
        sns_alert = None
        if "BLOCKED" in final_decision:
            sns_alert = sns_publish_fraud_alert(
                case_id=case_id,
                amount_usd=proposal["hedge_amount_usd"],
                reason=verification_result["decision_reason"]
            )
            
        return {
            "statusCode": 200,
            "body": {
                "message": f"HITL Voice Gate Processed (Language: {language.upper()})",
                "case_id": case_id,
                "language": language,
                "exposure_proposal": proposal,
                "verification_result": verification_result,
                "sns_alert_fired": sns_alert is not None
            }
        }
    else:
        return {
            "statusCode": 200,
            "body": {
                "message": "Low Risk Transfer Auto-Executed",
                "case_id": case_id,
                "exposure_proposal": proposal
            }
        }
