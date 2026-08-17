"""
WhatsApp chatbot inbound handler + Evolution API webhook receiver.
"""
import asyncio
import logging

from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from config import settings
from database import get_db, SessionLocal
from models import Message
from services import evolution, chat_buffer, vision

router = APIRouter()
logger = logging.getLogger(__name__)


def _extract_upsert_messages(payload: dict) -> list[dict]:
    """Normalize Evolution message payloads across supported versions."""
    data = payload.get("data")
    if not isinstance(data, dict):
        return []

    nested = data.get("messages")
    if isinstance(nested, list):
        return [message for message in nested if isinstance(message, dict)]
    if isinstance(nested, dict):
        return [nested]

    # Evolution v2 sends a single message directly inside `data`.
    if isinstance(data.get("key"), dict) and isinstance(data.get("message"), dict):
        return [data]

    return []


def _message_phone(message: dict) -> str:
    """Return the best phone-like identifier from an Evolution message key."""
    key = message.get("key", {})
    if not isinstance(key, dict):
        return ""

    remote_jid = key.get("remoteJid", "")
    remote_jid_alt = key.get("remoteJidAlt", "")

    # Recent Baileys payloads may use an opaque @lid remoteJid and provide the
    # real WhatsApp phone number in remoteJidAlt.
    jid = remote_jid
    if isinstance(remote_jid_alt, str) and remote_jid_alt.endswith("@s.whatsapp.net"):
        jid = remote_jid_alt

    if not isinstance(jid, str) or "@" not in jid:
        return ""
    return jid.split("@", 1)[0]


async def _handle_image(phone: str, message_id: str, caption: str):
    """
    Background: fetch the photo from Evolution, have Gemini describe it, then
    push a text summary into the same debounce buffer as normal messages —
    so an image followed by a text ("under 1000") still merges into one reply.
    """
    description = ""
    try:
        b64, mime = await evolution.get_media_base64(message_id)
        description = await vision.describe_image(b64, mime, caption)
    except Exception as e:
        logger.error(f"Image handling failed for {phone}: {e}")

    if description:
        text = f"{caption}\n(ग्राहक ने एक फोटो भेजी। फोटो में: {description})".strip()
    else:
        # Never leave the customer on silence, even if vision fails.
        text = caption or "(ग्राहक ने एक फोटो भेजी — कृपया पूछें कि उन्हें क्या चाहिए)"

    async with SessionLocal() as db:
        db.add(Message(phone=phone, direction="inbound", content=text,
                       status="replied", msg_type="image"))
        await db.commit()

    await chat_buffer.enqueue(phone, text)


@router.post("/webhook")
async def evolution_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Receives inbound WhatsApp messages from Evolution API webhook.

    Each inbound message is saved and handed to the debounce buffer, which
    waits a few seconds for follow-up messages and then answers the whole
    burst with a single, context-aware reply. Returns immediately so Evolution
    gets a fast 200 (the reply is generated in the background).
    """
    try:
        payload = await request.json()
    except Exception as e:
        logger.warning(f"webhook: non-JSON body: {e}")
        return {"ok": False, "reason": "invalid-json"}

    event = payload.get("event", "")
    if event != "messages.upsert":
        logger.info(f"webhook: ignoring event={event!r}")
        return {"ok": True}

    messages = _extract_upsert_messages(payload)

    logger.info(f"webhook: messages.upsert with {len(messages)} msg(s)")

    for msg in messages:
        if msg.get("key", {}).get("fromMe"):
            continue  # skip outbound

        phone = _message_phone(msg)
        if not phone:
            logger.warning(f"webhook: msg without remoteJid, skipping: {msg.get('key')}")
            continue

        msg_body = msg.get("message", {})

        # Image message → describe with Gemini in the background (slow), then
        # it flows into the buffer like any other message.
        image = msg_body.get("imageMessage")
        if image is not None:
            message_id = msg.get("key", {}).get("id", "")
            caption = image.get("caption", "")
            if message_id:
                asyncio.create_task(_handle_image(phone, message_id, caption))
            continue

        text = msg_body.get("conversation", "") or \
               msg_body.get("extendedTextMessage", {}).get("text", "")

        if not text:
            logger.info(f"webhook: msg from {phone} has no text, skipping")
            continue

        logger.info(f"webhook: {phone} -> {text!r}")

        # Persist the inbound message (record + history source of truth).
        db.add(Message(phone=phone, direction="inbound", content=text, status="replied"))
        await db.commit()

        # Buffer + debounce: a single coherent reply per burst, no races.
        await chat_buffer.enqueue(phone, text)

    return {"ok": True}


@router.get("/status")
async def whatsapp_status():
    status = await evolution.get_instance_status()
    return status


@router.post("/webhook/simulate")
async def simulate_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Dev-only: manually push a message through the same path Evolution uses.
    Lets you test the chatbot end-to-end without depending on Evolution's
    webhook URL being wired up.

    Body: {"phone": "918287367640", "text": "hello"}
    """
    if not settings.DEBUG:
        raise HTTPException(status_code=404, detail="Not available")

    body = await request.json()
    phone = body.get("phone", "").replace("@s.whatsapp.net", "")
    text = body.get("text", "")
    if not phone or not text:
        raise HTTPException(status_code=400, detail="phone and text required")

    db.add(Message(phone=phone, direction="inbound", content=text, status="replied"))
    await db.commit()
    await chat_buffer.enqueue(phone, text)
    return {"ok": True, "phone": phone, "text": text}


@router.get("/conversations")
async def list_conversations(db: AsyncSession = Depends(get_db)):
    """
    One row per phone number: last message + timestamp + unread (inbound
    since last outbound) count, newest activity first.
    """
    last_ts_sq = (
        select(Message.phone, func.max(Message.created_at).label("last_at"))
        .group_by(Message.phone)
        .subquery()
    )

    result = await db.execute(
        select(Message)
        .join(last_ts_sq, (Message.phone == last_ts_sq.c.phone) & (Message.created_at == last_ts_sq.c.last_at))
        .order_by(last_ts_sq.c.last_at.desc())
    )
    last_messages = result.scalars().all()

    return [
        {
            "phone": last.phone,
            "last": last.content,
            "direction": last.direction,
            "time": last.created_at.isoformat() if last.created_at else None,
        }
        for last in last_messages
    ]


@router.get("/messages")
async def get_messages(phone: str, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """Full chat history for one phone number, oldest first."""
    result = await db.execute(
        select(Message)
        .where(Message.phone == phone)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(reversed(result.scalars().all()))
    return [
        {
            "id": m.id,
            "direction": m.direction,
            "content": m.content,
            "status": m.status,
            "msg_type": m.msg_type,
            "time": m.created_at.isoformat() if m.created_at else None,
        }
        for m in messages
    ]
