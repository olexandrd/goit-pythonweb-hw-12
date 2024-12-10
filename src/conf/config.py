"""
Configuration settings for the application
"""

from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Settings class for the application configuration.
    """

    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 120
    JWT_REFRESH_EXPIRATION_SECONDS: int = 600

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int = 1080
    MAIL_SERVER: str = "mailcatcher"
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = False
    VALIDATE_CERTS: bool = False

    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


settings = Settings()
