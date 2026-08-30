from datetime import datetime

from pydantic import BaseModel


# ============================================================
# BUYER
# ============================================================

class BuyerCreate(BaseModel):
    name: str
    buyer_type: str | None = None
    location: str | None = None


class BuyerResponse(BaseModel):
    id: int
    name: str
    buyer_type: str | None = None
    location: str | None = None

    class Config:
        from_attributes = True


# ============================================================
# BUYER OFFER
# ============================================================

class BuyerOfferCreate(BaseModel):
    buyer_id: int
    harvest_id: int
    offered_price_per_kg: float
    quantity_kg: float


class BuyerOfferResponse(BaseModel):
    id: int
    buyer_id: int
    harvest_id: int

    offered_price_per_kg: float
    quantity_kg: float

    status: str

    counteroffer_per_kg: float | None = None

    created_at: datetime

    class Config:
        from_attributes = True