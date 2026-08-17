from pydantic import BaseModel, Field


class CategorizeRequest(BaseModel):
    merchant: str = ""
    description: str = ""
    amount: float = Field(gt=0)


class CategorizeResponse(BaseModel):
    category: str
    confidence: float


class MonthlyTotal(BaseModel):
    month: str
    total: float


class ForecastRequest(BaseModel):
    history: list[MonthlyTotal]


class ForecastResponse(BaseModel):
    nextMonthTotal: float
    trend: str
    monthlyChange: float
