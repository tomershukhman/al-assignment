from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    MATHPIX_APP_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    OCR_CONFIDENCE_THRESHOLD: float = 0.2

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
