from datetime import date, timedelta
from unittest.mock import AsyncMock

from src.conf import messages


def test_get_contacts(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["name"] == "John"
    assert "id" in data[0]


def test_get_contact(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "John"
    assert data["surname"] == "Doe"
    assert data["phone_number"] == "+1234567890"
    assert data["email"] == "john@example.com"
    assert data["birstday"] == str(date.today() + timedelta(days=5))
    assert "id" in data


def test_get_contact_not_found(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.get(
        "/api/contacts/100", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_create_contact(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.post(
        "/api/contacts",
        json={
            "name": "Bob",
            "surname": "BobSurname",
            "phone_number": "+43800901000",
            "email": "bob@example.com",
            "birstday": "2022-01-01",
            "notes": "Some note",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Bob"
    assert data["surname"] == "BobSurname"
    assert data["phone_number"] == "tel:+43-800-901000"
    assert data["email"] == "bob@example.com"
    assert "id" in data


def test_update_contact(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.put(
        "/api/contacts/1",
        json={
            "name": "new_test_contact",
            "surname": "new_test_surname",
            "phone_number": "+380661122333",
            "email": "updated_email@example.com",
            "birstday": "2022-01-01",
            "notes": "Some note",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "new_test_contact"
    assert data["surname"] == "new_test_surname"
    assert data["phone_number"] == "tel:+380-66-112-2333"
    assert data["email"] == "updated_email@example.com"
    assert "id" in data


def test_update_contact_not_found(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.put(
        "/api/contacts/100",
        json={
            "name": "new_test_contact",
            "surname": "new_test_surname",
            "phone_number": "+380661122333",
            "email": "updated_email@example.com",
            "birstday": "2022-01-01",
            "notes": "Some note",
        },
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_delete_contact(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.delete(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Bob"
    assert "id" in data


def test_delete_nonexistent_contact(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.delete(
        "/api/contacts/100", headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND
