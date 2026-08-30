from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db

from api.services.optimization_service import (
    get_farmer_optimal_strategy
)

from api.services.fairdeal_service import (
    get_farmer_fairdeal
)

from database.models import Harvest


router = APIRouter(
    prefix="/fairdeal",
    tags=["FairDeal"]
)


# ============================================================
# GET FAIRDEAL ANALYSIS
# ============================================================

@router.get("/{farmer_id}")
def get_fairdeal_analysis(
    farmer_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate FairDeal analysis for the farmer's
    latest harvest.
    """

    # --------------------------------------------------------
    # Get latest harvest
    # --------------------------------------------------------

    harvest = (
        db.query(Harvest)
        .filter(
            Harvest.farmer_id == farmer_id
        )
        .order_by(
            Harvest.id.desc()
        )
        .first()
    )

    if not harvest:

        raise HTTPException(
            status_code=404,
            detail="No harvest found for this farmer."
        )

    # --------------------------------------------------------
    # Get optimization
    # --------------------------------------------------------

    optimization_result = (
        get_farmer_optimal_strategy(
            db=db,
            farmer_id=farmer_id
        )
    )

    if not optimization_result:

        raise HTTPException(
            status_code=404,
            detail=(
                "Unable to generate optimization "
                "result."
            )
        )

    # --------------------------------------------------------
    # Get FairDeal
    # --------------------------------------------------------

    fairdeal_result = (
        get_farmer_fairdeal(
            db=db,
            farmer_id=farmer_id,
            optimization_result=optimization_result
        )
    )

    if not fairdeal_result:

        raise HTTPException(
            status_code=404,
            detail=(
                "Unable to generate FairDeal analysis."
            )
        )

    # --------------------------------------------------------
    # Return latest harvest ID
    # --------------------------------------------------------

    return {

        "farmer_id":
            farmer_id,

        "harvest_id":
            harvest.id,

        "crop":
            harvest.crop,

        "variety":
            harvest.variety,

        "quantity_kg":
            harvest.quantity_kg,

        "optimization":
            optimization_result,

        "fairdeal":
            fairdeal_result
    }