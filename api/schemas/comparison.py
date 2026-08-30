from pydantic import BaseModel


# ============================================================
# MARKET COST
# ============================================================

class MarketCost(BaseModel):
    market_id: int

    transport_cost_per_kg: float = 0.0

    commission_per_kg: float = 0.0

    expected_loss_per_kg: float = 0.0


# ============================================================
# MARKET COMPARISON REQUEST
# ============================================================

class MarketComparisonRequest(BaseModel):
    crop: str

    variety: str

    quantity_kg: float

    market_costs: list[MarketCost]

    prediction_date: str | None = None


# ============================================================
# MARKET COMPARISON RESULT
# ============================================================

class MarketComparisonResult(BaseModel):
    market_id: int

    market_name: str

    district: str

    # ML dataset market name
    ml_market: str | None = None

    # XGBoost predicted price
    predicted_price_per_kg: float

    transport_cost_per_kg: float

    commission_per_kg: float

    expected_loss_per_kg: float

    net_price_per_kg: float

    expected_return: float


# ============================================================
# MARKET COMPARISON RESPONSE
# ============================================================

class MarketComparisonResponse(BaseModel):
    crop: str

    variety: str

    quantity_kg: float

    markets: list[MarketComparisonResult]

    best_market_id: int

    best_market_name: str

    best_expected_return: float