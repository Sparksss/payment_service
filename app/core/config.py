from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "Payment Service API"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"
    BANK_API_URL: str = "https://api.examplebank.com"
    BANK_API_KEY: str = "your_bank_api_key"
    BANK_TIMEOUT: float = 5.0

    model_config = SettingsConfigDict(env_file=".env",extra="ignore")

settings = Settings()