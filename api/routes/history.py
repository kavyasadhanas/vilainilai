import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db

from database.models import (
    Farmer,
    Harvest,
    Recommendation,
)


router = APIRouter(
    prefix="/history",
    tags=["History"]
)


@router.get("/{farmer_id}")
def get_farmer_history(
    farmer_id: int,
    db: Session = Depends(get_db)
):

    # ========================================================
    # CHECK FARMER
    # ========================================================

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

    # ========================================================
    # GET HARVESTS
    # ========================================================

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

    history = []

    for harvest in harvests:

        # ====================================================
        # GET LATEST RECOMMENDATION FOR THIS HARVEST
        # ====================================================

        recommendation = (
            db.query(Recommendation)
            .filter(
                Recommendation.harvest_id
                == harvest.id
            )
            .order_by(
                Recommendation.created_at.desc()
            )
            .first()
        )

        # ====================================================
        # DESERIALIZE SNAPSHOTS
        # ====================================================

        optimization_result = None

        fairdeal_result = None

        if recommendation:

            if recommendation.optimization_result:

                try:

                    optimization_result = json.loads(
                        recommendation.optimization_result
                    )

                except (
                    json.JSONDecodeError,
                    TypeError
                ):

                    optimization_result = None

            if recommendation.fairdeal_result:

                try:

                    fairdeal_result = json.loads(
                        recommendation.fairdeal_result
                    )

                except (
                    json.JSONDecodeError,
                    TypeError
                ):

                    fairdeal_result = None

        # ====================================================
        # BUILD HISTORY RECORD
        # ====================================================

        history.append({

            # ------------------------------------------------
            # HARVEST
            # ------------------------------------------------

            "harvest_id":
                harvest.id,

            "crop":
                harvest.crop,

            "variety":
                harvest.variety,

            "quantity_kg":
                harvest.quantity_kg,

            "quality":
                harvest.quality,

            "harvest_date":
                harvest.harvest_date,

            "shelf_life_days":
                harvest.shelf_life_days,

            # ------------------------------------------------
            # RECOMMENDATION
            # ------------------------------------------------

            "recommendation_id":
                (
                    recommendation.id
                    if recommendation
                    else None
                ),

            "action":
                (
                    recommendation.action
                    if recommendation
                    else None
                ),

            "destination":
                (
                    recommendation.destination
                    if recommendation
                    else None
                ),

            "recommended_quantity_kg":
                (
                    recommendation.quantity_kg
                    if recommendation
                    else None
                ),

            "expected_return":
                (
                    recommendation.expected_return
                    if recommendation
                    else None
                ),

            # ------------------------------------------------
            # ML SNAPSHOT
            # ------------------------------------------------

            "predicted_price_per_kg":
                (
                    recommendation.predicted_price_per_kg
                    if recommendation
                    else None
                ),

            "net_price_per_kg":
                (
                    recommendation.net_price_per_kg
                    if recommendation
                    else None
                ),

            # ------------------------------------------------
            # FAIRDEAL SNAPSHOT
            # ------------------------------------------------

            "risk_preference":
                (
                    recommendation.risk_preference
                    if recommendation
                    else None
                ),

            "reservation_price":
                (
                    recommendation.reservation_price
                    if recommendation
                    else None
                ),

            # ------------------------------------------------
            # OPTIMIZATION
            # ------------------------------------------------

            "optimization":
                optimization_result,

            # ------------------------------------------------
            # FAIRDEAL
            # ------------------------------------------------

            "fairdeal":
                fairdeal_result,

            # ------------------------------------------------
            # EXPLANATION
            # ------------------------------------------------

            "explanation":
                (
                    recommendation.explanation
                    if recommendation
                    else None
                ),

            "created_at":
                (
                    recommendation.created_at
                    if recommendation
                    else None
                ),
        })

    return {

        "farmer_id":
            farmer_id,

        "farmer_name":
            farmer.name,

        "history":
            history
    }