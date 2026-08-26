from sqlalchemy.orm import Session

from database.models import Harvest
from api.services.recommendation_service import (
    generate_market_recommendation
)


def get_farmer_dashboard(
    db: Session,
    farmer_id: int
):
    # Get latest harvest
    harvest = (
        db.query(Harvest)
        .filter(Harvest.farmer_id == farmer_id)
        .order_by(Harvest.id.desc())
        .first()
    )

    # No harvest
    if not harvest:
        return {
            "farmer_id": farmer_id,
            "harvest": None,
            "recommendation": None
        }

    # Harvest information
    harvest_data = {
        "id": harvest.id,
        "crop": harvest.crop,
        "quantity_kg": harvest.quantity_kg,
        "quality": harvest.quality,
        "harvest_date": harvest.harvest_date,
        "shelf_life_days": harvest.shelf_life_days
    }

    # Generate recommendation
    recommendation = generate_market_recommendation(
        db=db,
        crop=harvest.crop,
        quantity_kg=harvest.quantity_kg
    )

    return {
        "farmer_id": farmer_id,
        "harvest": harvest_data,
        "recommendation": recommendation
    }