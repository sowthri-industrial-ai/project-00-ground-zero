"""Langfuse tracing · every invocation tagged with pillar/mode/gate_result."""
from __future__ import annotations
import contextlib
from typing import Any
from src.config import get_settings


class Tracer:
    def __init__(self):
        self.s = get_settings()
        self._lf = None
        try:
            from langfuse import Langfuse
            if self.s.langfuse_public_key and self.s.langfuse_secret_key:
                self._lf = Langfuse(
                    public_key=self.s.langfuse_public_key,
                    secret_key=self.s.langfuse_secret_key,
                    host=self.s.langfuse_host,
                )
        except ImportError:
            self._lf = None

    @contextlib.contextmanager
    def trace(self, name: str, pillar: str, **tags: Any):
        if not self._lf:
            yield None
            return
        trace = self._lf.trace(name=name, tags=[f"pillar={pillar}", f"mode={self.s.mode}",
                                                 *(f"{k}={v}" for k, v in tags.items())])
        try:
            yield trace
        finally:
            self._lf.flush()


tracer = Tracer()
