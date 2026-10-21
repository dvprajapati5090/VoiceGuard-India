import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.fixtures.fake_audio import make_fake_b64_chunk
import json
import base64

client = TestClient(app)

def test_new_session_id_generation():
    with client.websocket_connect("/ws/session/new") as websocket:
        websocket.send_text(json.dumps({"language": "hi"}))
        data = websocket.receive_json()
        assert "session_id" in data
        assert isinstance(data["session_id"], str)

def test_full_session_flow():
    with client.websocket_connect("/ws/session/test-flow") as websocket:
        websocket.send_text(json.dumps({"language": "gu", "session_id": "test-flow"}))
        
        for i in range(3):
            msg = {
                "chunk_id": i,
                "audio_b64": make_fake_b64_chunk(3.0),
                "language": "gu",
                "sample_rate": 16000
            }
            websocket.send_text(json.dumps(msg))
            resp = websocket.receive_json()
            assert "score" in resp
            assert "verdict_so_far" in resp
            
        websocket.send_text(json.dumps({"action": "end_session"}))
        summary = websocket.receive_json()
        assert summary["audio_retained"] is False
        assert summary["total_chunks"] == 3

def test_oversized_chunk_rejected():
    with client.websocket_connect("/ws/session/test-size") as websocket:
        websocket.send_text(json.dumps({"language": "hi"}))
        
        large_bytes = b"0" * 600000
        large_b64 = base64.b64encode(large_bytes).decode()
        msg = {
            "chunk_id": 1,
            "audio_b64": large_b64,
            "language": "hi"
        }
        websocket.send_text(json.dumps(msg))
        resp = websocket.receive_json()
        assert "error" in resp
        assert resp["error"] == "chunk_too_large"

def test_invalid_json_recovers():
    with client.websocket_connect("/ws/session/test-json") as websocket:
        websocket.send_text(json.dumps({"language": "hi"}))
        websocket.send_text("this is not json")
        resp = websocket.receive_json()
        assert "error" in resp
        assert resp["error"] == "processing_error"
