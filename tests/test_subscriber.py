import pytest


@pytest.mark.asyncio
async def test_add_subscriber(client, test_user, test_organization):

    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    subscriber_data = {
        "email": "rohitankolnerkar@gmail.com",
        "organization_id": test_organization.id,
    }

    response = await client.post(
        f"/api/subscriber/subscribe/{test_organization.slug}",
        json=subscriber_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    data = response.json()


@pytest.mark.asyncio
async def test_list_subscribers(client, test_user):

    token = (
        await client.post(
            "/api/user_auth/login",
            json={"email": test_user.email, "password": "password123"},
        )
    ).json()["access_token"]

    response = await client.get(
        f"/api/subscriber/subscriber_list", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["subscribers"], list)


@pytest.mark.asyncio
async def test_list_subscriber(client, test_user, test_organization):
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]
    response2 = await client.get(
        f"/api/subscriber/subscriber_list/{test_organization.slug}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response2.status_code == 200
    data = response2.json()
    assert isinstance(data["subscribers"], list)
