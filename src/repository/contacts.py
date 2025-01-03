"""
This module defines the ContactRepository class, which provides methods to interact with the contacts stored in the database for a specific user.

Classes:
    ContactRepository:
        Provides methods to interact with the contacts stored in the database for a specific user.

"""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


class ContactRepository:
    """
    ContactRepository provides methods to interact with the contacts stored in the database for a specific user.

    Methods:
        get_contacts(skip: int, limit: int, search_queue: str | None, user: User) -> List[Contact]:
        get_contact_by_id(contact_id: int, user: User) -> Contact | None: Return a contact by id, needed for create, update and delete operations.
        create_contact(body: ContactModel, user: User) -> Contact:
        remove_contact(contact_id: int, user: User) -> Contact | None:
        update_contact(contact_id: int, body: ContactUpdate, user: User) -> Contact | None:

    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self, skip: int, limit: int, search_queue: str | None, user: User
    ) -> List[Contact]:
        """
        Retrieve a list of contacts for a given user with optional search functionality.

        Args:
            skip (int): The number of records to skip for pagination.
            limit (int): The maximum number of records to return.
            search_queue (str | None): An optional search string to filter contacts by name, surname, or email.
            user (User): The user whose contacts are to be retrieved.

        Returns:
            List[Contact]: A list of contacts matching the search criteria and pagination settings.

        """
        if search_queue:
            stmt = (
                select(Contact)
                .filter_by(user=user)
                .filter(
                    Contact.name.ilike(f"%{search_queue}%")
                    | Contact.surname.ilike(f"%{search_queue}%")
                    | Contact.email.ilike(f"%{search_queue}%")
                )
                .offset(skip)
                .limit(limit)
            )
        else:
            stmt = select(Contact).filter_by(user=user).offset(skip).limit(limit)
        contacts = await self.db.execute(stmt)
        return contacts.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a contact by its ID for a specific user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact | None: The contact if found, otherwise None.

        """
        stmt = select(Contact).filter_by(id=contact_id, user=user)
        contact = await self.db.execute(stmt)
        return contact.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact for the given user.

        Args:
            body (ContactModel): The data model containing the contact information.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact: The newly created contact with the given information.

        Raises:
            SQLAlchemyError: If there is an error committing the contact to the database.

        """
        contact = Contact(
            **body.model_dump(exclude_unset=True),
            user=user,
        )
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return await self.get_contact_by_id(contact.id, user)

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Remove a contact by its ID for a given user.

        Args:
            contact_id (int): The ID of the contact to be removed.
            user (User): The user who owns the contact.

        Returns:
            Contact | None: The removed contact if it existed, otherwise None.
        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def update_contact(
        self, contact_id: int, body: ContactUpdate, user: User
    ) -> Contact | None:
        """
        Update an existing contact with new information.

        Args:
            contact_id (int): The ID of the contact to update.
            body (ContactUpdate): An object containing the updated contact information.
            user (User): The user performing the update.

        Returns:
            Contact | None: The updated contact if found, otherwise None.

        """
        contact = await self.get_contact_by_id(contact_id, user)
        if contact:
            for key, value in body.dict(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact
