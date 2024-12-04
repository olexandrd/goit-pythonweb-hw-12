"""
This module defines the database models for the application using SQLAlchemy ORM.

Classes:
    Base: A base class for declarative class definitions.
    Contact: Represents a contact in the database.
    User: Represents a user in the database.

Contact:

User:
"""

from datetime import date
from sqlalchemy import Integer, String, func, Column
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Date, DateTime, Boolean


class Base(DeclarativeBase):  # pylint: disable=[missing-class-docstring]
    pass


class Contact(Base):
    """
    Represents a contact in the database.

    Attributes:
        id (int): The primary key of the contact.
        user_id (int): The foreign key referencing the user who owns the contact.
        name (str): The first name of the contact.
        surname (str): The surname of the contact.
        email (str): The email address of the contact.
        phone_number (str): The phone number of the contact.
        birstday (date): The birth date of the contact.
        notes (str): Additional notes about the contact.
        user (User): The user who owns the contact.
    """

    __tablename__ = "contacts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    surname: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(50))
    phone_number: Mapped[str] = mapped_column(String(50))
    birstday: Mapped[date] = mapped_column(
        "birstday", Date, default=func.now()  # pylint: disable=not-callable
    )
    notes: Mapped[str] = mapped_column(String(500), nullable=True)
    user = relationship("User", backref="contacts")


class User(Base):
    """
    User model for the database.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username for the user.
        email (str): Unique email address for the user.
        hashed_password (str): Hashed password for the user.
        created_at (datetime): Timestamp when the user was created.
        avatar (str, optional): URL or path to the user's avatar image.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())  # pylint: disable=not-callable
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
