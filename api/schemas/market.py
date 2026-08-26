from datetime import datetime

from pydantic import BaseModel


class MarketCreate(BaseModel):
    name: str
    district: str
    latitude: float | None = None
    longitude: float | None = None


class MarketResponse(MarketCreate):
    id: int

    class Config:
        from_attributes = True


class MarketPriceCreate(BaseModel):
    market_id: int
    crop: str
    price_per_kg: float
    arrival_quantity_kg: float | None = None


class MarketPriceResponse(MarketPriceCreate):
    id: int
    recorded_at: datetime

    class Config:
        from_attributes = True