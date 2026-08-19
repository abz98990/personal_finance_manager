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
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
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


def build_candidates(random_state: int = 42) -> dict:
    """The two algorithms compared in the study, as set out in the project objectives."""
    return {
        "logistic_regression": build_pipeline(LogisticRegression(max_iter=1000)),
        "random_forest": build_pipeline(
            RandomForestClassifier(n_estimators=200, max_depth=None, random_state=random_state)
        ),
    }


def cross_validate_candidates(df: pd.DataFrame, n_splits: int = 5, random_state: int = 42) -> dict:
    """Stratified k-fold cross-validation, reporting mean and standard deviation of macro F1.

    A single train/test split gives one number with no indication of its
    variability; k-fold makes the comparison between the two algorithms
    defensible rather than an artefact of one lucky partition.
    """
    X = df[["merchant", "description", "amount"]]
    y = df["category"]
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

    results = {}
    for name, pipeline in build_candidates(random_state).items():
        scores = cross_val_score(pipeline, X, y, cv=cv, scoring="f1_macro")
        results[name] = {
            "f1_macro_mean": float(scores.mean()),
            "f1_macro_std": float(scores.std()),
            "folds": [float(s) for s in scores],
        }
    return results


def train_and_select_best(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """Trains Logistic Regression and Random Forest, returns the best pipeline plus a metrics report for both.

    The report includes headline metrics, per-class precision/recall/F1 and a
    confusion matrix so that failure modes can be analysed, not just scored.
    """
    X = df[["merchant", "description", "amount"]]
    y = df["category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    report = {}
    best_name, best_pipeline, best_f1 = None, None, -1.0
    for name, pipeline in build_candidates(random_state).items():
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        labels = sorted(y.unique())

        report[name] = {
            **evaluate(pipeline, X_test, y_test),
            "per_class": classification_report(
                y_test, y_pred, labels=labels, output_dict=True, zero_division=0
            ),
            "confusion_matrix": {
                "labels": labels,
                "matrix": confusion_matrix(y_test, y_pred, labels=labels).tolist(),
            },
        }
        if report[name]["f1_macro"] > best_f1:
            best_name, best_pipeline, best_f1 = name, pipeline, report[name]["f1_macro"]

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
