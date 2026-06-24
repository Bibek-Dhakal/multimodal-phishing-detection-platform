This is the **Single Source of Truth (SSoT) Visual CNN Implementation Master Plan**. This document covers the exact
dataset source selection, download paths, storage management rules, and code architecture for your future computer
vision branch.

---

## 1. Dataset Verification & Link Registry

The complete PhishIntention data suite is maintained by the National University of Singapore (NUS) security research
team.

* **Official Research Site:
  ** [PhishIntention Experiment Structure Portal](https://sites.google.com/view/phishintention/experiment-structure)
* **Official Open-Source Engine Code base:
  ** [GitHub - lindsey98/PhishIntention](https://github.com/lindsey98/PhishIntention)

---

## 2. Resource Constraints & Download Selection Strategy

The PhishIntention dataset is split into separate packages designed for different deep learning tasks (Object Detection,
Siamese Logo Matching, and Layout Classification). To prevent your development machine from running out of disk space,
you must select the correct subset:

* ❌ **DO NOT DOWNLOAD: Experiment Dataset (25K Benign + 25K Phishing) [~18 GB]**
* *Reason:* This contains uncompressed high-resolution raw page layouts. Downloading and unpacking this directory
  requires over 40 GB of free space, which will overwhelm a local 16 GB laptop and slow down development cycles.

* ✅ **DOWNLOAD THIS SUBSET: CRP Transition Detector Split [~3.5 GB]**
* *Reason:* This package provides pre-split training and testing partitions featuring full-page layout screenshots. It
  is explicitly labeled by whether a page dynamically captures credentials (Credential Requiring Page). At **~3.5 GB
  total**, it fits comfortably on your local drive and provides enough layout variations to train your binary visual CNN
  model.

### 2.1 Selected Component Data Metrics

| Subset Component        | Instance Volumetrics                                               | Primary Target Focus                    |
|-------------------------|--------------------------------------------------------------------|-----------------------------------------|
| **`4843 training set`** | 1,774 Phishing Page Screenshots <br> 3,069 Benign Page Screenshots | Training loop tuning baseline           |
| **`1210 test set`**     | 445 Phishing Page Screenshots <br> 765 Benign Page Screenshots     | Final generalization evaluation metrics |

---

## 3. Project Storage Integration Layout

Keep your data and model directories clean and easy to manage by adding these explicit paths to your local workspace.
Ensure your project's main `.gitignore` file completely excludes these folders from version control.

```text
phishing-detection-system/
├── .gitignore                      # Verifies binary exclusion boundaries
├── src/
│   ├── __init__.py
│   └── vision_pipeline_todo.py     # Future PyTorch data handler & training logic
└── data/                           # --- EXTENSION WORKING DIRECTORY (GIT-IGNORED) ---
    └── vision_todo/
        ├── raw_zips/               # Holds raw downloaded PhishIntention zip components
        ├── train/
        │   ├── benign/             # Place the 3,069 clean full-page images here
        │   └── phishing/           # Place the 1,774 phishing full-page images here
        └── test/
            ├── benign/             # Place the 765 clean validation images here
            └── phishing/           # Place the 445 phishing validation images here
```

---

## 4. Architectural Data Flow: The Ingestion Pipeline

```text
========================================================================================
                               PRODUCTION INGESTION ARCHITECTURE
========================================================================================

    [ Raw Playwright Screen Capture ] ──> Saved as temporary layout asset (1280 × 720)
                  │
                  ▼
    [ RGB Mode Normalization Step ]  ──> Drops Alpha channels (RGBA -> RGB conversions)
                  │
                  ▼
    [ Bilinear Downscale Matrix ]    ──> Compresses image to fixed dimensions (224 × 224)
                  │
                  ▼
    [ ImageNet Tensor Scaling ]      ──> Normalizes pixel data: Mean/Std Dev parameters
                  │
                  ▼
    [ EfficientNet-B0 / MobileNet ]  ──> Outputs low-latency binary classification scores
========================================================================================
```

### 4.1 Production Engineering Implementation Specs

1. **Avoid Asset Mismatches with Fixed Viewports:** Phishing landing pages use responsive CSS designs that break or
   shift layout elements when shrunk abnormally. To prevent distortion, your inference engine must use Playwright to
   load pages at a standard desktop resolution (**1280 x 720**) before applying downscaling filters.
2. **Defend Closures with Explicit Timeout Bounds:** Phishing sites are often hosted on slow, unstable servers, or they
   may intentionally run infinite-hang scripts to crash scraping tools. Always enforce a strict navigation timeout
   constraint:

```python
# Fallback safeguard protecting inference workers from infinite connection stalls
await page.goto(url, timeout=15000, wait_until="domcontentloaded")
```

3. **Geometric Image Compression Dimensions:** Use `torchvision.transforms` or `PIL` to cleanly compress your captured
   snapshots into a structured **224 x 224 x 3 matrix**. This allows you to deploy lightweight models like *
   *EfficientNet-B0** or **MobileNetV3-Large** that fit easily within your laptop's **6 GB VRAM physical hardware limits
   ** while processing inputs in milliseconds.

---

## 5. Microservice Integration Strategy

1. **Isolate Code Updates into Separate Modules:** Package your inference rules into an isolated helper class inside
   `src/vision_pipeline_todo.py`.
2. **Coordinate Model Results via Soft Voting:** Pass predictions into the aggregator established in `app/main.py` using
   custom weight distributions:

`Unified Risk Rating = (Tabular XGBoost Score * 0.4) + (Contextual MiniLM Score * 0.4) + (Vision CNN Score * 0.2)`

---
