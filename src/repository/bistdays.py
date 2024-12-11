"""
This module provides a repository class for managing contacts with upcoming birthdays.

Classes:
    BirthdayRepository: A repository class for retrieving contacts based on birthday criteria.

Functions:
    BirthdayRepository.__init__(session: AsyncSession): Initializes the repository with a database session.
    BirthdayRepository.get_contacts(skip: int, limit: int, daygap: int, user: User) -> List[Contact]: Retrieves a list of contacts based on the specified criteria.

"""

from datetime import timedelta, datetime
from typing import List

from sqlalchemy import select
from sqlalchemy.sql import extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User


class BirthdayRepository:
    """
    A repository class for managing and retrieving contacts based on their birthdays.

    Attributes:
        db (AsyncSession): The database session used for executing queries.

    Methods:
        get_contacts(skip: int, limit: int, daygap: int, user: User) -> List[Contact]: Retrieves a list of contacts based on the specified criteria.

    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self, skip: int, limit: int, daygap: int, user: User
    ) -> List[Contact]:
        """
        Retrieve a list of contacts based on the specified criteria.

        Args:
            skip (int): The number of records to skip.
            limit (int): The maximum number of records to return.
            daygap (int): The number of days from today to consider for filtering contacts by birthday.
            user (User): The user whose contacts are to be retrieved.

        Returns:
            List[Contact]: A list of contacts that match the specified criteria.

        """
        today = datetime.now()
        start_day = today.timetuple().tm_yday
        end_day = (today + timedelta(days=daygap)).timetuple().tm_yday

        if end_day < start_day:
            stmt = (
                select(Contact)
                .filter_by(user=user)
                .filter(
                    (extract("doy", Contact.birstday) >= start_day)
                    | (extract("doy", Contact.birstday) <= end_day)
                )
                .offset(skip)
                .limit(limit)
            )
        else:
            stmt = (
                select(Contact)
                .filter_by(user=user)
                .filter(extract("doy", Contact.birstday).between(start_day, end_day))
                .offset(skip)
                .limit(limit)
            )

        contacts_result = await self.db.execute(stmt)
        contacts = contacts_result.scalars().all()

        return contacts
