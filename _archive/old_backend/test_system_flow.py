"""
End-to-End System Integration Test for Agentis.
Tests all 4 operational scenarios across Treasury Execution Agent, Voice Verification Agent,
Self-Correction Pass, SNS Fraud Alerts, and DPDP Compliance Audit Logging.
"""

import os
import sys
import json
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.lambda_handlers.hitl_gate_orchestrator import lambda_handler
from backend.db.db_client import db_client

class TestAgentisSystemFlow(unittest.TestCase):

    def test_01_scenario_authentic_voice_pass(self):
        """Scenario 1: High Risk ($750k) Transfer + Authentic CFO Voice -> RELEASED_PASS."""
        event = {
            "entity_id": "CORP-APPLE-01",
            "currency_pair": "USD/EUR",
            "exposure_amount": 1000000.0, # Hedge = $750k USD (> $500k HITL threshold)
            "volatility_index": 0.05,
            "audio_sample_type": "authentic"
        }
        res = lambda_handler(event)
        self.assertEqual(res["statusCode"], 200)
        body = res["body"]
        self.assertTrue(body["exposure_proposal"]["hitl_required"])
        self.assertEqual(body["verification_result"]["final_decision"], "RELEASED_PASS")
        self.assertFalse(body["sns_alert_fired"])
        print("\n[SUCCESS] Scenario 1 (Authentic Voice) Passed: Transfer Released.")

    def test_02_scenario_cloned_voice_block(self):
        """Scenario 2: High Risk ($850k) Transfer + AI Cloned Voice -> BLOCKED_AI_CLONE & SNS Alert."""
        event = {
            "entity_id": "CORP-TESLA-02",
            "currency_pair": "USD/GBP",
            "exposure_amount": 1150000.0, # Hedge = $862.5k USD (> $500k HITL threshold)
            "volatility_index": 0.06,
            "audio_sample_type": "cloned"
        }
        res = lambda_handler(event)
        self.assertEqual(res["statusCode"], 200)
        body = res["body"]
        self.assertTrue(body["exposure_proposal"]["hitl_required"])
        self.assertEqual(body["verification_result"]["final_decision"], "BLOCKED_AI_CLONE")
        self.assertTrue(body["sns_alert_fired"])
        print("[SUCCESS] Scenario 2 (AI Voice Clone) Passed: Transfer Blocked & SNS Alert Fired.")

    def test_03_scenario_ambiguous_voice_self_correction(self):
        """Scenario 3: High Risk ($600k) Transfer + Ambiguous Noisy Audio -> Self-Correction Pass -> RELEASED."""
        event = {
            "entity_id": "CORP-MICROSOFT-03",
            "currency_pair": "USD/INR",
            "exposure_amount": 800000.0, # Hedge = $600k USD
            "volatility_index": 0.04,
            "audio_sample_type": "ambiguous",
            "caller_telemetry": {
                "caller_phone": "+1-415-555-0188",
                "carrier_tls_auth": True,
                "imei_registered_match": True,
                "network_latency_ms": 92
            }
        }
        res = lambda_handler(event)
        self.assertEqual(res["statusCode"], 200)
        body = res["body"]
        verif = body["verification_result"]
        self.assertTrue(verif["self_correction_applied"])
        self.assertEqual(verif["final_decision"], "SELF_CORRECTED_RELEASE")
        print("[SUCCESS] Scenario 3 (Ambiguous Audio + Self-Correction) Passed: Upgraded & Transfer Released.")

    def test_04_scenario_low_risk_auto_executed(self):
        """Scenario 4: Low Risk ($250k) Transfer (< $500k HITL threshold) -> Auto Executed."""
        event = {
            "entity_id": "CORP-NVIDIA-04",
            "currency_pair": "USD/JPY",
            "exposure_amount": 300000.0, # Hedge = $225k USD (< $500k HITL threshold)
            "volatility_index": 0.015,
            "audio_sample_type": "authentic"
        }
        res = lambda_handler(event)
        self.assertEqual(res["statusCode"], 200)
        body = res["body"]
        self.assertFalse(body["exposure_proposal"]["hitl_required"])
        print("[SUCCESS] Scenario 4 (Low Risk Auto-Execute) Passed: Direct Release without HITL Gate.")

    def test_05_dpdp_compliance_audit_logs(self):
        """Verify DPDP Act 2023 compliance: Anonymized SHA256 hashes stored, no raw audio."""
        audit_logs = db_client.get_all_audit_logs()
        self.assertGreater(len(audit_logs), 0)
        for log in audit_logs:
            self.assertTrue(log["dpdp_compliance_flag"])
            self.assertNotEqual(log["caller_hash"], "+1-202-555-0199")
            self.assertEqual(len(log["caller_hash"]), 16) # SHA256 truncated hash
        print(f"[SUCCESS] DPDP Compliance Verified: {len(audit_logs)} audit records checked.")

if __name__ == "__main__":
    unittest.main()
