"""
Postiz integration — POST ONCE, FAN OUT to all connected platforms.
Owner writes one caption + one media, we push to Instagram + YouTube + Facebook + Google My Business simultaneously.
"""
import httpx
import asyncio
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import SocialPost
from config import settings

router = APIRouter()

VALID_PLATFORMS = ["instagram", "youtube", "facebook", "google_my_business"]


class MultiPostRequest(BaseModel):
    caption: str
    media_url: str
    scheduled_at: datetime
    platforms: list[str] = VALID_PLATFORMS  # default → all three


async def _postiz_create(platform: str, caption: str, media_url: str, when: datetime) -> dict:
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            f"{settings.POSTIZ_URL}/api/posts",
            headers={
                "Authorization": f"Bearer {settings.POSTIZ_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "platform": platform,
                "content": caption,
                "media": [{"url": media_url}],
                "publishDate": when.isoformat(),
            }
        )
        r.raise_for_status()
        return r.json()


@router.post("/schedule")
async def schedule_post_everywhere(req: MultiPostRequest, db: AsyncSession = Depends(get_db)):
    """
    ONE compose → posts on IG + YT + FB simultaneously.
    Owner never has to duplicate content.
    """
    platforms = [p for p in req.platforms if p in VALID_PLATFORMS]
    if not platforms:
        raise HTTPException(400, "Pick at least one platform")

    # Fan out in parallel
    tasks = [
        _postiz_create(p, req.caption, req.media_url, req.scheduled_at)
        for p in platforms
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    saved = []
    for platform, resp in zip(platforms, results):
        if isinstance(resp, Exception):
            # Save as failed record so owner sees it
            post = SocialPost(
                platform=platform,
                caption=req.caption,
                media_url=req.media_url,
                scheduled_at=req.scheduled_at,
                status="failed",
            )
        else:
            post = SocialPost(
                platform=platform,
                caption=req.caption,
                media_url=req.media_url,
                postiz_post_id=str(resp.get("id", "")),
                scheduled_at=req.scheduled_at,
                status="scheduled",
            )
        db.add(post)
        saved.append({"platform": platform, "status": post.status})

    await db.commit()
    return {
        "posted_to": platforms,
        "results": saved,
        "caption": req.caption,
        "scheduled_at": req.scheduled_at.isoformat(),
    }


@router.get("/posts")
async def list_posts(platform: str = None, db: AsyncSession = Depends(get_db)):
    q = select(SocialPost).order_by(SocialPost.created_at.desc()).limit(50)
    if platform:
        q = q.where(SocialPost.platform == platform)
    result = await db.execute(q)
    return [p.__dict__ for p in result.scalars().all()]
