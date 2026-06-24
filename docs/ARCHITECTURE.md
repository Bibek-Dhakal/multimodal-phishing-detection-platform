# Deployment & System Architecture Core Topology

The Phishing Detection System is designed following strict MLOps and decoupled software engineering principles. The
architecture isolates the underlying inference models, the API gateway, and the frontend to guarantee high availability,
clean dependency management, and fault tolerance.

## Architecture Flow Diagram

```mermaid
graph TR
    %% Interface Layer
    User[Web Client Browser Engine] <-->|Interacts with Dashboard Interface| UI[Streamlit User Interface Service]
    
    %% Configuration Framework
    DotEnv[python-dotenv Core Manager] -.->|Injects Active Routing Ports / Variables| UI
    DotEnv -.->|Injects Memory Weights Constraints| API[FastAPI Gateway Engine]

    %% Ingestion Interface Pipelines
    UI -->|Transmits Raw URL String Text Payload via HTTP POST| API
    
    subgraph Container Service Isolation [Docker Multi-Container Microservices Architecture]
        UI
        API
    end

    %% Decoupled Branch Routing Logic Split
    API -->|Imported Route 1: Offline Lexical Extractor| FE[src/feature_extractor.py: 79-Feature Math & Whitelist]
    API -->|Imported Route 2: Sequential Linguistic Mapping| Tokenizer[Hugging Face Transformer Tokenizer]
    
    %% Tabular Execution Track
    FE -->|Generates 79-Dimension Float Vector| TabPipeline[src/tabular_pipeline.py]
    TabPipeline -->|Generates Model-Ready Vector| XGB[Trained Production Tabular Champion: XGBoost Model]
    
    %% Deep NLP Execution Track
    Tokenizer -->|Encodes Input IDs & Attention Mask Vectors| MiniLM[Trained Contextual Transformer: MiniLM-L12-H384]
    
    %% Soft Voting Fusion Aggregation Node
    XGB -->|Calculates Independent Structural Risk Logits| Aggregator[Soft-Voting Ensemble Logic Aggregator]
    MiniLM -->|Calculates Contextual Linguistic Risk Logits| Aggregator
    
    Aggregator -->|Returns Consolidated Predictive Risk Vector Payload| API
    API -->|Returns Verified JSON Output Verdict Back to Interface| UI
```

## 1. Multi-Branch Machine Learning Strategy

### 1.1 Tabular Multi-Estimator Evaluation Arena (`src/train_tabular.py`)

The tabular processing logic is isolated from NLP execution blocks. The script evaluates 9 classifiers on the
79-dimension numerical layout:
`Logistic Regression`, `Naive Bayes`, `KNN`, `SVM`, `Decision Tree`, `Random Forest`, `AdaBoost`, `ANN (MLP)`, and
`XGBoost`.
**XGBoost** is the selected production champion due to its resilience against unscaled data and cross-feature
relationships.

### 1.2 Deep Learning NLP Branch (`src/train_nlp.py`)

* **Production Model:** `microsoft/MiniLM-L12-H384-uncased` (Chosen because its highly optimized parameter profile
  scales smoothly within tight VRAM spaces while offering near BERT-level performance).
* **Preprocessing Strategy:** URLs are explicitly converted to lowercase via `.lower()`, but structural delimiters (`-`,
  `.`, `/`, `?`, `=`, `&`) are strictly preserved rather than stripped. This enables the transformer to effectively
  detect heavily mutated typosquatting paths (e.g. `paypal-security-login.com`).
* Processes sequential linguistic patterns natively via attention masks, completely avoiding fragile heuristic text
  extraction.

### 1.3 Soft Voting Fusion Aggregation

FastAPI aggregates individual model outputs seamlessly applying specific probability weights:

* **Tabular XGBoost:** 40%
* **Contextual MiniLM:** 40%
* **Vision CNN (Mocked/Future):** 20%

If the fused sum evaluates over 0.75, it triggers a `Phishing` verdict. Values between 0.40 and 0.75 are flagged as
`Suspicious`.

## 2. Decoupled Directory Responsibilities

* **`src/feature_extractor.py`**: Compiles exactly 79 mathematical and structural ISCX features entirely offline.
  Includes an **Enterprise Whitelist** (Google, Microsoft, Amazon, etc.) to immediately bypass the ML model and prevent
  false positives on highly trusted domains.
* **`src/tabular_pipeline.py`**: Target transformation and imputation logic standardizing input states (handles
  scrubbing of `np.inf` values).
* **`app/main.py`**: The FastAPI Gateway loading binaries via ContextLib lifespan methods for maximum speed and safety.
  Implements the soft-voting matrix.
* **`app/ui.py`**: Lightweight Streamlit client that never interacts with raw models directly. Explicitly informs users
  that the Vision CNN branch is currently a mocked placeholder in the roadmap.
* **`notebooks/`**: Four targeted `.ipynb` research sandboxes verifying EDA, NLP token limits, model arena baselines,
  and proving the exact 79-feature extraction mathematical pipeline.

---
