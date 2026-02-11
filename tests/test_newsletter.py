import pytest


@pytest.mark.asyncio
async def test_create_newsletter(client, test_user):
    # Login to get token
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    payload = {
        "subject": "Test Newsletter",
        "content": "This is a test newsletter content.",
    }

    response_create = await client.post(
        "/api/newsletter/create_newsletter",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response_create.status_code == 201
    data = response_create.json()
    assert data["subject"] == payload["subject"]
    assert data["content"] == payload["content"]
    assert data["status"] == "draft"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_newsletter(client, test_user):
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    response_list = await client.get(
        "/api/newsletter/list_newsletter", headers={"Authorization": f"Bearer {token}"}
    )

    assert response_list.status_code == 200
    newsletters = response_list.json()
    assert isinstance(newsletters, list)


@pytest.mark.asyncio
async def test_get_newsletter(client, test_user):
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    # First, create a newsletter to get
    payload = {"subject": "Get Test", "content": "Content for get test"}
    response_create = await client.post(
        "/api/newsletter/create_newsletter",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    newsletter_id = response_create.json()["id"]

    # Now get the newsletter
    response_get = await client.get(
        f"/api/newsletter/get_newsletter/{newsletter_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response_get.status_code == 200
    data = response_get.json()
    assert data["id"] == newsletter_id
    assert data["subject"] == payload["subject"]
    assert data["content"] == payload["content"]


@pytest.mark.asyncio
async def test_update_newsletter(client, test_user):
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    # Create newsletter first
    payload_create = {"subject": "Original", "content": "Original content"}
    response_create = await client.post(
        "/api/newsletter/create_newsletter",
        json=payload_create,
        headers={"Authorization": f"Bearer {token}"},
    )
    newsletter_id = response_create.json()["id"]

    # Update newsletter
    payload_update = {"subject": "Updated", "content": "Updated content"}
    response_update = await client.put(
        f"/api/newsletter/update_newsletter/{newsletter_id}",
        json=payload_update,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response_update.status_code == 200
    data = response_update.json()
    assert data["id"] == newsletter_id
    assert data["subject"] == payload_update["subject"]
    assert data["content"] == payload_update["content"]
    assert data["status"] == "draft"


@pytest.mark.asyncio
async def test_delete_newsletter(client, test_user):
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    # Create newsletter first
    payload_create = {"subject": "Delete Test", "content": "Content to delete"}
    response_create = await client.post(
        "/api/newsletter/create_newsletter",
        json=payload_create,
        headers={"Authorization": f"Bearer {token}"},
    )
    newsletter_id = response_create.json()["id"]

    # Delete newsletter
    response_delete = await client.delete(
        f"/api/newsletter/delete_newsletter/{newsletter_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response_delete.status_code == 204

    # Check that it no longer exists
    response_get = await client.get(
        f"/api/newsletter/get_newsletter/{newsletter_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_get.status_code == 404
