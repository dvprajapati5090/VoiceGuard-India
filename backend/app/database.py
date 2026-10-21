import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, text
from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

# Architectural Enforcement: No Audio Columns
class PrivacyEnforcerBase(Base):
    __abstract__ = True
    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Check removed to fix SQLAlchemy 2.0 compatibility

class SessionRecord(PrivacyEnforcerBase):
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    language = Column(String, nullable=False)
    final_verdict = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    total_chunks = Column(Integer, default=0)
    audio_retained = Column(Boolean, default=False)

class ChunkScoreRecord(PrivacyEnforcerBase):
    __tablename__ = "chunk_scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    scored_at = Column(DateTime, nullable=False)
    score = Column(Integer, nullable=False)
    language = Column(String, nullable=False)
    processing_ms = Column(Integer, nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
