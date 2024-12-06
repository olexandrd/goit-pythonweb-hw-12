"""
DB operations for bistdays
"""

from datetime import timedelta, datetime, date
from typing import List

from sqlalchemy import select
from sqlalchemy.sql import extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

from src.database.models import Contact, User


class BirthdayRepository:
    """
    Birthday repository
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(
        self, skip: int, limit: int, daygap: int, user: User
    ) -> List[Contact]:
        """
        Retrieve contacts, skip and limit are used for pagination
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
