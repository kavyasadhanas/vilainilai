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

    result = generate_market_recommendation(
        db=db,
        crop=request.crop,
        quantity_kg=request.quantity_kg,
        market_costs=request.market_costs
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Unable to generate recommendation."
        )

    return result