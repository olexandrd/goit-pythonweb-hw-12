# def test_create_contact(client, get_token):
#     response = client.post(
#         "/api/contacts",
#         json={
#             "name": "bob",
#             "surname": "bob",
#             "phone_number": "+43800901000",
#             "email": "bob@example.com",
#             "birstday": "2022-01-01",
#             "notes": "Some note",
#         },
#         headers={"Authorization": f"Bearer {get_token}"},
#     )
#     assert response.status_code == 201, response.text
#     data = response.json()
#     assert data["name"] == "bob"
#     assert data["surname"] == "bob"
#     assert data["phone_number"] == "tel:+43-800-901000"
#     assert data["email"] == "bob@example.com"
#     assert "id" in data


# def test_get_contact(client, get_token):
#     response = client.get(
#         "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["name"] == "test_contact"
#     assert "id" in data


# def test_get_contact_not_found(client, get_token):
#     response = client.get(
#         "/api/contacts/2", headers={"Authorization": f"Bearer {get_token}"}
#     )
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "Contact not found"


# def test_get_contacts(client, get_token):
#     response = client.get(
#         "/api/contacts", headers={"Authorization": f"Bearer {get_token}"}
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert isinstance(data, list)
#     assert data[0]["name"] == "test_contact"
#     assert "id" in data[0]


# def test_update_contact(client, get_token):
#     response = client.put(
#         "/api/contacts/1",
#         json={"name": "new_test_contact"},
#         headers={"Authorization": f"Bearer {get_token}"},
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["name"] == "new_test_contact"
#     assert "id" in data


# def test_update_contact_not_found(client, get_token):
#     response = client.put(
#         "/api/contacts/2",
#         json={"name": "new_test_contact"},
#         headers={"Authorization": f"Bearer {get_token}"},
#     )
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "contact not found"


# def test_delete_contact(client, get_token):
#     response = client.delete(
#         "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["name"] == "new_test_contact"
#     assert "id" in data


# def test_repeat_delete_contact(client, get_token):
#     response = client.delete(
#         "/api/contacts/1", headers={"Authorization": f"Bearer {get_token}"}
#     )
#     assert response.status_code == 404, response.text
#     data = response.json()
#     assert data["detail"] == "contact not found"
