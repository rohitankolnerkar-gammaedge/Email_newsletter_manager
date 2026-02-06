from fastapi import APIRouter
from app.api.routes import subscriber

router=APIRouter()

router.include_router(subscriber.router,
                      prefix="/subscriber",
                      tags=["Subscriber"])
