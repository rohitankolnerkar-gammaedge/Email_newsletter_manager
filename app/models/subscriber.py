from sqlalchemy import Column, Integer, String, Text, DateTime,Boolean,ForeignKey
from datetime import datetime
from app.db.base import Base
from sqlalchemy.sql import func
class Subscriber(Base):
    __tablename__="Subscriber"
    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, nullable=False, index=True)

    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    is_active = Column(Boolean, default=False, nullable=False)

    confirmation_token = Column(String, unique=True, index=True)
    unsubscribe_token = Column(String, unique=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    unsubscribed_at = Column(DateTime(timezone=True))