"""
This module defines Pydantic models for various schemas used in the application.

Classes:
    ContactModel (BaseModel): Represents a contact with attributes such as 
        name, surname, email, phone number, birthday, and notes.
    ContactUpdate (ContactModel): Represents an update to a contact, 
        including a 'done' attribute.
    ContactResponse (ContactModel): Represents the response schema for a 
        contact, extending ContactModel with an 'id' attribute.
    UserModel (BaseModel): Represents a user with attributes such 
        as id, username, email, and avatar.
    UserCreate (BaseModel): Represents the schema for creating a new 
        user with attributes such as username, email, and password.
    Token (BaseModel): Represents the schema for authentication tokens 
        with attributes such as access_token and token_type.
    RequestEmail (BaseModel): Represents a schema for requesting 
        an email with an 'email' attribute.


"""

from datetime import date
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber


class ContactModel(BaseModel):
    """
    ContactModel is a Pydantic model representing a contact with the following attributes:
    Attributes:
        name (str): The first name of the contact. Maximum length is 50 characters.
        surname (str): The surname of the contact. Maximum length is 50 characters.
        email (EmailStr): The email address of the contact. Maximum length is 50 characters.
        phone_number (PhoneNumber): The phone number of the contact, validated in E.164 format.
        birstday (date): The birth date of the contact.
        notes (str | None): Optional notes about the contact. Maximum length is 500 characters.
            Default is None.
    """

    name: str = Field(max_length=50)
    surname: str = Field(max_length=50)
    email: EmailStr = Field(max_length=50)
    phone_number: PhoneNumber
    birstday: date
    notes: str | None = Field(max_length=500, default=None)
    model_config = ConfigDict(validate_number_format="E.164")


class ContactUpdate(ContactModel):
    """
    ContactUpdate is a subclass of ContactModel that represents an update to a contact.

    Attributes:
        done (bool): Indicates whether the contact update is completed.
    """

    done: bool


class ContactResponse(ContactModel):
    """
    ContactResponse is a data model that extends ContactModel and
        represents the response schema for a contact.

    Attributes:
        id (int): The unique identifier of the contact.
        name (str): The first name of the contact.
        surname (str): The last name of the contact.
        email (str): The email address of the contact.
        phone_number (str): The phone number of the contact.
        birstday (date): The birth date of the contact.
        model_config (ConfigDict): Configuration dictionary
            for the model, with attributes sourced from the base model.
    """

    id: int
    name: str
    surname: str
    email: str
    phone_number: str
    birstday: date
    model_config = ConfigDict(from_attributes=True)


class UserModel(BaseModel):
    """
    User schema model.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        avatar (str): The URL or path to the user's avatar image.

    Config:
        model_config (ConfigDict): Configuration dictionary for the model.
    """

    id: int
    username: str
    email: EmailStr = Field(max_length=50)
    avatar: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    UserCreate schema for creating a new user.

    Attributes:
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password for the user.
    """

    username: str
    email: EmailStr = Field(max_length=50)
    password: str


class Token(BaseModel):
    """
    Token schema for authentication.

    Attributes:
        access_token (str): The access token provided after successful authentication.
        token_type (str): The type of the token, typically "Bearer".
    """

    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    RequestEmail schema for requesting an email.
    """

    email: EmailStr
