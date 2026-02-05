from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Database settings
    database_url: str = "postgresql+asyncpg://username:password@localhost/dbname"

    @property
    def sync_database_url(self) -> str:
        """
        Convert async database URL to sync version for synchronous operations.
        Replaces asyncpg with psycopg (psycopg3 sync mode) and adds SSL for Neon.
        """
        url = self.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")
        separator = "&" if "?" in url else "?"
        return f"{url}{separator}sslmode=require"

    # LLM settings
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_base_url: Optional[str] = None
    llm_api_key: Optional[str] = None

    # OpenAI-specific settings
    openai_api_key: Optional[str] = None

    # MCP settings
    mcp_host: str = "localhost"
    mcp_port: int = 8001

    # Server settings
    server_host: str = "localhost"
    server_port: int = 8000
    request_timeout_seconds: float = 30.0

    # CORS settings (comma-separated list of allowed origins, "*" = allow all)
    cors_origins: str = "*"

    # Logging settings
    log_level: str = "INFO"

    # Authentication settings
    better_auth_secret: str = "dev-secret-key-minimum-32-characters-long-for-development"
    jwt_algorithm: str = "HS256"
    jwt_expiry_days: int = 7

    @model_validator(mode="after")
    def validate_auth_secret(self) -> "Settings":
        """Validate that BETTER_AUTH_SECRET is at least 32 characters."""
        if len(self.better_auth_secret) < 32:
            raise ValueError(
                "BETTER_AUTH_SECRET must be at least 32 characters long. "
                f"Current length: {len(self.better_auth_secret)}. "
                "Generate a secure secret with: openssl rand -hex 32"
            )
        return self

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }


# Create a global settings instance
settings = Settings()