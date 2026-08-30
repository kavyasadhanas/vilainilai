from typing import Optional

from sqlalchemy.orm import Session

from database.models import (
    Farmer,
    Harvest,
    Market,
    MarketCost,
    Buyer,
)

from api.services.optimization_service import (
    build_harvest_state,
    build_market_price_list,
    build_buyer_offer_list,
    build_future_storage_price,
    normalize_risk_preference,
)

from optimization.optimizer import (
    get_optimal_strategy,
)


# ============================================================
# SIMULATION HELPERS
# ============================================================


def _calculate_allocation_totals(
    result: dict
) -> dict:

    market_kg = 0.0
    buyer_kg = 0.0
    storage_kg = 0.0

    for detail in result.get(
        "details",
        []
    ):

        quantity = float(
            detail.get(
                "allocated_kg",
                0
            )
        )

        kind = detail.get(
            "kind"
        )

        if kind == "MARKET":

            market_kg += quantity

        elif kind == "BUYER":

            buyer_kg += quantity

        elif kind == "STORE":

            storage_kg += quantity

    return {

        "market_kg":
            round(
                market_kg,
                2
            ),

        "buyer_kg":
            round(
                buyer_kg,
                2
            ),

        "storage_kg":
            round(
                storage_kg,
                2
            )
    }


# ============================================================
# ADD USER-FRIENDLY DESTINATION NAMES
# ============================================================

def _add_destination_names(
    db: Session,
    details: list[dict]
) -> list[dict]:
    """
    Convert optimizer internal IDs into user-friendly names.

    Examples:

        market_3
            -> Attayampatti(Uzhavar Sandhai )

        buyer_6
            -> Salem Fresh Traders

        store
            -> Storage

    The optimizer itself continues to use destination_id.
    This function only enriches the response sent to the UI.
    """

    enriched = []

    for detail in details:

        item = dict(
            detail
        )

        destination_id = (
            item.get(
                "destination_id"
            )
            or ""
        )

        kind = (
            item.get(
                "kind"
            )
            or ""
        ).upper()


        # ----------------------------------------------------
        # MARKET
        # ----------------------------------------------------

        if kind == "MARKET":

            market_id = None

            if destination_id.startswith(
                "market_"
            ):

                try:

                    market_id = int(
                        destination_id.split(
                            "_",
                            1
                        )[1]
                    )

                except (
                    ValueError,
                    IndexError
                ):

                    market_id = None


            market = None

            if market_id is not None:

                market = (
                    db.query(Market)
                    .filter(
                        Market.id
                        == market_id
                    )
                    .first()
                )


            if market:

                item[
                    "destination_name"
                ] = market.name

                item[
                    "district"
                ] = market.district

            else:

                item[
                    "destination_name"
                ] = destination_id


        # ----------------------------------------------------
        # BUYER
        # ----------------------------------------------------

        elif kind == "BUYER":

            buyer_id = None

            if destination_id.startswith(
                "buyer_"
            ):

                try:

                    buyer_id = int(
                        destination_id.split(
                            "_",
                            1
                        )[1]
                    )

                except (
                    ValueError,
                    IndexError
                ):

                    buyer_id = None


            buyer = None

            if buyer_id is not None:

                buyer = (
                    db.query(Buyer)
                    .filter(
                        Buyer.id
                        == buyer_id
                    )
                    .first()
                )


            if buyer:

                item[
                    "destination_name"
                ] = buyer.name

                item[
                    "buyer_location"
                ] = buyer.location

                item[
                    "buyer_type"
                ] = buyer.buyer_type

            else:

                item[
                    "destination_name"
                ] = destination_id


        # ----------------------------------------------------
        # STORAGE
        # ----------------------------------------------------

        elif kind == "STORE":

            item[
                "destination_name"
            ] = "Storage"


        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        else:

            item[
                "destination_name"
            ] = destination_id


        enriched.append(
            item
        )


    return enriched


# ============================================================
# APPLY WHAT-IF MARKET CHANGES
# ============================================================

