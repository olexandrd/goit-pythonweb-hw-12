from datetime import date, timedelta
from unittest.mock import AsyncMock


def test_read_bistdays(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.get(
        "api/birstdays/nearest",
        headers={"Authorization": f"Bearer {get_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == [
        {
            "birstday": str(date.today() + timedelta(days=5)),
            "email": "john@example.com",
            "id": 1,
            "name": "John",
            "notes": "Some note",
            "phone_number": "+1234567890",
            "surname": "Doe",
        },
    ]


def test_read_bistdays_empty(client, get_token, monkeypatch):
    mock_redis_client = AsyncMock()
    mock_redis_client.get.return_value = None
    monkeypatch.setattr(
        "src.services.auth.get_redis_client", AsyncMock(return_value=mock_redis_client)
    )
    response = client.get(
        "api/birstdays/nearest",
        headers={"Authorization": f"Bearer {get_token}"},
        params={"daygap": 1},
    )
    print(response.url)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == []
