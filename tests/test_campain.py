import pytest


@pytest.mark.asyncio
async def test_send_newsletter_success(
    client, test_user, test_organization, test_newsletter
):
    """
    Test sending a newsletter as a campaign successfully.
    """
    # Login first
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    payload = {"newsletter_id": test_newsletter.id}

    response_campaign = await client.post(
        "/api/campain/", json=payload, headers={"Authorization": f"Bearer {token}"}
    )

    assert response_campaign.status_code == 200
    data = response_campaign.json()

    # Validate response
    assert "id" in data
    assert data["newsletter_id"] == test_newsletter.id
    assert data["organization_id"] == test_user.organization_id
    assert data["status"] == "pending"
    assert data["created_by"] == test_user.id

    # Check that the newsletter status is now 'locked'
    assert test_newsletter.status == "locked"


@pytest.mark.asyncio
async def test_send_newsletter_not_found(client, test_user):
    """
    Test sending a newsletter that does not exist.
    """
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    payload = {"newsletter_id": 9999}  # Assuming this ID does not exist

    response_campaign = await client.post(
        "/api/campain/", json=payload, headers={"Authorization": f"Bearer {token}"}
    )

    assert response_campaign.status_code == 404
    data = response_campaign.json()
    assert data["detail"] == "Newsletter not found"


@pytest.mark.asyncio
async def test_send_newsletter_already_used(client, test_user, test_newsletter):
    """
    Test sending a newsletter that is already used/locked.
    """
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    # First, set newsletter status to something other than draft
    test_newsletter.status = "locked"

    payload = {"newsletter_id": test_newsletter.id}

    response_campaign = await client.post(
        "/api/campain/", json=payload, headers={"Authorization": f"Bearer {token}"}
    )

    assert response_campaign.status_code == 400
    data = response_campaign.json()
    assert data["detail"] == "Newsletter already used"
