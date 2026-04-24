"""Presidio PII redaction · blocks SSN/credit card · redacts others."""
from __future__ import annotations
from dataclasses import dataclass, field

CRITICAL = {"US_SSN", "CREDIT_CARD"}


@dataclass
class RedactionResult:
    text: str
    blocked: bool
    reason: str = ""
    entities: list[str] = field(default_factory=list)


def redact(text: str) -> RedactionResult:
    try:
        from presidio_analyzer import AnalyzerEngine
        from presidio_anonymizer import AnonymizerEngine
        analyzer = AnalyzerEngine()
        anonymizer = AnonymizerEngine()
        results = analyzer.analyze(text=text, language="en")
        found = {r.entity_type for r in results}
        if found & CRITICAL:
            return RedactionResult(text="[BLOCKED · critical PII detected]", blocked=True,
                                   reason=f"pii_{','.join(found & CRITICAL)}", entities=list(found))
        anon = anonymizer.anonymize(text=text, analyzer_results=results)
        return RedactionResult(text=anon.text, blocked=False, entities=list(found))
    except ImportError:
        import re
        entities = []
        if re.search(r"\b\d{3}-\d{2}-\d{4}\b", text):
            return RedactionResult(text="[BLOCKED · SSN]", blocked=True, reason="pii_US_SSN", entities=["US_SSN"])
        text_out = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "<EMAIL>", text)
        if text != text_out:
            entities.append("EMAIL_ADDRESS")
        return RedactionResult(text=text_out, blocked=False, entities=entities)
