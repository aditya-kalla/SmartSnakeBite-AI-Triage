import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
    class Settings(BaseSettings):
        host: str = "127.0.0.1"
        port: int = 8000
        env: str = "development"
        
        # HuggingFace / External URLs for model downloading (optional fallback)
        tts_model_url: Optional[str] = None
        stt_model_url: Optional[str] = None
        classifier_model_url: Optional[str] = None

        model_config = SettingsConfigDict(
            env_file=os.path.join(os.path.dirname(__file__), ".env"),
            env_file_encoding="utf-8",
            extra="ignore"
        )
except ImportError:
    try:
        from pydantic import BaseSettings
        class Settings(BaseSettings):
            host: str = "127.0.0.1"
            port: int = 8000
            env: str = "development"
            
            tts_model_url: Optional[str] = None
            stt_model_url: Optional[str] = None
            classifier_model_url: Optional[str] = None

            class Config:
                env_file = os.path.join(os.path.dirname(__file__), ".env")
                extra = "ignore"
    except ImportError:
        # Fallback setting class if neither is available
        class Settings:
            def __init__(self):
                self.host = os.getenv("HOST", "127.0.0.1")
                self.port = int(os.getenv("PORT", "8000"))
                self.env = os.getenv("ENV", "development")
                self.tts_model_url = os.getenv("TTS_MODEL_URL")
                self.stt_model_url = os.getenv("STT_MODEL_URL")
                self.classifier_model_url = os.getenv("CLASSIFIER_MODEL_URL")

settings = Settings()