def _apply_plan_changes(
    market_price_list: list[dict],
    price_change_pct: float,
    transport_change_per_kg: float,
    spoilage_risk_pct: float
) -> list[dict]:

    modified_markets = []


    price_multiplier = (
        1
        + (
            price_change_pct
            / 100
        )
    )


    spoilage_fraction = (
        spoilage_risk_pct
        / 100
    )


    for market in market_price_list:

        modified = dict(
            market
        )


        # ----------------------------------------------------
        # PRICE CHANGE
        # ----------------------------------------------------

        modified_price = (
            float(
                modified.get(
                    "price_per_kg",
                    0
                )
            )
            * price_multiplier
        )


        modified[
            "price_per_kg"
        ] = round(
            modified_price,
            4
        )


        modified[
            "predicted_price_per_kg"
        ] = round(
            modified_price,
            4
        )


        # ----------------------------------------------------
        # TRANSPORT COST CHANGE
        # ----------------------------------------------------

        current_transport = float(
            modified.get(
                "transport_cost_per_kg",
                0
            )
        )


        modified_transport = max(
            0.0,
            current_transport
            + transport_change_per_kg
        )


        modified[
            "transport_cost_per_kg"
        ] = round(
            modified_transport,
            4
        )


        # ----------------------------------------------------
        # SPOILAGE / LOSS RISK
        # ----------------------------------------------------

        current_loss = float(
            modified.get(
                "expected_loss_per_kg",
                0
            )
        )


        modified_loss = min(
            1.0,
            max(
                0.0,
                current_loss
                + spoilage_fraction
            )
        )


        modified[
            "expected_loss_per_kg"
        ] = round(
            modified_loss,
            6
        )


        modified_markets.append(
            modified
        )


    return modified_markets


# ============================================================
# BUILD SIMULATED RESULT
# ============================================================

