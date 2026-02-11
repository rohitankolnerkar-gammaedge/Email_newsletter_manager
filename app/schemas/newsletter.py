from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class NewsletterBase(BaseModel):
    subject: str
    content: str


class NewsletterCreate(NewsletterBase):
    pass


class NewsletterCreateRequest(BaseModel):
    newsletter: NewsletterCreate


class NewsletterResponse(NewsletterBase):
    id: int
    organization_id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class NewsletterUpdate(BaseModel):
    subject: Optional[str] = None
    content: Optional[str] = None
