import pytest

from app.forecast.model import forecast_next_month


def test_increasing_trend():
    history = [
        {"month": "2026-01", "total": 100.0},
        {"month": "2026-02", "total": 150.0},
        {"month": "2026-03", "total": 200.0},
    ]
    result = forecast_next_month(history)
    assert result["trend"] == "increasing"
    assert result["nextMonthTotal"] > 200.0


def test_decreasing_trend():
    history = [
        {"month": "2026-01", "total": 300.0},
        {"month": "2026-02", "total": 200.0},
        {"month": "2026-03", "total": 100.0},
    ]
    result = forecast_next_month(history)
    assert result["trend"] == "decreasing"
    assert result["nextMonthTotal"] < 100.0


def test_stable_trend():
    history = [
        {"month": "2026-01", "total": 200.0},
        {"month": "2026-02", "total": 201.0},
        {"month": "2026-03", "total": 199.0},
    ]
    result = forecast_next_month(history)
    assert result["trend"] == "stable"


def test_forecast_never_negative():
    history = [
        {"month": "2026-01", "total": 50.0},
        {"month": "2026-02", "total": 10.0},
        {"month": "2026-03", "total": 0.0},
    ]
    result = forecast_next_month(history)
    assert result["nextMonthTotal"] >= 0.0


def test_requires_at_least_two_months():
    with pytest.raises(ValueError):
        forecast_next_month([{"month": "2026-01", "total": 50.0}])
