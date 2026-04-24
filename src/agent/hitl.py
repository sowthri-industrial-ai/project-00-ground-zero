"""Human-in-the-loop · flag risky queries."""
from __future__ import annotations
from src.config import get_settings


def is_risky(query: str) -> bool:
    s = get_settings()
    q = query.lower()
    return any(kw in q for kw in s.risky_keywords)
