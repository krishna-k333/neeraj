"""
Reply router for inbound WhatsApp messages.

Decides: static reply (no LLM) vs LLM reply.

Design goals:
  - Keep the first customer reply and menu navigation deterministic.
  - Use AI for every later non-menu message.
  - Scoped to ONE phone for safe roll-out; every other customer is receive-only.

Rules (evaluated in order):
  1. First customer message                        -> static welcome
  2. Exact single digit '1'/'2'/'3'                -> static menu replies
  3. Exact single digit '4'/'5'                   -> static price replies
  4. Everything else                               -> LLM
"""
import re
from dataclasses import dataclass

from sqlalchemy import select, func

from database import SessionLocal
from models import Message
from services import menu

# === Test-scope: ONLY this phone receives automated replies for now ===
# Other phones are recorded by the webhook but the response pipeline stops.
TEST_PHONE = "918287367640"


@dataclass
class RouteDecision:
    use_llm: bool
    reply: str | None  # populated only when use_llm=False
    reason: str


# ---------------------------------------------------------------------------
# Pattern matchers
# ---------------------------------------------------------------------------
_DIGIT_RE = re.compile(r"^\s*([0-9])\s*$")
# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def is_first_customer_message(phone: str, current_batch_size: int = 1) -> bool:
    """True when the current inbound batch contains the customer's first text."""
    async with SessionLocal() as db:
        result = await db.execute(
            select(func.count(Message.id)).where(
                Message.phone == phone,
                Message.direction == "inbound",
            )
        )
        inbound_count = result.scalar() or 0
        return inbound_count <= max(current_batch_size, 1)


async def _price_menu_is_active(phone: str) -> bool:
    """Return True when the last bot menu asks the customer for a category."""
    async with SessionLocal() as db:
        result = await db.execute(
            select(Message.content)
            .where(
                Message.phone == phone,
                Message.direction == "outbound",
            )
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(1)
        )
        last_reply = result.scalar_one_or_none()
    return bool(last_reply and last_reply == menu.PRICE_MENU)


def _norm(text: str) -> str:
    return (text or "").strip()


# ---------------------------------------------------------------------------
# The decision
# ---------------------------------------------------------------------------
async def decide(
    phone: str,
    combined_text: str,
    history: list[dict] | None = None,
    is_first_message: bool = False,
) -> RouteDecision:
    """
    Decide what to do with this inbound batch.

    `combined_text` is the merged text from the chat_buffer (multiple messages
    joined with newlines). `history` is the prior LLM-context for this phone.
    `is_first_message` is computed after the inbound row is persisted.
    """
    text = _norm(combined_text)

    # ------------------------------------------------------------------
    # ONLY the test phone uses this engine. Everyone else is receive-only.
    # ------------------------------------------------------------------
    if phone != TEST_PHONE:
        return RouteDecision(use_llm=False, reply=None, reason="phone-not-test-scope")

    # ------------------------------------------------------------------
    # 0. Empty / whitespace -> ignore silently (chat_buffer filters upstream,
    #    but be defensive).
    # ------------------------------------------------------------------
    if not text:
        return RouteDecision(use_llm=False, reply=None, reason="empty")

    if is_first_message:
        return RouteDecision(use_llm=False, reply=menu.WELCOME, reason="first-message")

    # ------------------------------------------------------------------
    # 1. Pure single-digit input
    # ------------------------------------------------------------------
    m = _DIGIT_RE.match(text)
    if m and "\n" not in text:
        digit = m.group(1)
        # Once the customer selected Products & Price, 1–5 belong to the
        # category menu. This takes precedence over the top-level menu so a
        # follow-up "1" cannot incorrectly return the store location.
        if digit in ("1", "2", "3", "4", "5") and await _price_menu_is_active(phone):
            r = menu.price_reply(digit)
            if r:
                return RouteDecision(use_llm=False, reply=r, reason=f"price-submenu:{digit}")
        # 1/2/3 are inside the menu
        if digit == "1":
            return RouteDecision(use_llm=False, reply=menu.LOCATION_REPLY, reason="menu:1-location")
        if digit == "2":
            return RouteDecision(use_llm=False, reply=menu.PRICE_MENU, reason="menu:2-price")
        if digit == "3":
            return RouteDecision(use_llm=False, reply=menu.CATALOGUE_REPLY, reason="menu:3-catalogue")
        # 4/5 are inside the PRICE sub-menu
        if digit in ("4", "5"):
            r = menu.price_reply(digit)
            if r:
                return RouteDecision(use_llm=False, reply=r, reason=f"price-submenu:{digit}")
    # Every later non-menu message uses AI, including 6, greetings, thanks,
    # contact details, and ordinary product questions.
    return RouteDecision(use_llm=True, reply=None, reason="fallback-llm")
