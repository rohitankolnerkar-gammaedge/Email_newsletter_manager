from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.db.session import get_async_db
from app.models.campain import Campaign
from app.models.newsletter import Newsletter
from app.schemas.campain import CampaignCreate, CampaignResponse
from app.tasks.send_campain_emails import send_campaign_emails

router = APIRouter()


@router.post("/", response_model=CampaignResponse)
async def send_newsletter(
    payload: CampaignCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(require_admin),
):
    result = await db.execute(
        select(Newsletter).where(
            Newsletter.id == payload.newsletter_id,
            Newsletter.organization_id == current_user.organization_id,
        )
    )
    newsletter = result.scalar_one_or_none()

    if not newsletter:
        raise HTTPException(404, "Newsletter not found")

    if newsletter.status != "draft":
        raise HTTPException(400, "Newsletter already used")

    campaign = Campaign(
        newsletter_id=newsletter.id,
        organization_id=current_user.organization_id,
        created_by=current_user.id,
        status="pending",
    )

    newsletter.status = "locked"

    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    background_tasks.add_task(send_campaign_emails, campaign.id)

    return campaign
