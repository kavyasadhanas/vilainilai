from sqlalchemy.orm import Session

from database.models import Market
from api.services.ml_service import (
    predict_market_price,
    historical_features,
)


# ============================================================
# DATABASE MARKET → ML DATASET MARKET
# ============================================================
#
# Keep explicit aliases only where the application's display
# name differs from Member 1's dataset market name.
#
# All other markets are matched automatically against the
# processed ML dataset.
# ============================================================

ML_MARKET_MAPPING = {

    # Existing application aliases
    "Oddanchatram Market":
        "Dindigul(Uzhavar Sandhai )",

    "Madurai Market":
        "Melur(Uzhavar Sandhai )",
}


# ============================================================
# MARKET NAME NORMALIZATION
# ============================================================

def normalize_market_name(
    name: str | None
) -> str:

    if not name:
        return ""

    return " ".join(
        str(name)
        .strip()
        .split()
    )


# ============================================================
# BUILD DATASET MARKET LOOKUP
# ============================================================

def build_dataset_market_lookup() -> dict[str, str]:
    """
    Build:

        normalized dataset name -> original dataset name

    from Member 1's processed forecasting dataset.
    """

    lookup = {}

    if historical_features.empty:
        return lookup

    dataset_markets = (
        historical_features["Market"]
        .dropna()
        .astype(str)
        .unique()
    )

    for dataset_market in dataset_markets:

        normalized = normalize_market_name(
            dataset_market
        )

        if normalized:

            lookup[
                normalized
            ] = dataset_market

    return lookup


DATASET_MARKET_LOOKUP = (
    build_dataset_market_lookup()
)


# ============================================================
# RESOLVE ML MARKET
# ============================================================

def get_ml_market_name(
    market_name: str
) -> str | None:
    """
    Resolve a database market to the exact market name used
    by Member 1's ML dataset.

    Priority:
        1. Explicit alias
        2. Exact normalized dataset match
        3. None
    """

    if not market_name:
        return None


    # --------------------------------------------------------
    # 1. Explicit alias
    # --------------------------------------------------------

    explicit_mapping = (
        ML_MARKET_MAPPING.get(
            market_name
        )
    )

    if explicit_mapping:

        return explicit_mapping


    # --------------------------------------------------------
    # 2. Automatic exact dataset match
    # --------------------------------------------------------

    normalized_name = (
        normalize_market_name(
            market_name
        )
    )

    return (
        DATASET_MARKET_LOOKUP.get(
            normalized_name
        )
    )


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
    """
    Compare all database markets that have:

        - a MarketCost record
        - a matching market in Member 1's dataset
        - a valid ML price prediction

    This means the recommendation endpoint uses the same
    multi-market ML universe as the optimizer.
    """

    results = []


    # --------------------------------------------------------
    # Compare every configured market cost
    # --------------------------------------------------------

    for cost in market_costs:

        # ----------------------------------------------------
        # Get market
        # ----------------------------------------------------

        market = (
            db.query(Market)
            .filter(
                Market.id
                == cost.market_id
            )
            .first()
        )

        if not market:
            continue


        # ----------------------------------------------------
        # Resolve corresponding ML market
        # ----------------------------------------------------

        ml_market = (
            get_ml_market_name(
                market.name
            )
        )

        if not ml_market:

            print(
                f"[MARKET SKIP] "
                f"{market.name}: "
                f"not found in ML dataset."
            )

            continue


        # ----------------------------------------------------
        # Predict market price
        # ----------------------------------------------------

        try:

            predicted_price = (
                predict_market_price(

                    market=ml_market,

                    district=(
                        market.district
                        or ""
                    ),

                    variety=(
                        variety
                        or "Deshi"
                    ),

                    arrival_quantity=(
                        quantity_kg
                    ),

                    prediction_date=(
                        prediction_date
                    )
                )
            )

        except (
            ValueError,
            KeyError,
            TypeError
        ) as exc:

            print(
                f"[MARKET SKIP] "
                f"{market.name}: "
                f"prediction failed: {exc}"
            )

            continue


        # ----------------------------------------------------
        # Validate predicted price
        # ----------------------------------------------------

        try:

            predicted_price = float(
                predicted_price
            )

        except (
            TypeError,
            ValueError
        ):

            print(
                f"[MARKET SKIP] "
                f"{market.name}: "
                f"invalid predicted price."
            )

            continue


        if predicted_price <= 0:

            print(
                f"[MARKET SKIP] "
                f"{market.name}: "
                f"predicted price <= 0."
            )

            continue


        # ----------------------------------------------------
        # Cost values
        # ----------------------------------------------------

        transport_cost = float(
            cost.transport_cost_per_kg
            or 0
        )

        commission = float(
            cost.commission_per_kg
            or 0
        )

        expected_loss = float(
            cost.expected_loss_per_kg
            or 0
        )


        # ----------------------------------------------------
        # NET PRICE
        # ----------------------------------------------------
        #
        # Net price =
        # predicted price
        # - transport
        # - commission
        # - expected loss
        #
        # ----------------------------------------------------

        net_price = (
            predicted_price
            - transport_cost
            - commission
            - expected_loss
        )


        # ----------------------------------------------------
        # EXPECTED RETURN
        # ----------------------------------------------------

        expected_return = (
            net_price
            * float(
                quantity_kg
            )
        )


        # ----------------------------------------------------
        # ADD RESULT
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
                round(
                    predicted_price,
                    2
                ),

            "transport_cost_per_kg":
                round(
                    transport_cost,
                    2
                ),

            "commission_per_kg":
                round(
                    commission,
                    2
                ),

            "expected_loss_per_kg":
                round(
                    expected_loss,
                    2
                ),

            "net_price_per_kg":
                round(
                    net_price,
                    2
                ),

            "expected_return":
                round(
                    expected_return,
                    2
                )
        })


    # --------------------------------------------------------
    # No valid markets
    # --------------------------------------------------------

    if not results:

        return None


    # --------------------------------------------------------
    # BEST MARKET
    # --------------------------------------------------------

    best_market = max(
        results,
        key=lambda x:
            x["expected_return"]
    )


    # --------------------------------------------------------
    # SORT FOR FRONTEND
    # --------------------------------------------------------

    results.sort(
        key=lambda x:
            x["expected_return"],
        reverse=True
    )


    # --------------------------------------------------------
    # FINAL RESULT
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
            best_market[
                "market_id"
            ],

        "best_market_name":
            best_market[
                "market_name"
            ],

        "best_expected_return":
            best_market[
                "expected_return"
            ]
    }