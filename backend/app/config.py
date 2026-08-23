from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AETERNUM API"
    app_env: str = "development"
    trading_mode: str = "PAPER"
    database_url: str = "sqlite:///./aeternum.db"
    postgres_url: str | None = None
    cors_origins: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3010,http://localhost:3011,http://localhost:3012,http://localhost:3013,http://localhost:3014,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:3010,http://127.0.0.1:3011,http://127.0.0.1:3012,http://127.0.0.1:3013,http://127.0.0.1:3014"
    market_data_provider: str = "brapi"
    market_data_api_url: str = "https://brapi.dev/api"
    market_data_api_token: str | None = None
    market_data_api_key: str | None = None
    b3_api_enabled: bool = False
    b3_api_url: str | None = None
    b3_client_id: str | None = None
    b3_client_secret: str | None = None
    market_poll_interval_seconds: int = 300
    news_poll_interval_seconds: int = 900
    macro_poll_interval_seconds: int = 3600
    worker_enabled: bool = False
    news_provider: str = "rss"
    news_api_key: str | None = None
    news_api_url: str = "https://newsapi.org/v2"
    news_rss_urls: str = "https://www.cvm.gov.br/feed/decisoes.xml,https://www.cvm.gov.br/feed/legislacao.xml,https://www.cvm.gov.br/feed/audiencias.xml,https://www.gov.br/pt-br/noticias/ultimas-noticias/RSS"
    openai_api_key: str | None = None
    ai_api_key: str | None = None
    ai_provider: str = "gemini"
    ai_model: str = "gemini-3.5-flash-lite"
    model_config = SettingsConfigDict(env_file=("backend/.env", ".env"), extra="ignore")


settings = Settings()
