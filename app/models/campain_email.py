from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base import Base


class CampaignEmail(Base):
    __tablename__ = "campaign_emails"

    id = Column(Integer, primary_key=True)
    campaign_id = Column(
        Integer, ForeignKey("campaigns.id", ondelete="CASCADE"), index=True
    )
    subscriber_id = Column(
        Integer, ForeignKey("Subscriber.id", ondelete="CASCADE"), index=True
    )

    status = Column(String(20), default="pending")  # pending | sent | failed
    sent_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
    error = Column(Text, nullable=True)

    # relationships
    campaign = relationship("Campaign", back_populates="emails")
    subscriber = relationship("Subscriber")
