from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db
from database.models import Harvest

from api.schemas.harvest import (
    HarvestCreate,
    HarvestResponse
)


router = APIRouter(
    prefix="/harvests",
    tags=["Harvests"]
)


# ============================================================
# CREATE HARVEST
# ============================================================

@router.post(
    "/",
    response_model=HarvestResponse
)
def create_harvest(
    harvest_data: HarvestCreate,
    db: Session = Depends(get_db)
):

    harvest = Harvest(
        farmer_id=harvest_data.farmer_id,
        crop=harvest_data.crop,
        variety=harvest_data.variety,
        quantity_kg=harvest_data.quantity_kg,
        quality=harvest_data.quality,
        harvest_date=harvest_data.harvest_date,
        shelf_life_days=harvest_data.shelf_life_days
    )

    db.add(harvest)

    db.commit()

    db.refresh(harvest)

    return harvest


# ============================================================
# GET HARVEST
# ============================================================

@router.get(
    "/{harvest_id}",
    response_model=HarvestResponse
)
def get_harvest(
    harvest_id: int,
    db: Session = Depends(get_db)
):

    harvest = (
        db.query(Harvest)
        .filter(
            Harvest.id == harvest_id
        )
        .first()
    )

    if not harvest:
        raise HTTPException(
            status_code=404,
            detail="Harvest not found"
        )

    return harvest