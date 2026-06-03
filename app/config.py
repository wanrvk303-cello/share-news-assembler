from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./stock_news.db"
    RSS_POLL_INTERVAL_MINUTES: int = 30
    NEWS_RETENTION_DAYS: int = 30
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
