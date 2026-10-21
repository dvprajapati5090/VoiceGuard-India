"""
Voice Verification & Audit Agent (Bedrock Powered + SageMaker ML Endpoint).
Scores incoming CFO approval calls in English, Hindi, or Gujarati,
executes the self-correction metadata re-check on ambiguous scores,
manages fund release/block decisions, and writes DPDP Act 2023 compliance audit logs.
"""

import time
import uuid
import hashlib

from backend.config import SPOOF_PASS_THRESHOLD, SPOOF_BLOCK_THRESHOLD
from backend.db.models import ComplianceAuditLogRecord, hash_dpdp_identifier
from backend.db.db_client import db_client
from backend.agents.prompts import VOICE_VERIFICATION_AGENT_PROMPT
from ml_engine.ensemble_scorer import SpoofDetectionEnsemble

class VoiceVerificationAuditAgent:
    """
    Autonomous Voice Verification & Audit Agent.
    Evaluates multi-lingual ML voice spoof scores, applies metadata self-correction pass, and logs DPDP compliance records.
    """
    
    def __init__(self, db=db_client):
        self.db = db
        self.ensemble = SpoofDetectionEnsemble()
        self.system_prompt = VOICE_VERIFICATION_AGENT_PROMPT

    def evaluate_telemetry_metadata(self, metadata: dict) -> dict:
        """
        Self-Correction Telemetry Metadata Pass.
        Re-scores ambiguous calls (0.35 <= score < 0.65) using network & device signatures.
        """
        carrier_pass = metadata.get("carrier_tls_auth", True)
        imei_pass = metadata.get("imei_registered_match", True)
        latency_ms = metadata.get("network_latency_ms", 95)
        latency_pass = latency_ms < 150.0
        
        passed_checks = sum([1 for chk in [carrier_pass, imei_pass, latency_pass] if chk])
        
        if passed_checks >= 2:
            return {
                "self_correction_result": "PASS",
                "score_adjustment": +0.25,
                "passed_checks_count": passed_checks,
                "details": f"Self-Correction Passed ({passed_checks}/3 telemetry checks verified: Carrier TLS, Device IMEI, Latency {latency_ms}ms)"
            }
        else:
            return {
                "self_correction_result": "BLOCK",
                "score_adjustment": -0.30,
                "passed_checks_count": passed_checks,
                "details": f"Self-Correction Failed ({passed_checks}/3 telemetry checks verified: Telemetry anomaly detected)"
            }

    def verify_transfer_call(self, case_id: str, audio_file_path: str = None, sample_type: str = "authentic", language: str = "en", caller_metadata: dict = None):
        """
        Evaluates incoming CFO sign-off audio across English (en), Hindi (hi), or Gujarati (gu).
        """
        case = self.db.get_case(case_id)
        if not case:
            return {"error": f"Case {case_id} not found."}
            
        if caller_metadata is None:
            caller_metadata = {
                "caller_phone": "+91-98765-43210" if language in ["hi", "gu"] else "+1-202-555-0199",
                "carrier_tls_auth": True,
                "imei_registered_match": True,
                "network_latency_ms": 88
            }

        if audio_file_path:
            ml_res = self.ensemble.score_audio_file(audio_file_path, language=language)
        else:
            from ml_engine.dataset.generator import AudioSampleGenerator
            gen = AudioSampleGenerator()
            file_path = gen.generate_waveform(duration_sec=4.0, sample_type=sample_type, language=language)
            ml_res = self.ensemble.score_audio_file(file_path, language=language)

        score = ml_res["ensemble_score"]
        classification = ml_res["classification"]
        
        final_decision = classification
        decision_reason = ml_res["decision_explanation"]
        self_correction_applied = False
        final_score = score
        
        if classification == "AMBIGUOUS":
            self_correction_applied = True
            telemetry_res = self.evaluate_telemetry_metadata(caller_metadata)
            
            if telemetry_res["self_correction_result"] == "PASS":
                final_decision = "SELF_CORRECTED_RELEASE"
                final_score = round(min(1.0, score + telemetry_res["score_adjustment"]), 4)
                decision_reason = f"Ambiguous acoustic score ({score}, {language.upper()}) resolved via Self-Correction: {telemetry_res['details']}. FUNDS RELEASED."
            else:
                final_decision = "BLOCKED_SUSPECT"
                final_score = round(max(0.0, score + telemetry_res["score_adjustment"]), 4)
                decision_reason = f"Ambiguous acoustic score ({score}, {language.upper()}) failed Self-Correction: {telemetry_res['details']}. TRANSFER BLOCKED."
        elif classification == "PASS":
            final_decision = "RELEASED_PASS"
            decision_reason = f"Authentic voice verified in {language.upper()} (Score: {score}). FUNDS RELEASED."
        elif classification == "BLOCK":
            final_decision = "BLOCKED_AI_CLONE"
            decision_reason = f"AI Voice Clone / Deepfake detected in {language.upper()} (Score: {score}). TRANSFER BLOCKED."

        self.db.update_case_status(
            case_id=case_id,
            new_status=final_decision,
            ensemble_score=final_score,
            self_corrected=self_correction_applied
        )

        caller_phone = caller_metadata.get("caller_phone", "UNKNOWN")
        dpdp_caller_hash = hash_dpdp_identifier(caller_phone)
        
        audit_id = f"AUDIT-{uuid.uuid4().hex[:8].upper()}"
        audit_record = ComplianceAuditLogRecord(
            audit_id=audit_id,
            case_id=case_id,
            timestamp=time.time(),
            caller_hash=dpdp_caller_hash,
            ensemble_score=final_score,
            submodel_breakdown=ml_res["submodel_breakdown"],
            decision=final_decision,
            decision_reason=decision_reason,
            dpdp_compliance_flag=True
        )
        saved_audit = self.db.log_audit(audit_record)

        return {
            "agent": "VoiceVerificationAuditAgent",
            "case_id": case_id,
            "language": language,
            "original_ml_score": score,
            "final_score": final_score,
            "classification": classification,
            "final_decision": final_decision,
            "decision_reason": decision_reason,
            "self_correction_applied": self_correction_applied,
            "caller_hash_dpdp": dpdp_caller_hash,
            "audit_record": saved_audit,
            "submodel_breakdown": ml_res["submodel_breakdown"]
        }
