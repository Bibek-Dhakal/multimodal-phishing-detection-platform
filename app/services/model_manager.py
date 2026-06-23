import os
import pickle

import torch
import torchvision.transforms as transforms
from torchvision import models as torch_models

from app.neural_network import PhishingANN

try:
    from transformers import pipeline

    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    from PIL import Image
    import io

    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False


class ModelRegistry:
    def __init__(self):
        self.ml_model = None
        self.ann_model = None
        self.nlp_model = None
        self.vision_model = None
        self.vision_preprocess = None


registry = ModelRegistry()


def load_models():
    ml_path = "models/best_traditional_ml.pkl"
    ann_path = "models/tabular_ann.pt"

    print("[*] Booting Inference Engines...")
    if os.path.exists(ml_path):
        with open(ml_path, "rb") as f:
            registry.ml_model = pickle.load(f)
        print("[+] ML Model loaded.")

    if os.path.exists(ann_path):
        ann = PhishingANN(input_dim=30)
        ann.load_state_dict(torch.load(ann_path, map_location=torch.device('cpu')))
        ann.eval()
        registry.ann_model = ann
        print("[+] ANN Model loaded.")

    if TRANSFORMERS_AVAILABLE:
        try:
            print("[*] Initializing NLP Transformer Pipeline...")
            registry.nlp_model = pipeline("text-classification", model="distilroberta-base")
        except Exception as e:
            print(f"[-] Failed to load NLP Model: {e}")

    if VISION_AVAILABLE:
        try:
            print("[*] Initializing CNN Vision Engine...")
            registry.vision_model = torch_models.efficientnet_b0(pretrained=True)
            registry.vision_model.eval()
            registry.vision_preprocess = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
        except Exception as e:
            print(f"[-] Failed to load Vision Model: {e}")
