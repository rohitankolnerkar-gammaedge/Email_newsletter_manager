# app/models/campaign.py

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(
        Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False
    )

    newsletter_id = Column(
        Integer, ForeignKey("newsletters.id", ondelete="CASCADE"), nullable=False
    )

    created_by = Column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    status = Column(
        String(20), nullable=False, default="pending"
    )  # pending , sending , sent ,failed

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    sent_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
    newsletter = relationship("Newsletter", lazy="selectin")
    organization = relationship("Organization", lazy="selectin")
