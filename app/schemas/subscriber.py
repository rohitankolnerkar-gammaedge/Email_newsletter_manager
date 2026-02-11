"""from pydantic import fields,EmailStr
from datetime import datetime
from pydantic import BaseModel
class SubscriberBase(BaseModel):
    email:EmailStr

class SubscriberCreate(SubscriberBase):
    pass
class SubscriberCreateRequest(BaseModel):
    user:SubscriberCreate

class SubscriberResponseBase(SubscriberBase):
    id: int
    is_active: bool
    created_at: datetime
class SubscriberResponse(BaseModel):
    single:SubscriberResponseBase  """

from datetime import datetime

from pydantic import BaseModel, EmailStr


class SubscriberCreate(BaseModel):
    email: EmailStr


class SubscriberResponse(BaseModel):
    id: int
    email: EmailStr
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class SubscribePublicResponse(BaseModel):
    message: str


class Subscriberlist(BaseModel):
    subscribers: list[SubscriberResponse]
