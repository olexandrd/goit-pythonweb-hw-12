"""


This module contains the configuration settings for the application.

Classes:
    Settings: A Pydantic BaseSettings class that defines the configuration settings for the application.

Attributes:
    DB_URL (str): The database URL.
    JWT_SECRET (str): The secret key used for JWT encoding and decoding.
    JWT_ALGORITHM (str): The algorithm used for JWT encoding. Default is "HS256".
    JWT_EXPIRATION_SECONDS (int): The expiration time for JWT tokens in seconds. Default is 120 seconds.
    JWT_REFRESH_EXPIRATION_SECONDS (int): The expiration time for JWT refresh tokens in seconds. Default is 600 seconds.
    REDIS_HOST (str): The hostname for the Redis server. Default is "localhost".
    REDIS_PORT (int): The port number for the Redis server. Default is 6379.
    MAIL_USERNAME (EmailStr): The username for the mail server.
    MAIL_PASSWORD (str): The password for the mail server.
    MAIL_FROM (EmailStr): The email address from which emails are sent.
    MAIL_PORT (int): The port number for the mail server. Default is 1080.
    MAIL_SERVER (str): The mail server address. Default is "mailcatcher".
    MAIL_FROM_NAME (str): The name displayed in the "from" field of sent emails. Default is "Rest API Service".
    MAIL_STARTTLS (bool): Whether to use STARTTLS for the mail server. Default is False.
    MAIL_SSL_TLS (bool): Whether to use SSL/TLS for the mail server. Default is False.
    USE_CREDENTIALS (bool): Whether to use credentials for the mail server. Default is False.
    VALIDATE_CERTS (bool): Whether to validate certificates for the mail server. Default is False.
    CLD_NAME (str): The Cloudinary cloud name.
    CLD_API_KEY (int): The Cloudinary API key.
    CLD_API_SECRET (str): The Cloudinary API secret.
    model_config (ConfigDict): Configuration for the Pydantic model, including environment file settings and case sensitivity.

Instances:
    settings (Settings): An instance of the Settings class with the configuration loaded from the environment file.

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
