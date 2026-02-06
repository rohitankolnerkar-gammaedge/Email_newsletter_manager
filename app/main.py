from fastapi import FastAPI
from app.db.session import engine
from app.db .base import Base
from app.models.newsletter import Newsletter
from app.models.subscriber import Subscriber
from app.api.api import router
app=FastAPI()
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(router,prefix="/api")

@app.on_event("startup")
async def on_startup():
    await create_tables()

@app.get("/")
def read_root():
    return {"msg": "Hello World"}