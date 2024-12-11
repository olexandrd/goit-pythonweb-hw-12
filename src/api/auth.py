"""
This module provides authentication and authorization endpoints for the FastAPI application.

Endpoints:
- POST /auth/register: Registers a new user.
- POST /auth/login: Authenticates a user and generates access and refresh tokens.
- GET /auth/confirmed_email/{token}: Confirms the user's email address using the provided token.
- POST /auth/request_email: Requests email confirmation for a user.
- POST /auth/token/refresh: Refreshes the access token using the provided refresh token.
- POST /auth/logout: Logs out the current user by deleting their session from the Redis cache.
- POST /auth/reset_password: Handles a password reset request by generating a reset token and sending a reset password email.
- GET /auth/confirm_reset_password/{token}: Confirms and resets the user's password using the provided token.

Dependencies:
- FastAPI
- SQLAlchemy
- Redis

Imports:
- FastAPI dependencies: APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
- FastAPI security: OAuth2PasswordRequestForm
- Schemas: UserCreate, Token, RefreshToken, UserModel, RequestEmail, ResetPassword
- Services: create_access_token, Hash, get_email_from_token, get_current_user, get_password_from_token, create_refresh_token, get_user_id_from_token
- User service: UserService
- Database: get_db
- Email services: send_registration_email, send_reset_password_email
- Redis client: get_redis_client
- Configuration: settings
- Messages: messages

"""

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import (
    UserCreate,
    Token,
    RefreshToken,
    UserModel,
    RequestEmail,
    ResetPassword,
)
from src.services.auth import (
    create_access_token,
    Hash,
    get_email_from_token,
    get_current_user,
    get_password_from_token,
    create_refresh_token,
    get_user_id_from_token,
)
from src.services.users import UserService
from src.database.db import get_db
from src.services.email import send_registration_email, send_reset_password_email
from src.conf.redis_client import get_redis_client
from src.conf.config import settings
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

    Args:
        user_data (UserCreate): The data required to create a new user.
        background_tasks (BackgroundTasks): The background tasks to be executed.
        request (Request): The request object.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Raises:
        HTTPException: If a user with the given email already exists.
        HTTPException: If a user with the given username already exists.

    Returns:
        User: The newly created user.

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
        send_registration_email, new_user.email, new_user.username, request.base_url
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Authenticate a user and generate access and refresh tokens.

    Args:
        form_data (OAuth2PasswordRequestForm): The form data containing the username and password.
        db (Session): The database session dependency.

    Returns:
        dict: A dictionary containing the access token, refresh token, and token type.

    Raises:
        HTTPException: If the user credentials are incorrect or the user's email is not confirmed.

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

    access_token = await create_access_token(data={"sub": user.username, "id": user.id})
    refresh_token = await create_refresh_token(
        data={"sub": user.username, "id": user.id}
    )
    await redis_client.set(
        f"user:{user.id}", user_out.json(), ex=settings.JWT_REFRESH_EXPIRATION_SECONDS
    )
    await redis_client.set(
        f"refresh_token:{user.id}",
        refresh_token,
        ex=settings.JWT_REFRESH_EXPIRATION_SECONDS,
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirm the user's email address using the provided token.

    Args:
        token (str): The token used to confirm the email address.
        db (Session, optional): The database session dependency.

    Raises:
        HTTPException: If the user is not found or if there is a verification error.

    Returns:
        dict: A message indicating whether the email was confirmed or already confirmed.

    """
    email = await get_email_from_token(token)
    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": messages.USER_EMAIL_ALREADY_CONFIRMED}
    await user_service.confirmed_email(email)
    return {"message": messages.USER_EMAIL_CONFIRMED}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Args:
        body (RequestEmail): The request body containing the email to be confirmed.
        background_tasks (BackgroundTasks): Background tasks to be executed.
        request (Request): The request object.
        db (Session): Database session dependency.

    Returns:
        dict: A message indicating the status of the email confirmation request.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user.confirmed:
        return {"message": messages.USER_EMAIL_ALREADY_CONFIRMED}
    if user:
        background_tasks.add_task(
            send_registration_email, user.email, user.username, request.base_url
        )
    return {"message": messages.USER_EMAIL_CHECK_EMAIL}


@router.post("/token/refresh", response_model=Token)
async def refresh_token_check(
    refresh_token: RefreshToken,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Refresh the access token using the provided refresh token.

    Args:
        refresh_token (RefreshToken): The refresh token provided by the user.
        db (Session, optional): The database session dependency. Defaults to Depends(get_db).
        user (UserModel, optional): The current user dependency. Defaults to Depends(get_current_user).

    Raises:
        HTTPException: If the stored token does not match the provided token.
        HTTPException: If the user is not found in the database.

    Returns:
        dict: A dictionary containing the new access token, the provided refresh token, and the token type.

    """
    user_input = refresh_token.refresh_token
    user_id = await get_user_id_from_token(user_input)

    redis_client = await get_redis_client()
    stored_token = await redis_client.get(f"refresh_token:{user_id}")

    if stored_token != user_input:
        raise HTTPException(status_code=401, detail=messages.ERROR_TOKEN_REVOKED)

    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=messages.USER_NOT_FOUND)

    access_token = await create_access_token({"sub": user.username, "id": user.id})
    return {
        "access_token": access_token,
        "refresh_token": user_input,
        "token_type": "bearer",
    }


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
    await redis_client.delete(f"refresh_token:{user.id}")
    return {"message": messages.USER_LOGOUT}


@router.post("/reset_password")
async def reset_password_request(
    body: ResetPassword,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Handles a password reset request by generating a reset token and sending a reset password email.

    Args:
        body (ResetPassword): The request body containing the user's email and new password.
        background_tasks (BackgroundTasks): Background tasks to be executed after the response is sent.
        request (Request): The HTTP request object.
        db (Session, optional): The database session dependency.

    Returns:
        dict: A message indicating that the user should check their email.

    Raises:
        HTTPException: If the user's email is not confirmed.
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if not user:
        return {"message": messages.USER_EMAIL_CHECK_EMAIL}

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.USER_EMAIL_NOT_CONFIRMED,
        )

    hashed_password = Hash().get_password_hash(body.password)

    reset_token = await create_access_token(
        data={"sub": user.email, "password": hashed_password}
    )

    background_tasks.add_task(
        send_reset_password_email,
        email=body.email,
        username=user.username,
        host=str(request.base_url),
        reset_token=reset_token,
    )

    return {"message": messages.USER_EMAIL_CHECK_EMAIL}


@router.get("/confirm_reset_password/{token}")
async def confirm_reset_password(token: str, db: Session = Depends(get_db)):
    """
    Confirm and reset the user's password using the provided token.

    Args:
        token (str): The token containing the user's email and new password.
        db (Session, optional): The database session dependency.

    Raises:
        HTTPException: If the token is invalid or the user is not found.

    Returns:
        dict: A message indicating the password has been reset.

    """
    email = await get_email_from_token(token)
    hashed_password = await get_password_from_token(token)

    if not email or not hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messages.ERROR_WRONG_TOKEN,
        )

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=messages.ERROR_USER_NOT_FOUND,
        )

    redis_client = await get_redis_client()
    await redis_client.delete(f"user:{user.id}")
    await redis_client.delete(f"refresh_token:{user.id}")
    await user_service.reset_password(user.id, hashed_password)

    return {"message": messages.USER_PASSWORD_RESET}
