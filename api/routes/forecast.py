from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.ml_service import predict_market_price


router = APIRouter(
    prefix="/forecast",
    tags=["Price Forecast"]
)


# ============================================================
# REQUEST SCHEMA
# ============================================================

class PriceForecastRequest(BaseModel):
    market: str
    district: str
    variety: str
    arrival_quantity_kg: float
    prediction_date: str | None = None


# ============================================================
# PRICE FORECAST
# ============================================================

@router.post("/price")
def price_forecast(
    request: PriceForecastRequest
):
    """
    Generate an XGBoost-based tomato price forecast
    for the requested market and date.
    """

    try:

        predicted_price = predict_market_price(
            market=request.market,
            district=request.district,
            variety=request.variety,
            arrival_quantity=request.arrival_quantity_kg,
            prediction_date=request.prediction_date
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=404,
            detail=str(exc)
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Unable to generate price forecast: {exc}"
        )

    return {
        "market": request.market,
        "district": request.district,
        "variety": request.variety,
        "arrival_quantity_kg":
            request.arrival_quantity_kg,
        "prediction_date":
            request.prediction_date,
        "predicted_price_per_kg":
            predicted_price
    }