from sqlalchemy.orm import Session

from database.models import Market, MarketPrice


def compare_markets(
    db: Session,
    crop: str,
    quantity_kg: float,
    market_costs
):
    results = []

    for cost in market_costs:

        # -------------------------------------------------
        # Get market
        # -------------------------------------------------

        market = (
            db.query(Market)
            .filter(
                Market.id == cost.market_id
            )
            .first()
        )

        if not market:
            continue

        # -------------------------------------------------
        # Get latest price for this crop
        # -------------------------------------------------

        latest_price = (
            db.query(MarketPrice)
            .filter(
                MarketPrice.market_id == cost.market_id,
                MarketPrice.crop == crop
            )
            .order_by(
                MarketPrice.recorded_at.desc()
            )
            .first()
        )

        if not latest_price:
            continue

        market_price = latest_price.price_per_kg

        # -------------------------------------------------
        # Calculate net price
        # -------------------------------------------------

        net_price = (
            market_price
            - cost.transport_cost_per_kg
            - cost.commission_per_kg
            - cost.expected_loss_per_kg
        )

        # -------------------------------------------------
        # Calculate expected return
        # -------------------------------------------------

        expected_return = (
            net_price * quantity_kg
        )

        results.append({
            "market_id": market.id,

            "market_name": market.name,

            "district": market.district,

            "market_price_per_kg": market_price,

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

    # -----------------------------------------------------
    # No market available
    # -----------------------------------------------------

    if not results:
        return None

    # -----------------------------------------------------
    # Find best market
    # -----------------------------------------------------

    best_market = max(
        results,
        key=lambda x: x["expected_return"]
    )

    return {
        "crop": crop,

        "quantity_kg": quantity_kg,

        "markets": results,

        "best_market_id":
            best_market["market_id"],

        "best_market_name":
            best_market["market_name"],

        "best_expected_return":
            best_market["expected_return"]
    }