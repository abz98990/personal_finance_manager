"""Trains the category classifier and saves the better of the two candidates.

Usage:
    python train.py
"""
import json

from app.categorize.data import generate_dataset
from app.categorize.model import MODEL_DIR, save_model, train_and_select_best

METRICS_PATH = MODEL_DIR / "metrics.json"


def main():
    df = generate_dataset()
    print(f"Dataset: {len(df)} rows across {df['category'].nunique()} categories")

    best_name, best_pipeline, report = train_and_select_best(df)

    for name, metrics in report.items():
        print(f"\n{name}{'  <- selected' if name == best_name else ''}")
        for key, value in metrics.items():
            print(f"  {key}: {value:.4f}")

    save_model(best_pipeline)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(json.dumps({"best_model": best_name, "metrics": report}, indent=2))
    print(f"\nSaved '{best_name}' to {MODEL_DIR}")


if __name__ == "__main__":
    main()
