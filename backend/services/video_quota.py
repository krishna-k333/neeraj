"""
Video generation monthly quota.
- Hard cap: 40 videos per billing month
- Billing month starts on the 9th of each calendar month
- Example: cycle for July = 9 Jul → 8 Aug inclusive
"""
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

MONTHLY_CAP = 40
CYCLE_START_DAY = 9


def get_cycle_bounds(today: date | None = None) -> tuple[date, date]:
    """Returns (cycle_start, cycle_end_inclusive) for the current billing month."""
    if today is None:
        today = date.today()

    if today.day >= CYCLE_START_DAY:
        cycle_start = today.replace(day=CYCLE_START_DAY)
    else:
        # We're before the 9th — cycle started previous month
        cycle_start = (today.replace(day=CYCLE_START_DAY) - relativedelta(months=1))

    cycle_end = cycle_start + relativedelta(months=1) - relativedelta(days=1)
    return cycle_start, cycle_end


def days_until_reset(today: date | None = None) -> int:
    if today is None:
        today = date.today()
    _, cycle_end = get_cycle_bounds(today)
    return (cycle_end - today).days + 1
