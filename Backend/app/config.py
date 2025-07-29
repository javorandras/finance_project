from dataclasses import dataclass
from datetime import timedelta

from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class Settings:
    PROJECT_NAME: str = "Finance Categorizer"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    TOKEN_EXPIRE_MINUTES: int = 15
    TOKEN_EXPIRE_SECONDS: int = 0
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SECURE_COOKIES: bool = True
    V1_PREFIX: str = "/api/v1"
    AUTH_HEADER: str = "Bearer"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def TOKEN_EXPIRE_DELTA(self):
        return timedelta(minutes=self.TOKEN_EXPIRE_MINUTES, seconds=self.TOKEN_EXPIRE_SECONDS)

    class Endpoints:
        TRANSACTIONS = "/transactions"
        USERS = "/users"
        PREDICTIONS = "/predictions"
        ADMIN = "/admin"

settings = Settings()