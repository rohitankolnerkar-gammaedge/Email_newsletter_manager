from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import require_admin
from app.db.session import get_async_db
from app.models.newsletter import Newsletter
from app.models.users import User
from app.schemas.newsletter import (
    NewsletterCreate,
    NewsletterResponse,
    NewsletterUpdate,
)

router = APIRouter()


@router.post(
    "/create_newsletter",
    dependencies=[Depends(require_admin)],
    status_code=status.HTTP_201_CREATED,
    response_model=NewsletterResponse,
)
async def create_newsletter(
    payload: NewsletterCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    newsletter = Newsletter(
        subject=payload.subject,
        content=payload.content,
        organization_id=current_user.organization_id,
        status="draft",
    )

    db.add(newsletter)
    await db.commit()
    await db.refresh(newsletter)

    return newsletter


@router.get(
    "/list_newsletter",
    dependencies=[Depends(require_admin)],
    response_model=List[NewsletterResponse],
    status_code=status.HTTP_200_OK,
)
async def list_newsletter(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(
        select(Newsletter)
        .where(Newsletter.organization_id == current_user.organization_id)
        .order_by(desc(Newsletter.created_at))
    )
    Newsletters = result.scalars().all()
    return Newsletters


@router.get("/get_newsletter/{newsletter_id}", response_model=NewsletterResponse)
async def get_newsletter(
    newsletter_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(require_admin),
):
    result = await db.execute(
        select(Newsletter).where(
            Newsletter.id == newsletter_id,
            Newsletter.organization_id == current_user.organization_id,
        )
    )

    newsletter = result.scalar_one_or_none()

    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    return newsletter


@router.put("/update_newsletter/{newsletter_id}", response_model=NewsletterResponse)
async def update_newsletter(
    newsletter_id: int,
    payload: NewsletterUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(require_admin),
):
    result = await db.execute(
        select(Newsletter).where(
            Newsletter.id == newsletter_id,
            Newsletter.organization_id == current_user.organization_id,
        )
    )

    newsletter = result.scalar_one_or_none()

    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    if newsletter.status != "draft":
        raise HTTPException(
            status_code=400, detail="Only draft newsletters can be edited"
        )

    # Update only provided fields
    if payload.subject is not None:
        newsletter.subject = payload.subject

    if payload.content is not None:
        newsletter.content = payload.content

    await db.commit()
    await db.refresh(newsletter)

    return newsletter


@router.delete(
    "/delete_newsletter/{newsletter_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_newsletter(
    newsletter_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(require_admin),
):
    result = await db.execute(
        select(Newsletter).where(
            Newsletter.id == newsletter_id,
            Newsletter.organization_id == current_user.organization_id,
        )
    )

    newsletter = result.scalar_one_or_none()

    if not newsletter:
        raise HTTPException(status_code=404, detail="Newsletter not found")

    if newsletter.status != "draft":
        raise HTTPException(
            status_code=400, detail="Only draft newsletters can be deleted"
        )

    await db.delete(newsletter)
    await db.commit()
