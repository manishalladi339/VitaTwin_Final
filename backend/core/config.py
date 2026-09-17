from dataclasses import dataclass
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    mongo_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "vitatwin")
    jwt_secret: str = os.getenv("JWT_SECRET", "local-development-secret-change-me")
    jwt_hours: int = int(os.getenv("JWT_HOURS", "24"))
    app_env: str = os.getenv("APP_ENV", "development")
    cors_origins_raw: str = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    openai_api_base: str = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    def validate(self) -> None:
        if self.app_env == "production":
            if len(self.jwt_secret) < 32 or self.jwt_secret.startswith("local-"):
                raise RuntimeError("JWT_SECRET must be a unique value of at least 32 characters")
            if "*" in self.cors_origins:
                raise RuntimeError("CORS_ORIGINS must be explicit in production")


settings = Settings()
