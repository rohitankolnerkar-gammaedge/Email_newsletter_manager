from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime

from app.db.base import Base
class Newsletter(Base):
    __tablename__='Newsletter'
    id=Column(Integer,nullable=False,primary_key=True,unique=True )
    subject=Column(Text,nullable=False)
    content=Column(Text,nullable=False)
    created_at=Column(DateTime,nullable=False,default=datetime.now)

