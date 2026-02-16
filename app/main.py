from fastapi import FastAPI

from app.api.api import router
from app.db.base import Base
from app.db.session import engine

app = FastAPI()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app.include_router(router, prefix="/api")


@app.on_event("startup")
async def on_startup():
    await create_tables()


@app.get("/")
def read_root():
    return {"msg": "Hello World"}
