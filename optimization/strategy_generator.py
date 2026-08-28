from optimization.inputs import DestinationOption
from ML.digital_twin.harvest_state import HarvestState


def build_market_options(market_price_list: list[dict]) -> list[DestinationOption]:
    """
    Convert a list of market price/cost records into DestinationOptions.

    Each dict in market_price_list is expected to have:
      id, name, price_per_kg, transport_cost_per_kg,
      commission_per_kg, expected_loss_per_kg
    (these map directly to the Market + MarketPrice + MarketCost
    tables that Member 1 built)
    """
    options = []

    for market in market_price_list:
        options.append(
            DestinationOption(
                id=f"market_{market['id']}",
                kind="MARKET",
                price_per_kg=market["price_per_kg"],
                transport_cost_per_kg=market.get("transport_cost_per_kg", 0),
                commission_per_kg=market.get("commission_per_kg", 0),
                expected_loss_pct=market.get("expected_loss_per_kg", 0),
                days_to_realize=0  # selling at a market is treated as "now"
            )
        )

    return options


def build_buyer_options(buyer_offers: list[dict]) -> list[DestinationOption]:
    """
    Convert live buyer/trader offers into DestinationOptions.

    Each dict is expected to have:
      id, offered_price_per_kg, quantity_kg
    (maps to the BuyerOffer table)
    """
    options = []

    for offer in buyer_offers:
        options.append(
            DestinationOption(
                id=f"buyer_{offer['id']}",
                kind="BUYER",
                price_per_kg=offer["offered_price_per_kg"],
                capacity_kg=offer.get("quantity_kg"),
                days_to_realize=0
            )
        )

    return options


def build_store_option(harvest: HarvestState, expected_future_price_per_kg: float, days_to_wait: int) -> DestinationOption:
    """
    Build the STORE option from the farmer's actual harvest state.

    expected_future_price_per_kg should come from Member 2's
    predict_price() once that's wired up. For now it can be passed
    in directly (e.g. today's price + a manual estimate) for testing.
    """
    return DestinationOption(
        id="store",
        kind="STORE",
        price_per_kg=expected_future_price_per_kg,
        capacity_kg=harvest.storage_capacity_kg,
        days_to_realize=days_to_wait,
        storage_cost_per_kg_day=harvest.storage_cost_per_kg_day
    )


def generate_all_options(
    harvest: HarvestState,
    market_price_list: list[dict],
    buyer_offers: list[dict],
    expected_future_price_per_kg: float = None,
    days_to_wait: int = 2
) -> list[DestinationOption]:
    """
    Build the full list of destination options for one harvest:
    all markets, all live buyer offers, and (if a future price
    estimate is given) a storage option.
    """
    options = []
    options.extend(build_market_options(market_price_list))
    options.extend(build_buyer_options(buyer_offers))

    if expected_future_price_per_kg is not None:
        options.append(
            build_store_option(harvest, expected_future_price_per_kg, days_to_wait)
        )

    return options


if __name__ == "__main__":
    # Manual test using realistic-shaped data
    harvest = HarvestState(
        crop="Tomato",
        variety="Local",
        quantity_kg=500,
        quality="Grade A",
        harvest_date="2026-08-25",
        remaining_shelf_life_days=4,
        storage_capacity_kg=200,
        storage_cost_per_kg_day=0.3
    )

    market_price_list = [
        {"id": 1, "name": "Market A", "price_per_kg": 26, "transport_cost_per_kg": 1, "commission_per_kg": 0.5, "expected_loss_per_kg": 0.02},
        {"id": 2, "name": "Market B", "price_per_kg": 29, "transport_cost_per_kg": 3, "commission_per_kg": 0.5, "expected_loss_per_kg": 0.02},
    ]

    buyer_offers = [
        {"id": 7, "offered_price_per_kg": 24, "quantity_kg": 300},
    ]

    options = generate_all_options(
        harvest=harvest,
        market_price_list=market_price_list,
        buyer_offers=buyer_offers,
        expected_future_price_per_kg=32,
        days_to_wait=2
    )

    for opt in options:
        print(opt)