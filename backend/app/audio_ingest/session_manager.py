from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List
import uuid
from fastapi import WebSocket
from app.config import settings

@dataclass
class SessionState:
    session_id: str
    language: str
    chunk_scores: List[int]
    started_at: datetime
    websocket: WebSocket
    last_activity: datetime

class SessionManager:
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}
    
    async def create_session(self, ws: WebSocket, language: str, session_id: str = None) -> str:
        if not session_id or session_id == "new":
            session_id = str(uuid.uuid4())
        
        self._sessions[session_id] = SessionState(
            session_id=session_id,
            language=language,
            chunk_scores=[],
            started_at=datetime.utcnow(),
            websocket=ws,
            last_activity=datetime.utcnow()
        )
        return session_id

    async def get_session(self, session_id: str) -> SessionState:
        return self._sessions.get(session_id)

    async def record_chunk_score(self, session_id: str, score: int):
        if session_id in self._sessions:
            self._sessions[session_id].chunk_scores.append(score)
            self._sessions[session_id].last_activity = datetime.utcnow()

    async def close_session(self, session_id: str) -> SessionState:
        return self._sessions.pop(session_id, None)

    async def cleanup_expired(self):
        now = datetime.utcnow()
        expired = [
            sid for sid, state in self._sessions.items()
            if (now - state.last_activity).total_seconds() > settings.session_ttl_seconds
        ]
        for sid in expired:
            await self.close_session(sid)
            
    def count(self) -> int:
        return len(self._sessions)
        
    def clear_all(self):
        self._sessions.clear()

session_manager = SessionManager()
