from fastapi import FastAPI, HTTPException

from app.categorize.model import load_model, predict_one
from app.forecast.model import forecast_next_month
from app.schemas import (
    CategorizeRequest,
    CategorizeResponse,
    ForecastRequest,
    ForecastResponse,
)

app = FastAPI(title="PFM ML Service", version="1.0.0")

_category_model = None


def get_category_model():
    global _category_model
    if _category_model is None:
        _category_model = load_model()
    return _category_model


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict/category", response_model=CategorizeResponse)
def predict_category(req: CategorizeRequest):
    try:
        model = get_category_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    category, confidence = predict_one(model, req.merchant, req.description, req.amount)
    return CategorizeResponse(category=category, confidence=confidence)


@app.post("/predict/forecast", response_model=ForecastResponse)
def predict_forecast(req: ForecastRequest):
    try:
        result = forecast_next_month([h.model_dump() for h in req.history])
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ForecastResponse(**result)
