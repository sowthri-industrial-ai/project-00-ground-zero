"""Streamlit UI · 3 tabs · RAG · Agent · Multi-Agent · + Memory view."""
from __future__ import annotations
import asyncio
import uuid
import streamlit as st

from src.agent.graph import run_agent
from src.agent.memory import ConversationMemory
from src.config import get_settings
from src.guardrails.content_safety import input_gate, groundedness_check
from src.multi_agent.supervisor import run_multi_agent
from src.observability.cost_middleware import compute_cost
from src.rag.generate import generate

st.set_page_config(page_title="Hello AI · Ground Zero", layout="wide")
s = get_settings()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

with st.sidebar:
    st.header("⚙ Config")
    st.text(f"Mode: {s.mode}")
    st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"], key="model")
    st.selectbox("Language", ["English (GPT-4o-mini)", "Arabic (ALLaM)"], key="language")
    st.text_input("Session", st.session_state.session_id, disabled=True)
    if st.button("↻ New session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    st.caption(f"Langfuse: {s.langfuse_host}")
    st.caption("Last cost rollup: $0.00 (Functions cron)")

tab_rag, tab_agent, tab_ma, tab_mem = st.tabs(["🔍 RAG", "🤖 Agent", "👥 Multi-Agent", "🧠 Memory"])

with tab_rag:
    st.subheader("Retrieval-Augmented Generation")
    col1, col2 = st.columns([3, 1])
    with col1:
        q = st.text_input("Ask the NIST AI RMF", key="rag_q",
                          placeholder="What is the Govern function of the AI RMF?")
    with col2:
        top_k = st.slider("Top-k", 1, 10, 5)
    corpus = st.radio("Corpus", ["NIST doc (Docling)", "Sample form (Doc Intelligence)"], horizontal=True)
    retrieval = st.radio("Retrieval path", ["Native (Azure SDK)", "LlamaIndex", "ColPali (vision)"], horizontal=True)
    if st.button("Run RAG", type="primary"):
        with st.spinner("Retrieving + generating…"):
            gate = asyncio.run(input_gate(q))
            if not gate.pass_:
                st.error(f"🛡 Input rejected: {gate.reason}")
            else:
                index = (s.search_index_forms if "form" in corpus.lower() else
                         s.search_index_llamaindex if "LlamaIndex" in retrieval else
                         s.search_index_primary)
                result = asyncio.run(generate(q, top_k=top_k, index_name=index if s.mode == "azure" else None))
                grounded = asyncio.run(groundedness_check(q, result["answer"], [c["content"] for c in result["chunks"]]))
                cost = compute_cost(result.get("model", "gpt-4o-mini"), result.get("tokens_in", 0), result.get("tokens_out", 0))
                m1, m2, m3 = st.columns(3)
                m1.metric("Groundedness", f"{grounded:.2f}")
                m2.metric("Cost", f"${cost:.5f}")
                m3.metric("Tokens", result.get("tokens_in", 0) + result.get("tokens_out", 0))
                if grounded < 0.85:
                    st.warning("⚠️ Low groundedness · review citations")
                st.markdown("### Answer")
                st.write(result["answer"])
                with st.expander(f"📚 Sources ({len(result['chunks'])} chunks)"):
                    for c in result["chunks"]:
                        st.markdown(f"**[{c['id']}]** (score {c['score']:.3f})")
                        st.caption(c["content"][:500] + "…")

with tab_agent:
    st.subheader("LangGraph Agent · 4 nodes · HITL + reflection")
    aq = st.text_input("Agent query", key="agent_q",
                       placeholder="Try: 'compliance review of AI RMF Govern function'")
    if st.button("Run agent", type="primary"):
        with st.spinner("Running graph…"):
            res = asyncio.run(run_agent(aq, session_id=st.session_state.session_id))
        cols = st.columns(4)
        cols[0].metric("Groundedness", f"{res.get('groundedness', 0):.2f}")
        cols[1].metric("Reflect loops", res.get("reflect_count", 0))
        cols[2].metric("Risky", "Yes" if res.get("risky") else "No")
        cols[3].metric("Chunks", len(res.get("chunks", [])))
        if res.get("risky"):
            if st.button("✅ Approve (HITL)"):
                st.success("Approved · would resume with checkpoint token in production")
        st.markdown("### Response")
        st.write(res.get("final", ""))

with tab_ma:
    st.subheader("Multi-Agent · Supervisor + Retriever Specialist via MCP")
    mq = st.text_input("Multi-agent query", key="ma_q", placeholder="Ask anything the specialist might know")
    if st.button("Run multi-agent", type="primary"):
        with st.spinner("Routing through Supervisor → MCP Specialist…"):
            res = asyncio.run(run_multi_agent(mq))
        c1, c2, c3 = st.columns(3)
        c1.metric("Transport", "stdio (MCP)")
        c2.metric("Fallback", "Yes" if res.get("used_fallback") else "No")
        c3.metric("SK planner", res.get("sk_plan", {}).get("planner", "—"))
        if res.get("used_fallback"):
            st.warning("Specialist unreachable · using direct RAG fallback")
        st.markdown("### Synthesised answer")
        st.write(res.get("final", ""))
        with st.expander("Specialist trace"):
            st.code(res.get("specialist_result", ""))

with tab_mem:
    st.subheader("Conversation Memory · session-keyed")
    mem = ConversationMemory()
    history = asyncio.run(mem.load(st.session_state.session_id, limit=10))
    if not history:
        st.info("No turns yet for this session")
    for turn in history:
        with st.chat_message(turn["role"]):
            st.write(turn["content"])
            st.caption(turn.get("timestamp", ""))
