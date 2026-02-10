# mypy: ignore-errors
import asyncio
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import SessionLocal
from app.models.campain import Campaign
from app.models.campain_email import CampaignEmail
from app.models.subscriber import Subscriber
from app.services.send_email import send_email

MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]  # seconds, exponential backoff


async def safe_send_email(
    to_email: str,
    subject: str,
    html_content: str,
    sender_email: str,
    sender_name: str,
) -> bool:
    """
    Send an email safely with retries.
    Returns True if sent successfully, False otherwise.
    """
    for attempt in range(MAX_RETRIES):
        try:
            await asyncio.to_thread(
                send_email,
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                sender_email=sender_email,
                sender_name=sender_name,
            )
            return True
        except Exception as e:
            print(f"[Retry {attempt+1}] Failed to send email to {to_email}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAYS[attempt])
    return False


async def send_campaign_emails(campaign_id: int) -> None:
    async with SessionLocal() as db:
        campaign: Optional[Campaign] = await db.get(
            Campaign,
            campaign_id,
            options=[
                selectinload(Campaign.newsletter),
                selectinload(Campaign.organization),
            ],
        )

        if not campaign:
            return

        # Update campaign status safely
        campaign.status = "sending"
        await db.commit()

        # Fetch active subscribers
        result = await db.execute(
            select(Subscriber).where(
                Subscriber.organization_id == campaign.organization_id,
                Subscriber.is_active.is_(True),
            )
        )
        subscribers: list[Subscriber] = result.scalars().all()

        emails_to_send: list[tuple[Subscriber, CampaignEmail]] = []

        # Create pending CampaignEmail entries
        for sub in subscribers:
            email_record = CampaignEmail(
                campaign_id=campaign.id,
                subscriber_id=sub.id,
                status="pending",
            )
            db.add(email_record)
            emails_to_send.append((sub, email_record))

        await db.commit()  # commit once before sending

        # Send emails
        for sub, email_record in emails_to_send:
            unsubscribe_link = f"https://yourdomain.com/api/subscribe/unsubscribe?token={sub.unsubscribe_token}"

            html_content = f"""
            {campaign.newsletter.content}
            <hr>
            <p>
                If you want to unsubscribe,
                <a href="{unsubscribe_link}">click here</a>.
            </p>
            """

            # Pass only instance attributes (str/datetime) to functions
            success: bool = await safe_send_email(
                to_email=sub.email,  # ✅ str, not Column
                subject=campaign.newsletter.subject,
                html_content=html_content,
                sender_email=campaign.organization.sender_email,
                sender_name=campaign.organization.sender_name,
            )

            email_record.status = "sent" if success else "failed"

        # Update campaign status safely
        total = len(emails_to_send)
        sent_count = sum(1 for _, e in emails_to_send if e.status == "sent")

        if sent_count == total:
            campaign.status = "sent"
        elif sent_count > 0:
            campaign.status = "partial"
        else:
            campaign.status = "failed"

        campaign.sent_at = datetime.now(timezone.utc)
        await db.commit()
