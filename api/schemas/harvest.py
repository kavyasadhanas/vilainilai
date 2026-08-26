from datetime import date

from pydantic import BaseModel


class HarvestCreate(BaseModel):
    farmer_id: int
    crop: str
    quantity_kg: float
    quality: str
    harvest_date: date
    shelf_life_days: int


class HarvestResponse(HarvestCreate):
    id: int

    class Config:
        from_attributes = True