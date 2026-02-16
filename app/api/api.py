from fastapi import APIRouter

from app.api.routes import admin_auth, campain, newsletter, subscriber

router = APIRouter()

router.include_router(subscriber.router, prefix="/subscriber", tags=["Subscriber"])
router.include_router(admin_auth.router, prefix="/user_auth", tags=["user_auth"])

router.include_router(newsletter.router, prefix="/newsletter", tags=["newsletter"])

router.include_router(campain.router, prefix="/campain", tags=["campain"])
