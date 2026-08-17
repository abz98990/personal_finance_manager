import pandas as pd
import pytest

from app.categorize.data import generate_dataset
from app.categorize.model import predict_one, train_and_select_best


@pytest.fixture(scope="module")
def trained_pipeline():
    df = generate_dataset(n_per_category=150, seed=7)
    _, pipeline, _ = train_and_select_best(df)
    return pipeline


def test_predicts_known_category_confidently(trained_pipeline):
    category, confidence = predict_one(trained_pipeline, "Netflix", "Monthly subscription", 14.0)
    assert category == "Entertainment"
    assert 0.0 <= confidence <= 1.0


def test_predicts_groceries(trained_pipeline):
    category, _ = predict_one(trained_pipeline, "Tesco", "Weekly shop", 45.0)
    assert category == "Groceries"


def test_confidence_is_normalized_probability(trained_pipeline):
    _, confidence = predict_one(trained_pipeline, "Landlord Payment", "Monthly rent", 650.0)
    assert confidence <= 1.0
