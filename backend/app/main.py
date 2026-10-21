import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.detection.acoustic_model import XLSRAcousticModel
from app.audio_ingest.session_manager import session_manager
from app.audio_ingest.router import ws_router
from app.audit.router import audit_router
from app.detection.router import detect_router

async def periodic_session_cleanup():
    while True:
        await asyncio.sleep(300)
        await session_manager.cleanup_expired()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    print("? VoiceGuard India starting up...")
    await init_db()
    
    print("?? Loading XLS-R acoustic model (may take 30-60s first run)...")
    try:
        XLSRAcousticModel.get_instance()
    except ImportError:
        print("?? Torch not installed, skipping XLS-R acoustic model load.")
    print("? Model loaded. VoiceGuard India is ready.")
    
    cleanup_task = asyncio.create_task(periodic_session_cleanup())
    
    yield
    
    # SHUTDOWN
    print("?? VoiceGuard shutting down. Clearing all in-memory session state...")
    cleanup_task.cancel()
    session_manager.clear_all()

app = FastAPI(
    title="VoiceGuard India API",
    description="Real-time voice-clone detection for Indian-language calls. Privacy by architecture.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    # STRETCH: Add JWT auth middleware for production API key gating
    # STRETCH: Add Prometheus metrics endpoint /metrics
    return {
        "status": "ok",
        "model_loaded": XLSRAcousticModel.get_instance().is_loaded,
        "active_sessions": session_manager.count(),
        "version": "1.0.0"
    }

app.include_router(ws_router, prefix="/ws", tags=["ingest"])
app.include_router(audit_router, prefix="", tags=["audit"])
app.include_router(detect_router, prefix="/api", tags=["detect"])
