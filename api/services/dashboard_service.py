from sqlalchemy.orm import Session

from database.models import Harvest

from api.services.recommendation_service import (
    generate_market_recommendation,
    save_decision_snapshot
)

from api.services.optimization_service import (
    get_farmer_optimal_strategy
)

from api.services.fairdeal_service import (
    get_farmer_fairdeal
)


def get_farmer_dashboard(
    db: Session,
    farmer_id: int
):

    # =====================================================
    # GET LATEST HARVEST
    # =====================================================

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

    # =====================================================
    # NO HARVEST
    # =====================================================

    if not harvest:

        return {
            "farmer_id": farmer_id,
            "harvest": None,
            "recommendation": None,
            "optimization": None,
            "fairdeal": None
        }

    # =====================================================
    # HARVEST INFORMATION
    # =====================================================

    harvest_data = {

        "id":
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
            harvest.shelf_life_days
    }

    # =====================================================
    # MARKET RECOMMENDATION
    # =====================================================

    recommendation = (
        generate_market_recommendation(

            db=db,

            crop=harvest.crop,

            variety=harvest.variety,

            quantity_kg=harvest.quantity_kg,

            harvest_id=harvest.id
        )
    )

    # =====================================================
    # OPTIMAL STRATEGY
    # =====================================================

    optimization = None

    try:

        optimization = (
            get_farmer_optimal_strategy(

                db=db,

                farmer_id=farmer_id
            )
        )

    except Exception as err:

        print(
            f"Optimization error: {err}"
        )

    # =====================================================
    # FAIRDEAL
    # =====================================================

    fairdeal = None

    if optimization:

        try:

            fairdeal = (
                get_farmer_fairdeal(

                    db=db,

                    farmer_id=farmer_id,

                    optimization_result=optimization
                )
            )

        except Exception as err:

            print(
                f"FairDeal error: {err}"
            )

    # =====================================================
    # SAVE COMPLETE DECISION SNAPSHOT
    # =====================================================

    if recommendation:

        try:

            save_decision_snapshot(

                db=db,

                harvest_id=harvest.id,

                recommendation_result=
                    recommendation,

                optimization_result=
                    optimization,

                fairdeal_result=
                    fairdeal
            )

        except Exception as err:

            print(
                f"Decision history error: {err}"
            )

    # =====================================================
    # FINAL DASHBOARD RESPONSE
    # =====================================================

    return {

        "farmer_id":
            farmer_id,

        "harvest":
            harvest_data,

        "recommendation":
            recommendation,

        "optimization":
            optimization,

        "fairdeal":
            fairdeal
    }