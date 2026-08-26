from pydantic import BaseModel


class MarketCost(BaseModel):
    market_id: int
    transport_cost_per_kg: float = 0
    commission_per_kg: float = 0
    expected_loss_per_kg: float = 0


class MarketComparisonRequest(BaseModel):
    crop: str
    quantity_kg: float
    market_costs: list[MarketCost]


class MarketComparisonResult(BaseModel):
    market_id: int
    market_name: str
    district: str

    market_price_per_kg: float
    transport_cost_per_kg: float
    commission_per_kg: float
    expected_loss_per_kg: float

    net_price_per_kg: float
    expected_return: float


class MarketComparisonResponse(BaseModel):
    crop: str
    quantity_kg: float
    markets: list[MarketComparisonResult]
    best_market_id: int
    best_market_name: str
    best_expected_return: float