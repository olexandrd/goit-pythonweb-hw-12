"""
This module defines the API routes for managing contacts using FastAPI.

Routes:
    - GET /contacts: Fetch a list of contacts from the database.
    - GET /contacts/{contact_id}: Retrieve a contact by its ID.
    - POST /contacts: Create a new contact.
    - PUT /contacts/{contact_id}: Update an existing contact.
    - DELETE /contacts/{contact_id}: Remove a contact by its ID.

Dependencies:
    - db: The database session dependency, provided by `get_db`.

Schemas:
    - ContactModel: The schema for contact data input.
    - ContactResponse: The schema for contact data output.

Services:
    - ContactService: The service class for handling contact-related operations.
"""

from typing import List
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactModel, ContactResponse, UserModel
from src.services.contacts import ContactService
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    queue: str | None = None,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Fetch a list of contacts from the database.
    """
    contact_service = ContactService(db)
    contacts = await contact_service.get_contacts(skip, limit, queue, user)
    return contacts


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Retrieve a contact by its ID.
    """

    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Create a new contact.
    """

    contact_service = ContactService(db)
    return await contact_service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    body: ContactModel,
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Update an existing contact.
    """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    """
    Remove a contact by its ID.
    """
    contact_service = ContactService(db)
    contact = await contact_service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
