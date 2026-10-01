from typing import Optional
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

class Settings(BaseSettings):
    PROJECT_NAME: str = "IP-SAKTI Sahayak"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Environment & Modes
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    DEMO_MODE: bool = True
    CONFIDENTIAL_MODE_DEFAULT: bool = False
    FRONTEND_URL: Optional[str] = None
    ALLOWED_ORIGINS: list[str] = []

    # Database
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: Optional[int] = None
    POSTGRES_DB: Optional[str] = None
    DATABASE_URL: Optional[str] = None
    
    # Provider Abstractions
    LLM_PROVIDER: str = "mock"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-2.0-flash"
    
    EMBEDDING_PROVIDER: str = "mock"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    TRANSLATION_PROVIDER: str = "mock"
    BHASHINI_API_KEY: Optional[str] = None
    BHASHINI_USER_ID: Optional[str] = None
    BHASHINI_PIPELINE_ID: Optional[str] = None
    
    # RAG Settings
    RETRIEVAL_TOP_K: int = 5
    RERANK_TOP_K: int = 3
    MIN_EVIDENCE_SCORE: float = 0.70
    ABSTAIN_ON_LOW_CONFIDENCE: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore"
    )

    @model_validator(mode="after")
    def validate_production_mode(self):
        if self.ENVIRONMENT.lower() in {"production", "prod"} and self.DEMO_MODE:
            raise ValueError("DEMO_MODE must be false in production.")
        return self

    def get_database_url(self) -> str:
        if self.DATABASE_URL:
            database_url = self.DATABASE_URL.strip()
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
            elif database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
            if self.ENVIRONMENT.lower() in {"production", "prod"} and not database_url.startswith("postgresql+asyncpg://"):
                raise ValueError("Production DATABASE_URL must use PostgreSQL with the asyncpg driver.")
            return database_url

        postgres_settings = {
            "POSTGRES_USER": self.POSTGRES_USER,
            "POSTGRES_PASSWORD": self.POSTGRES_PASSWORD,
            "POSTGRES_HOST": self.POSTGRES_HOST,
            "POSTGRES_PORT": self.POSTGRES_PORT,
            "POSTGRES_DB": self.POSTGRES_DB,
        }
        if all(value is not None for value in postgres_settings.values()):
            return URL.create(
                "postgresql+asyncpg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_HOST,
                port=self.POSTGRES_PORT,
                database=self.POSTGRES_DB,
            ).render_as_string(hide_password=False)

        configured_postgres_fields = any(value is not None for value in postgres_settings.values())
        if configured_postgres_fields or self.ENVIRONMENT.lower() in {"production", "prod"}:
            raise ValueError("Set DATABASE_URL or provide all POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, and POSTGRES_DB settings.")

        return "sqlite+aiosqlite:///./ip_sakti_db.sqlite"

    def get_allowed_origins(self) -> list[str]:
        origins = [origin.strip().rstrip("/") for origin in self.ALLOWED_ORIGINS if origin.strip()]
        if self.FRONTEND_URL and self.FRONTEND_URL.strip():
            origins.append(self.FRONTEND_URL.strip().rstrip("/"))

        production = self.ENVIRONMENT.lower() in {"production", "prod"}
        if not production:
            origins.extend([
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://localhost:4173",
                "http://127.0.0.1:4173",
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ])

        if "*" in origins:
            raise ValueError("Wildcard CORS origins are not allowed.")
        if production and not origins:
            raise ValueError("Set FRONTEND_URL or ALLOWED_ORIGINS for production CORS.")
        if production and any(not origin.lower().startswith("https://") for origin in origins):
            raise ValueError("Production CORS origins must use HTTPS.")
        return list(dict.fromkeys(origins))

settings = Settings()
