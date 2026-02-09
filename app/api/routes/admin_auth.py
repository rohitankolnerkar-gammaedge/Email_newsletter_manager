from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_async_db
from app.models.users import User
from app.models.organization import Organization
from app.core.security import hash_password,verify_password,create_access_token
from app.schemas.auth import UserCreate,UserLogin,Token

router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user: UserCreate, db: AsyncSession = Depends(get_async_db)):
    # check existing
    result = await db.execute(select(User).where(User.email == user.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    org = await db.get(Organization, user.organization_id)
    if not org:
        raise HTTPException(status_code=400, detail="Organization not found")

    new_user = User(
        email=user.email,
        password_hash=hash_password(user.password),
        role=user.role,
        organization_id=org.id
    )
    db.add(new_user)
    await db.commit()
    return {"message": "User created successfully"}

@router.post("/login", response_model=Token)
async def login(payload: UserLogin, db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "role": user.role, "org_id": user.organization_id})
    return {"access_token": access_token, "token_type": "bearer"}
