# app/main.py
from fastapi import FastAPI

from app.api.api import router
from app.db.base import Base
from app.db.session import engine
from app.services.redis import redis_client

app = FastAPI()
app.include_router(router, prefix="/api")


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created successfully")


@app.on_event("startup")
async def on_startup():
    # 1. Create tables safely
    try:
        await create_tables()
    except Exception as e:
        print(f"Database tables creation failed: {e}")

    # 2. Ping Redis safely
    if redis_client:
        try:
            pong = await redis_client.ping()
            print(f" Redis connected: {pong}")
        except Exception as e:
            print(f"Redis ping failed: {e}")


@app.get("/")
def read_root():
    return {"msg": "Hello World"}
