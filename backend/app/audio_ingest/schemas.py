from pydantic import BaseModel
from typing import Literal

class ChunkMessage(BaseModel):
    chunk_id: int
    audio_b64: str          # base64-encoded raw PCM, 16kHz mono, 16-bit LE
    language: Literal["hi", "gu"]
    sample_rate: int = 16000

class EndSessionMessage(BaseModel):
    action: Literal["end_session"]

class ChunkResult(BaseModel):
    chunk_id: int
    score: int              # 0-100
    language: str
    processing_ms: int
    verdict_so_far: str     # "SAFE" | "SUSPICIOUS" | "CRITICAL"

class SessionSummary(BaseModel):
    session_id: str
    language: str
    chunk_scores: list[int]
    final_verdict: str      # "SYNTHETIC" | "AUTHENTIC" | "INCONCLUSIVE"
    confidence: float
    total_chunks: int
    audio_retained: bool    # always False
    started_at: str
    ended_at: str

