from typing import Optional

from fastapi import APIRouter, Form, File, UploadFile
from fastapi.concurrency import run_in_threadpool

from app.services.inference import run_multimodal_inference
from app.threat_intel import update_threat_feed

router = APIRouter()


@router.get("/")
def health_check():
    return {"status": "Active", "message": "Phishing Detection API is running."}


@router.post("/predict/multimodal")
async def predict_multimodal(
        features: Optional[str] = Form(None),
        url: Optional[str] = Form(None),
        image: Optional[UploadFile] = File(None)
):
    # Execute network call safely in a threadpool to prevent blocking the async event loop
    await run_in_threadpool(update_threat_feed)

    image_bytes = None
    if image and image.filename:
        image_bytes = await image.read()

    return await run_multimodal_inference(features, url, image_bytes)
