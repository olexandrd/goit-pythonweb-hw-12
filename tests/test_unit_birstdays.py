import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.bistdays import BirthdayRepository


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def birthday_repository(mock_session):
    return BirthdayRepository(mock_session)


@pytest.fixture
def user():
    return User(id=1, username="testuser", email="test@example.com")


@pytest.fixture
def contact():
    return Contact(
        id=1,
        name="John",
        surname="Doe",
        email="john.doe@example.com",
        birstday="2000-01-01",
        user=None,
    )


@pytest.mark.asyncio
async def test_get_contacts_within_daygap(
    birthday_repository, mock_session, user, contact
):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Run test
    result = await birthday_repository.get_contacts(
        skip=0, limit=10, daygap=30, user=user
    )

    # Assert
    assert result == [contact]
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_contacts_across_year_boundary(
    birthday_repository, mock_session, user, contact
):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Run test
    result = await birthday_repository.get_contacts(
        skip=0, limit=10, daygap=365, user=user
    )

    # Assert
    assert result == [contact]
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_contacts_no_results(birthday_repository, mock_session, user):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Run test
    result = await birthday_repository.get_contacts(
        skip=0, limit=10, daygap=30, user=user
    )

    # Assert
    assert result == []
    mock_session.execute.assert_called_once()
