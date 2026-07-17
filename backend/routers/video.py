from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Literal
from pydantic import BaseModel, Field
from database import get_db
from models import VideoJob, Product
from services import video_ai, llm
from services.cloudinary_client import upload_video
from services.video_quota import get_cycle_bounds, days_until_reset, MONTHLY_CAP
import httpx

router = APIRouter()


class VideoRequest(BaseModel):
    product_id: int
    video_style: Literal["showcase", "model_walk", "dynamic_cut"]
    audio_script: str = Field(min_length=1, max_length=1000)
    language_vibe: str = "High-energy Hinglish"
    product_reference: str = ""  # optional override of catalog product name/color/category


async def _used_this_cycle(db: AsyncSession) -> int:
    start, end = get_cycle_bounds()
    result = await db.execute(
        select(func.count(VideoJob.id)).where(
            VideoJob.status.in_(["pending", "processing", "done"]),
            func.date(VideoJob.created_at) >= start,
            func.date(VideoJob.created_at) <= end,
        )
    )
    return result.scalar() or 0


@router.get("/quota")
async def video_quota(db: AsyncSession = Depends(get_db)):
    used = await _used_this_cycle(db)
    start, end = get_cycle_bounds()
    return {
        "used": used,
        "limit": MONTHLY_CAP,
        "remaining": max(0, MONTHLY_CAP - used),
        "cycle_start": str(start),
        "cycle_end": str(end),
        "days_until_reset": days_until_reset(),
    }


async def _generate_and_save(job_id: int, image_url: str, prompt: str):
    from database import SessionLocal
    async with SessionLocal() as db:
        result = await db.execute(select(VideoJob).where(VideoJob.id == job_id))
        job = result.scalar_one()
        job.status = "processing"
        await db.commit()

        try:
            gen = await video_ai.generate_video(image_url, prompt)
            ai_job_id = gen.get("taskId")
            job.kieai_job_id = ai_job_id
            await db.commit()

            output_url = await video_ai.wait_for_video(ai_job_id)
            if not output_url:
                job.status = "failed"
                await db.commit()
                return

            async with httpx.AsyncClient() as client:
                r = await client.get(output_url)
                video_bytes = r.content

            cloud = upload_video(video_bytes, f"vid_{job_id}")
            job.output_url = output_url
            job.cloudinary_url = cloud["url"]
            job.status = "done"
            await db.commit()

        except Exception:
            job.status = "failed"
            await db.commit()
            raise


@router.post("/generate")
async def generate_video(
    req: VideoRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    # Quota check
    used = await _used_this_cycle(db)
    if used >= MONTHLY_CAP:
        raise HTTPException(
            429,
            detail=f"Monthly video cap reached ({MONTHLY_CAP}/month). "
                   f"Resets in {days_until_reset()} days."
        )

    result = await db.execute(select(Product).where(Product.id == req.product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(404, "Product not found")

    if product.media_type != "image":
        raise HTTPException(400, "Video generation requires an image product")

    product_reference = req.product_reference or f"{product.color} {product.category} — {product.name}"
    prompt = await llm.generate_video_prompt(
        product_reference=product_reference,
        video_style=req.video_style,
        audio_script=req.audio_script,
        language_vibe=req.language_vibe or "High-energy Hinglish",
    )

    job = VideoJob(product_id=req.product_id, prompt=prompt, status="pending")
    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(
        _generate_and_save, job.id, product.cloudinary_url, prompt
    )

    return {
        "job_id": job.id,
        "status": "queued",
        "quota_remaining": MONTHLY_CAP - used - 1,
    }


@router.get("/jobs")
async def list_video_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(VideoJob).order_by(VideoJob.created_at.desc()).limit(30)
    )
    return [j.__dict__ for j in result.scalars().all()]


@router.get("/jobs/{job_id}")
async def get_video_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VideoJob).where(VideoJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404)
    return job.__dict__
