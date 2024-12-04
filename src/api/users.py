"""
This module provides /me endpoint for logged users.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas import UserModel
from src.services.auth import get_current_user

from src.services.users import UserService
from src.services.upload_file import UploadFileService
from src.database.db import get_db
from src.database.models import User
from src.conf.config import settings

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
    """
    avatar_url = UploadFileService(
        settings.CLD_NAME, settings.CLD_API_KEY, settings.CLD_API_SECRET
    ).upload_file(file, user.username)

    user_service = UserService(db)
    user = await user_service.update_avatar_url(user.email, avatar_url)

    return user
