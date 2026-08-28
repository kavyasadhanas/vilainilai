from sqlalchemy.orm import Session

from database.models import Market
from api.services.ml_service import predict_market_price


# ============================================================
# DATABASE MARKET → ML DATASET MARKET MAPPING
# ============================================================

ML_MARKET_MAPPING = {
    "Oddanchatram Market": "Dindigul(Uzhavar Sandhai )",
    "Madurai Market": "Melur(Uzhavar Sandhai )",
}


# ============================================================
# COMPARE MARKETS
# ============================================================

def compare_markets(
    db: Session,
    crop: str,
    variety: str,
    quantity_kg: float,
    market_costs,
    prediction_date=None
):
    results = []

    # --------------------------------------------------------
    # Compare every configured market
    # --------------------------------------------------------

    for cost in market_costs:

        # ----------------------------------------------------
        # Get market
        # ----------------------------------------------------

        market = (
            db.query(Market)
            .filter(
                Market.id == cost.market_id
            )
            .first()
        )

        if not market:
            continue

        # ----------------------------------------------------
        # Find corresponding ML market
        # ----------------------------------------------------

        ml_market = ML_MARKET_MAPPING.get(
            market.name
        )

        if not ml_market:
            # No ML mapping available for this market
            continue

        # ----------------------------------------------------
        # Predict future market price using XGBoost
        # ----------------------------------------------------

        try:

            predicted_price = predict_market_price(
                market=ml_market,
                district=market.district,
                variety=variety,
                arrival_quantity=quantity_kg,
                prediction_date=prediction_date
            )

        except ValueError:

            # No historical data available
            # for this market/district combination
            continue

        # ----------------------------------------------------
        # Calculate net predicted price
        #
        # Net price =
        # predicted market price
        # - transportation cost
        # - commission
        # - expected loss
        # ----------------------------------------------------

        net_price = (
            predicted_price
            - cost.transport_cost_per_kg
            - cost.commission_per_kg
            - cost.expected_loss_per_kg
        )

        # ----------------------------------------------------
        # Calculate expected return
        # ----------------------------------------------------

        expected_return = (
            net_price * quantity_kg
        )

        # ----------------------------------------------------
        # Store market result
        # ----------------------------------------------------

        results.append({

            "market_id":
                market.id,

            "market_name":
                market.name,

            "district":
                market.district,

            "ml_market":
                ml_market,

            "predicted_price_per_kg":
                round(predicted_price, 2),

            "transport_cost_per_kg":
                cost.transport_cost_per_kg,

            "commission_per_kg":
                cost.commission_per_kg,

            "expected_loss_per_kg":
                cost.expected_loss_per_kg,

            "net_price_per_kg":
                round(net_price, 2),

            "expected_return":
                round(expected_return, 2)
        })

    # --------------------------------------------------------
    # No valid market available
    # --------------------------------------------------------

    if not results:
        return None

    # --------------------------------------------------------
    # Find market with highest expected return
    # --------------------------------------------------------

    best_market = max(
        results,
        key=lambda x: x["expected_return"]
    )

    # --------------------------------------------------------
    # Final comparison result
    # --------------------------------------------------------

    return {

        "crop":
            crop,

        "variety":
            variety,

        "quantity_kg":
            quantity_kg,

        "markets":
            results,

        "best_market_id":
            best_market["market_id"],

        "best_market_name":
            best_market["market_name"],

        "best_expected_return":
            best_market["expected_return"]
    }