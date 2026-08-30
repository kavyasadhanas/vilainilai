from datetime import timedelta

from sqlalchemy.orm import Session

from database.models import (
    Farmer,
    Harvest,
    Market,
    MarketCost,
    BuyerOffer,
)

from ML.digital_twin.farmer_state import FarmerState
from ML.digital_twin.harvest_state import HarvestState

from api.services.ml_service import (
    predict_market_price,
    historical_features,
)

from optimization.optimizer import (
    get_optimal_strategy,
)


# ============================================================
# DEFAULT STORAGE SETTINGS
# ============================================================

DEFAULT_STORAGE_COST_PER_KG_DAY = 0.30

DEFAULT_STORAGE_DAYS = 2


# ============================================================
# DATABASE MARKET -> ML DATASET MARKET
# ============================================================
#
# Explicit aliases are required only when the database display
# name differs from Member 1's dataset market name.
#
# Example:
#
# Database:
#   "Oddanchatram Market"
#
# Dataset:
#   "Dindigul(Uzhavar Sandhai )"
#
# For all other markets, the application automatically tries
# to match the database market name with Member 1's dataset.
# ============================================================

ML_MARKET_MAPPING = {

    # --------------------------------------------------------
    # Existing application-specific aliases
    # --------------------------------------------------------

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
    """
    Normalize repeated/internal whitespace and surrounding
    whitespace.

    This helps match database names with Member 1 dataset
    names when there are small formatting differences.
    """

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
    Build a normalized lookup from Member 1's processed
    forecasting dataset.

    Example:

        "Attayampatti(Uzhavar Sandhai )"
            ->
        "Attayampatti(Uzhavar Sandhai )"

    The normalized form is used as the key while the original
    dataset value is returned to the ML model.
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


# Build once when the service module is loaded.
DATASET_MARKET_LOOKUP = (
    build_dataset_market_lookup()
)


# ============================================================
# RESOLVE DATABASE MARKET -> ML MARKET
# ============================================================

def get_ml_market_name(
    market_name: str
) -> str | None:
    """
    Resolve a database Market.name to the exact market name
    expected by Member 1's ML forecasting data.

    Priority:

        1. Explicit alias
        2. Exact normalized dataset match
        3. No match -> None
    """

    if not market_name:
        return None

    # --------------------------------------------------------
    # 1. Explicit application alias
    # --------------------------------------------------------

    explicit_mapping = (
        ML_MARKET_MAPPING.get(
            market_name
        )
    )

    if explicit_mapping:
        return explicit_mapping


    # --------------------------------------------------------
    # 2. Automatic dataset match
    # --------------------------------------------------------

    normalized_name = (
        normalize_market_name(
            market_name
        )
    )

    return DATASET_MARKET_LOOKUP.get(
        normalized_name
    )


# ============================================================
# RISK PREFERENCE NORMALIZATION
# ============================================================

def normalize_risk_preference(
    risk_preference: str | None
) -> str:

    value = (
        risk_preference
        or "MEDIUM"
    ).strip().upper()

    mapping = {
        "LOW": "LOW",
        "MEDIUM": "MEDIUM",
        "MODERATE": "MEDIUM",
        "HIGH": "HIGH",
    }

    return mapping.get(
        value,
        "MEDIUM"
    )


# ============================================================
# BUILD FARMER STATE
# ============================================================

def build_farmer_state(
    farmer: Farmer,
) -> FarmerState:

    return FarmerState(

        farmer_id=str(
            farmer.id
        ),

        location=(
            farmer.location
            or ""
        ),

        risk_preference=(
            normalize_risk_preference(
                farmer.risk_preference
            )
        ),
    )


# ============================================================
# BUILD HARVEST STATE
# ============================================================

def build_harvest_state(
    farmer: Farmer,
    harvest: Harvest,
) -> HarvestState:

    return HarvestState(

        crop=harvest.crop,

        variety=(
            harvest.variety
            or "Deshi"
        ),

        quantity_kg=float(
            harvest.quantity_kg
        ),

        quality=(
            harvest.quality
            or "Unknown"
        ),

        harvest_date=str(
            harvest.harvest_date
            or ""
        ),

        remaining_shelf_life_days=float(
            harvest.shelf_life_days
            or 0
        ),

        storage_capacity_kg=float(
            farmer.storage_capacity_kg
            or 0
        ),

        storage_cost_per_kg_day=(
            DEFAULT_STORAGE_COST_PER_KG_DAY
        ),
    )


# ============================================================
# BUILD MARKET INPUTS
# ============================================================

def build_market_price_list(
    db: Session,
    variety: str,
    quantity_kg: float,
):
    """
    Build all valid market destinations for the optimizer.

    A market is included only when:

        1. It exists in the database.
        2. It has a MarketCost record.
        3. It can be resolved to Member 1's dataset market.
        4. The ML model successfully predicts its price.

    This means the optimizer receives the same market universe
    that the ML layer can actually evaluate.
    """

    markets = (
        db.query(Market)
        .order_by(
            Market.id
        )
        .all()
    )

    market_price_list = []


    for market in markets:

        # ----------------------------------------------------
        # MARKET COST
        # ----------------------------------------------------

        cost = (
            db.query(MarketCost)
            .filter(
                MarketCost.market_id
                == market.id
            )
            .first()
        )

        if not cost:

            print(
                f"[MARKET SKIP] "
                f"{market.name}: "
                f"no MarketCost record."
            )

            continue


        # ----------------------------------------------------
        # RESOLVE ML MARKET
        # ----------------------------------------------------

        ml_market = get_ml_market_name(
            market.name
        )

        if not ml_market:

            print(
                f"[MARKET SKIP] "
                f"{market.name}: "
                f"not found in Member 1 dataset."
            )

            continue


        # ----------------------------------------------------
        # CURRENT ML PRICE
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
                f"ML prediction failed: {exc}"
            )

            continue


        # ----------------------------------------------------
        # VALIDATE PREDICTION
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
        # EXPECTED LOSS
        # ----------------------------------------------------
        #
        # Database stores loss as ₹/kg.
        # DestinationOption expects a fraction.
        #
        # Example:
        #
        # loss = ₹0.30/kg
        # price = ₹20/kg
        #
        # loss fraction = 0.30 / 20 = 0.015
        #
        # ----------------------------------------------------

        loss_per_kg = float(
            cost.expected_loss_per_kg
            or 0
        )

        expected_loss_pct = (
            loss_per_kg
            / predicted_price
        )


        # ----------------------------------------------------
        # ADD MARKET OPTION
        # ----------------------------------------------------

        market_price_list.append({

            "id":
                market.id,

            "name":
                market.name,

            "dataset_market":
                ml_market,

            "district":
                market.district,

            "price_per_kg":
                predicted_price,

            "predicted_price_per_kg":
                predicted_price,

            "transport_cost_per_kg":
                float(
                    cost.transport_cost_per_kg
                    or 0
                ),

            "commission_per_kg":
                float(
                    cost.commission_per_kg
                    or 0
                ),

            "expected_loss_per_kg":
                float(
                    expected_loss_pct
                ),
        })


    return market_price_list


