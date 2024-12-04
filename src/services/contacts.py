"""
- **create_contact(body: ContactModel, user: User):**

- **get_contacts(skip: int, limit: int, queue: str | None, user: User):**
    Retrieves a list of contacts with pagination and optional queue filtering.

- **get_contact(contact_id: int, user: User):**
    Retrieves a contact by its ID for a specific user.

- **update_contact(contact_id: int, body: ContactModel, user: User):**

- **remove_contact(contact_id: int, user: User):**


        Contact: The created contact object.

Retrieves a list of contacts with pagination and optional queue filtering.


Retrieves a contact by its ID for a specific user.

        Contact: The updated contact information.

"""

from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, UserModel


class ContactService:
    """
    ContactService provides asynchronous methods to manage contacts for a user.

    Methods:

        create_contact(body: ContactModel, user: User):

        get_contacts(skip: int, limit: int, queue: str | None, user: User):

        get_contact(contact_id: int, user: User):

        update_contact(contact_id: int, body: ContactModel, user: User):

        remove_contact(contact_id: int, user: User):
    """

    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: UserModel):
        """
        Asynchronously creates a new contact.

        Args:
            body (ContactModel): The data model representing the contact to be created.
            user (User): The user associated with the contact.

        Returns:
            The created contact object.
        """
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self, skip: int, limit: int, queue: str | None, user: UserModel
    ):
        """
        Retrieve a list of contacts with pagination and optional queue filtering.

        Args:
            skip (int): The number of contacts to skip for pagination.
            limit (int): The maximum number of contacts to return.
            queue (str | None): An optional queue filter to apply to the contacts.
            user (User): The user requesting the contacts.

        Returns:
            List[Contact]: A list of contacts matching the criteria.
        """
        return await self.repository.get_contacts(skip, limit, queue, user)

    async def get_contact(self, contact_id: int, user: UserModel):
        """
        Retrieve a contact by its ID for a specific user.

        Args:
            contact_id (int): The ID of the contact to retrieve.
            user (User): The user to whom the contact belongs.

        Returns:
            Contact: The contact object if found, otherwise None.
        """
        return await self.repository.get_contact_by_id(contact_id, user)

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: UserModel
    ):
        """
        Asynchronously updates a contact with the given contact ID.

        Args:
            contact_id (int): The ID of the contact to be updated.
            body (ContactModel): The data model containing updated contact information.
            user (User): The user performing the update operation.

        Returns:
            The updated contact information.

        Raises:
            Exception: If the update operation fails.
        """
        return await self.repository.update_contact(contact_id, body, user)

    async def remove_contact(self, contact_id: int, user: UserModel):
        """
        Asynchronously removes a contact for a given user.

        Args:
            contact_id (int): The ID of the contact to be removed.
            user (User): The user who owns the contact.

        Returns:
            bool: True if the contact was successfully removed, False otherwise.
        """
        return await self.repository.remove_contact(contact_id, user)