def _build_simulated_result(
    db: Session,
    farmer: Farmer,
    harvest: Harvest,
    price_change_pct: float,
    transport_change_per_kg: float,
    spoilage_risk_pct: float,
    storage_capacity_kg: Optional[float],
) -> dict:

    # ========================================================
    # BUILD HARVEST STATE
    # ========================================================

    simulated_harvest = build_harvest_state(
        farmer,
        harvest
    )


    # --------------------------------------------------------
    # Override storage capacity for simulation
    # --------------------------------------------------------

    if storage_capacity_kg is not None:

        simulated_harvest.storage_capacity_kg = (
            float(
                storage_capacity_kg
            )
        )


    # ========================================================
    # BUILD CURRENT MARKET DATA
    # ========================================================

    market_price_list = build_market_price_list(

        db=db,

        variety=(
            harvest.variety
            or "Deshi"
        ),

        quantity_kg=float(
            harvest.quantity_kg
        )
    )


    # ========================================================
    # APPLY SCENARIO CHANGES
    # ========================================================

    modified_market_price_list = (
        _apply_plan_changes(

            market_price_list=(
                market_price_list
            ),

            price_change_pct=(
                price_change_pct
            ),

            transport_change_per_kg=(
                transport_change_per_kg
            ),

            spoilage_risk_pct=(
                spoilage_risk_pct
            )
        )
    )


    # ========================================================
    # BUYER OFFERS
    # ========================================================

    buyer_offers = (
        build_buyer_offer_list(

            db=db,

            harvest_id=(
                harvest.id
            )
        )
    )


    # ========================================================
    # FIND REFERENCE MARKET
    # ========================================================

    reference_market = None

    reference_market_cost = None


    if modified_market_price_list:

        best_market_input = max(

            modified_market_price_list,

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
                ==
                best_market_input["id"]
            )
            .first()
        )


        if reference_market:

            reference_market_cost = (
                db.query(MarketCost)
                .filter(
                    MarketCost.market_id
                    ==
                    reference_market.id
                )
                .first()
            )


    # ========================================================
    # FUTURE STORAGE PRICE
    # ========================================================

    expected_future_price = None

    days_to_wait = 2


    if reference_market:

        expected_future_price = (
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

                days_to_wait=(
                    days_to_wait
                )
            )
        )


    # ========================================================
    # APPLY PRICE SCENARIO TO FUTURE PRICE
    # ========================================================

    if (
        expected_future_price
        is not None
        and
        expected_future_price > 0
    ):

        expected_future_price *= (
            1
            + (
                price_change_pct
                / 100
            )
        )


        expected_future_price = round(
            expected_future_price,
            4
        )


    # ========================================================
    # FUTURE REFERENCE-MARKET COSTS
    # ========================================================

    future_transport_cost_per_kg = 0.0

    future_commission_per_kg = 0.0

    future_expected_loss_pct = 0.0


    if reference_market_cost:

        # ----------------------------------------------------
        # Use the simulated transport cost for the reference
        # market when available.
        # ----------------------------------------------------

        matching_market = next(
            (
                market
                for market
                in modified_market_price_list

                if market.get(
                    "id"
                )
                ==
                reference_market.id
            ),
            None
        )


        if matching_market:

            future_transport_cost_per_kg = (
                float(
                    matching_market.get(
                        "transport_cost_per_kg",
                        0
                    )
                )
            )


            future_expected_loss_pct = (
                float(
                    matching_market.get(
                        "expected_loss_per_kg",
                        0
                    )
                )
            )


        else:

            future_transport_cost_per_kg = (
                float(
                    reference_market_cost
                    .transport_cost_per_kg
                    or 0
                )
            )


            future_loss_per_kg = (
                float(
                    reference_market_cost
                    .expected_loss_per_kg
                    or 0
                )
            )


            if (
                expected_future_price
                is not None
                and
                expected_future_price > 0
            ):

                future_expected_loss_pct = (
                    future_loss_per_kg
                    /
                    expected_future_price
                )


        future_commission_per_kg = (
            float(
                reference_market_cost
                .commission_per_kg
                or 0
            )
        )


    # ========================================================
    # RISK PREFERENCE
    # ========================================================

    risk_preference = (
        normalize_risk_preference(
            farmer.risk_preference
        )
    )


    # ========================================================
    # RUN SAME OPTIMIZER
    # ========================================================

    result = get_optimal_strategy(

        harvest=simulated_harvest,

        risk_preference=(
            risk_preference
        ),

        market_price_list=(
            modified_market_price_list
        ),

        buyer_offers=(
            buyer_offers
        ),

        expected_future_price_per_kg=(
            expected_future_price
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
    # ALLOCATION SUMMARY
    # ========================================================

    totals = (
        _calculate_allocation_totals(
            result
        )
    )


    # ========================================================
    # STORAGE INFORMATION
    # ========================================================

    result["storage"] = {

        "enabled":
            expected_future_price
            is not None,

        "days_to_wait":
            days_to_wait,

        "storage_capacity_kg":
            simulated_harvest
            .storage_capacity_kg,

        "storage_cost_per_kg_day":
            simulated_harvest
            .storage_cost_per_kg_day,

        "expected_future_price_per_kg":
            (
                round(
                    expected_future_price,
                    2
                )

                if
                expected_future_price
                is not None

                else None
            ),

        "reference_market":
            (
                reference_market.name

                if reference_market

                else None
            )
    }


    # ========================================================
    # RETURN SIMULATED RESULT
    # ========================================================

    return {

        "allocations":
            result.get(
                "allocations",
                {}
            ),

        "details":
            result.get(
                "details",
                []
            ),

        "total_expected_return":
            round(
                float(
                    result.get(
                        "total_expected_return",
                        0
                    )
                ),
                2
            ),

        "risk_preference":
            result.get(
                "risk_preference"
            ),

        "storage":
            result.get(
                "storage"
            ),

        "allocation_summary":
            totals
    }


# ============================================================
# PUBLIC WHAT-IF FUNCTION
# ============================================================

def simulate_farmer_what_if(
    db: Session,
    farmer_id: int,
    harvest_id: Optional[int] = None,
    price_change_pct: float = 0.0,
    transport_change_per_kg: float = 0.0,
    storage_capacity_kg: Optional[float] = None,
    spoilage_risk_pct: float = 0.0,
) -> dict:

    # ========================================================
    # CHECK FARMER
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

        raise ValueError(
            "Farmer not found."
        )


    # ========================================================
    # GET HARVEST
    # ========================================================

    if harvest_id is not None:

        harvest = (
            db.query(Harvest)
            .filter(
                Harvest.id
                == harvest_id
            )
            .filter(
                Harvest.farmer_id
                == farmer_id
            )
            .first()
        )

    else:

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

        raise ValueError(
            "No harvest found for this farmer."
        )


    # ========================================================
    # VALIDATE SCENARIO
    # ========================================================

    if price_change_pct < -100:

        raise ValueError(
            "Price change cannot be less than -100%."
        )


    if spoilage_risk_pct < 0:

        raise ValueError(
            "Spoilage risk cannot be negative."
        )


    if spoilage_risk_pct > 100:

        raise ValueError(
            "Spoilage risk cannot exceed 100%."
        )


    if storage_capacity_kg is not None:

        storage_capacity_kg = float(
            storage_capacity_kg
        )


        if storage_capacity_kg < 0:

            raise ValueError(
                "Storage capacity cannot be negative."
            )


        harvest_quantity_kg = float(
            harvest.quantity_kg
            or 0
        )


        farmer_storage_capacity_kg = float(
            farmer.storage_capacity_kg
            or 0
        )


        if (
            storage_capacity_kg
            > harvest_quantity_kg
        ):

            raise ValueError(
                "Storage capacity cannot exceed "
                "the harvest quantity."
            )


        if (
            storage_capacity_kg
            > farmer_storage_capacity_kg
        ):

            raise ValueError(
                "Storage capacity cannot exceed "
                "the farmer's actual storage capacity "
                f"of {farmer_storage_capacity_kg:g} kg."
            )


    # ========================================================
    # CURRENT / BASELINE STRATEGY
    # ========================================================

    from api.services.optimization_service import (
        get_farmer_optimal_strategy
    )


    current_result = (
        get_farmer_optimal_strategy(

            db=db,

            farmer_id=(
                farmer_id
            )
        )
    )


    if not current_result:

        raise ValueError(
            "Unable to generate current optimization."
        )


    # ========================================================
    # SIMULATED STRATEGY
    # ========================================================

    simulated_result = (
        _build_simulated_result(

            db=db,

            farmer=farmer,

            harvest=harvest,

            price_change_pct=(
                price_change_pct
            ),

            transport_change_per_kg=(
                transport_change_per_kg
            ),

            spoilage_risk_pct=(
                spoilage_risk_pct
            ),

            storage_capacity_kg=(
                storage_capacity_kg
            )
        )
    )


    # ========================================================
    # ADD USER-FRIENDLY DESTINATION NAMES
    # ========================================================

    current_result["details"] = (
        _add_destination_names(

            db=db,

            details=(
                current_result.get(
                    "details",
                    []
                )
            )
        )
    )


    simulated_result["details"] = (
        _add_destination_names(

            db=db,

            details=(
                simulated_result.get(
                    "details",
                    []
                )
            )
        )
    )


    # ========================================================
    # CURRENT ALLOCATION SUMMARY
    # ========================================================

    current_totals = (
        _calculate_allocation_totals(
            current_result
        )
    )


    # ========================================================
    # SIMULATED ALLOCATION SUMMARY
    # ========================================================

    simulated_totals = (
        simulated_result.get(
            "allocation_summary",
            {}
        )
    )


    # ========================================================
    # PROFIT DIFFERENCE
    # ========================================================

    current_return = float(
        current_result.get(
            "total_expected_return",
            0
        )
    )


    simulated_return = float(
        simulated_result.get(
            "total_expected_return",
            0
        )
    )


    return_difference = round(
        simulated_return
        - current_return,
        2
    )


    # ========================================================
    # PROFIT CHANGE %
    # ========================================================

    if current_return != 0:

        profit_change_percent = round(
            (
                return_difference
                / current_return
            )
            * 100,
            2
        )

    else:

        profit_change_percent = 0.0


    # ========================================================
    # RETURN
    # ========================================================

    return {

        "farmer_id":
            farmer_id,

        "harvest_id":
            harvest.id,

        "crop":
            harvest.crop,

        "variety":
            harvest.variety,

        "quantity_kg":
            float(
                harvest.quantity_kg
            ),


        "scenario": {

            "price_change_pct":
                round(
                    price_change_pct,
                    2
                ),

            "transport_change_per_kg":
                round(
                    transport_change_per_kg,
                    2
                ),

            "storage_capacity_kg":
                (
                    round(
                        storage_capacity_kg,
                        2
                    )

                    if storage_capacity_kg
                    is not None

                    else float(
                        farmer.storage_capacity_kg
                        or 0
                    )
                ),

            "spoilage_risk_pct":
                round(
                    spoilage_risk_pct,
                    2
                )
        },


        # ====================================================
        # CURRENT PLAN
        # ====================================================

        "current_plan": {

            "total_expected_return":
                round(
                    current_return,
                    2
                ),

            "allocations":
                current_result.get(
                    "allocations",
                    {}
                ),

            "details":
                current_result.get(
                    "details",
                    []
                ),

            "allocation_summary":
                current_totals
        },


        # ====================================================
        # SIMULATED PLAN
        # ====================================================

        "simulated_plan": {

            "total_expected_return":
                round(
                    simulated_return,
                    2
                ),

            "allocations":
                simulated_result.get(
                    "allocations",
                    {}
                ),

            "details":
                simulated_result.get(
                    "details",
                    []
                ),

            "allocation_summary":
                simulated_totals,

            "storage":
                simulated_result.get(
                    "storage"
                )
        },


        "profit_difference":
            return_difference,

        "profit_change_percent":
            profit_change_percent
    }