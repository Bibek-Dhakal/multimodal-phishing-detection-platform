import os

from dotenv import load_dotenv

try:
    load_dotenv()
except ImportError:
    pass


class Settings:
    PROJECT_NAME = "Phishing Detection API"
    PHISHING_THRESHOLD = float(os.getenv("PHISHING_THRESHOLD", "0.85"))
    BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000/predict/multimodal")


settings = Settings()
