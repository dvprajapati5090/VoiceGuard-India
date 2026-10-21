from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, Boolean
from typing import List
from app.database import get_db, SessionRecord, ChunkScoreRecord
from app.audit.schemas import SessionSummaryResponse, ChunkScoreRecordResponse

audit_router = APIRouter()

@audit_router.get("/sessions", response_model=List[SessionSummaryResponse])
async def get_sessions(
    limit: int = 50, 
    offset: int = 0, 
    verdict: str = None, 
    language: str = None, 
    db: AsyncSession = Depends(get_db)
):
    q = select(SessionRecord)
    if verdict:
        q = q.where(SessionRecord.final_verdict == verdict)
    if language:
        q = q.where(SessionRecord.language == language)
        
    q = q.limit(limit).offset(offset).order_by(SessionRecord.started_at.desc())
    res = await db.execute(q)
    records = res.scalars().all()
    
    out = []
    for r in records:
        out.append(SessionSummaryResponse(
            session_id=r.id,
            started_at=r.started_at.isoformat(),
            ended_at=r.ended_at.isoformat() if r.ended_at else None,
            language=r.language,
            final_verdict=r.final_verdict,
            confidence=r.confidence,
            total_chunks=r.total_chunks,
            audio_retained=r.audio_retained
        ))
    return out

@audit_router.get("/sessions/{session_id}", response_model=SessionSummaryResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(SessionRecord).where(SessionRecord.id == session_id))
    r = res.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Session not found")
        
    chunks_res = await db.execute(select(ChunkScoreRecord).where(ChunkScoreRecord.session_id == session_id).order_by(ChunkScoreRecord.chunk_index))
    chunks = chunks_res.scalars().all()
    
    chunk_list = [
        ChunkScoreRecordResponse(
            chunk_index=c.chunk_index,
            scored_at=c.scored_at.isoformat(),
            score=c.score,
            language=c.language,
            processing_ms=c.processing_ms
        ) for c in chunks
    ]
    
    return SessionSummaryResponse(
        session_id=r.id,
        started_at=r.started_at.isoformat(),
        ended_at=r.ended_at.isoformat() if r.ended_at else None,
        language=r.language,
        final_verdict=r.final_verdict,
        confidence=r.confidence,
        total_chunks=r.total_chunks,
        audio_retained=r.audio_retained,
        chunks=chunk_list
    )

@audit_router.get("/sessions/{session_id}/chunks", response_model=List[ChunkScoreRecordResponse])
async def get_session_chunks(session_id: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ChunkScoreRecord).where(ChunkScoreRecord.session_id == session_id).order_by(ChunkScoreRecord.chunk_index))
    chunks = res.scalars().all()
    return [
        ChunkScoreRecordResponse(
            chunk_index=c.chunk_index,
            scored_at=c.scored_at.isoformat(),
            score=c.score,
            language=c.language,
            processing_ms=c.processing_ms
        ) for c in chunks
    ]

@audit_router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count(SessionRecord.id)))
    synth = await db.scalar(select(func.count(SessionRecord.id)).where(SessionRecord.final_verdict == "SYNTHETIC"))
    auth = await db.scalar(select(func.count(SessionRecord.id)).where(SessionRecord.final_verdict == "AUTHENTIC"))
    inconclusive = await db.scalar(select(func.count(SessionRecord.id)).where(SessionRecord.final_verdict == "INCONCLUSIVE"))
    
    avg_conf = await db.scalar(select(func.avg(SessionRecord.confidence)))
    
    hi_count = await db.scalar(select(func.count(SessionRecord.id)).where(SessionRecord.language == "hi"))
    gu_count = await db.scalar(select(func.count(SessionRecord.id)).where(SessionRecord.language == "gu"))
    
    audio_retained_check = await db.scalar(select(func.count(SessionRecord.id)).where(SessionRecord.audio_retained == True))
    
    return {
       "total_sessions": total or 0,
       "synthetic_detected": synth or 0,
       "authentic_verified": auth or 0,
       "inconclusive": inconclusive or 0,
       "avg_confidence": avg_conf or 0.0,
       "by_language": {"hi": hi_count or 0, "gu": gu_count or 0},
       "audio_retained_anywhere": (audio_retained_check or 0) > 0
    }
