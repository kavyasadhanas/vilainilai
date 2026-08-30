from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db

from api.schemas.recommendation import (
    RecommendationRequest,
    RecommendationResponse
)

from api.services.recommendation_service import (
    generate_market_recommendation
)

from database.models import Harvest


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.post(
    "/market",
    response_model=RecommendationResponse
)
def market_recommendation(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):

    # =========================================================
    # TRY TO FIND THE FARMER'S MATCHING LATEST HARVEST
    # =========================================================

    harvest_query = (
        db.query(Harvest)
        .filter(
            Harvest.crop == request.crop
        )
        .filter(
            Harvest.variety == request.variety
        )
        .filter(
            Harvest.quantity_kg == request.quantity_kg
        )
        .order_by(
            Harvest.id.desc()
        )
    )

    harvest = harvest_query.first()

    harvest_id = (
        harvest.id
        if harvest
        else None
    )

    # =========================================================
    # GENERATE RECOMMENDATION
    # =========================================================

    result = generate_market_recommendation(
        db=db,

        crop=request.crop,

        variety=request.variety,

        quantity_kg=request.quantity_kg,

        harvest_id=harvest_id
    )

    if not result:

        raise HTTPException(
            status_code=404,

            detail=(
                "Unable to generate recommendation."
            )
        )

    return result