from fastapi import APIRouter
from app.api.routes import subscriber
from app.api.routes import admin_auth
from app.api.routes import newsletter
router=APIRouter()

router.include_router(subscriber.router,
                      prefix="/subscriber",
                      tags=["Subscriber"])
router.include_router(admin_auth.router,
                      prefix="/user_auth",
                      tags=['user_auth'])

router.include_router(newsletter.router,
                      prefix="/newsletter",
                      tags=['newsletter'])

