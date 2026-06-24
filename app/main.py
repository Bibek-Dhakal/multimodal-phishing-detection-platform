from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import os
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from contextlib import asynccontextmanager

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from src.feature_extractor import FeatureExtractor
from src.vision_pipeline_todo import VisionPipelineMock

class ModelRegistry:
    def __init__(self):
        self.tabular_model = None
        self.nlp_tokenizer = None
        self.nlp_model = None
        self.vision_pipeline = None

registry = ModelRegistry()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n[*] Booting Production Intelligence Ensembles...")
    
    # 1. Load Structural ML Engine (XGBoost)
    if os.path.exists(settings.TABULAR_MODEL_PATH):
        with open(settings.TABULAR_MODEL_PATH, 'rb') as f:
            registry.tabular_model = pickle.load(f)
        print("[+] XGBoost Structural Engine Ready.")
    else:
        print("[-] Tabular model absent. Proceeding with dummy values. Please run 'python src/train_tabular.py' first.")

    # 2. Load Deep Contextual Transformer (MiniLM)
    if os.path.exists(settings.NLP_FINAL_DIR) and os.path.exists(settings.NLP_TOKENIZER_DIR):
        registry.nlp_tokenizer = AutoTokenizer.from_pretrained(settings.NLP_TOKENIZER_DIR)
        registry.nlp_model = AutoModelForSequenceClassification.from_pretrained(settings.NLP_FINAL_DIR)
        registry.nlp_model.eval()
        print("[+] Contextual NLP Transformer Ready.")
    else:
        print("[-] NLP Transformer absent. Proceeding with dummy values. Please run 'python src/train_nlp.py' first.")
        
    # 3. Load Vision CNN Integration Module
    registry.vision_pipeline = VisionPipelineMock()
    print("[+] Visual CNN Interface Attached.\n")
    
    yield
    print("\n[*] Safely terminating model bindings...")

app = FastAPI(
    title="Multi-Modal Phishing Intelligence Engine", 
    description="Soft-Voting Aggregation API", 
    lifespan=lifespan
)

class URLRequest(BaseModel):
    url: str

@app.get("/")
def health_check():
    return {"status": "active", "message": "Multi-Modal Aggregation Gateway Running"}

@app.post("/api/v1/predict")
async def predict_url(request: URLRequest):
    url = request.url
    
    # ------------- 1. Structural Tabular Intelligence (Weight: 40%) -------------
    tabular_prob = 0.0
    if registry.tabular_model:
        try:
            extractor = FeatureExtractor(url)
            features = extractor.extract().reshape(1, -1)
            tabular_prob = float(registry.tabular_model.predict_proba(features)[0][1])
        except Exception as e:
            print(f"Tabular Execution Error: {e}")
            
    # ------------- 2. Contextual Linguistic NLP Logic (Weight: 40%) -------------
    nlp_prob = 0.0
    if registry.nlp_model and registry.nlp_tokenizer:
        try:
            # Lowercase the incoming URL for the transformer to match training logic
            # Delimiters like '-' and '.' are explicitly preserved 
            inputs = registry.nlp_tokenizer(url.lower(), return_tensors="pt", truncation=True, max_length=settings.TRANSFORMER_MAX_SEQUENCE_LENGTH)
            with torch.no_grad():
                outputs = registry.nlp_model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                nlp_prob = float(probs[0][1].item())
        except Exception as e:
            print(f"NLP Execution Error: {e}")
            
    # ------------- 3. Asynchronous Visual CNN Intelligence (Weight: 20%) ---------
    vision_prob = await registry.vision_pipeline.capture_and_predict(url)
    
    # ------------- 4. The Soft-Voting Fusion Matrix Aggregation ------------------
    tabular_risk = tabular_prob * 0.40
    nlp_risk = nlp_prob * 0.40
    vision_risk = vision_prob * 0.20
    
    unified_risk = tabular_risk + nlp_risk + vision_risk
    
    if unified_risk >= 0.75:
        verdict = "Phishing"
    elif unified_risk >= 0.40:
        verdict = "Suspicious"
    else:
        verdict = "Legitimate"
        
    return {
        "url": url,
        "unified_risk_score": round(unified_risk, 4),
        "verdict": verdict,
        "components": {
            "tabular_xgboost_probability": round(tabular_prob, 4),
            "nlp_transformer_probability": round(nlp_prob, 4),
            "vision_cnn_probability": round(vision_prob, 4)
        }
    }