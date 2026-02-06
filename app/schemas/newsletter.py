from datetime import datetime
from pydantic import fields,EmailStr,BaseModel
class NewsletterBase(BaseModel):
    subject:str
    content:str
class NewsletterCreate(NewsletterBase):
    pass  
class NewsletterCreateRequest(BaseModel):
    newsletter:NewsletterCreate


class NewsletterResponseBase(NewsletterBase):
    id:int
    created_at:datetime  
class NewsletterResponse(BaseModel):
    response:NewsletterResponseBase
