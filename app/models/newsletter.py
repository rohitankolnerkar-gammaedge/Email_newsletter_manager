from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.db.base import Base
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, String
from datetime import datetime
from app.db.base import Base

class Newsletter(Base):
    __tablename__ = "newsletters"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False
    )
    created_by = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    subject = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default="draft")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
