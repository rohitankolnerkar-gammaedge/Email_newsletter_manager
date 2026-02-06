from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.subscriber import SubscribePublicResponse,SubscriberCreate
from app.db.session import get_async_db
from app.models.subscriber import Subscriber
from sqlalchemy import select
import uuid
import datetime
from app.models.organization import Organization

router=APIRouter()

@router.post("/subscribe/{company_slug}",operation_id="subscribe",description="user subscribe",response_model=SubscribePublicResponse)
async def subscribe(company_slug:str,
                    payload:SubscriberCreate,
                    db:AsyncSession=Depends(get_async_db)):
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
    conformation_token = str(uuid.uuid4())
    unsubscribe_token=str(uuid.uuid4())
    subscriber = Subscriber(
        email=payload.email,
        organization_id=organization.id,
        is_active=False,
        confirmation_token=conformation_token,
        unsubscribe_token=unsubscribe_token,
        created_at=datetime.datetime.now()
    )

    db.add(subscriber)
    await db.commit()
    return {
        "message": "Please check your email to confirm your subscription."
    }

@router.get("/unsubscribe")
async def unsubscribe(
    token: str,
    db: AsyncSession = Depends(get_async_db),
):
    result = await db.execute(
        select(Subscriber).where(Subscriber.unsubscribe_token == token)
    )
    subscriber = result.scalar_one_or_none()

    if not subscriber:
        # Do NOT reveal anything
        return {"message": "You have been unsubscribed."}

    if not subscriber.is_active:
        return {"message": "You are already unsubscribed."}

    subscriber.is_active = False
    subscriber.unsubscribed_at = datetime.datetime.now()

    await db.commit()

    return {"message": "You have been unsubscribed successfully."}