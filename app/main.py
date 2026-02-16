import os

import uvicorn
from fastapi import FastAPI

from app.api.api import router
from app.db.base import Base
from app.db.session import engine

app = FastAPI()

# Include routers
app.include_router(router, prefix="/api")


# Create database tables
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Startup event
@app.on_event("startup")
async def on_startup():
    await create_tables()


# Root endpoint
@app.get("/")
def read_root():
    return {"msg": "Hello World"}


# Only run with Python, not when imported
if __name__ == "__main__":
    port = int(
        os.environ.get("PORT", 8000)
    )  # use PORT from env or default 8000 locally
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)
