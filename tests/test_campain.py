from unittest.mock import patch

import pytest


@pytest.mark.asyncio
async def test_send_newsletter_success(
    client, test_user, test_organization, test_newsletter, db_session
):
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    payload = {"newsletter_id": test_newsletter.id}

    with patch("app.api.routes.campain.send_campaign_emails"):
        response_campaign = await client.post(
            "/api/campain/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response_campaign.status_code == 200
    data = response_campaign.json()

    assert "id" in data
    assert data["newsletter_id"] == test_newsletter.id
    assert data["organization_id"] == test_user.organization_id
    assert data["status"] == "pending"
    assert data["created_by"] == test_user.id

    await db_session.refresh(test_newsletter)
    assert test_newsletter.status == "locked"


@pytest.mark.asyncio
async def test_send_newsletter_not_found(client, test_user):
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    payload = {"newsletter_id": 9999}

    with patch("app.api.routes.campain.send_campaign_emails"):
        response_campaign = await client.post(
            "/api/campain/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response_campaign.status_code == 404
    data = response_campaign.json()
    assert data["detail"] == "Newsletter not found"


@pytest.mark.asyncio
async def test_send_newsletter_already_used(client, test_user, test_newsletter):
    login_data = {"email": test_user.email, "password": "password123"}
    response = await client.post("/api/user_auth/login", json=login_data)
    token = response.json()["access_token"]

    test_newsletter.status = "locked"

    payload = {"newsletter_id": test_newsletter.id}

    with patch("app.api.routes.campain.send_campaign_emails"):
        response_campaign = await client.post(
            "/api/campain/",
            json=payload,
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response_campaign.status_code == 400
    data = response_campaign.json()
    assert data["detail"] == "Newsletter already used"
