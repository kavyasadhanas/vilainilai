from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db

from database.models import (
    Farmer,
    Harvest
)

from api.schemas.farmer import (
    FarmerCreate,
    FarmerResponse
)

from api.schemas.harvest import (
    HarvestResponse
)


router = APIRouter(
    prefix="/farmers",
    tags=["Farmers"]
)


# ============================================================
# CREATE FARMER
# ============================================================

@router.post(
    "/",
    response_model=FarmerResponse
)
def create_farmer(
    farmer_data: FarmerCreate,
    db: Session = Depends(get_db)
):

    farmer = Farmer(
        name=farmer_data.name,
        location=farmer_data.location,
        risk_preference=farmer_data.risk_preference,
        storage_capacity_kg=(
            farmer_data.storage_capacity_kg
        )
    )

    db.add(farmer)

    db.commit()

    db.refresh(farmer)

    return farmer


# ============================================================
# GET FARMER
# ============================================================

@router.get(
    "/{farmer_id}",
    response_model=FarmerResponse
)
def get_farmer(
    farmer_id: int,
    db: Session = Depends(get_db)
):

    farmer = (
        db.query(Farmer)
        .filter(
            Farmer.id == farmer_id
        )
        .first()
    )

    if not farmer:

        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    return farmer


# ============================================================
# GET ALL HARVESTS FOR FARMER
# ============================================================

@router.get(
    "/{farmer_id}/harvests",
    response_model=list[HarvestResponse]
)
def get_farmer_harvests(
    farmer_id: int,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Check farmer exists
    # --------------------------------------------------------

    farmer = (
        db.query(Farmer)
        .filter(
            Farmer.id == farmer_id
        )
        .first()
    )

    if not farmer:

        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    # --------------------------------------------------------
    # Get all harvests
    # --------------------------------------------------------

    harvests = (
        db.query(Harvest)
        .filter(
            Harvest.farmer_id
            == farmer_id
        )
        .order_by(
            Harvest.harvest_date.desc(),
            Harvest.id.desc()
        )
        .all()
    )

    return harvests

# ============================================================
# UPDATE FARMER SETTINGS
# ============================================================

@router.patch(
    "/{farmer_id}",
    response_model=FarmerResponse
)
def update_farmer(
    farmer_id: int,
    farmer_data: FarmerCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # Find farmer
    # --------------------------------------------------------

    farmer = (
        db.query(Farmer)
        .filter(
            Farmer.id == farmer_id
        )
        .first()
    )

    if not farmer:

        raise HTTPException(
            status_code=404,
            detail="Farmer not found"
        )

    # --------------------------------------------------------
    # Update fields
    # --------------------------------------------------------

    farmer.name = farmer_data.name

    farmer.location = farmer_data.location

    farmer.risk_preference = (
        farmer_data.risk_preference
    )

    farmer.storage_capacity_kg = (
        farmer_data.storage_capacity_kg
    )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    db.commit()

    db.refresh(
        farmer
    )

    return farmer