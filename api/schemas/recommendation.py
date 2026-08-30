from typing import Any

from pydantic import BaseModel


# ============================================================
# REQUEST
# ============================================================

class RecommendationRequest(BaseModel):
    crop: str
    variety: str
    quantity_kg: float


# ============================================================
# MARKET RECOMMENDATION
# ============================================================

class MarketRecommendation(BaseModel):
    market_id: int
    market_name: str
    district: str

    predicted_price_per_kg: float
    net_price_per_kg: float

    transport_cost_per_kg: float
    commission_per_kg: float
    expected_loss_per_kg: float

    expected_return: float


# ============================================================
# RESPONSE
# ============================================================

class RecommendationResponse(BaseModel):
    crop: str
    variety: str
    quantity_kg: float

    recommended_market_id: int
    recommended_market_name: str

    predicted_price_per_kg: float
    net_price_per_kg: float

    expected_return: float
    advantage_over_next_best: float

    recommendation: str
    reason: str

    alternatives: list[MarketRecommendation]

    # --------------------------------------------------------
    # Optional history information
    # --------------------------------------------------------

    reservation_price: float | None = None

    risk_preference: str | None = None

    optimization: dict[str, Any] | None = None

    fairdeal: dict[str, Any] | None = None