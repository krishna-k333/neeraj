"""
Reply router for inbound WhatsApp messages.

Decides: static reply (no LLM) vs LLM reply.

Design goals:
  - Cut Sarvam cost on menu navigation, greetings, thank-yous, OK/goodbye.
  - Keep AI for real, ambiguous questions.
  - Scoped to ONE phone for safe roll-out; every other customer keeps the
    existing LLM-only behaviour untouched.

Rules (evaluated in order):
  1. Exact single digit '1'/'2'/'3'                -> static menu replies
  2. Exact single digit '4'/'5'                     -> static sub-menu (PRICE)
  3. Exact single digit '6'/'7'/'8'/'9'/'0'         -> go to LLM (off-menu help)
  4. Greeting triggers (hi/hello/namaste/type/menu) -> static welcome/help
  5. Thanks / thank you                            -> static
  6. OK / okay / theek hai                         -> static
  7. Bye / goodbye / phir milenge                  -> static
  8. Phone number / UPI / address snippet shared    -> static "received"
  9. Otherwise                                     -> LLM
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
_GREETING_RE = re.compile(
    r"^\s*(hi|hello|hey|namaste|नमस्ते|namaskar|type|menu|start|hello\s*ji|hi\s*ji)\s*$",
    re.IGNORECASE,
)
_THANKS_RE = re.compile(
    r"^\s*(thanks|thank\s*you|thx|ty|shukriya|dhanyavaad|धन्यवाद|शुक्रिया)\s*\.?\s*$",
    re.IGNORECASE,
)
_OK_RE = re.compile(
    r"^\s*(ok|okay|theek|theek\s+hai|ठीक\s*है|ठीक|ack|got\s*it|noted|ji\s*haan|haan|haanji)\s*\.?\s*$",
    re.IGNORECASE,
)
_GOODBYE_RE = re.compile(
    r"^\s*(bye|by|goodbye|phir\s*milenge|alvida|see\s*you|tata)\s*\.?\s*$",
    re.IGNORECASE,
)
# 10-digit phone / UPI / "address" type submissions (sharing contact-ish)
_PHONE_RE = re.compile(r"^\s*\+?\d[\d\s\-]{8,}\s*$")
_UPI_RE = re.compile(r"^\s*[\w.\-]{2,}@[\w.\-]{2,}\s*$", re.IGNORECASE)
_ADDRESS_RE = re.compile(r"^\s*(sector|plot|flat|house|street|road|nagar| colony|lane|gali|मकान)\b", re.IGNORECASE)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
async def is_new_customer(phone: str) -> bool:
    """True if this phone has zero prior messages in the DB."""
    async with SessionLocal() as db:
        result = await db.execute(
            select(func.count(Message.id)).where(Message.phone == phone)
        )
        return (result.scalar() or 0) == 0


def _norm(text: str) -> str:
    return (text or "").strip()


# ---------------------------------------------------------------------------
# The decision
# ---------------------------------------------------------------------------
async def decide(phone: str, combined_text: str, history: list[dict] | None = None) -> RouteDecision:
    """
    Decide what to do with this inbound batch.

    `combined_text` is the merged text from the chat_buffer (multiple messages
    joined with newlines). `history` is the prior LLM-context for this phone
    (most recent last, [{role, content}, ...]).
    """
    text = _norm(combined_text)
    lower = text.lower().strip()
    lines = [l.strip() for l in text.splitlines() if l.strip()]

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

    # ------------------------------------------------------------------
    # 1. Pure single-digit input
    # ------------------------------------------------------------------
    m = _DIGIT_RE.match(text)
    if m and "\n" not in text:
        digit = m.group(1)
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
        # 6 = explicit "let AI handle this", 7/8/9/0 also go to AI
        if digit in ("6", "7", "8", "9", "0"):
            return RouteDecision(use_llm=True, reply=None, reason=f"off-menu-digit:{digit}")

    # ------------------------------------------------------------------
    # 2. Single-line "1" / "type 1" etc. — only if the FIRST (and only)
    #    token is a digit, treat as menu nav. If user adds words, it's a
    #    real question -> LLM.
    # ------------------------------------------------------------------
    first_line_is_pure_digit = (
        len(lines) == 1 and bool(_DIGIT_RE.match(lines[0]))
    )
    if first_line_is_pure_digit:
        # already handled above; this is unreachable but keep for clarity
        digit = _DIGIT_RE.match(lines[0]).group(1)
        return RouteDecision(use_llm=True, reply=None, reason=f"digit-mixed:{digit}")

    # ------------------------------------------------------------------
    # 3. Greetings / menu-trigger words  (always static)
    # ------------------------------------------------------------------
    if len(lines) == 1 and _GREETING_RE.match(lines[0]):
        return RouteDecision(use_llm=False, reply=menu.WELCOME, reason="greeting")

    # ------------------------------------------------------------------
    # 4. Polite one-word replies (thanks / ok / bye)
    # ------------------------------------------------------------------
    if len(lines) == 1 and _THANKS_RE.match(lines[0]):
        return RouteDecision(use_llm=False, reply=menu.THANKS_REPLY, reason="thanks")
    if len(lines) == 1 and _OK_RE.match(lines[0]):
        return RouteDecision(use_llm=False, reply=menu.OK_REPLY, reason="ok")
    if len(lines) == 1 and _GOODBYE_RE.match(lines[0]):
        return RouteDecision(use_llm=False, reply=menu.GOODBYE_REPLY, reason="goodbye")

    # ------------------------------------------------------------------
    # 5. Customer is sharing contact / UPI / address snippet
    # ------------------------------------------------------------------
    if len(lines) == 1 and (
        _PHONE_RE.match(lines[0]) or _UPI_RE.match(lines[0]) or _ADDRESS_RE.match(lines[0])
    ):
        return RouteDecision(
            use_llm=False,
            reply="✅ Received! Hum aapko jaldi call karenge. Aur kuch? *Type 6* 🙏",
            reason="contact-shared",
        )

    # ------------------------------------------------------------------
    # 6. ALL ELSE -> LLM
    # ------------------------------------------------------------------
    return RouteDecision(use_llm=True, reply=None, reason="fallback-llm")
