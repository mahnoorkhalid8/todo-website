try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    SECRET_KEY: str = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "o2nmkwIUqotG5dDCWR0a0rk2Uk2rL0DPBvqbdkwZ54N"))
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")

    @classmethod
    def get_default_expire_minutes(cls) -> int:
        """Get default access token expire minutes with error handling"""
        try:
            value = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
            return int(value)
        except (ValueError, TypeError):
            return 30

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Will be overridden in __init_subclass__
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://neondb_owner:npg_1wiNqRWc4MPh@ep-sparkling-term-a4onppqn-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require")
    ALLOWED_ORIGINS: List[str] = [
        "https://todo-website-bot.vercel.app",
        "https://mahnoorkhalid8-todo-bot.hf.space",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:8000"
    ]

    def __init__(self, **values):
        # Set ACCESS_TOKEN_EXPIRE_MINUTES with error handling
        expire_str = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
        try:
            values.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', int(expire_str))
        except (ValueError, TypeError):
            values.setdefault('ACCESS_TOKEN_EXPIRE_MINUTES', 30)

        super().__init__(**values)

    class Config:
        env_file = ".env"


settings = Settings()