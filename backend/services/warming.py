"""
WhatsApp number warming schedule enforcement.
Days counted from WA_ACCOUNT_START_DATE in .env.
"""
from datetime import date
from config import settings

WARMING_SCHEDULE = [
    (3, 0),      # days 0-3: no outbound
    (7, 150),    # days 4-7: 150/day
    (14, 400),   # days 8-14: 400/day
    (21, 1000),  # days 15-21: 1000/day
    (9999, 2000) # day 22+: 2000/day (permanent cap)
]

def get_daily_limit() -> int:
    today = date.today()
    start = settings.WA_ACCOUNT_START_DATE
    days_active = (today - start).days

    for threshold, limit in WARMING_SCHEDULE:
        if days_active <= threshold:
            return limit
    return 2000

def can_send_outbound() -> bool:
    """Returns False during the first 3 days — listen-only mode."""
    today = date.today()
    start = settings.WA_ACCOUNT_START_DATE
    days_active = (today - start).days
    return days_active > 3

def get_warming_status() -> dict:
    today = date.today()
    start = settings.WA_ACCOUNT_START_DATE
    days_active = (today - start).days
    limit = get_daily_limit()
    outbound_ok = can_send_outbound()

    phase = "listen-only" if not outbound_ok else f"active (max {limit}/day)"

    return {
        "days_active": days_active,
        "daily_limit": limit,
        "outbound_allowed": outbound_ok,
        "phase": phase,
        "start_date": str(start),
    }
