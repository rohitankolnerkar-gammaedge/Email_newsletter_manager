from datetime import datetime, timezone

from sqlalchemy import INTEGER, Boolean, Column, DateTime, String, func

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(INTEGER, primary_key=True, index=True)

    name = Column(String(255), nullable=False)

    slug = Column(String(255), unique=True, nullable=False, index=True)

    email_domain = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    sender_name = Column(String, nullable=False)
    sender_email = Column(String, nullable=False)
