"""Model Registry stub · placeholder registration · no real weights."""
from __future__ import annotations
from datetime import datetime, timezone


def register_placeholder(name: str = "hello-ai-finetune-v1", stage: str = "dev") -> dict:
    try:
        from azure.ai.ml import MLClient
        from azure.ai.ml.entities import Model
        from azure.identity import DefaultAzureCredential
        ml = MLClient(DefaultAzureCredential(), subscription_id="<sub>",
                      resource_group_name="<rg>", workspace_name="<ws>")
        model = Model(
            name=name, version="1", type="mlflow_model",
            description="Ground Zero fine-tune scaffold placeholder · no real weights",
            tags={"stage": stage, "project": "ground-zero", "type": "scaffold",
                  "created": datetime.now(timezone.utc).isoformat()},
        )
        ml.models.create_or_update(model)
        return {"name": name, "stage": stage, "status": "registered"}
    except Exception as e:
        return {"name": name, "stage": stage, "status": f"stub · {type(e).__name__}"}


if __name__ == "__main__":
    print(register_placeholder())