# ============================================================
# BUILD BUYER OFFERS
# ============================================================

def build_buyer_offer_list(
    db: Session,
    harvest_id: int,
):

    offers = (
        db.query(BuyerOffer)
        .filter(
            BuyerOffer.harvest_id
            == harvest_id
        )
        .filter(
            BuyerOffer.status
            == "PENDING"
        )
        .order_by(
            BuyerOffer.created_at.desc()
        )
        .all()
    )

    buyer_offers = []


    for offer in offers:

        buyer_offers.append({

            "id":
                offer.id,

            "offered_price_per_kg":
                float(
                    offer.offered_price_per_kg
                ),

            "quantity_kg":
                float(
                    offer.quantity_kg
                ),
        })


    return buyer_offers


# ============================================================
# BUILD FUTURE STORAGE PRICE
# ============================================================

def build_future_storage_price(
    harvest: Harvest,
    market: Market,
    variety: str,
    quantity_kg: float,
    days_to_wait: int
):
    """
    Predict the price after the waiting period.

    The selected market is resolved through the same market
    resolution system used by current market prediction.
    """

    ml_market = get_ml_market_name(
        market.name
    )


    if not ml_market:

        return None


    if not harvest.harvest_date:

        return None


    base_date = (
        harvest.harvest_date
    )


    future_date = (
        base_date
        + timedelta(
            days=days_to_wait
        )
    )


    try:

        future_price = (
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
                    future_date
                )
            )
        )

    except (
        ValueError,
        KeyError,
        TypeError
    ):

        return None


    try:

        return float(
            future_price
        )

    except (
        TypeError,
        ValueError
    ):

        return None


# ============================================================
# GET FARMER OPTIMAL STRATEGY
# ============================================================

