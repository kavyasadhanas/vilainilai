from optimization.inputs import DestinationOption
from ML.digital_twin.harvest_state import HarvestState


# ============================================================
# MARKET OPTIONS
# ============================================================

def build_market_options(
    market_price_list: list[dict]
) -> list[DestinationOption]:
    """
    Convert market price/cost records into DestinationOptions.

    Expected input fields:

        id
        name
        price_per_kg
        transport_cost_per_kg
        commission_per_kg
        expected_loss_per_kg

    expected_loss_per_kg must already be a fraction.

    Example:
        5% loss -> 0.05
    """

    options = []

    for market in market_price_list:

        options.append(
            DestinationOption(
                id=f"market_{market['id']}",

                kind="MARKET",

                price_per_kg=float(
                    market["price_per_kg"]
                ),

                transport_cost_per_kg=float(
                    market.get(
                        "transport_cost_per_kg",
                        0
                    )
                ),

                commission_per_kg=float(
                    market.get(
                        "commission_per_kg",
                        0
                    )
                ),

                expected_loss_pct=float(
                    market.get(
                        "expected_loss_per_kg",
                        0
                    )
                ),

                days_to_realize=0
            )
        )

    return options


# ============================================================
# BUYER OPTIONS
# ============================================================

def build_buyer_options(
    buyer_offers: list[dict]
) -> list[DestinationOption]:
    """
    Convert active buyer/trader offers into
    DestinationOptions.
    """

    options = []

    for offer in buyer_offers:

        quantity = offer.get(
            "quantity_kg"
        )

        options.append(
            DestinationOption(
                id=f"buyer_{offer['id']}",

                kind="BUYER",

                price_per_kg=float(
                    offer["offered_price_per_kg"]
                ),

                capacity_kg=(
                    float(quantity)
                    if quantity is not None
                    else None
                ),

                days_to_realize=0
            )
        )

    return options


# ============================================================
# STORE OPTION
# ============================================================

def build_store_option(
    harvest: HarvestState,
    expected_future_price_per_kg: float,
    days_to_wait: int,

    future_transport_cost_per_kg: float = 0.0,

    future_commission_per_kg: float = 0.0,

    future_expected_loss_pct: float = 0.0

) -> DestinationOption:
    """
    Build the STORE option.

    The stored produce will eventually be sold through
    a market. Therefore the future selling price should
    also account for the future market's:

        - transport cost
        - commission
        - expected loss

    Storage cost is handled separately using:

        storage_cost_per_kg_day × days_to_wait

    Risk adjustment is handled later by risk.py.
    """

    return DestinationOption(

        id="store",

        kind="STORE",

        price_per_kg=float(
            expected_future_price_per_kg
        ),

        transport_cost_per_kg=float(
            future_transport_cost_per_kg
        ),

        commission_per_kg=float(
            future_commission_per_kg
        ),

        expected_loss_pct=float(
            future_expected_loss_pct
        ),

        capacity_kg=float(
            harvest.storage_capacity_kg
        ),

        days_to_realize=int(
            days_to_wait
        ),

        storage_cost_per_kg_day=float(
            harvest.storage_cost_per_kg_day
        )
    )


# ============================================================
# GENERATE ALL DESTINATION OPTIONS
# ============================================================

def generate_all_options(
    harvest: HarvestState,

    market_price_list: list[dict],

    buyer_offers: list[dict],

    expected_future_price_per_kg: float = None,

    days_to_wait: int = 2,

    future_transport_cost_per_kg: float = 0.0,

    future_commission_per_kg: float = 0.0,

    future_expected_loss_pct: float = 0.0

) -> list[DestinationOption]:
    """
    Build all possible destinations for the harvest:

        MARKET
        BUYER
        STORE
    """

    options = []


    # --------------------------------------------------------
    # MARKETS
    # --------------------------------------------------------

    options.extend(
        build_market_options(
            market_price_list
        )
    )


    # --------------------------------------------------------
    # BUYERS
    # --------------------------------------------------------

    options.extend(
        build_buyer_options(
            buyer_offers
        )
    )


    # --------------------------------------------------------
    # STORAGE
    # --------------------------------------------------------

    if (
        expected_future_price_per_kg is not None
        and expected_future_price_per_kg > 0
        and harvest.storage_capacity_kg > 0
    ):

        options.append(
            build_store_option(

                harvest=harvest,

                expected_future_price_per_kg=(
                    expected_future_price_per_kg
                ),

                days_to_wait=days_to_wait,

                future_transport_cost_per_kg=(
                    future_transport_cost_per_kg
                ),

                future_commission_per_kg=(
                    future_commission_per_kg
                ),

                future_expected_loss_pct=(
                    future_expected_loss_pct
                )
            )
        )


    return options


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

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

        {
            "id": 1,
            "name": "Market A",
            "price_per_kg": 26,
            "transport_cost_per_kg": 1,
            "commission_per_kg": 0.5,
            "expected_loss_per_kg": 0.02
        },

        {
            "id": 2,
            "name": "Market B",
            "price_per_kg": 29,
            "transport_cost_per_kg": 3,
            "commission_per_kg": 0.5,
            "expected_loss_per_kg": 0.02
        }

    ]


    buyer_offers = [

        {
            "id": 7,
            "offered_price_per_kg": 24,
            "quantity_kg": 300
        }

    ]


    options = generate_all_options(

        harvest=harvest,

        market_price_list=market_price_list,

        buyer_offers=buyer_offers,

        expected_future_price_per_kg=32,

        days_to_wait=2,

        future_transport_cost_per_kg=1,

        future_commission_per_kg=0.5,

        future_expected_loss_pct=0.02
    )


    for option in options:

        print(option)