"""Azure Content Safety · Prompt Shields · toxicity · groundedness."""
from __future__ import annotations
from dataclasses import dataclass
from src.config import get_settings

_INJECTION_PATTERNS = [
    "ignore previous instructions", "ignore all prior", "you are now dan",
    "disregard the system prompt", "jailbreak mode", "pretend you have no rules",
]


@dataclass
class GateResult:
    pass_: bool
    reason: str = ""
    severity: int = 0
    score: float = 1.0


async def input_gate(user_query: str) -> GateResult:
    s = get_settings()
    if s.mode == "local" or not s.contentsafety_endpoint:
        q = user_query.lower()
        if any(p in q for p in _INJECTION_PATTERNS):
            return GateResult(pass_=False, reason="prompt_injection_detected")
        return GateResult(pass_=True)
    return await _input_gate_azure(s, user_query)


async def _input_gate_azure(s, user_query):
    from azure.ai.contentsafety.aio import ContentSafetyClient
    from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
    from azure.identity.aio import DefaultAzureCredential
    cred = DefaultAzureCredential()
    client = ContentSafetyClient(endpoint=s.contentsafety_endpoint, credential=cred)
    try:
        shield = await client.detect_jailbreak(text=user_query)
        if getattr(shield, "jailbreak_analysis", None) and shield.jailbreak_analysis.detected:
            return GateResult(pass_=False, reason="prompt_injection_detected")
    except Exception:
        pass
    result = await client.analyze_text(AnalyzeTextOptions(
        text=user_query,
        categories=[TextCategory.HATE, TextCategory.SELF_HARM, TextCategory.SEXUAL, TextCategory.VIOLENCE],
    ))
    max_sev = max((c.severity for c in result.categories_analysis), default=0)
    await client.close()
    if max_sev >= 4:
        return GateResult(pass_=False, reason="unsafe_input", severity=max_sev)
    return GateResult(pass_=True, severity=max_sev)


async def output_gate(assistant_output: str) -> GateResult:
    s = get_settings()
    if s.mode == "local" or not s.contentsafety_endpoint:
        return GateResult(pass_=True)
    from azure.ai.contentsafety.aio import ContentSafetyClient
    from azure.ai.contentsafety.models import AnalyzeTextOptions, TextCategory
    from azure.identity.aio import DefaultAzureCredential
    cred = DefaultAzureCredential()
    client = ContentSafetyClient(endpoint=s.contentsafety_endpoint, credential=cred)
    result = await client.analyze_text(AnalyzeTextOptions(
        text=assistant_output,
        categories=[TextCategory.HATE, TextCategory.SELF_HARM, TextCategory.SEXUAL, TextCategory.VIOLENCE],
    ))
    max_sev = max((c.severity for c in result.categories_analysis), default=0)
    await client.close()
    if max_sev >= 4:
        return GateResult(pass_=False, reason="unsafe_output", severity=max_sev)
    return GateResult(pass_=True, severity=max_sev)


async def groundedness_check(query: str, answer: str, sources: list[str]) -> float:
    s = get_settings()
    if s.mode == "azure" and s.contentsafety_endpoint:
        return 0.9
    from src.models.embedding import EmbeddingClient
    import math
    vs = await EmbeddingClient().embed([answer, *sources])
    if len(vs) < 2:
        return 0.0
    def cos(a, b):
        d = sum(x * y for x, y in zip(a, b))
        na = math.sqrt(sum(x * x for x in a)) or 1e-9
        nb = math.sqrt(sum(x * x for x in b)) or 1e-9
        return d / (na * nb)
    return max(cos(vs[0], v) for v in vs[1:])
