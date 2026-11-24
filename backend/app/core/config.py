from typing import List, Optional
import os
from pydantic_settings import BaseSettings
from pydantic import field_validator

def parse_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url

class Settings(BaseSettings):
    PROJECT_NAME: str = "MatchIQ — Opportunity Intelligence Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Security
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/matchiq")
    # For standalone SQLite fallback during local development/evaluation if PostgreSQL is offline
    SQLITE_FALLBACK_URL: str = "sqlite:///./matchiq.db"
    
    # AI Models
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION: int = 384
    RERANKER_MODEL_NAME: str = os.getenv("RERANKER_MODEL_NAME", "cross-encoder/ms-marco-MiniLM-L-6-v2")
    ENABLE_CROSS_ENCODER_DEFAULT: bool = False
    
    # Google Gemini API
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
    
    # CORS
    BACKEND_CORS_ORIGINS: str = os.getenv(
        "BACKEND_CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000"
    )
    
    # RRF (Reciprocal Rank Fusion) Hyperparameters
    RRF_K: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value):
        return parse_database_url(str(value))

    def cors_origins(self) -> List[str]:
        return [
            origin.strip().rstrip("/")
            for origin in str(self.BACKEND_CORS_ORIGINS).split(",")
            if origin.strip()
        ]

    def validate_production(self) -> None:
        if self.ENVIRONMENT.lower() == "production":
            if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
                raise RuntimeError("SECRET_KEY must contain at least 32 characters in production.")
            if "*" in self.cors_origins():
                raise RuntimeError("Wildcard CORS origin is prohibited in production.")

settings = Settings()
