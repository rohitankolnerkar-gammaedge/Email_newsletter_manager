import pytest


@pytest.mark.asyncio
async def test_login_and_access_protected_route(client, test_user):
    """
    Test that a user can login with correct credentials and access protected routes.
    """
    login_data = {"email": test_user.email, "password": "password123"}

    response = await client.post("/api/user_auth/login", json=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    token = data["access_token"]

    protected_response = await client.get(
        "/api/newsletter/list_newsletter", headers={"Authorization": f"Bearer {token}"}
    )
    assert protected_response.status_code == 200


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    """
    Test that login fails with an incorrect password.
    """
    wrong_login_data = {"email": test_user.email, "password": "wrongpassword"}

    response = await client.post("/api/user_auth/login", json=wrong_login_data)
    assert response.status_code == 401

    data = response.json()
    assert "detail" in data

    assert data["detail"] == "Invalid credentials"
