"""
Broadcast message sender with warming schedule enforcement.
Anti-block: 2.5–5s random delay between messages.
"""
import asyncio
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from database import get_db
from models import BroadcastJob, Message, DailyStat
from services import evolution
from services.warming import get_daily_limit, can_send_outbound, get_warming_status
from datetime import date

router = APIRouter()
logger = logging.getLogger(__name__)


class BroadcastRequest(BaseModel):
    name: str
    message_text: str
    phones: list[str]
    media_url: str = ""


async def _get_today_sent_count(db: AsyncSession) -> int:
    today = str(date.today())
    result = await db.execute(
        select(func.count(Message.id)).where(
            Message.direction == "outbound",
            func.date(Message.created_at) == today,
        )
    )
    return result.scalar() or 0


async def _run_broadcast(job_id: int, phones: list[str], text: str, media_url: str):
    """Background task: send messages with rate limiting and random delays."""
    from database import SessionLocal
    async with SessionLocal() as db:
        result = await db.execute(select(BroadcastJob).where(BroadcastJob.id == job_id))
        job = result.scalar_one()
        job.status = "running"
        await db.commit()

        daily_limit = get_daily_limit()
        today_sent = await _get_today_sent_count(db)
        remaining_quota = daily_limit - today_sent

        if remaining_quota <= 0:
            job.status = "cancelled"
            job.failed_count = len(phones)
            await db.commit()
            logger.warning(f"Broadcast {job_id}: daily limit reached ({daily_limit})")
            return

        phones_to_send = phones[:remaining_quota]
        skipped = len(phones) - len(phones_to_send)
        if skipped > 0:
            logger.info(f"Broadcast {job_id}: skipping {skipped} recipients (daily limit)")

        for phone in phones_to_send:
            try:
                # Normalize phone
                clean = phone.replace("+", "").replace(" ", "").replace("-", "")
                if not clean.startswith("91"):
                    clean = f"91{clean}"

                if media_url:
                    await evolution.send_image(clean, media_url, text)
                else:
                    await evolution.send_text(clean, text)

                msg = Message(phone=clean, direction="outbound", content=text,
                              status="sent", msg_type="broadcast")
                db.add(msg)
                job.sent_count += 1
                await db.commit()

            except Exception as e:
                logger.error(f"Broadcast send failed to {phone}: {e}")
                msg = Message(phone=phone, direction="outbound", content=text,
                              status="failed", msg_type="broadcast")
                db.add(msg)
                job.failed_count += 1
                await db.commit()

        job.status = "done"
        from datetime import datetime
        job.completed_at = datetime.utcnow()
        await db.commit()
        logger.info(f"Broadcast {job_id} complete: {job.sent_count} sent, {job.failed_count} failed")


@router.get("/warming-status")
async def warming_status():
    return get_warming_status()


@router.post("/send")
async def send_broadcast(
    req: BroadcastRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    if not can_send_outbound():
        raise HTTPException(
            403,
            detail="Outbound messages blocked during the first 3 days (listen-only mode). "
                   "This protects your WhatsApp number from being banned."
        )

    daily_limit = get_daily_limit()
    today_sent = await _get_today_sent_count(db)

    if today_sent >= daily_limit:
        raise HTTPException(
            429,
            detail=f"Daily limit of {daily_limit} messages reached. Try again tomorrow."
        )

    job = BroadcastJob(
        name=req.name,
        message_text=req.message_text,
        media_url=req.media_url,
        total_recipients=len(req.phones),
        status="queued",
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    background_tasks.add_task(
        _run_broadcast, job.id, req.phones, req.message_text, req.media_url
    )

    return {
        "job_id": job.id,
        "queued": len(req.phones),
        "daily_limit": daily_limit,
        "already_sent_today": today_sent,
        "will_send": min(len(req.phones), daily_limit - today_sent),
    }


@router.get("/jobs")
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(BroadcastJob).order_by(BroadcastJob.created_at.desc()).limit(50)
    )
    return [j.__dict__ for j in result.scalars().all()]


@router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BroadcastJob).where(BroadcastJob.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Job not found")
    return job.__dict__
