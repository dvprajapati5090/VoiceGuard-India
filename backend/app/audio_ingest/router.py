import json
import time
from datetime import datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from app.audio_ingest.schemas import ChunkMessage, EndSessionMessage, ChunkResult, SessionSummary
from app.audio_ingest.session_manager import session_manager
from app.utils.audio_utils import decode_audio_chunk
from app.utils.privacy_guard import AudioSandbox
from app.config import settings
from app.database import AsyncSessionLocal, ChunkScoreRecord, SessionRecord
from app.detection.ensemble import EnsembleScorer

ws_router = APIRouter()
scorer = EnsembleScorer()

@ws_router.websocket("/session/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    try:
        first_msg_raw = await websocket.receive_text()
        first_msg = json.loads(first_msg_raw)
        language = first_msg.get("language", "hi")
        
        session_id = await session_manager.create_session(websocket, language, session_id)
        if first_msg.get("session_id") == "new":
            await websocket.send_json({"session_id": session_id})
            
    except Exception as e:
        await websocket.send_json({"error": "invalid_initial_message", "detail": str(e)})
        await websocket.close()
        return

    chunk_index = 0
    while True:
        try:
            data = await websocket.receive_text()
            msg_dict = json.loads(data)
            
            if "action" in msg_dict and msg_dict["action"] == "end_session":
                break
                
            chunk_msg = ChunkMessage(**msg_dict)
            
            if len(chunk_msg.audio_b64) > settings.max_chunk_bytes:
                await websocket.send_json({"error": "chunk_too_large"})
                continue
                
            audio_np = decode_audio_chunk(chunk_msg.audio_b64, chunk_msg.sample_rate)
            
            start_time = time.time()
            with AudioSandbox(audio_np) as sandbox_audio:
                score, proc_ms = scorer.score_chunk(sandbox_audio, chunk_msg.language, chunk_msg.sample_rate)
                
            # Timeout guard check handled in acoustic_model, but double check overall time
            if time.time() - start_time > 0.5:
                # Took too long
                pass
                
            await session_manager.record_chunk_score(session_id, score)
            
            verdict_so_far = "SAFE"
            if score >= 70:
                verdict_so_far = "CRITICAL"
            elif score >= 40:
                verdict_so_far = "SUSPICIOUS"
                
            res = ChunkResult(
                chunk_id=chunk_msg.chunk_id,
                score=score,
                language=chunk_msg.language,
                processing_ms=proc_ms,
                verdict_so_far=verdict_so_far
            )
            await websocket.send_json(res.model_dump())
            
            # Persist chunk to DB (NO AUDIO)
            async with AsyncSessionLocal() as db_session:
                record = ChunkScoreRecord(
                    session_id=session_id,
                    chunk_index=chunk_index,
                    scored_at=datetime.utcnow(),
                    score=score,
                    language=chunk_msg.language,
                    processing_ms=proc_ms
                )
                db_session.add(record)
                await db_session.commit()
                
            chunk_index += 1
            
        except WebSocketDisconnect:
            break
        except Exception as e:
            await websocket.send_json({"error": "processing_error", "detail": str(e)})

    # Session end handling
    state = await session_manager.get_session(session_id)
    if state:
        final_verdict, confidence = scorer.compute_final_verdict(state.chunk_scores)
        ended_at = datetime.utcnow()
        
        summary = SessionSummary(
            session_id=session_id,
            language=state.language,
            chunk_scores=state.chunk_scores,
            final_verdict=final_verdict,
            confidence=confidence,
            total_chunks=len(state.chunk_scores),
            audio_retained=False,
            started_at=state.started_at.isoformat(),
            ended_at=ended_at.isoformat()
        )
        
        try:
            await websocket.send_json(summary.model_dump())
        except Exception:
            pass
            
        async with AsyncSessionLocal() as db_session:
            db_session.add(SessionRecord(
                id=session_id,
                started_at=state.started_at,
                ended_at=ended_at,
                language=state.language,
                final_verdict=final_verdict,
                confidence=confidence,
                total_chunks=len(state.chunk_scores),
                audio_retained=False
            ))
            await db_session.commit()
            
        await session_manager.close_session(session_id)
