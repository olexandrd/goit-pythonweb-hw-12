"""
This module provides an API endpoint for fetching contacts with upcoming birthdays.Router, Depends

Endpoints:
    - GET /birstdays/nearest: Fetch contacts with upcoming birthdays within a specified day gap.

Dependencies:
    - FastAPI APIRouter for routing.
    - SQLAlchemy AsyncSession for database interactions.
    - BirthdayService for business logic related to birthdays.
    - get_current_user for authentication.

Functions:
    - read_bistdays: Fetch contacts with upcoming birthdays.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactResponse, UserModel
from src.services.birstdays import BirthdayService
from src.services.auth import get_current_user

router = APIRouter(prefix="/birstdays", tags=["birstdays"])


@router.get("/nearest", response_model=List[ContactResponse])
async def read_bistdays(
    skip: int = 0,
    limit: int = 100,
    daygap: int = 7,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Fetch contacts with upcoming birthdays.
    """
    contact_service = BirthdayService(db)
    contacts = await contact_service.get_contacts(skip, limit, daygap, user)
    return contacts
