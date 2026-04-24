"""RAGAS wrapper · faithfulness + context precision · regression gate."""
from __future__ import annotations
import json
from pathlib import Path


async def run_golden_eval(golden_path: str = "tests/eval/golden.jsonl") -> dict[str, float]:
    from src.rag.generate import generate
    examples = [json.loads(l) for l in Path(golden_path).read_text().splitlines() if l.strip()]
    try:
        from ragas import evaluate
        from ragas.metrics import faithfulness, context_precision
        from datasets import Dataset
        questions, answers, contexts, refs = [], [], [], []
        for ex in examples:
            g = await generate(ex["question"])
            questions.append(ex["question"])
            answers.append(g["answer"])
            contexts.append([c["content"] for c in g["chunks"]])
            refs.append(ex["reference_answer"])
        ds = Dataset.from_dict({"question": questions, "answer": answers, "contexts": contexts, "ground_truth": refs})
        result = evaluate(ds, metrics=[faithfulness, context_precision])
        return {k: float(v) for k, v in result.items()}
    except ImportError:
        scores = []
        for ex in examples:
            g = await generate(ex["question"])
            ref_terms = set(ex["reference_answer"].lower().split())
            ans_terms = set(g["answer"].lower().split())
            scores.append(len(ref_terms & ans_terms) / max(len(ref_terms), 1))
        return {"faithfulness": sum(scores) / len(scores) if scores else 0.0, "context_precision": 0.0}
