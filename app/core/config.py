from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    REDIS_URL: str = "redis://user:pass@localhost:6379/1"
    DATABASE_URL: str = "sqlite:///test.db"
    TESTING: bool = True


settings: Settings = Settings()
