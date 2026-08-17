# PFM ML Service

FastAPI microservice providing the two ML-driven features of the AI-Based
Personal Financial Management System:

- `POST /predict/category` — predicts an expense category from merchant,
  description and amount. Compares a Logistic Regression baseline against a
  Random Forest classifier on TF-IDF text + scaled amount features, and
  keeps whichever scores higher on macro F1.
- `POST /predict/forecast` — predicts next month's total spending from a
  user's monthly expense history using a least-squares linear trend, and
  reports whether spending is increasing, decreasing or stable.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

## Train the classifier

Training data is synthetic (see `app/categorize/data.py` for why: real
transaction data is sensitive personal financial data, see IPR section 5.2).

```bash
python train.py
```

This prints accuracy/precision/recall/F1 for both algorithms and saves the
better-performing pipeline to `models/category_classifier.joblib`.

## Run the API

```bash
uvicorn app.main:app --reload --port 8000
```

## Test

```bash
python -m pytest -v
```
