from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Message, SocialPost, VideoJob, Product
from services.warming import get_warming_status
from services.evolution import get_instance_status
from datetime import date, timedelta

router = APIRouter()


def _delta_str(today: int, yesterday: int) -> dict | None:
    """Build a {value, up} trend chip from two daily counts.

    - Returns None when both are 0 so the UI can hide the chip instead of
      showing a fake "0%" or misleading arrow.
    - When yesterday is 0 but today > 0, format as absolute delta (+N) to
      avoid "Infinity%" or "NaN%" chips.
    """
    if today == 0 and yesterday == 0:
        return None
    if yesterday == 0:
        return {"value": f"+{today}", "up": today > 0}
    diff = today - yesterday
    pct = (diff / yesterday) * 100
    if pct == 0:
        return {"value": "0%", "up": False}
    sign = "+" if pct > 0 else ""
    return {"value": f"{sign}{pct:.0f}%", "up": diff > 0}


async def _daily_count(db: AsyncSession, model, where_clauses, day: str) -> int:
    """Generic daily row count for any model with `created_at`."""
    stmt = select(func.count(model.id)).where(
        func.date(model.created_at) == day,
        *where_clauses,
    )
    return (await db.scalar(stmt)) or 0


@router.get("/stats")
async def dashboard_stats(db: AsyncSession = Depends(get_db)):
    today = str(date.today())
    yesterday = str(date.today() - timedelta(days=1))

    msgs_sent = await _daily_count(db, Message, [Message.direction == "outbound"], today)
    msgs_received = await _daily_count(db, Message, [Message.direction == "inbound"], today)
    thankyou_sent = await _daily_count(db, Message, [Message.msg_type == "thankyou"], today)

    msgs_sent_y = await _daily_count(db, Message, [Message.direction == "outbound"], yesterday)
    msgs_received_y = await _daily_count(db, Message, [Message.direction == "inbound"], yesterday)
    thankyou_sent_y = await _daily_count(db, Message, [Message.msg_type == "thankyou"], yesterday)

    posts_today = await _daily_count(db, SocialPost, [], today)
    videos_today = await _daily_count(db, VideoJob, [VideoJob.status == "done"], today)
    total_products = (await db.scalar(select(func.count(Product.id)))) or 0

    # Recent activity (last 20 messages)
    recent = await db.execute(
        select(Message).order_by(Message.created_at.desc()).limit(20)
    )
    recent_messages = [m.__dict__ for m in recent.scalars().all()]

    # Keep the dashboard chart tied to actual message activity, including days
    # with no messages so the last-seven-days timeline remains stable.
    chart_start = date.today() - timedelta(days=6)
    chart_rows = await db.execute(
        select(func.date(Message.created_at), func.count(Message.id))
        .where(func.date(Message.created_at) >= str(chart_start))
        .group_by(func.date(Message.created_at))
    )
    chart_counts = {str(day): count for day, count in chart_rows.all()}
    seven_day_messages = [
        chart_counts.get(str(chart_start + timedelta(days=offset)), 0)
        for offset in range(7)
    ]

    warming = get_warming_status()

    try:
        wa_status = await get_instance_status()
    except Exception:
        wa_status = {"state": "unknown"}

    # Real trends: today vs yesterday. None means "no data, hide the chip".
    trends = {
        "messages_received": _delta_str(msgs_received, msgs_received_y),
        "messages_sent": _delta_str(msgs_sent, msgs_sent_y),
        "thankyou_sent": _delta_str(thankyou_sent, thankyou_sent_y),
    }

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
        "seven_day_messages": seven_day_messages,
        "trends": trends,
    }
