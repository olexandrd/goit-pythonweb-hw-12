"""
UserService class provides methods to manage user-related operations such as creating a user,
retrieving user information by ID, username, email, confirming email, and updating avatar URL.
Methods:
    __init__(db: AsyncSession):
        Initializes the UserService with a database session.
    create_user(body: UserCreate):
        Creates a new user with the provided information and generates an avatar.
    get_user_by_id(user_id: int):
        Retrieves a user by their unique identifier.
    get_user_by_username(username: str):
        Retrieves a user by their username.
    get_user_by_email(email: str):
        Retrieves a user by their email address.
    confirmed_email(email: str):
        Checks if the email is confirmed.
    update_avatar_url(email: str, url: str):
        Asynchronously updates the avatar URL for a user identified by their email.

"""

from sqlalchemy.ext.asyncio import AsyncSession

from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate


class UserService:
    """
    UserService class provides methods to manage user-related operations such as creating a user,
    retrieving user information by ID, username, email, confirming email, and updating avatar URL.
    Methods:
        __init__(db: AsyncSession):
            Initializes the UserService with a database session.
        create_user(body: UserCreate):
            Creates a new user with the provided information and generates an avatar.
        get_user_by_id(user_id: int):
            Retrieves a user by their unique identifier.
        get_user_by_username(username: str):
            Retrieves a user by their username.
        get_user_by_email(email: str):
            Retrieves a user by their email address.
        confirmed_email(email: str):
            Checks if the email is confirmed.
        update_avatar_url(email: str, url: str):
    """

    def __init__(self, db: AsyncSession):
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Creates a new user with the provided information.
        Args:
            body (UserCreate): The user information required to create a new user.
        Returns:
            User: The created user object with the provided information and generated avatar.
        Raises:
            Exception: If there is an error generating the avatar.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:  # pylint: disable=broad-except
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their unique identifier.
        Args:
            user_id (int): The unique identifier of the user.
        Returns:
            User: The user object corresponding to the given user_id.
        Raises:
            UserNotFoundError: If no user is found with the given user_id.
        """

        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.
        Args:
            username (str): The username of the user to retrieve.
        Returns:
            User: The user object corresponding to the given username.
        """

        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email address.
        Args:
            email (str): The email address of the user to retrieve.
        Returns:
            User: The user object corresponding to the given email address,
                or None if no user is found.
        """

        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
        Check if the email is confirmed.
        Args:
            email (str): The email address to check.
        Returns:
            bool: True if the email is confirmed, False otherwise.
        """

        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Asynchronously updates the avatar URL for a user identified by their email.
        Args:
            email (str): The email address of the user whose avatar URL is to be updated.
            url (str): The new avatar URL to be set for the user.
        Returns:
            The result of the repository's update_avatar_url method.
        """

        return await self.repository.update_avatar_url(email, url)
