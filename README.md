# ReviewGuard AI

**Fake Review Detection & Purchase Behavior Intelligence**

An end-to-end machine learning platform that classifies fake e-commerce reviews in real time, quantifies their impact on trust and ratings, and simulates how removing fake reviews would correct purchase behavior — all through an interactive Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![License](https://img.shields.io/badge/License-MIT-green)

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

| Module | What it does |
|---|---|
| **Overview Dashboard** | Platform-wide KPIs, fake-ratio by category, trust erosion & rating inflation charts |
| **Review Analyzer** | Paste any review text → instant fake-probability score, confidence gauge, and signal breakdown |
| **Purchase Impact Simulator** | What-if slider to model rating correction from removing X% of fake reviews |
| **Category Deep-Dive** | Per-category KPIs, rating histograms, sentiment scatter, top fake-review samples |
| **Model Comparison** | 6 ML models benchmarked on accuracy, precision, train time, and inference speed |

---

## Tech Stack

- **Language:** Python 3.11
- **Dashboard:** Streamlit
- **ML:** Scikit-learn, XGBoost, TF-IDF vectorization
- **Data:** Pandas, NumPy
- **NLP/Sentiment:** TextBlob
- **Visualization:** Plotly

---

## System Architecture

```
Presentation Layer   → app.py (router), overview.py, analyzer.py,
                        purchase_impact.py, category_deepdive.py,
                        model_comparison.py

Application Logic    → utils.py (data + inference + caching)
                        insights.py (insight generator)

Data Layer           → fake_reviews_dataset.csv (~40K rows)
                        model.pkl (Naive Bayes)
                        vectorizer.pkl (TF-IDF)
                        df_with_scores.pkl (cached)
```

**Key design choices:**
- Cache-first architecture: 30s cold start → <400ms warm navigation
- File-based persistence (no database required)
- Modular pages, one `render()` function per view
- Stateless functions backed by shared `utils.py`

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

### Model Benchmarks

| Model | Accuracy | Precision | Train Time | Inference |
|---|---|---|---|---|
| Logistic Regression | 85.53% | 85.34% | 2.61s | 0.48s |
| **Multinomial Naive Bayes ★** | 83.95% | **85.37%** | 0.41s | **0.056s** |
| Random Forest | 83.15% | 85.48% | 46.18s | 0.61s |
| XGBoost | 81.62% | 79.40% | 25.08s | 0.18s |
| Voting Classifier | 86.56% | 87.15% | 81.79s | 1.08s |
| Stacking Classifier | 85.70% | 85.67% | 493.67s | 1.16s |

**Why Multinomial Naive Bayes was selected for production:**
- 19× faster inference than the Voting Classifier (0.056s vs 1.08s) — critical for real-time screening
- Precision equivalent to Random Forest, with a 2.6% accuracy gap that isn't operationally significant
- Fully interpretable — TF-IDF weights show exactly which words drive classification
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
streamlit run app.py
```

## Usage

1. Launch the app with `streamlit run app.py`
2. Navigate between the five dashboard views from the sidebar
3. Use **Review Analyzer** to test any review text against the classifier
4. Use **Purchase Impact Simulator** to model the effect of fake-review removal on ratings

---

## Project Structure

```
reviewguard-ai/
├── app.py
├── pages/
│   ├── overview.py
│   ├── analyzer.py
│   ├── purchase_impact.py
│   ├── category_deepdive.py
│   └── model_comparison.py
├── utils.py
├── insights.py
├── data/
│   └── fake_reviews_dataset.csv
├── models/
│   ├── model.pkl
│   └── vectorizer.pkl
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
