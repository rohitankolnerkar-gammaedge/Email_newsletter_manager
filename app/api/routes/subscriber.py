import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import APP_BASE_URL
from app.core.security import require_admin
from app.db.session import get_async_db
from app.models.organization import Organization
from app.models.subscriber import Subscriber
from app.models.users import User
from app.schemas.subscriber import (
    SubscribePublicResponse,
    SubscriberCreate,
    Subscriberlist,
)
from app.services.confirmation_email import send_confirmation_email

router = APIRouter()


@router.post(
    "/subscribe/{company_slug}",
    response_model=SubscribePublicResponse,
    status_code=status.HTTP_201_CREATED,
)
async def subscribe(
    company_slug: str,
    payload: SubscriberCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(
        select(Organization).where(Organization.slug == company_slug)
    )
    organization = result.scalar_one_or_none()

    if not organization:
        raise HTTPException(status_code=404, detail="Company not found")

    result = await db.execute(
        select(Subscriber).where(
            Subscriber.email == payload.email,
            Subscriber.organization_id == organization.id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        return {
            "message": "If this email is not subscribed, a confirmation email will be sent."
        }

    confirmation_token = str(uuid.uuid4())
    unsubscribe_token = str(uuid.uuid4())

    subscriber = Subscriber(
        email=payload.email,
        organization_id=organization.id,
        is_active=False,
        status="pending",
        confirmation_token=confirmation_token,
        unsubscribe_token=unsubscribe_token,
        created_at=datetime.now(timezone.utc),
        confirmation_expires_at=datetime.now(timezone.utc) + timedelta(hours=24),
    )

    db.add(subscriber)
    await db.commit()

    confirmation_link = (
        f"{APP_BASE_URL}/api/subscribe/confirm?token={confirmation_token}"
    )

    background_tasks.add_task(
        send_confirmation_email,
        subscriber.email,
        confirmation_link,
        organization.sender_email,
        organization.sender_name,
    )

    return {"message": "Please check your email to confirm your subscription."}


@router.get("/confirm", status_code=status.HTTP_200_OK)
async def confirm_subscription(token: str, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(
        select(Subscriber).where(Subscriber.confirmation_token == token)
    )
    subscriber = result.scalar_one_or_none()

    if not subscriber:
        return {"message": "Invalid or expired confirmation link."}

    if subscriber.status == "active":
        return {"message": "Subscription already confirmed."}

    if subscriber.confirmation_expires_at < datetime.now(timezone.utc):
        return {"message": "Confirmation link expired."}

    subscriber.status = "active"
    subscriber.is_active = True
    subscriber.confirmed_at = datetime.now(timezone.utc)

    subscriber.confirmation_token = None
    subscriber.confirmation_expires_at = None

    await db.commit()
    return {"" "message": "Your subscription has been confirmed."}


@router.get(
    "/subscriber_list",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
    response_model=Subscriberlist,
)
async def get_subscriber_list(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):

    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="only admin")

    result = await db.execute(select(Subscriber))

    subscriber = result.scalars().all()

    return Subscriberlist(subscribers=subscriber)


@router.get(
    "/subscriber_list/{slug}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(require_admin)],
    response_model=Subscriberlist,
)
async def get_subscriber_list_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="only admin")

    result = await db.execute(
        select(Subscriber).where(Subscriber.organization_id == slug)
    )

    subscriber = result.scalars().all()

    return Subscriberlist(subscribers=subscriber)
