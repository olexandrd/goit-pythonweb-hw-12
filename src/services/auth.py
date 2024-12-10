"""
This module provides authentication services including password hashing, 
    token generation, and user retrieval.

Classes:
    Hash: Provides methods to hash and verify passwords using bcrypt.

Functions:
    create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:

    get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    create_email_token(data: dict) -> str:
        Creates a confirmation token for the given data with an expiration of 7 days.

    get_email_from_token(token: str) -> str:
        Retrieves the email from the provided JWT token.

"""

import json

from typing import Optional
from datetime import datetime, timedelta, UTC
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.schemas import UserModel
from src.database.models import User, UserRole
from src.conf.redis_client import get_redis_client
from src.conf import messages


class Hash:
    """
    Hash class provides methods to hash and verify passwords using bcrypt.

    Attributes:
        pwd_context (CryptContext): The context for password hashing and verification.

    Methods:
        verify_password(plain_password, hashed_password):
            Verifies a plain password against a hashed password.

        get_password_hash(password: str):
            Hashes a plain password and returns the hashed password.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verify if the provided plain password matches the hashed password.

        Args:
            plain_password (str): The plain text password to verify.
            hashed_password (str): The hashed password to compare against.

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hashes the provided password using the password context.

        Args:
            password (str): The plain text password to be hashed.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# define a function to generate a new access token
async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Creates a JSON Web Token (JWT) for the given data with an optional expiration time.

    Args:
        data (dict): The data to encode in the JWT.
        expires_delta (Optional[int], optional): The number of seconds until the token expires.
                If not provided, defaults to the configured expiration time.

    Returns:
        str: The encoded JWT.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def store_refresh_token(user_id: int, refresh_token: str):
    """
    Store the refresh token in Redis with an expiration time.

    Args:
        user_id (int): The ID of the user.
        refresh_token (str): The refresh token to store.
    """
    redis_client = await get_redis_client()
    await redis_client.set(
        f"refresh_token:{user_id}",
        refresh_token,
        ex=settings.JWT_REFRESH_EXPIRATION_SECONDS,
    )


async def create_refresh_token(data: dict, expires_delta: Optional[int] = None):
    """
    Creates a refresh token with an optional expiration time.
    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[int], optional): The time in seconds until the token expires.
            If not provided, the default expiration time from settings is used.
    Returns:
        str: The encoded JWT refresh token.
    """

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(
            days=settings.JWT_REFRESH_EXPIRATION_SECONDS
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """
    Retrieve the current user based on the provided JWT token.

    Args:
        token (str): The JWT token provided by the user.
        db (Session): The database session dependency.

    Returns:
        User: The user object corresponding to the username in the token.

    Raises:
        HTTPException: If the token is invalid or the user does not exist.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload["sub"]
        user_id = payload["id"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    redis_client = await get_redis_client()
    cached_user = await redis_client.get(f"user:{user_id}")
    if cached_user:
        user_data = json.loads(cached_user)
        return User.from_dict(user_data)

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    user_out = UserModel.from_orm(user)
    await redis_client.set(
        f"user:{user.id}",
        user_out.json(),
        ex=3600,
    )
    return user


def create_email_token(data: dict) -> str:
    """
    Create a configmation token for the given data with an expiration of 7 days.
    Args:
        data (dict): The data to encode in the token.
    Returns:
        str: The encoded JWT token.
    """

    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return token


def is_current_user_admin(current_user: User = Depends(get_current_user)) -> bool:
    """
    Check if the current user has an admin role.
    Args:
        current_user (User): The user object obtained from the dependency injection.
    Returns:
        bool: True if the current user's role is admin, False otherwise.
    """

    return current_user.role == UserRole.ADMIN


async def get_email_from_token(token: str) -> str:
    """
    Retrieve the email from the provided JWT token.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Wrong token",
        ) from e


async def get_user_id_from_token(token: str) -> int:
    """
    Retrieve the user ID from the provided JWT token.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload["id"]
        return user_id
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Wrong token",
        ) from e


async def get_password_from_token(token: str):
    """
    Extracts the password from a given JWT token.
    Args:
        token (str): The JWT token from which to extract the password.
    Returns:
        str: The password extracted from the token.
    Raises:
        HTTPException: If the token is invalid or cannot be decoded.
    """

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        password = payload["password"]
        return password
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=messages.ERROR_WRONG_TOKEN,
        ) from exc
