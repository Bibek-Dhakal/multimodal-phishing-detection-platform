from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings
from app.services.model_manager import load_models
from app.threat_intel import update_threat_feed, get_threat_feed

# Initialize FastAPI App Entry Point
app = FastAPI(title=settings.PROJECT_NAME, description="Multi-Modal Threat Analysis Backend")

# Include the modularized endpoints
app.include_router(router)


@app.on_event("startup")
def startup_event():
    """Application initialization logic executed on server boot."""
    load_models()
    update_threat_feed()
    print(f"[+] Loaded {len(get_threat_feed())} active zero-day phishing URLs into RAM.")
