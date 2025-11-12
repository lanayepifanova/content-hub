"""Calendar-specific helpers for rendering pages and API responses."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from typing import Iterable

from app.models import Idea


def month_context(year: int, month: int) -> dict:
    """Return metadata for a 6-week (42 day) calendar grid."""
    first_day = date(year, month, 1)
    start = first_day - timedelta(days=first_day.weekday())
    days = [start + timedelta(days=i) for i in range(42)]
    weeks = [days[i : i + 7] for i in range(0, 42, 7)]
    last_day = days[-1]

    prev_month_anchor = first_day - timedelta(days=1)
    next_month_anchor = last_day + timedelta(days=1)

    return {
        "weeks": weeks,
        "range_start": days[0],
        "range_end": days[-1],
        "current_month": month,
        "current_year": year,
        "previous": (prev_month_anchor.year, prev_month_anchor.month),
        "next": (next_month_anchor.year, next_month_anchor.month),
        "current_label": first_day.strftime("%B %Y"),
        "previous_label": date(prev_month_anchor.year, prev_month_anchor.month, 1).strftime("%b"),
        "next_label": date(next_month_anchor.year, next_month_anchor.month, 1).strftime("%b"),
    }


def group_ideas_by_day(ideas: Iterable[Idea]) -> dict[date, list[Idea]]:
    """Index ideas by day for quick lookups inside a template."""
    ideas_by_day: dict[date, list[Idea]] = defaultdict(list)
    for idea in ideas:
        ideas_by_day[idea.target_date].append(idea)
    return ideas_by_day
