"""App Insights · OpenTelemetry · custom metrics."""
from __future__ import annotations
from src.config import get_settings


def configure():
    s = get_settings()
    if not s.appinsights_connection_string:
        return
    try:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(connection_string=s.appinsights_connection_string)
    except ImportError:
        pass


def emit_metric(name: str, value: float, **attrs):
    try:
        from opentelemetry import metrics
        meter = metrics.get_meter("hello-ai")
        hist = meter.create_histogram(name)
        hist.record(value, attributes=attrs)
    except Exception:
        pass
