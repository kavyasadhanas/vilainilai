from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.core.database import get_db
from database.models import Farmer
from api.schemas.farmer import FarmerCreate, FarmerResponse

router = APIRouter(
    prefix="/farmers",
    tags=["Farmers"]
)


@router.post("/", response_model=FarmerResponse)
def create_farmer(
    farmer_data: FarmerCreate,
    db: Session = Depends(get_db)
):
    farmer = Farmer(
        name=farmer_data.name,
        location=farmer_data.location,
        risk_preference=farmer_data.risk_preference,
        storage_capacity_kg=farmer_data.storage_capacity_kg
    )

    db.add(farmer)
    db.commit()
    db.refresh(farmer)

    return farmer


@router.get("/{farmer_id}", response_model=FarmerResponse)
def get_farmer(
    farmer_id: int,
    db: Session = Depends(get_db)
):
    return db.query(Farmer).filter(
        Farmer.id == farmer_id
    ).first()