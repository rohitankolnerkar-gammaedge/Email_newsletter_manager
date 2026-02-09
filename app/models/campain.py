# app/models/campaign.py
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from datetime import datetime
from app.db.base import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )

    newsletter_id = Column(
        Integer,
        ForeignKey("newsletters.id", ondelete="CASCADE"),
        nullable=False
    )

    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending"
    )# pending , sending , sent ,failed

    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True)
