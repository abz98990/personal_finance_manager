"""Spending forecast from a user's monthly expense history.

With only a handful of monthly totals per user, a full ARIMA-style
time-series model would badly overfit. Instead this fits a simple linear
trend (least-squares regression of total against month index) which is the
standard, well-understood baseline referenced in the IPR's methodology
(section 2.2 / objective 5) and is robust with as few as two data points.
"""
import numpy as np


def forecast_next_month(history: list[dict]) -> dict:
    """history: [{"month": "YYYY-MM", "total": float}, ...] sorted ascending by month."""
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
