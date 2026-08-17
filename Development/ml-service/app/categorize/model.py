"""Expense category classifier.

Combines a TF-IDF representation of merchant+description text with the
transaction amount (scaled) and feeds both into a classifier. Two algorithms
are compared, as set out in the IPR objectives: Logistic Regression as a
linear baseline and Random Forest to capture non-linear spending patterns.
"""
from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODEL_PATH = MODEL_DIR / "category_classifier.joblib"


def _combine_text(df: pd.DataFrame) -> pd.Series:
    return (df["merchant"].fillna("") + " " + df["description"].fillna("")).str.lower()


def build_preprocessor() -> ColumnTransformer:
    text_pipeline = Pipeline(
        steps=[
            ("combine", FunctionTransformer(_combine_text)),
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("text", text_pipeline, ["merchant", "description"]),
            ("amount", StandardScaler(), ["amount"]),
        ]
    )


def build_pipeline(estimator) -> Pipeline:
    return Pipeline(steps=[("preprocess", build_preprocessor()), ("clf", estimator)])


def evaluate(pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> dict:
    y_pred = pipeline.predict(X_test)
    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision_macro": precision_score(y_test, y_pred, average="macro", zero_division=0),
        "recall_macro": recall_score(y_test, y_pred, average="macro", zero_division=0),
        "f1_macro": f1_score(y_test, y_pred, average="macro", zero_division=0),
    }


def train_and_select_best(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """Trains Logistic Regression and Random Forest, returns the best pipeline plus a metrics report for both."""
    X = df[["merchant", "description", "amount"]]
    y = df["category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    candidates = {
        "logistic_regression": build_pipeline(LogisticRegression(max_iter=1000)),
        "random_forest": build_pipeline(
            RandomForestClassifier(n_estimators=200, max_depth=None, random_state=random_state)
        ),
    }

    report = {}
    best_name, best_pipeline, best_f1 = None, None, -1.0
    for name, pipeline in candidates.items():
        pipeline.fit(X_train, y_train)
        metrics = evaluate(pipeline, X_test, y_test)
        report[name] = metrics
        if metrics["f1_macro"] > best_f1:
            best_name, best_pipeline, best_f1 = name, pipeline, metrics["f1_macro"]

    return best_name, best_pipeline, report


def save_model(pipeline: Pipeline) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)


def load_model() -> Pipeline:
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"No trained model found at {MODEL_PATH}. Run `python train.py` first."
        )
    return joblib.load(MODEL_PATH)


def predict_one(pipeline: Pipeline, merchant: str, description: str, amount: float):
    row = pd.DataFrame([{"merchant": merchant or "", "description": description or "", "amount": amount}])
    proba = pipeline.predict_proba(row)[0]
    classes = pipeline.classes_
    best_idx = proba.argmax()
    return str(classes[best_idx]), float(proba[best_idx])
