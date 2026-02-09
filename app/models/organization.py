from sqlalchemy import String, Boolean, DateTime, func,Column,INTEGER


from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(INTEGER, primary_key=True, index=True)

    name = Column(String(255), nullable=False)

    slug = Column(String(255), unique=True, nullable=False, index=True)

    email_domain = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
