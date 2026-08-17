import pytest
from fastapi.testclient import TestClient

from app.categorize.data import generate_dataset
from app.categorize.model import save_model, train_and_select_best


@pytest.fixture(scope="module", autouse=True)
def ensure_model_trained():
    df = generate_dataset(n_per_category=150, seed=7)
    _, pipeline, _ = train_and_select_best(df)
    save_model(pipeline)


@pytest.fixture()
def client():
    from app.main import app

    return TestClient(app)


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_predict_category(client):
    res = client.post(
        "/predict/category",
        json={"merchant": "Netflix", "description": "Monthly subscription", "amount": 14.0},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["category"] == "Entertainment"
    assert 0.0 <= body["confidence"] <= 1.0


def test_predict_category_requires_positive_amount(client):
    res = client.post("/predict/category", json={"merchant": "Netflix", "amount": -5})
    assert res.status_code == 422


def test_predict_forecast(client):
    res = client.post(
        "/predict/forecast",
        json={
            "history": [
                {"month": "2026-01", "total": 100.0},
                {"month": "2026-02", "total": 150.0},
                {"month": "2026-03", "total": 200.0},
            ]
        },
    )
    assert res.status_code == 200
    body = res.json()
    assert body["trend"] == "increasing"


def test_predict_forecast_requires_two_months(client):
    res = client.post("/predict/forecast", json={"history": [{"month": "2026-01", "total": 100.0}]})
    assert res.status_code == 422
