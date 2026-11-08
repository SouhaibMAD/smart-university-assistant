from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    # PostgreSQL
    postgres_user: str = "sua"
    postgres_password: str = "change_me"
    postgres_db: str = "sua"
    postgres_host: str = "db"
    postgres_port: int = 5432

    # Groq
    groq_api_key: str = ""
    groq_model: str = "qwen/qwen3.8-27b"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1024

    # Embeddings
    embedding_model: str = "intfloat/multilingual-e5-base"
    embedding_dim: int = 768

    # RAG
    chunk_size: int = 1000
    chunk_overlap: int = 150
    top_k: int = 5
    min_score: float = 0.35
    max_upload_mb: int = 20

    # Auth / API
    jwt_secret: str = "change_me_long_random_string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    n8n_api_key: str = "change_me_n8n_key"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
