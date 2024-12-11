"""
This module provides endpoints for user-related operations, including retrieving the current authenticated user and updating the user's avatar.

Endpoints:
- GET /users/me: Retrieve the current authenticated user.
- PATCH /users/avatar: Update the avatar of the current authenticated user.

Dependencies:
- slowapi.Limiter: Rate limiting for the endpoints.
- fastapi.APIRouter: Router for the user-related endpoints.
- fastapi.Depends: Dependency injection for the endpoints.
- fastapi.Request: The incoming HTTP request.
- fastapi.UploadFile: File upload handling.
- fastapi.File: File upload handling.
- fastapi.HTTPException: Exception handling for HTTP errors.
- fastapi.status: HTTP status codes.
- sqlalchemy.ext.asyncio.AsyncSession: Asynchronous database session handling.
- src.schemas.UserModel: Schema for the user model.
- src.services.auth.get_current_user: Dependency to get the current authenticated user.
- src.services.auth.is_current_user_admin: Dependency to check if the current user is an admin.
- src.services.users.UserService: Service for user-related operations.
- src.services.upload_file.UploadFileService: Service for file upload operations.
- src.database.db.get_db: Dependency to get the database session.
- src.database.models.User: User model.
- src.conf.config.settings: Configuration settings.
- src.conf.messages: Message constants.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from fastapi import APIRouter, Depends, Request, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import UserModel
from src.services.auth import get_current_user, is_current_user_admin

from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.database.db import get_db
from src.database.models import User
from src.conf.config import settings
from src.conf import messages

router = APIRouter(prefix="/users", tags=["users"])
limiter = Limiter(key_func=get_remote_address)


@router.get(
    "/me", response_model=UserModel, description="No more than 5 requests per minute"
)
@limiter.limit("5/minute")
async def me(
    request: Request, user: UserModel = Depends(get_current_user)
):  # pylint: disable=W0613
    """
    Retrieve the current authenticated user.

    Args:
        request (Request): The incoming HTTP request.
        user (UserModel, optional): The current authenticated user, injected by dependency.

    Returns:
        UserModel: The current authenticated user.

    """
    return user


@router.patch("/avatar", response_model=UserModel)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update the avatar of the current authenticated user.

    Args:
        file (UploadFile): The new avatar file to be uploaded.
        user (User): The current authenticated user, obtained from the dependency injection.
        db (AsyncSession): The database session, obtained from the dependency injection.

    Raises:
        HTTPException: If the current user does not have sufficient permissions.

    Returns:
        User: The updated user object with the new avatar URL.

    """
    if not is_current_user_admin(user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.ERROR_UNSUFFICIENT_PERMISSIONS,
        )
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
