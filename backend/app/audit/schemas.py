from pydantic import BaseModel
from typing import List, Optional

class ChunkScoreRecordResponse(BaseModel):
    chunk_index: int
    scored_at: str
    score: int
    language: str
    processing_ms: Optional[int]
    
    class Config:
        from_attributes = True

class SessionSummaryResponse(BaseModel):
    session_id: str
    started_at: str
    ended_at: Optional[str]
    language: str
    final_verdict: Optional[str]
    confidence: Optional[float]
    total_chunks: int
    audio_retained: bool
    chunks: Optional[List[ChunkScoreRecordResponse]] = None
    
    class Config:
        from_attributes = True
