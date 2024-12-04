"""
BirthdayService class, which is responsible for handling operations related to birthdays.

Classes:
    BirthdayService: A service class for managing birthday-related operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.bistdays import BirthdayRepository
from src.schemas import UserModel


class BirthdayService:
    """
    BirthdayService is a service class responsible for handling operations related to birthdays.

    Attributes:
        repository (BirthdayRepository): An instance of BirthdayRepository for database operations.

    Methods:
        __init__(db: AsyncSession):
            Initializes the BirthdayService with a database session.

        get_contacts(skip: int, limit: int, daygap: int, user: User) -> List[Contact]:


    """

    def __init__(self, db: AsyncSession):
        self.repository = BirthdayRepository(db)

    async def get_contacts(self, skip: int, limit: int, daygap: int, user: UserModel):
        """
        Retrieve a list of contacts with upcoming birthdays.
        """
        return await self.repository.get_contacts(skip, limit, daygap, user)
