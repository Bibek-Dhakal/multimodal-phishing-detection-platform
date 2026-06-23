# Multi-Modal Phishing Intelligence & Defense Platform

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![PyTorch](https://img.shields.io/badge/PyTorch-Deep%20Learning-ee4c2c)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B)

## Project Overview

Phishing attacks remain one of the most pervasive cyber threats, causing billions of dollars in losses annually. This
project is a **Phishing Detection System** that automatically evaluates suspicious URLs using a production-grade *
*Layered Hybrid Defense Architecture**.

Instead of relying solely on isolated machine learning models, this platform combines:

1. **Live Threat Intelligence:** Integrates OpenPhish zero-day feeds via HTTPS/RDAP.
2. **Structural ML/DL Engines:** Benchmarks 8 traditional Machine Learning algorithms (with **XGBoost** achieving top
   accuracy) and a custom PyTorch **Artificial Neural Network (ANN)**.
3. **Continuous Heuristics:** Uses Shannon Entropy and mathematical gradient penalties to prevent false positives and
   catch zero-day obfuscation.

Both engines run concurrently via a FastAPI backend, utilizing a Weighted Priority Matrix to aggregate predictions and
completely eliminate "alarm fatigue," displaying results through a Streamlit dashboard.

---

## Documentation

For a deep dive into the methodology and technical details, please refer to the following documents:

* [System Architecture](docs/architecture.md) - Details the Data Pipeline, ML/DL Models, and App Deployment.
* [Dataset Information](docs/dataset_info.md) - Explains the UCI Phishing dataset features and structure.

---

## Architecture

1. **Threat Intelligence Layer**: Live TTL caching of the OpenPhish database and local Apex domain whitelisting.
2. **Machine Learning Engine**: Benchmarks Logistic Regression, Naive Bayes, KNN, SVM, Decision Tree, Random Forest,
   AdaBoost, and XGBoost.
3. **Deep Learning Engine**: A Dense Multi-Layer Perceptron (MLP) built in PyTorch to evaluate complex non-linear
   patterns in structured features.
4. **Inference Gateway**: FastAPI backend (`app/main.py`) that loads models into memory, applies Probabilistic
   Thresholding (0.85), and serves consensus predictions.
5. **User Interface**: Streamlit dashboard (`app/dashboard.py`) for security analysts to test web profile vectors and
   raw URLs natively.

---

## Installation & Setup

### 1. Prerequisites

- Python 3.9+
- *(Optional but recommended)* NVIDIA GPU with CUDA support for accelerated PyTorch training.

### 2. Environment Setup

Clone the repository (or extract the folder) and create a virtual environment:

```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate
```

Install dependencies:

```bash
pip install pandas numpy matplotlib seaborn scikit-learn xgboost torch torchvision torchaudio scipy fastapi uvicorn streamlit python-whois python-multipart
```

### 3. Data Setup

Ensure the UCI Phishing dataset (`dataset.arff`) is located in the `data/` directory.

---

## Running the Pipeline

### 1. Train the Models

If you wish to retrain the models from scratch, run the training scripts. This will output serialized `.pkl` and `.pt`
files to the `models/` directory.

```bash
# Train the traditional ML models
python train_ml.py

# Train the PyTorch ANN
python train_ann.py
```

### 2. Boot the Production Application

The application requires two terminals. Ensure your virtual environment is activated in both.

**Terminal 1: Start the FastAPI Backend**

```bash
uvicorn app.main:app --reload
```

*(The API will be available at http://127.0.0.1:8000. It will automatically download the OpenPhish feed on boot).*

**Terminal 2: Start the Streamlit Dashboard**

```bash
streamlit run app/dashboard.py
```

*(The Dashboard will open automatically in your browser at http://localhost:8501)*

---

## Future Scope (Max Version)

The roadmap for this platform includes scaling into a Multi-Modal architecture:

* **NLP Linguistic Engine**: Integrating a fine-tuned `distilroberta-base` Transformer to analyze raw URL strings for
  typosquatting and malicious subdomains.
* **Computer Vision Engine**: Utilizing a pre-trained `EfficientNet-B0` CNN to analyze website screenshots for spatial
  layout anomalies and brand logo spoofing.

---
