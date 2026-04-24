"""Azure Functions · timer trigger · hourly cost rollup Langfuse → Cosmos."""
from __future__ import annotations
import logging
from datetime import datetime, timedelta, timezone
import azure.functions as func

app = func.FunctionApp()


@app.timer_trigger(schedule="0 */1 * * * *", arg_name="mytimer", run_on_startup=False)
def cost_aggregator(mytimer: func.TimerRequest) -> None:
    logging.info("cost_aggregator tick · %s", datetime.now(timezone.utc).isoformat())
    try:
        from langfuse import Langfuse
        from azure.cosmos import CosmosClient
        from azure.identity import DefaultAzureCredential
        import os

        lf = Langfuse(
            public_key=os.environ["LANGFUSE_PUBLIC_KEY"],
            secret_key=os.environ["LANGFUSE_SECRET_KEY"],
            host=os.environ["LANGFUSE_HOST"],
        )
        window_start = datetime.now(timezone.utc) - timedelta(hours=1)
        traces = lf.api.trace.list(from_timestamp=window_start.isoformat())
        total_cost = sum(float((t.metadata or {}).get("cost_usd", 0.0)) for t in traces.data)

        cred = DefaultAzureCredential()
        cosmos = CosmosClient(os.environ["COSMOS_ENDPOINT"], credential=cred)
        container = cosmos.get_database_client(os.environ["COSMOS_DB"]).get_container_client("cost_rollups")
        container.upsert_item({
            "id": window_start.strftime("%Y%m%d%H"),
            "hour": window_start.isoformat(),
            "total_cost_usd": total_cost,
            "trace_count": len(traces.data),
        })
        logging.info("rollup · $%.4f · %d traces", total_cost, len(traces.data))
    except Exception as e:
        logging.exception("cost_aggregator failed: %s", e)
