from functools import cached_property
import urllib.parse

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/intelscout"

    NVIDIA_API_KEY: str = ""
    PINECONE_API_KEY: str = ""
    SLACK_WEBHOOK_URL: str = ""

    CLERK_SECRET_KEY: str = ""
    CLERK_JWKS_URL: str = ""
    CLERK_JWT_ISSUER: str = ""
    CLERK_JWT_AUDIENCE: str = ""

    # Dev-only: allow x-user-id when Clerk JWKS is not configured (never in production)
    AUTH_ALLOW_DEV_HEADER: bool = False

    ALLOWED_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"
    HTTP_VERIFY_SSL: bool = True
    MAX_CONCURRENT_SCRAPE_JOBS: int = 3
    LLM_MAX_CONCURRENT: int = 3
    SCRAPE_JOB_SEMAPHORE: int = 2

    @field_validator("DATABASE_URL")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if not value:
            return value
        v = value.strip()
        if v.startswith("postgres://"):
            v = "postgresql+asyncpg://" + v[len("postgres://") :]
        elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            v = "postgresql+asyncpg://" + v[len("postgresql://") :]

        if v.startswith("postgresql+asyncpg://"):
            parsed = urllib.parse.urlsplit(v)
            query_params = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            if "sslmode" in query_params:
                ssl_val = query_params.pop("sslmode")[0]
                if "ssl" not in query_params:
                    query_params["ssl"] = [ssl_val]
            query_params.pop("channel_binding", None)
            query_params.pop("gssencmode", None)
            query_params.pop("target_session_attrs", None)
            new_query = urllib.parse.urlencode([(k, val[0]) for k, val in query_params.items()])
            v = urllib.parse.urlunsplit(
                (parsed.scheme, parsed.netloc, parsed.path, new_query, parsed.fragment)
            )

        return v

    @field_validator("ENVIRONMENT")
    @classmethod
    def normalize_environment(cls, value: str) -> str:
        return (value or "development").lower().strip()

    @cached_property
    def allowed_origins_list(self) -> list[str]:
        if not self.ALLOWED_ORIGINS.strip():
            return []
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @cached_property
    def clerk_jwks_url(self) -> str:
        if self.CLERK_JWKS_URL.strip():
            return self.CLERK_JWKS_URL.strip()
        if self.CLERK_JWT_ISSUER.strip():
            issuer = self.CLERK_JWT_ISSUER.rstrip("/")
            return f"{issuer}/.well-known/jwks.json"
        return ""

    def validate_for_production(self) -> None:
        if self.ENVIRONMENT != "production":
            return
        missing: list[str] = []
        if not self.DATABASE_URL:
            missing.append("DATABASE_URL")
        if not self.NVIDIA_API_KEY:
            missing.append("NVIDIA_API_KEY")
        if not self.PINECONE_API_KEY:
            missing.append("PINECONE_API_KEY")
        if not self.clerk_jwks_url and not self.CLERK_SECRET_KEY:
            missing.append("CLERK_JWKS_URL or CLERK_JWT_ISSUER")
        if self.AUTH_ALLOW_DEV_HEADER:
            raise ValueError("AUTH_ALLOW_DEV_HEADER must be false in production")
        if missing:
            raise ValueError(f"Missing required production environment variables: {', '.join(missing)}")


settings = Settings()
