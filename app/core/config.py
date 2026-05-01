from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Market Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Redis connection
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0

    # Cache TTLs (seconds)
    PRICE_TTL: int = 30          # live stock price — refreshed every 30s
    SEARCH_TTL: int = 86_400     # search/company info — 1 day
    FUNDAMENTALS_TTL: int = 86_400  # PE ratio, financials — 1 day
    NIFTY50_TTL: int = 60      # Nifty 50 list — 1 minute
    INDICES_TTL: int = 60         # market indices (Nifty/Sensex) — 60s

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
