"""
Static menu + staff contacts for Neeraj Enterprises WhatsApp flow.

Source: message insp.txt (verbatim). All strings Hinglish-friendly,
ready to send without any LLM intervention.
"""

# ---------------------------------------------------------------------------
# Staff contacts (verbatim from doc)
# ---------------------------------------------------------------------------
STAFF = {
    "manoj":   {"name": "Manoj",   "phone": "919911569029"},
    "vijay":   {"name": "Vijay",   "phone": "918860321521"},
    "anil":    {"name": "Anil",    "phone": "919711158358"},
    "durgesh": {"name": "Durgesh", "phone": "918700840135"},
}


def _wa_link(phone_e164: str, msg: str = "") -> str:
    """Return a click-to-chat WhatsApp link."""
    text = f"&text={msg}" if msg else ""
    return f"https://wa.me/{phone_e164}?text={msg}{text}".replace("?text=&", "?text=")


# ---------------------------------------------------------------------------
# Welcome (top-level menu)
# ---------------------------------------------------------------------------
WELCOME = (
    "🙏 Welcome to *Neeraj Enterprises*!\n"
    "Saree | Suit | Lehenga | Dresses — sab kuch ek hi jagah.\n\n"
    "*Type 1* for 📍 Location\n"
    "*Type 2* for 💰 Price\n"
    "*Type 3* for 📸 Catalogue\n"
    "*Type 6* for any other help"
)


# ---------------------------------------------------------------------------
# Sub-menus
# ---------------------------------------------------------------------------
LOCATION_REPLY = (
    "📍 *Humari shop ki location:*\n"
    "https://maps.app.goo.gl/MeMWnNrG3DJHNRZ3A\n\n"
    "Kuch aur poochna ho toh *Type 6* dabayein 🙏"
)


PRICE_MENU = (
    "💰 *Price category batao:*\n\n"
    "*Type 1* for Astar / Fall / Peticot\n"
    "*Type 2* for Saree\n"
    "*Type 3* for Lehenga\n"
    "*Type 4* for Suit (Unstitch + Ready-made)\n"
    "*Type 5* for Dresses\n\n"
    "Baaki kuch? *Type 6*"
)


# Category → staff handling the price
PRICE_STAFF_MAP = {
    "1": "anil",    # Astar / Fall / Peticot
    "2": "durgesh", # Saree
    "3": "durgesh", # Lehenga
    "4": ["manoj", "vijay"],  # Suit
    "5": ["manoj", "vijay"],  # Dresses
}


def price_reply(digit: str) -> str | None:
    staff_keys = PRICE_STAFF_MAP.get(digit)
    if not staff_keys:
        return None
    keys = staff_keys if isinstance(staff_keys, list) else [staff_keys]
    lines = ["💬 *Price ke liye inse baat karo:*\n"]
    for k in keys:
        s = STAFF[k]
        lines.append(f"👉 *{s['name']}* — wa.me/{s['phone']}\n")
    lines.append("\nAur kuch? *Type 6* 🙏")
    return "".join(lines)


CATALOGUE_REPLY = (
    "📸 *Humara latest catalogue:*\n"
    "https://whatsapp.com/channel/0029VbB3ji3ICVfd7aCbhX1o\n\n"
    "Aur kuch chahiye? *Type 6* 🙏"
)


# ---------------------------------------------------------------------------
# Static short replies (no LLM for trivial inputs)
# ---------------------------------------------------------------------------
THANKS_REPLY = (
    "🙏 Dhanyavaad! Aapka order confirm ho gaya hai.\n"
    "Koi aur sawaal? *Type 6*"
)

OK_REPLY = "👍 Theek hai! Kuch aur chahiye toh *Type 6* 🙏"

GOODBYE_REPLY = "🙏 Shukriya! Phir milte hain. Jab bhi zaroorat ho *Type 6* likh dena."

HELP_REPLY = (
    "ℹ️ *Yeh kar sakte hain aap:*\n\n"
    "*Type 1* for 📍 Location\n"
    "*Type 2* for 💰 Price\n"
    "*Type 3* for 📸 Catalogue\n"
    "*Type 6* for kuch bhi poochna (AI se baat hogi)"
)


def fallback_menu() -> str:
    """When a digit is out of range (e.g. user typed '7')."""
    return (
        "🙏 Sahi option chune:\n\n"
        "*Type 1* for 📍 Location\n"
        "*Type 2* for 💰 Price\n"
        "*Type 3* for 📸 Catalogue\n"
        "*Type 6* for any other help"
    )


def stale_repeat() -> str:
    """User hit same menu digit twice — gently remind them of the menu."""
    return "😊 Main yahi hoon. Kripya *Type 6* likh kar apna sawaal batao."
