"""Token → USD cost · sourced from pricing.yml."""
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
import yaml


@lru_cache(maxsize=1)
def _pricing() -> dict:
    p = Path("pricing.yml")
    if not p.exists():
        return {"gpt-4o-mini": {"input_per_1k": 0.00015, "output_per_1k": 0.0006},
                "text-embedding-3-small": {"input_per_1k": 0.00002, "output_per_1k": 0.0}}
    return yaml.safe_load(p.read_text())


def compute_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    p = _pricing().get(model) or _pricing().get("gpt-4o-mini", {})
    return (tokens_in / 1000) * p.get("input_per_1k", 0) + (tokens_out / 1000) * p.get("output_per_1k", 0)
