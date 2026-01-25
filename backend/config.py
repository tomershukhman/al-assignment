from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MATHPIX_APP_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OCR_CONFIDENCE_THRESHOLD: float = 0.2
    
    # Server Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # File Upload Settings
    UPLOAD_URL_PREFIX: str = "/api/uploads"
    
    @property
    def UPLOADS_DIR(self) -> Path:
        # Resolves to project_root/uploads
        # config.py is in backend/, so parent is backend, parent.parent is project root
        return Path(__file__).parent.parent / "uploads"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
