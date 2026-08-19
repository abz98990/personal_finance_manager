"""Spending forecast from a user's monthly totals.

A least-squares linear trend rather than anything fancier: users typically have
only a handful of months of history, and ARIMA-style models overfit badly on that.
"""
import numpy as np


def forecast_next_month(history: list[dict]) -> dict:
    """history: [{"month": "YYYY-MM", "total": float}, ...] ascending by month."""
    if len(history) < 2:
        raise ValueError("At least 2 months of history are required to forecast")

    totals = np.array([h["total"] for h in history], dtype=float)
    x = np.arange(len(totals))

    slope, intercept = np.polyfit(x, totals, 1)
    next_x = len(totals)
    predicted = float(slope * next_x + intercept)
    predicted = max(0.0, predicted)

    if slope > 0.5:
        trend = "increasing"
    elif slope < -0.5:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "nextMonthTotal": round(predicted, 2),
        "trend": trend,
        "monthlyChange": round(float(slope), 2),
    }
