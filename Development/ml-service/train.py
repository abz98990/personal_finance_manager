"""Train the expense-category classifier and report evaluation metrics.

Usage:
    python train.py
"""
import json
from pathlib import Path

from app.categorize.data import generate_dataset
from app.categorize.model import MODEL_DIR, save_model, train_and_select_best

METRICS_PATH = MODEL_DIR / "metrics.json"


def main():
    print("Generating synthetic training data...")
    df = generate_dataset(n_per_category=400)
    print(f"Dataset: {len(df)} rows across {df['category'].nunique()} categories")

    print("Training Logistic Regression and Random Forest classifiers...")
    best_name, best_pipeline, report = train_and_select_best(df)

    print("\nEvaluation (held-out 20% test set):")
    for name, metrics in report.items():
        marker = " <- selected" if name == best_name else ""
        print(f"  {name}{marker}")
        for metric_name, value in metrics.items():
            print(f"    {metric_name}: {value:.4f}")

    save_model(best_pipeline)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps({"best_model": best_name, "report": report}, indent=2))

    print(f"\nSaved best model ('{best_name}') and metrics to {MODEL_DIR}")


if __name__ == "__main__":
    main()
