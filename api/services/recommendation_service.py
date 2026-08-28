from sqlalchemy.orm import Session

from api.services.market_service import compare_markets
from database.models import MarketCost


def generate_market_recommendation(
    db: Session,
    crop: str,
    variety: str,
    quantity_kg: float
):

    # -----------------------------------------------------
    # Get all market costs
    # -----------------------------------------------------

    market_costs = (
        db.query(MarketCost)
        .all()
    )

    # -----------------------------------------------------
    # No market cost data
    # -----------------------------------------------------

    if not market_costs:
        return None

    # -----------------------------------------------------
    # Compare all markets using ML predicted prices
    # -----------------------------------------------------

    result = compare_markets(
        db=db,
        crop=crop,
        variety=variety,
        quantity_kg=quantity_kg,
        market_costs=market_costs
    )

    # -----------------------------------------------------
    # No valid market result
    # -----------------------------------------------------

    if not result:
        return None

    markets = result["markets"]

    # -----------------------------------------------------
    # Sort by expected return
    # Highest first
    # -----------------------------------------------------

    markets = sorted(
        markets,
        key=lambda x: x["expected_return"],
        reverse=True
    )

    # -----------------------------------------------------
    # Best market
    # -----------------------------------------------------

    best = markets[0]

    # -----------------------------------------------------
    # Advantage over second-best
    # -----------------------------------------------------

    if len(markets) > 1:

        second_best = markets[1]

        advantage = round(
            best["expected_return"]
            - second_best["expected_return"],
            2
        )

    else:

        advantage = 0.0

    # -----------------------------------------------------
    # Explanation
    # -----------------------------------------------------

    reason = (
        f'{best["market_name"]} provides the highest '
        f'expected net return based on the predicted '
        f'market price after considering transportation, '
        f'commission and expected loss.'
    )

    # -----------------------------------------------------
    # Final recommendation
    # -----------------------------------------------------

    return {

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