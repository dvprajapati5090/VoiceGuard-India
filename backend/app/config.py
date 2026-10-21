from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    env: str = "development"
    database_url: str = "sqlite+aiosqlite:///./voiceguard_audit.db"
    model_name: str = "facebook/wav2vec2-large-xlsr-53"
    score_threshold: int = 70
    max_chunk_bytes: int = 500_000
    session_ttl_seconds: int = 3600

    class Config:
        env_file = ".env"

settings = Settings()
