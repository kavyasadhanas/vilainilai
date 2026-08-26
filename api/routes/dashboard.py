from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.services.dashboard_service import (
    get_farmer_dashboard
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/{farmer_id}")
def dashboard(
    farmer_id: int,
    db: Session = Depends(get_db)
):

    return get_farmer_dashboard(
        db=db,
        farmer_id=farmer_id
    )