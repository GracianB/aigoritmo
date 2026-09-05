from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = BACKEND_DIR.parent
LAB_DIR = PROJECT_DIR.parent
PIPER_CANDIDATES = (
    Path(r"X:\Aigoritmo\piper"),
    Path(r"X:\GitHub\systems-lab\Aigoritmo-legacy\piper"),
    LAB_DIR / "Aigoritmo-legacy" / "piper",
)


def resolve_piper_root() -> Path:
    for root in PIPER_CANDIDATES:
        if (root / "piper.exe").is_file() and (root / "models").is_dir():
            return root
    return PIPER_CANDIDATES[0]


PIPER_ROOT = resolve_piper_root()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "127.0.0.1"
    port: int = 8000

    # Empty = no global override; resolve via avatar preferred_provider then provider.
    # Set LLM_PROVIDER or FORCE_LLM_PROVIDER (e.g. spacexai) to force one provider.
    llm_provider: str = ""
    force_llm_provider: str = ""

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_vision_model: str = "llama3.2:3b"
    ollama_timeout: float = 180.0

    xai_api_key: str = ""
    xai_base_url: str = "https://api.x.ai/v1"
    xai_model: str = "grok-4.5"
    xai_vision_model: str = "grok-4.5"

    piper_executable: Path = Field(default_factory=lambda: PIPER_ROOT / "piper.exe")
    piper_models_dir: Path = Field(default_factory=lambda: PIPER_ROOT / "models")
    piper_fallback_voice: str = "es-odal-medium"
    default_avatar: str = "arcana"
    database_path: Path = Field(default_factory=lambda: PROJECT_DIR / "data" / "aigoritmo.db")

    @field_validator("host")
    @classmethod
    def localhost_only(cls, value: str) -> str:
        host = (value or "127.0.0.1").strip()
        if host in {"0.0.0.0", "::", "[::]"}:
            return "127.0.0.1"
        return host

    @field_validator("piper_executable", "piper_models_dir", mode="before")
    @classmethod
    def empty_path_uses_default(cls, value: object, info) -> object:
        if value is None or value == "":
            if info.field_name == "piper_executable":
                return PIPER_ROOT / "piper.exe"
            return PIPER_ROOT / "models"
        return value

    avatars_dir: Path = Field(default_factory=lambda: PROJECT_DIR / "avatars")
    media_dir: Path = Field(default_factory=lambda: PROJECT_DIR / "media")
    data_dir: Path = Field(default_factory=lambda: PROJECT_DIR / "data")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.media_dir / "audio").mkdir(parents=True, exist_ok=True)
    (settings.media_dir / "spreads").mkdir(parents=True, exist_ok=True)
    return settings
