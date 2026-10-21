"""
Agentis REST API Server for Frontend & Amplify Dashboard Integration.
Exposes RESTful endpoints for Treasury Exposure Evaluation, Voice Verification, HITL Gate, and DPDP Audit Logs.

Zero External Dependencies: Implemented using Python's native http.server module.
"""

import sys
import os
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.lambda_handlers.hitl_gate_orchestrator import lambda_handler
from backend.agents.execution_agent import TreasuryExecutionAgent
from backend.agents.verification_agent import VoiceVerificationAuditAgent
from backend.db.db_client import db_client

HOST = "0.0.0.0"
PORT = 8000

class AgentisAPIRequestHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler exposing REST endpoints for Agentis Frontend."""

    def _set_headers(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self._set_headers(200)

    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip('/')

        if path in ["", "/api", "/index.html"]:
            response = {
                "status": "ONLINE",
                "system": "Agentis Autonomous Treasury & Voice Authentication System",
                "message": "Welcome to Agentis REST API Server",
                "available_endpoints": {
                    "GET /api/health": "System health and multi-lingual capabilities",
                    "GET /api/cases": "List all treasury transfer cases and HITL statuses",
                    "GET /api/audit_logs": "DPDP Act 2023 compliance audit logs",
                    "POST /api/evaluate": "Evaluate currency exposure & propose FX hedge",
                    "POST /api/verify": "Perform multi-lingual voice spoof verification (EN/HI/GU)",
                    "POST /api/full_demo": "Run complete end-to-end multi-agent execution"
                }
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))

        elif path == "/api/health":
            response = {
                "status": "ONLINE",
                "system": "Agentis Autonomous Treasury & Voice Authentication Guardrail",
                "version": "1.0.0",
                "timestamp": time.time(),
                "multilingual_support": ["en", "hi", "gu"]
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))

        elif path == "/api/audit_logs":
            logs = db_client.get_all_audit_logs()
            response = {
                "status": "SUCCESS",
                "count": len(logs),
                "dpdp_compliance": "STRICT_ANONYMIZED_HASH",
                "audit_logs": logs
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))

        elif path == "/api/cases":
            cases = db_client._cases
            response = {
                "status": "SUCCESS",
                "count": len(cases),
                "cases": list(cases.values())
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(response, indent=2).encode('utf-8'))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": f"Endpoint '{path}' Not Found. Visit GET /api to see available endpoints."}).encode('utf-8'))

    def do_POST(self):
        """Handle POST requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path.rstrip('/')

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            body = json.loads(post_data.decode('utf-8')) if post_data else {}
        except Exception:
            body = {}

        if path == "/api/evaluate":
            entity_id = body.get("entity_id", "CORP-GIFT-CITY-01")
            currency_pair = body.get("currency_pair", "USD/INR")
            exposure_amount = float(body.get("exposure_amount", 750000.0))
            volatility_index = float(body.get("volatility_index", 0.048))

            exec_agent = TreasuryExecutionAgent(db=db_client)
            proposal = exec_agent.evaluate_exposure_and_propose_hedge(
                entity_id=entity_id,
                currency_pair=currency_pair,
                exposure_amount=exposure_amount,
                volatility_index=volatility_index
            )

            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "SUCCESS", "proposal": proposal}, indent=2).encode('utf-8'))

        elif path == "/api/verify":
            case_id = body.get("case_id")
            sample_type = body.get("sample_type", "authentic")
            language = body.get("language", "en")
            caller_metadata = body.get("caller_telemetry", None)

            if not case_id:
                event_res = lambda_handler(body)
                self._set_headers(200)
                self.wfile.write(json.dumps(event_res["body"], indent=2).encode('utf-8'))
                return

            verif_agent = VoiceVerificationAuditAgent(db=db_client)
            result = verif_agent.verify_transfer_call(
                case_id=case_id,
                sample_type=sample_type,
                language=language,
                caller_metadata=caller_metadata
            )

            self._set_headers(200)
            self.wfile.write(json.dumps({"status": "SUCCESS", "verification": result}, indent=2).encode('utf-8'))

        elif path == "/api/full_demo":
            event_res = lambda_handler(body)
            self._set_headers(200)
            self.wfile.write(json.dumps(event_res["body"], indent=2).encode('utf-8'))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"error": f"Endpoint '{path}' Not Found."}).encode('utf-8'))

def run_server():
    server_address = (HOST, PORT)
    httpd = HTTPServer(server_address, AgentisAPIRequestHandler)
    print("=" * 70)
    print(f" AGENTIS REST API SERVER ONLINE — Listening on http://localhost:{PORT}")
    print(" Endpoints:")
    print("   GET  http://localhost:8000/             (API Overview)")
    print("   GET  http://localhost:8000/api/health   (System Health)")
    print("   GET  http://localhost:8000/api/cases    (Transfer Cases)")
    print("   GET  http://localhost:8000/api/audit_logs (Compliance Logs)")
    print("   POST http://localhost:8000/api/evaluate (Risk Evaluation)")
    print("   POST http://localhost:8000/api/verify   (Voice Verification)")
    print("   POST http://localhost:8000/api/full_demo (Full Workflow)")
    print("=" * 70)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[API Server] Shutting down...")
        httpd.server_close()

if __name__ == "__main__":
    run_server()
