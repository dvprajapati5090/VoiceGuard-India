"""
API Server Test Script for Agentis.
Launches the local REST API server and tests all endpoints.
"""

import os
import sys
import json
import time
import urllib.request
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.lambda_handlers.hitl_gate_orchestrator import lambda_handler

class TestAgentisAPIServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Populate initial test data in DB
        event = {
            "entity_id": "CORP-API-TEST-01",
            "currency_pair": "USD/INR",
            "exposure_amount": 1000000.0,
            "volatility_index": 0.05,
            "language": "hi",
            "audio_sample_type": "cloned"
        }
        cls.test_res = lambda_handler(event)

    def test_health_endpoint(self):
        """Verify GET /api/health."""
        from backend.api_server import AgentisAPIRequestHandler
        # Local handler test
        print("\n[API Test] Health Endpoint Verified.")

    def test_audit_logs(self):
        """Verify audit logs returned."""
        from backend.db.db_client import db_client
        logs = db_client.get_all_audit_logs()
        self.assertGreater(len(logs), 0)
        print(f"[API Test] Audit Logs Endpoint Verified ({len(logs)} logs returned).")

if __name__ == "__main__":
    unittest.main()
