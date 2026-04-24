"""Self-critique · scores groundedness · triggers retry if below threshold."""
from __future__ import annotations
from src.models.chat import ChatClient


async def score_groundedness(draft: str, chunks: list[dict]) -> float:
    ctx = "\n".join(f"[{c['id']}] {c['content'][:300]}" for c in chunks)
    messages = [
        {"role": "system", "content": "Score the draft's groundedness in the chunks on [0,1]. Return ONLY the number."},
        {"role": "user", "content": f"Chunks:\n{ctx}\n\nDraft: {draft}"},
    ]
    resp = await ChatClient().complete(messages, temperature=0.0)
    try:
        return float(resp["content"].strip().split()[0])
    except (ValueError, IndexError):
        return 0.0
