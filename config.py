import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_PORT = int(os.getenv("API_PORT", 8000))
    API_ENDPOINT_URL = os.getenv("API_ENDPOINT_URL", "http://127.0.0.1:8000/api/v1/predict")
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
    TRANSFORMER_MAX_SEQUENCE_LENGTH = int(os.getenv("TRANSFORMER_MAX_SEQUENCE_LENGTH", 128))
    
    # Path Anchors
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    
    # Fallback to standard names to prevent FileNotFoundError, using your requested paths
    ISCX_CSV = os.path.join(DATA_DIR, "iscx_phishing", "All.csv")
    PHIUSIIL_CSV = os.path.join(DATA_DIR, "phiusil_phshing_urls", "PhiUSIIL_Phishing_URL_Dataset.csv")
    
    # Artifact Locations
    TABULAR_MODEL_PATH = os.path.join(MODELS_DIR, "tabular", "xgboost_production.pkl")
    
    # New NLP Layout
    NLP_CHECKPOINT_DIR = os.path.join(MODELS_DIR, "nlp", "checkpoint-best")
    NLP_FINAL_DIR = os.path.join(MODELS_DIR, "nlp", "final")
    NLP_TOKENIZER_DIR = os.path.join(MODELS_DIR, "nlp", "tokenizer")

settings = Settings()