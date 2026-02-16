import asyncio
from datetime import datetime, timezone

from celery import shared_task
from sqlalchemy import select

from app.db.celery_session import SessionLocal
from app.models.campaign import Campaign
from app.models.campain_email import CampaignEmail
from app.models.subscriber import Subscriber
from app.services.send_email import send_email

MAX_RETRIES = 3
RETRY_DELAYS = [1, 2, 4]


def run_async_email(**kwargs):
    return asyncio.run(send_email(**kwargs))


@shared_task(bind=True, max_retries=3)
def send_campaign_emails(self, campaign_id: int):
    db = SessionLocal()

    try:
        campaign = db.get(Campaign, campaign_id)
        if not campaign:
            return "Campaign not found"

        campaign.status = "sending"
        db.commit()

        subscribers = (
            db.execute(
                select(Subscriber).where(
                    Subscriber.organization_id == campaign.organization_id,
                    Subscriber.is_active.is_(True),
                )
            )
            .scalars()
            .all()
        )

        emails_to_send = []

        for sub in subscribers:
            email_record = CampaignEmail(
                campaign_id=campaign.id,
                subscriber_id=sub.id,
                status="pending",
            )
            db.add(email_record)
            emails_to_send.append((sub, email_record))

        db.commit()

        for sub, email_record in emails_to_send:
            success = False

            for attempt in range(MAX_RETRIES):
                try:
                    html_content = f"""
                    {campaign.newsletter.content}
                    <hr>
                    <p>If you want to unsubscribe,
                    <a href="#">{sub.unsubscribe_token}</a></p>
                    """

                    run_async_email(
                        to_email=sub.email,
                        subject=campaign.newsletter.subject,
                        html_content=html_content,
                        sender_email=campaign.organization.sender_email,
                        sender_name=campaign.organization.sender_name,
                    )

                    success = True
                    break

                except Exception as e:
                    print(f"[Retry {attempt+1}] Failed: {e}")

                    if attempt < MAX_RETRIES - 1:
                        import time

                        time.sleep(RETRY_DELAYS[attempt])

            email_record.status = "sent" if success else "failed"

        sent_count = sum(1 for _, e in emails_to_send if e.status == "sent")
        total = len(emails_to_send)

        if total == 0:
            campaign.status = "failed"
        elif sent_count == total:
            campaign.status = "sent"
        elif sent_count > 0:
            campaign.status = "partial"
        else:
            campaign.status = "failed"

        campaign.sent_at = datetime.now(timezone.utc)
        db.commit()

    except Exception as exc:
        db.rollback()
        raise self.retry(exc=exc, countdown=60)

    finally:
        db.close()
