from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from app.db.base import Base


class Subscriber(Base):
    __tablename__ = "Subscriber"
    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, nullable=False, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    status = Column(String(20), default="pending", nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)

    confirmation_token = Column(String, unique=True, index=True)
    unsubscribe_token = Column(String, unique=True, index=True)
    confirmation_expires_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), unique=True
    )
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    unsubscribed_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    confirmed_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=True,
    )
