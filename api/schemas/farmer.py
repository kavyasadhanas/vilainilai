from pydantic import BaseModel


class FarmerCreate(BaseModel):
    name: str
    location: str
    risk_preference: str = "moderate"
    storage_capacity_kg: float = 0


class FarmerResponse(FarmerCreate):
    id: int

    class Config:
        from_attributes = True