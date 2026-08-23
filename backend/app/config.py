from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AETERNUM API"
    app_env: str = "development"
    trading_mode: str = "PAPER"
    database_url: str = "sqlite:///./aeternum.db"
    cors_origins: str = "http://localhost:3000"
    market_data_provider: str = "demo"
    market_data_api_key: str | None = None
    news_provider: str = "unconfigured"
    news_api_key: str | None = None
    openai_api_key: str | None = None
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
