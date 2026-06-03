from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_host: str = "0.0.0.0"
    app_port: int = 8080
    debug: bool = True
    secret_key: str = "dev-secret-key-change-in-production"
    database_url: str = "mysql+pymysql://root:123456@localhost:3306/pdf_vl?charset=utf8mb4"
    upload_dir: str = str(BASE_DIR / "uploads")
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    ai_provider: str = "kimi"  # kimi | mock | local
    moonshot_api_key: str = ""
    moonshot_base_url: str = "https://api.moonshot.cn/v1"
    kimi_model: str = "kimi-k2.5"
    local_base_url: str = "http://localhost:11434/v1"
    local_api_key: str = "ollama"
    local_model: str = "qwen3-vl:8b"
    ai_request_timeout: int = 120

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def upload_path(self) -> Path:
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
