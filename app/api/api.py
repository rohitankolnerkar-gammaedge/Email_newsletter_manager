from fastapi import APIRouter
from app.api.routes import subscriber
from app.api.routes import admin_auth

router=APIRouter()

router.include_router(subscriber.router,
                      prefix="/subscriber",
                      tags=["Subscriber"])
router.include_router(admin_auth.router,prefix="/user_auth",tags=['user_auth'])
