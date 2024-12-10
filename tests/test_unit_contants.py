import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)


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
        user=None,
    )


@pytest.fixture
def contact_model():
    return ContactModel(
        name="John",
        surname="Doe",
        email="john.doe@example.com",
        phone_number="+380-66-112-2333",
        birstday="2022-01-01",
    )


@pytest.fixture
def contact_update():
    return ContactUpdate(
        name="Jane",
        surname="Doe",
        email="jane.doe@example.com",
        phone_number="+380-66-112-2333",
        birstday="2000-01-01",
        done=True,
    )


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user, contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Run test
    result = await contact_repository.get_contacts(0, 10, None, user)

    # Assert
    assert result == [contact]
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user, contact):
    # Setup mock
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    # Run test
    result = await contact_repository.get_contact_by_id(contact.id, user)

    # Assert
    assert result == contact
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_contact(
    contact_repository, mock_session, user, contact_model, contact
):
    # Setup mock
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=contact))
    )

    # Run test
    result = await contact_repository.create_contact(contact_model, user)

    # Assert
    assert result == contact
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user, contact):
    # Setup mock
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=contact))
    )
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    # Run test
    result = await contact_repository.remove_contact(contact.id, user)

    # Assert
    assert result == contact
    mock_session.delete.assert_called_once_with(contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_contact(
    contact_repository, mock_session, user, contact, contact_update
):
    # Setup mock
    mock_session.execute = AsyncMock(
        return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=contact))
    )
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    # Run test
    result = await contact_repository.update_contact(contact.id, contact_update, user)

    # Assert
    assert result.name == contact_update.name
    assert result.email == contact_update.email
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(contact)
