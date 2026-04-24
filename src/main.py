"""FastAPI stub · Brief E replaces with actual Hello AI payload."""
from fastapi import FastAPI
import uvicorn

app = FastAPI(title="Project Ground Zero · Hello AI Stub")

@app.get("/health")
def health():
    return {"status": "healthy", "note": "Brief E fills this with real dependency checks"}

@app.get("/ready")
def ready():
    return {"status": "ready"}

@app.get("/")
def root():
    return {"message": "Hello AI stub · Brief E fills this with real endpoints"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
