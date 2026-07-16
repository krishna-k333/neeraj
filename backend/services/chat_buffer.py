"""
Debounce buffer for inbound WhatsApp messages.

Problem it solves: customers often fire 2-3 messages in a row
("मुझे red saree चाहिए" ... "under 1000"). Evolution API delivers each as a
separate webhook, which previously triggered concurrent handlers that:
  - raced on the in-memory history dict (one turn got clobbered), and
  - produced multiple fragmented replies, each blind to the other message.

This module instead buffers messages per phone number for a few seconds. When
the customer goes quiet, all buffered messages are combined into ONE prompt and
answered with a SINGLE reply. A per-phone lock serializes processing so bursts
can never race. Conversation history is rebuilt from the `messages` table, so
it survives restarts (no in-memory history dict).

NOTE: buffers are per-process. If you ever run more than one Uvicorn worker,
route a phone number to a consistent worker or move this to Redis — otherwise
two workers could buffer the same burst separately.
"""
import asyncio
import logging
from collections import defaultdict

from sqlalchemy import select

from database import SessionLocal
from models import Message
from services import evolution, llm

logger = logging.getLogger(__name__)

# How long to wait for more messages before answering (seconds).
DEBOUNCE_SECONDS = 4.0
# How many past messages of context to load into the LLM.
HISTORY_MESSAGES = 6

_FALLBACK_REPLY = "नमस्ते! हम आपकी बात सुन रहे हैं। कृपया थोड़ा इंतजार करें। 🙏"

_buffers: dict[str, list[str]] = {}
_timers: dict[str, asyncio.Task] = {}
_locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


async def enqueue(phone: str, text: str) -> None:
    """Buffer an inbound message and (re)start the debounce countdown."""
    _buffers.setdefault(phone, []).append(text)

    existing = _timers.get(phone)
    if existing and not existing.done():
        existing.cancel()  # newer message arrived — reset the countdown

    _timers[phone] = asyncio.create_task(_wait_and_flush(phone))


async def _wait_and_flush(phone: str) -> None:
    try:
        await asyncio.sleep(DEBOUNCE_SECONDS)
    except asyncio.CancelledError:
        return  # superseded by a newer message; that timer will flush instead
    await _flush(phone)


async def _flush(phone: str) -> None:
    # Lock serializes bursts for this phone: a reply in progress finishes (and
    # is recorded to history) before the next batch is answered.
    async with _locks[phone]:
        texts = _buffers.pop(phone, [])
        _timers.pop(phone, None)
        if not texts:
            return

        combined = "\n".join(texts)
        history = await _load_history(phone)

        try:
            reply = await llm.chat(combined, history)
        except Exception as e:
            logger.error(f"AI chat error for {phone}: {e}")
            reply = _FALLBACK_REPLY

        await _send_and_record(phone, reply)


async def _load_history(phone: str) -> list[dict]:
    """
    Rebuild recent conversation from the DB as [{role, content}, ...].

    Only inbound messages and AI replies count as conversation. Trailing
    inbound rows (the current unanswered batch we're about to answer) are
    dropped so they aren't duplicated alongside the combined prompt.
    """
    async with SessionLocal() as db:
        result = await db.execute(
            select(Message)
            .where(
                Message.phone == phone,
                (Message.direction == "inbound") | (Message.msg_type == "reply"),
            )
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(HISTORY_MESSAGES + 8)
        )
        rows = list(result.scalars().all())

    rows.reverse()  # oldest -> newest

    # Drop the current unanswered batch (trailing inbound rows).
    while rows and rows[-1].direction == "inbound":
        rows.pop()

    rows = rows[-HISTORY_MESSAGES:]
    return [
        {
            "role": "user" if r.direction == "inbound" else "assistant",
            "content": r.content,
        }
        for r in rows
    ]


async def _send_and_record(phone: str, reply: str) -> None:
    try:
        await evolution.send_text(f"91{phone}", reply, delay=False)
    except Exception as e:
        logger.error(f"Evolution send error for {phone}: {e}")
        return

    async with SessionLocal() as db:
        db.add(
            Message(
                phone=phone,
                direction="outbound",
                content=reply,
                status="sent",
                msg_type="reply",
            )
        )
        await db.commit()
