from datetime import datetime

from pydantic import BaseModel


class CampaignCreate(BaseModel):
    newsletter_id: int


class CampaignResponse(BaseModel):
    id: int
    newsletter_id: int
    status: str
    created_at: datetime
    sent_at: datetime | None

    class Config:
        from_attributes = True
