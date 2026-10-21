import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base

client = TestClient(app)

def test_stats_endpoint():
    resp = client.get("/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["audio_retained_anywhere"] is False

def test_no_audio_column_in_schema():
    forbidden = ["audio", "wav", "pcm", "blob", "bytes"]
    for table_name, table in Base.metadata.tables.items():
        for column in table.columns:
            name = column.name.lower()
            for f in forbidden:
                assert f not in name, f"Column {name} in {table_name} contains forbidden word {f}"
