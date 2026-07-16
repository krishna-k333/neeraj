from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Message, SocialPost, VideoJob, Product
from services.warming import get_warming_status
from services.evolution import get_instance_status
from datetime import date

router = APIRouter()


@router.get("/stats")
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    today = str(date.today())

    msgs_sent = await db.scalar(
        select(func.count(Message.id)).where(
            Message.direction == "outbound",
            func.date(Message.created_at) == today,
        )
    ) or 0

    msgs_received = await db.scalar(
        select(func.count(Message.id)).where(
            Message.direction == "inbound",
            func.date(Message.created_at) == today,
        )
    ) or 0

    thankyou_sent = await db.scalar(
        select(func.count(Message.id)).where(
            Message.msg_type == "thankyou",
            func.date(Message.created_at) == today,
        )
    ) or 0

    posts_today = await db.scalar(
        select(func.count(SocialPost.id)).where(
            func.date(SocialPost.created_at) == today,
        )
    ) or 0

    videos_today = await db.scalar(
        select(func.count(VideoJob.id)).where(
            VideoJob.status == "done",
            func.date(VideoJob.created_at) == today,
        )
    ) or 0

    total_products = await db.scalar(select(func.count(Product.id))) or 0

    # Recent activity (last 20 messages)
    recent = await db.execute(
        select(Message).order_by(Message.created_at.desc()).limit(20)
    )
    recent_messages = [m.__dict__ for m in recent.scalars().all()]

    warming = get_warming_status()

    try:
        wa_status = await get_instance_status()
    except Exception:
        wa_status = {"state": "unknown"}

    return {
        "date": today,
        "messages_sent": msgs_sent,
        "messages_received": msgs_received,
        "thankyou_sent": thankyou_sent,
        "posts_scheduled_today": posts_today,
        "videos_created_today": videos_today,
        "total_products_in_catalog": total_products,
        "warming": warming,
        "whatsapp_status": wa_status,
        "recent_activity": recent_messages,
    }
