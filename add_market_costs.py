from api.core.database import SessionLocal
from database.models import Market, MarketCost


TRANSPORT_COSTS = {
    "Hasthampatti(Uzhavar Sandhai )": 0.50,
    "Sooramangalam(Uzhavar Sandhai )": 0.50,
    "Ammapet(Uzhavar Sandhai )": 0.75,
    "Elampillai(Uzhavar Sandhai )": 1.00,
    "Athur(Uzhavar Sandhai )": 1.00,
    "Attayampatti(Uzhavar Sandhai )": 1.25,
    "Mecheri(Uzhavar Sandhai)": 1.50,
    "Edapadi (Uzhavar Sandhai )": 1.75,
    "Mettur(Uzhavar Sandhai )": 2.00,
    "Thammampatti (Uzhavar Sandhai )": 2.25,
}


db = SessionLocal()

try:
    for market_name, transport_cost in TRANSPORT_COSTS.items():

        market = (
            db.query(Market)
            .filter(
                Market.name == market_name
            )
            .first()
        )

        if not market:
            print(f"NOT FOUND: {market_name}")
            continue

        cost = (
            db.query(MarketCost)
            .filter(
                MarketCost.market_id == market.id
            )
            .first()
        )

        if cost:

            cost.transport_cost_per_kg = (
                transport_cost
            )

            cost.commission_per_kg = (
                0.50
            )

            cost.expected_loss_per_kg = (
                0.30
            )

            print(
                f"UPDATED: {market.name} "
                f"→ ₹{transport_cost:.2f}/kg"
            )

        else:

            cost = MarketCost(

                market_id=market.id,

                transport_cost_per_kg=(
                    transport_cost
                ),

                commission_per_kg=0.50,

                expected_loss_per_kg=0.30
            )

            db.add(cost)

            print(
                f"ADDED: {market.name} "
                f"→ ₹{transport_cost:.2f}/kg"
            )

    db.commit()

finally:
    db.close()