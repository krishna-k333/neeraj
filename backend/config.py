from pydantic_settings import BaseSettings
from datetime import date

class Settings(BaseSettings):
    EVOLUTION_API_URL: str = "http://whats-evolution-api.vvbe62.easypanel.host"
    EVOLUTION_API_KEY: str = "429683C4C977415CAAFCCE10F7D57E11"
    EVOLUTION_INSTANCE: str = "neeraj1"

    WA_ACCOUNT_START_DATE: date = date(2026, 7, 3)

    AI_API_KEY: str = ""
    AI_MODEL: str = ""

    # Gemini — used only to "see" inbound customer photos (product images).
    # Sarvam stays the text brain; Gemini's description feeds into it.
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.5-flash-lite"

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    VIDEO_AI_API_KEY: str = ""

    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REFRESH_TOKEN: str = ""

    POSTIZ_URL: str = "http://postiz:5000"
    POSTIZ_API_KEY: str = ""

    DATABASE_URL: str = "sqlite+aiosqlite:///./neeraj.db"
    SECRET_KEY: str = "change-me"
    FRONTEND_URL: str = "http://localhost:3000"

    N8N_THANKYOU_WEBHOOK: str = "98d5228d-32e5-4064-84fd-af63ad59cee2"

    class Config:
        env_file = ".env"

settings = Settings()
