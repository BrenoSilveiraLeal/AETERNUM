from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AETERNUM API"
    trading_mode: str = "PAPER"
    database_url: str = "sqlite:///./aeternum.db"
    cors_origins: str = "http://localhost:3000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
