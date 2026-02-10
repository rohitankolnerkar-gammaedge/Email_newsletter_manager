from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models.campain import Campaign
from app.models.subscriber import Subscriber
from app.services.send_email import send_email


async def send_campaign_emails(campaign_id: int):
    async with SessionLocal() as db:
        campaign = await db.get(
            Campaign,
            campaign_id,
            options=[
                selectinload(Campaign.newsletter),
                selectinload(Campaign.organization),
            ],
        )

        if not campaign:
            return

        campaign.status = "sending"
        await db.commit()

        result = await db.execute(
            select(Subscriber).where(
                Subscriber.organization_id == campaign.organization_id,
                Subscriber.is_active.is_(True),
            )
        )
        subscribers = result.scalars().all()

        try:
            for sub in subscribers:
                unsubscribe_link = (
                    f"https://yourdomain.com/api/subscribe/unsubscribe"
                    f"?token={sub.unsubscribe_token}"
                )

                html_content = f"""
                {campaign.newsletter.content}
                <hr>
                <p>
                    If you want to unsubscribe,
                    <a href="{unsubscribe_link}">click here</a>.
                </p>
                """

                # IMPORTANT: send_email is SYNC → do NOT await
                send_email(
                    to_email=sub.email,
                    subject=campaign.newsletter.subject,
                    html_content=html_content,
                    sender_email=campaign.organization.sender_email,
                    sender_name=campaign.organization.sender_name,
                )

            campaign.status = "sent"
            campaign.sent_at = datetime.now(timezone.utc)

        except Exception as e:
            campaign.status = "failed"

        await db.commit()
