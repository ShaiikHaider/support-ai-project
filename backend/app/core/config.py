"""
Central application configuration.
All values are overridable via environment variables (.env locally,
Render/Vercel dashboard env vars in production).
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    APP_NAME: str = "Agentic AI Customer Support Resolution System"
    ENVIRONMENT: str = "development"
    API_V1_PREFIX: str = "/api/v1"

    # --- CORS ---
    
    from pydantic import field_validator
    
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str):
            import json
            return json.loads(v)
        return v


    # --- Auth / JWT ---
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    # --- Database (PostgreSQL) ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/support_ai"

    # --- Redis (short-term memory / session cache) ---
    REDIS_URL: str = "redis://localhost:6379/0"
    CONVERSATION_MEMORY_TTL_SECONDS: int = 60 * 60 * 6  # 6 hours of short-term memory

    # --- Vector store (RAG knowledge base) ---
    CHROMA_PERSIST_DIR: str = "./chroma_store"
    KB_COLLECTION_NAME: str = "support_knowledge_base"

    # --- LLM Provider ---
    LLM_PROVIDER: str = "openrouter"
    LLM_BASE_URL: str = "https://openrouter.ai/api/v1"
    LLM_API_KEY: str = ""
    LLM_CHAT_MODEL: str = "nvidia/nemotron-3-ultra-550b-a55b:free"
    LLM_REASONING_ENABLED: bool = False
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    MAX_LLM_CALLS_PER_TICKET: int = 20

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-sonnet-4-6"

    # --- Escalation ---
    ESCALATION_EMAIL_TO: str = "support-escalations@brightcone.ai"
    HIGH_RISK_ACTIONS: List[str] = [
        "refund",
        "account_deletion",
        "subscription_cancellation",
        "chargeback_dispute",
        "data_export",
        "identity_change",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

