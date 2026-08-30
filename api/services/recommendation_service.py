import json

from sqlalchemy.orm import Session

from api.services.market_service import compare_markets

from database.models import (
    MarketCost,
    Recommendation,
)


# ============================================================
# GENERATE MARKET RECOMMENDATION
# ============================================================

def generate_market_recommendation(
    db: Session,
    crop: str,
    variety: str,
    quantity_kg: float,
    harvest_id: int | None = None
):

    # ---------------------------------------------------------
    # Get market costs
    # ---------------------------------------------------------

    market_costs = (
        db.query(MarketCost)
        .all()
    )

    if not market_costs:
        return None

    # ---------------------------------------------------------
    # Compare markets
    # ---------------------------------------------------------

    result = compare_markets(
        db=db,
        crop=crop,
        variety=variety,
        quantity_kg=quantity_kg,
        market_costs=market_costs
    )

    if not result:
        return None

    markets = result["markets"]

    # ---------------------------------------------------------
    # Sort by expected return
    # ---------------------------------------------------------

    markets = sorted(
        markets,
        key=lambda x: x["expected_return"],
        reverse=True
    )

    best = markets[0]

    # ---------------------------------------------------------
    # Advantage over second best
    # ---------------------------------------------------------

    if len(markets) > 1:

        second_best = markets[1]

        advantage = round(
            best["expected_return"]
            - second_best["expected_return"],
            2
        )

    else:

        advantage = 0.0

    # ---------------------------------------------------------
    # Explanation
    # ---------------------------------------------------------

    reason = (
        f'{best["market_name"]} provides the highest '
        f'expected net return based on the predicted '
        f'market price after considering transportation, '
        f'commission and expected loss.'
    )

    # ---------------------------------------------------------
    # Result returned to API
    # ---------------------------------------------------------

    recommendation_data = {

        "crop":
            crop,

        "variety":
            variety,

        "quantity_kg":
            quantity_kg,

        "recommended_market_id":
            best["market_id"],

        "recommended_market_name":
            best["market_name"],

        "predicted_price_per_kg":
            best["predicted_price_per_kg"],

        "net_price_per_kg":
            best["net_price_per_kg"],

        "expected_return":
            best["expected_return"],

        "advantage_over_next_best":
            advantage,

        "recommendation":
            f'Sell at {best["market_name"]}',

        "reason":
            reason,

        "alternatives":
            markets
    }

    # ---------------------------------------------------------
    # Save basic recommendation when harvest is known
    # ---------------------------------------------------------

    if harvest_id is not None:

        existing = (
            db.query(Recommendation)
            .filter(
                Recommendation.harvest_id
                == harvest_id
            )
            .first()
        )

        if existing:

            existing.action = "SELL"

            existing.destination = (
                best["market_name"]
            )

            existing.quantity_kg = (
                quantity_kg
            )

            existing.expected_return = (
                best["expected_return"]
            )

            existing.predicted_price_per_kg = (
                best["predicted_price_per_kg"]
            )

            existing.net_price_per_kg = (
                best["net_price_per_kg"]
            )

            existing.explanation = reason

        else:

            recommendation = Recommendation(

                harvest_id=harvest_id,

                action="SELL",

                destination=(
                    best["market_name"]
                ),

                quantity_kg=quantity_kg,

                expected_return=(
                    best["expected_return"]
                ),

                predicted_price_per_kg=(
                    best["predicted_price_per_kg"]
                ),

                net_price_per_kg=(
                    best["net_price_per_kg"]
                ),

                explanation=reason
            )

            db.add(
                recommendation
            )

        db.commit()

    return recommendation_data


# ============================================================
# SAVE COMPLETE DECISION SNAPSHOT
# ============================================================

def save_decision_snapshot(
    db: Session,
    harvest_id: int,
    recommendation_result: dict,
    optimization_result: dict | None = None,
    fairdeal_result: dict | None = None
):
    """
    Persist the complete ML + optimization + FairDeal
    decision snapshot for a harvest.
    """

    record = (
        db.query(Recommendation)
        .filter(
            Recommendation.harvest_id
            == harvest_id
        )
        .first()
    )

    # ---------------------------------------------------------
    # Basic recommendation information
    # ---------------------------------------------------------

    if record is None:

        record = Recommendation(
            harvest_id=harvest_id
        )

        db.add(record)

    record.action = "SELL"

    record.destination = (
        recommendation_result.get(
            "recommended_market_name"
        )
    )

    record.quantity_kg = (
        recommendation_result.get(
            "quantity_kg"
        )
    )

    record.expected_return = (
        recommendation_result.get(
            "expected_return"
        )
    )

    # ---------------------------------------------------------
    # ML values
    # ---------------------------------------------------------

    record.predicted_price_per_kg = (
        recommendation_result.get(
            "predicted_price_per_kg"
        )
    )

    record.net_price_per_kg = (
        recommendation_result.get(
            "net_price_per_kg"
        )
    )

    # ---------------------------------------------------------
    # FairDeal values
    # ---------------------------------------------------------

    if fairdeal_result:

        record.risk_preference = (
            fairdeal_result.get(
                "risk_preference"
            )
        )

        record.reservation_price = (
            fairdeal_result.get(
                "reservation_price"
            )
        )

        record.fairdeal_result = json.dumps(
            fairdeal_result,
            default=str
        )

    # ---------------------------------------------------------
    # Optimization values
    # ---------------------------------------------------------

    if optimization_result:

        record.optimization_result = json.dumps(
            optimization_result,
            default=str
        )

        # Use actual optimizer decision when possible

        active_details = [
            detail
            for detail in optimization_result.get(
                "details",
                []
            )
            if detail.get(
                "allocated_kg",
                0
            ) > 0
        ]

        if active_details:

            # Determine the primary destination

            best_detail = max(
                active_details,
                key=lambda detail:
                    detail.get(
                        "allocated_kg",
                        0
                    )
            )

            record.action = (
                "STORE"
                if best_detail.get("kind")
                == "STORE"
                else "SELL"
            )

    # ---------------------------------------------------------
    # Explanation
    # ---------------------------------------------------------

    record.explanation = (
        recommendation_result.get(
            "reason"
        )
    )

    db.commit()

    db.refresh(record)

    return record