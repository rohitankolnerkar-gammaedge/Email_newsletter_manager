import os

import uvicorn
from fastapi import FastAPI

from app.api.api import router
from app.db.base import Base
from app.db.session import engine

app = FastAPI()


app.include_router(router, prefix="/api")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("startup")
async def on_startup():
    await create_tables()


@app.get("/")
def read_root():
    return {"msg": "Hello World"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
