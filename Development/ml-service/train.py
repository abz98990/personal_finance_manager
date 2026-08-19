"""Train the expense-category classifier and report evaluation metrics.

Runs the full experimental protocol used in the project report:

1. A held-out 80/20 stratified split giving headline accuracy, macro
   precision/recall/F1, per-class scores and a confusion matrix.
2. Stratified 5-fold cross-validation giving mean +/- standard deviation of
   macro F1, so the comparison between algorithms is not an artefact of one
   partition.
3. An ablation run on a trivially separable version of the dataset (no
   ambiguous merchants, no generic memos, no label noise), which quantifies
   how much of the achievable score comes from the difficulty of the task
   rather than the capability of the model.

Usage:
    python train.py
"""
import json

from app.categorize.data import generate_dataset
from app.categorize.model import (
    MODEL_DIR,
    cross_validate_candidates,
    save_model,
    train_and_select_best,
)

METRICS_PATH = MODEL_DIR / "metrics.json"

HEADLINE_KEYS = ["accuracy", "precision_macro", "recall_macro", "f1_macro"]


def _print_headline(report: dict, best_name: str) -> None:
    for name, metrics in report.items():
        marker = "  <- selected" if name == best_name else ""
        print(f"  {name}{marker}")
        for key in HEADLINE_KEYS:
            print(f"    {key}: {metrics[key]:.4f}")


def main():
    print("Generating synthetic training data...")
    df = generate_dataset(n_per_category=400)
    print(f"Dataset: {len(df)} rows across {df['category'].nunique()} categories")

    print("\nTraining Logistic Regression and Random Forest classifiers...")
    best_name, best_pipeline, report = train_and_select_best(df)

    print("\nEvaluation (held-out 20% test set):")
    _print_headline(report, best_name)

    print("\nStratified 5-fold cross-validation (macro F1):")
    cv = cross_validate_candidates(df)
    for name, scores in cv.items():
        print(f"  {name}: {scores['f1_macro_mean']:.4f} +/- {scores['f1_macro_std']:.4f}")

    print("\nAblation - trivially separable data (no ambiguity, no noise):")
    easy_df = generate_dataset(
        n_per_category=400,
        ambiguous_merchant_rate=0.0,
        generic_description_rate=0.0,
        label_noise_rate=0.0,
    )
    easy_best_name, _, easy_report = train_and_select_best(easy_df)
    _print_headline(easy_report, easy_best_name)

    print(f"\nPer-class F1 for the selected model ({best_name}):")
    per_class = report[best_name]["per_class"]
    for label in report[best_name]["confusion_matrix"]["labels"]:
        print(f"    {label}: {per_class[label]['f1-score']:.4f} (n={int(per_class[label]['support'])})")

    save_model(best_pipeline)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_PATH.write_text(
        json.dumps(
            {
                "best_model": best_name,
                "holdout": report,
                "cross_validation": cv,
                "ablation_trivially_separable": {"best_model": easy_best_name, "holdout": easy_report},
            },
            indent=2,
        )
    )

    print(f"\nSaved best model ('{best_name}') and metrics to {MODEL_DIR}")


if __name__ == "__main__":
    main()
