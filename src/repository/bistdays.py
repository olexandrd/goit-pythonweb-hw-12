"""
DB operations for bistdays
"""

import json
from datetime import timedelta, datetime, date
from typing import List
import redis.asyncio as redis

from sqlalchemy import select
from sqlalchemy.sql import extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.inspection import inspect

from src.database.models import Contact, User
from src.conf.config import settings


class BirthdayRepository:
    """
    Birthday repository
    """

    def __init__(self, session: AsyncSession):
        self.db = session
        self._redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

    def serialize_contact(self, contact) -> dict:
        """
        Serialize a single Contact object into a dictionary, making all fields JSON-compatible.
        """
        mapper = inspect(contact)
        serialized = {}

        for column in mapper.attrs:
            value = getattr(contact, column.key)
            if isinstance(value, datetime):
                serialized[column.key] = value.isoformat()
            elif isinstance(value, date):
                serialized[column.key] = value.isoformat()
            elif isinstance(value, object):
                serialized[column.key] = str(value)
            else:
                serialized[column.key] = value

        return serialized

    async def get_contacts(
        self, skip: int, limit: int, daygap: int, user: User
    ) -> List[Contact]:
        """
        Retrieve contacts, skip and limit are used for pagination
        """

        today = datetime.now()
        start_day = today.timetuple().tm_yday
        end_day = (today + timedelta(days=daygap)).timetuple().tm_yday
        redis_key = f"{user.id}-{skip}-{limit}-{daygap}"

        cached_contacts = await self._redis.lrange(redis_key, 0, -1)
        if cached_contacts:
            return [json.loads(contact.decode("utf-8")) for contact in cached_contacts]

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

        for contact in contacts:
            await self._redis.rpush(
                redis_key, json.dumps(self.serialize_contact(contact))
            )

        await self._redis.expire(redis_key, 3600)

        return [self.serialize_contact(contact) for contact in contacts]