def get_farmer_optimal_strategy(
    db: Session,
    farmer_id: int,
):

    # ========================================================
    # GET FARMER
    # ========================================================

    farmer = (
        db.query(Farmer)
        .filter(
            Farmer.id
            == farmer_id
        )
        .first()
    )


    if not farmer:

        return None


    # ========================================================
    # GET LATEST HARVEST
    # ========================================================

    harvest = (
        db.query(Harvest)
        .filter(
            Harvest.farmer_id
            == farmer_id
        )
        .order_by(
            Harvest.id.desc()
        )
        .first()
    )


    if not harvest:

        return None


    # ========================================================
    # BUILD STATES
    # ========================================================

    farmer_state = (
        build_farmer_state(
            farmer
        )
    )


    harvest_state = (
        build_harvest_state(
            farmer,
            harvest
        )
    )


    # ========================================================
    # BUILD ML MARKET INPUTS
    # ========================================================

    market_price_list = (
        build_market_price_list(

            db=db,

            variety=(
                harvest.variety
                or "Deshi"
            ),

            quantity_kg=float(
                harvest.quantity_kg
            )
        )
    )


    # ========================================================
    # BUYER OFFERS
    # ========================================================

    buyer_offers = (
        build_buyer_offer_list(

            db=db,

            harvest_id=harvest.id
        )
    )


    # ========================================================
    # STORAGE DEFAULTS
    # ========================================================

    expected_future_price_per_kg = None

    days_to_wait = (
        DEFAULT_STORAGE_DAYS
    )


    # ========================================================
    # FIND REFERENCE MARKET
    # ========================================================

    reference_market = None

    reference_market_cost = None


    if market_price_list:

        # ----------------------------------------------------
        # Highest current predicted market price becomes the
        # reference market for storage forecasting.
        # ----------------------------------------------------

        best_market_input = max(

            market_price_list,

            key=lambda item:
                float(
                    item.get(
                        "predicted_price_per_kg",
                        0
                    )
                )
        )


        reference_market = (
            db.query(Market)
            .filter(
                Market.id
                == best_market_input["id"]
            )
            .first()
        )


        if reference_market:

            reference_market_cost = (
                db.query(MarketCost)
                .filter(
                    MarketCost.market_id
                    == reference_market.id
                )
                .first()
            )


    # ========================================================
    # PREDICT FUTURE STORAGE PRICE
    # ========================================================

    if reference_market:

        expected_future_price_per_kg = (
            build_future_storage_price(

                harvest=harvest,

                market=reference_market,

                variety=(
                    harvest.variety
                    or "Deshi"
                ),

                quantity_kg=float(
                    harvest.quantity_kg
                ),

                days_to_wait=days_to_wait
            )
        )


    # ========================================================
    # FUTURE REFERENCE-MARKET COSTS
    # ========================================================

    future_transport_cost_per_kg = 0.0

    future_commission_per_kg = 0.0

    future_expected_loss_pct = 0.0


    if reference_market_cost:

        future_transport_cost_per_kg = (
            float(
                reference_market_cost
                    .transport_cost_per_kg
                or 0
            )
        )


        future_commission_per_kg = (
            float(
                reference_market_cost
                    .commission_per_kg
                or 0
            )
        )


        if (
            expected_future_price_per_kg
            is not None
            and
            expected_future_price_per_kg > 0
        ):

            future_loss_per_kg = float(
                reference_market_cost
                    .expected_loss_per_kg
                or 0
            )


            future_expected_loss_pct = (
                future_loss_per_kg
                /
                float(
                    expected_future_price_per_kg
                )
            )


    # ========================================================
    # RUN OPTIMIZER
    # ========================================================

    result = get_optimal_strategy(

        harvest=harvest_state,

        risk_preference=(
            farmer_state.risk_preference
        ),

        market_price_list=(
            market_price_list
        ),

        buyer_offers=(
            buyer_offers
        ),

        expected_future_price_per_kg=(
            expected_future_price_per_kg
        ),

        days_to_wait=(
            days_to_wait
        ),

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


    # ========================================================
    # ADD STORAGE INFORMATION
    # ========================================================

    result["storage"] = {

        "enabled":
            (
                expected_future_price_per_kg
                is not None
            ),

        "days_to_wait":
            days_to_wait,

        "storage_capacity_kg":
            harvest_state.storage_capacity_kg,

        "storage_cost_per_kg_day":
            harvest_state.storage_cost_per_kg_day,

        "expected_future_price_per_kg":
            (
                round(
                    expected_future_price_per_kg,
                    2
                )

                if
                expected_future_price_per_kg
                is not None

                else None
            ),

        "reference_market":
            (
                reference_market.name

                if reference_market

                else None
            ),
    }


    # ========================================================
    # ADD MARKET SUMMARY
    # ========================================================
    #
    # Useful for frontend debugging and for showing which
    # markets actually participated in the optimization.
    # ========================================================

    result["market_summary"] = {

        "markets_considered":
            len(
                market_price_list
            ),

        "market_names":
            [
                item["name"]
                for item
                in market_price_list
            ],

        "dataset_market_names":
            [
                item["dataset_market"]
                for item
                in market_price_list
            ],
    }


    return result