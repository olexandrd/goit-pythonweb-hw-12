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


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
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
        if username is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user


def create_email_token(data: dict):
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


async def get_email_from_token(token: str):
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
