"""
This module provides authentication-related endpoints for user registration and login.

Endpoints:
- POST /auth/register: Registers a new user in the system.
- POST /auth/login: Authenticates a user and returns an access token.
"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, UserModel, RequestEmail
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    get_current_user,
)
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_email
from src.conf.redis_client import get_redis_client
from src.conf import messages

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Registers a new user in the system.
    """

    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_EMAIL_ALREADY_EXISTS,
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=messages.USER_USERNAME_ALREADY_EXISTS,
        )
    user_data.password = Hash().get_password_hash(user_data.password)
    new_user = await user_service.create_user(user_data)

    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Logs in a user by verifying their credentials and generating an access token.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.USER_WRONG_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.USER_EMAIL_NOT_CONFIRMED,
        )
    redis_client = await get_redis_client()
    user_out = UserModel.from_orm(user)
    await redis_client.set(f"user:{user.id}", user_out.json(), ex=600)

    access_token = await create_access_token(data={"sub": user.username, "id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirmed email
    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Email already confirmed"}
    await user_service.confirmed_email(email)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Request email confirmation
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": "Email already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for the confirmation link"}


@router.post("/logout")
async def logout(user: str = Depends(get_current_user)):
    """
    Logs out the current user by deleting their session from the Redis cache.
    Args:
        user (str): The current user obtained from the dependency injection.
    Returns:
        dict: A message indicating the user has been logged out successfully.
    """

    redis_client = await get_redis_client()
    await redis_client.delete(f"user:{user.id}")
    return {"message": "Logged out successfully"}
