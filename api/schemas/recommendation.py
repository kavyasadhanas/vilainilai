from pydantic import BaseModel

from api.schemas.comparison import MarketCost


class RecommendationRequest(BaseModel):
    crop: str
    quantity_kg: float
    market_costs: list[MarketCost]


class MarketRecommendation(BaseModel):
    market_id: int
    market_name: str
    district: str
    expected_return: float
    net_price_per_kg: float


class RecommendationResponse(BaseModel):
    crop: str
    quantity_kg: float

    recommended_market_id: int
    recommended_market_name: str

    expected_return: float
    advantage_over_next_best: float

    recommendation: str
    reason: str

    alternatives: list[MarketRecommendation]