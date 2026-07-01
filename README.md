# ReviewGuard AI

**Fake Review Detection & Purchase Behavior Intelligence**

An end-to-end machine learning platform that classifies fake e-commerce reviews in real time, quantifies their impact on trust and ratings, and simulates how removing fake reviews would correct purchase behavior — all through an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![License](https://img.shields.io/badge/License-MIT-green)

![Purchase Impact Dashboard](purchase_impact_analysis.png)

---

## Overview

Fake reviews distort purchase decisions — 90% of online shoppers rely on star ratings as their primary buying signal, and manipulated reviews artificially inflate ratings by 0.3–0.8 stars, eroding long-term platform trust.

ReviewGuard AI addresses this by:
- Classifying individual reviews as fake or genuine with a production-ready ML model
- Scoring platform-wide "trust erosion" using a custom composite metric
- Simulating the rating correction that would result from removing a given percentage of fake reviews
- Surfacing "Sneaky Fakes" — fake reviews that evade detection by mimicking genuine buyer language

---

## Features

| Page | What it does |
|---|---|
| **Overview** | Platform-wide KPIs, fake ratio by category, trust erosion & rating inflation charts |
| **Review Analyzer** | Paste any review text → instant fake-probability score, confidence gauge, and signal breakdown |
| **Purchase Impact** | What-if slider to model rating correction from removing X% of fake reviews; confidence-bucket analysis; Sneaky Fakes table |
| **Category Deep-Dive** | Per-category KPIs, rating histograms, confidence box plots, top fake-review samples |
| **Model Comparison** | 6 ML models benchmarked on accuracy, precision, train time, and inference speed |

---

## Tech Stack

- **Language:** Python 3.11
- **Dashboard:** Streamlit
- **ML:** Scikit-learn, XGBoost, TF-IDF vectorization
- **Data:** Pandas, NumPy
- **NLP/Sentiment:** TextBlob, NLTK
- **Visualization:** Plotly, Matplotlib, Seaborn, WordCloud

---

## System Architecture

```
app.py                    → sidebar router, page navigation, global styling

pages/
  overview.py              → platform-wide KPIs and category breakdowns
  analyzer.py               → real-time single-review classifier
  purchase_impact.py        → what-if simulator + Sneaky Fakes detection
  category_deepdive.py      → per-category analytics
  model_comparison.py       → benchmark table + radar chart

utils.py                  → data loading, caching, model inference
insights.py                → auto-generated narrative insights

model.pkl                 → trained Multinomial Naive Bayes classifier
vectorizer.pkl             → fitted TF-IDF vectorizer
df_with_scores.pkl         → cached, pre-scored dataframe (for fast page loads)
fake reviews dataset.csv  → raw dataset (~40K reviews)
```

**Key design choices:**
- Cache-first architecture (`st.cache_resource` / `st.cache_data`): cold start ~28–30s → warm navigation <400ms
- File-based persistence — no database required
- One `render()` function per page, routed from `app.py`
- Stateless helper functions in `utils.py`, shared across all pages

---

## ML Pipeline

```
Raw CSV (40K reviews)
      ↓
Feature Engineering  (is_fake, purchase_proxy, sentiment via TextBlob)
      ↓
TF-IDF Vectorization
      ↓
Naive Bayes Classification  (prob_fake, prob_real, confidence)
      ↓
Aggregation Engine  (fake_ratio, trust_erosion, rating_inflation)
```

Training and experimentation for this pipeline live in the two notebooks:
- `fake_review_detection.ipynb` — main EDA, feature engineering, and model training
- `fake_review_2.ipynb` — additional experiments / iteration

### Model Benchmarks

*(measured directly via wall-clock timing in the training notebook)*

| Model | Accuracy | Precision | Train Time | Inference |
|---|---|---|---|---|
| Logistic Regression | 85.53% | 85.34% | 2.61s | 0.475s |
| **Multinomial Naive Bayes ★** | 83.95% | **85.37%** | 0.41s | **0.056s** |
| Random Forest | 83.15% | 85.48% | 46.18s | 0.608s |
| XGBoost | 81.62% | 79.40% | 25.08s | 0.176s |
| Voting Classifier | 86.56% | 87.15% | 81.79s | 1.083s |
| Stacking Classifier | 85.70% | 85.67% | 493.67s | 1.155s |

**Why Multinomial Naive Bayes was selected for production:**
- 19× faster inference than the Voting Classifier (0.056s vs 1.08s) — critical for real-time screening
- Precision equivalent to Random Forest, with a ~2.6% accuracy gap that isn't operationally significant
- Fully interpretable — TF-IDF weights and log-probabilities show exactly which words drive classification
- Trains in 0.41s with a trivial memory footprint; no GPU required

---

## Key Results

**Trust Erosion Score** = `(fake_ratio × 0.5) + ((rating_inflation / 5) × 0.3) + (avg_confidence_fake × 0.2)`

- Fake reviews concentrate in specific categories, with some showing 3× the platform-average trust erosion score
- Rating inflation is measurable: fake reviews rate products 0.3–0.8 stars higher than genuine ones in the same category
- High fake probability correlates with high average rating and purchase-proxy rate, confirming a manipulation effect
- 5–15% of ground-truth fakes ("Sneaky Fakes") evade the classifier by mimicking genuine language with specific-sounding details

---

## Testing & Evaluation

49 total test cases across functional, performance, security, stress, recovery, and user-acceptance testing — 47 passed, 2 conditional passes (96% pass rate).

| Suite | Result |
|---|---|
| System / Functional | 10/10 |
| Performance | 6/6 (cold: 28s, warm nav: <400ms, inference: 58ms) |
| Security | 5/6 (1 acknowledged risk: pickle file source trust) |
| Stress & Volume | 6/6 (stable at 40K rows, 50 rapid submissions) |
| Recovery | 5/5 |
| User Acceptance | 2/3 (88% task completion) |

---

## Installation

```bash
git clone https://github.com/<your-username>/reviewguard-ai.git
cd reviewguard-ai
pip install -r requirements.txt
python -m textblob.download_corpora
streamlit run app.py
```

Make sure `model.pkl`, `vectorizer.pkl`, and `fake reviews dataset.csv` are present in the project root (see [Data & Model Files](#data--model-files) below).

## Usage

1. Launch the app with `streamlit run app.py`
2. Navigate between the five dashboard pages from the sidebar
3. Use **Review Analyzer** to test any review text against the classifier
4. Use **Purchase Impact** to model the effect of fake-review removal on ratings

---

## Data & Model Files

This repo includes the trained model artifacts and dataset so it runs out of the box:

| File | Size | Purpose |
|---|---|---|
| `fake reviews dataset.csv` | ~15 MB | Raw labeled review dataset (~40K rows) |
| `model.pkl` | ~92 MB | Trained Multinomial Naive Bayes classifier |
| `vectorizer.pkl` | ~108 KB | Fitted TF-IDF vectorizer |
| `df_with_scores.pkl` | ~18 MB | Pre-scored dataframe, cached for fast dashboard loads |

`model.pkl` is close to GitHub's file-size limits — it's tracked with **Git LFS** in this repo. If you clone without Git LFS installed, run `git lfs install && git lfs pull` after cloning to fetch it.

---

## Project Structure

```
reviewguard-ai/
├── app.py
├── pages/
│   ├── __init__.py
│   ├── overview.py
│   ├── analyzer.py
│   ├── purchase_impact.py
│   ├── category_deepdive.py
│   └── model_comparison.py
├── utils.py
├── insights.py
├── fake_review_detection.ipynb
├── fake_review_2.ipynb
├── fake reviews dataset.csv
├── model.pkl
├── vectorizer.pkl
├── df_with_scores.pkl
├── purchase_impact_analysis.png
├── confidence_purchase_impact.png
├── requirements.txt
└── README.md
```

---

## Future Scope

- **BERT / DistilBERT** — fine-tune a transformer model for >90% precision
- **FastAPI REST endpoint** — expose real-time screening for external e-commerce platforms
- **LIME / SHAP explainability** — word-level attribution per classification
- **Graph network analysis** — detect coordinated fake-review campaigns
- **Multi-platform generalization** — extend to Yelp, Google Reviews, Flipkart

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## Author

**Shafia Mahapule**
[LinkedIn](https://linkedin.com/in/mahapule-shafia) · [GitHub](https://github.com/s-mahapule)
