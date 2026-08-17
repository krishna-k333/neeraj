"""
Static menu + staff contacts for Neeraj Enterprises WhatsApp flow.

Source: message insp.txt (verbatim). All strings Hinglish-friendly,
ready to send without any LLM intervention.
"""

# ---------------------------------------------------------------------------
# Staff contacts (verbatim from doc)
# ---------------------------------------------------------------------------
SHOP_PHONE = "919312971238"
SHOP_NAME = "Neeraj Enterprises Fashion"


def _wa_link(phone_e164: str, msg: str = "") -> str:
    """Return a click-to-chat WhatsApp link."""
    text = f"&text={msg}" if msg else ""
    return f"https://wa.me/{phone_e164}?text={msg}{text}".replace("?text=&", "?text=")


# ---------------------------------------------------------------------------
# Welcome (top-level menu)
# ---------------------------------------------------------------------------
WELCOME = (
    "Namaste NE Fashion mein aapka swagat hai 🙏\n\n"
    "*Type 1* for 📍 Location\n"
    "*Type 2* for 🛍️ Products & Price\n"
    "*Type 3* for 📸 Collection\n"
    "*Type 6* for any other query"
)


# ---------------------------------------------------------------------------
# Sub-menus
# ---------------------------------------------------------------------------
LOCATION_REPLY = (
    "📍 *Neeraj Enterprises Fashion*\n"
    "D899, Chawla Colony, Ballabhgarh, Faridabad, Haryana 121004\n"
    "https://maps.app.goo.gl/MeMWnNrG3DJHNRZ3A\n\n"
    "Owner: Neeraj Aggarwal\n"
    "Open: 10 AM – 9 PM\n\n"
    "Kuch aur poochna ho toh *Type 6* dabayein 🙏"
)


PRICE_MENU = (
    "🛍️ *Products & Price category batao:*\n\n"
    "*Type 1* for Astar / Fall / Peticot\n"
    "*Type 2* for Saree\n"
    "*Type 3* for Lehenga\n"
    "*Type 4* for Suit (Unstitch + Ready-made)\n"
    "*Type 5* for Dresses\n\n"
    "Baaki kuch poochna ho toh *Type 6*"
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
    lines = ["💬 *Price ke liye inse baat karo:*\n"]
    # Always route customers to the shop number, regardless of category.
    lines.append(f"👉 *{SHOP_NAME}* — wa.me/{SHOP_PHONE}\n")
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
