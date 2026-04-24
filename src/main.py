"""FastAPI · /health · /ready · /chat · /metrics · safety-first ordering."""
from __future__ import annotations
import time
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.config import get_settings
from src.guardrails.content_safety import input_gate, output_gate, groundedness_check
from src.guardrails.presidio_redactor import redact
from src.observability.app_insights import configure as configure_ai, emit_metric
from src.observability.cost_middleware import compute_cost
from src.observability.langfuse_tracer import tracer
from src.rag.generate import generate

app = FastAPI(title="Hello AI Payload · Brief E")
configure_ai()


class ChatRequest(BaseModel):
    query: str
    session_id: str | None = None
    top_k: int = 5


class ChatResponse(BaseModel):
    answer: str
    chunks: list[dict]
    groundedness: float
    cost_usd: float
    latency_ms: int
    session_id: str
    entities_detected: list[str] = []


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    return {"status": "ready", "mode": get_settings().mode}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    t0 = time.time()
    session_id = req.session_id or str(uuid.uuid4())

    # ── BRIEF-E:GUARDRAIL-INPUT-GATE (demo-fails-guardrail removes these) ──
    gate_in = await input_gate(req.query)
    if not gate_in.pass_:
        raise HTTPException(status_code=400, detail=f"input_rejected:{gate_in.reason}")
    # ── /BRIEF-E:GUARDRAIL-INPUT-GATE ──

    with tracer.trace("chat", pillar="rag", gate_result="pass"):
        result = await generate(req.query, top_k=req.top_k)

        gate_out = await output_gate(result["answer"])
        if not gate_out.pass_:
            raise HTTPException(status_code=400, detail=f"output_rejected:{gate_out.reason}")

        red = redact(result["answer"])
        if red.blocked:
            raise HTTPException(status_code=400, detail=f"pii_blocked:{red.reason}")

        grounded = await groundedness_check(req.query, red.text, [c["content"] for c in result["chunks"]])

    model = result.get("model", "gpt-4o-mini")
    cost = compute_cost(model, result.get("tokens_in", 0), result.get("tokens_out", 0))
    latency = int((time.time() - t0) * 1000)

    emit_metric("request_cost_usd", cost, model=model)
    emit_metric("groundedness_score", grounded)
    emit_metric("request_latency_ms", latency)

    return ChatResponse(
        answer=red.text, chunks=result["chunks"], groundedness=grounded,
        cost_usd=cost, latency_ms=latency, session_id=session_id,
        entities_detected=red.entities or [],
    )


@app.get("/metrics")
async def metrics():
    return {"service": "hello-ai", "mode": get_settings().mode}
