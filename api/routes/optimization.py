from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db

from api.services.optimization_service import (
    get_farmer_optimal_strategy
)

from api.services.map_service import (
    get_market_map_data
)

from pydantic import BaseModel, Field

from typing import Optional

from api.services.whatif_service import (
    simulate_farmer_what_if
)

from database.models import (
    Farmer,
    Harvest
)


router = APIRouter(
    prefix="/optimization",
    tags=["Optimization"]
)


# ============================================================
# STORAGE ANALYSIS
# ============================================================

@router.get(
    "/storage/{farmer_id}"
)
def get_storage_analysis(
    farmer_id: int,
    db: Session = Depends(get_db)
):
    """
    Return storage-vs-selling analysis for the farmer's
    latest harvest.

    The endpoint reports the actual harvest quantity and
    separately shows allocations to markets, buyers and
    storage.
    """

    # --------------------------------------------------------
    # Check farmer
    # --------------------------------------------------------

    farmer = (
        db.query(Farmer)
        .filter(
            Farmer.id == farmer_id
        )
        .first()
    )

    if not farmer:

        raise HTTPException(
            status_code=404,
            detail="Farmer not found."
        )

    # --------------------------------------------------------
    # Get latest harvest
    # --------------------------------------------------------

    harvest = (
        db.query(Harvest)
        .filter(
            Harvest.farmer_id == farmer_id
        )
        .order_by(
            Harvest.id.desc()
        )
        .first()
    )

    if not harvest:

        raise HTTPException(
            status_code=404,
            detail="No harvest found."
        )

    # --------------------------------------------------------
    # Get complete optimization result
    # --------------------------------------------------------

    result = (
        get_farmer_optimal_strategy(
            db=db,
            farmer_id=farmer_id
        )
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail=(
                "Unable to generate optimization "
                "result."
            )
        )

    # --------------------------------------------------------
    # Find STORE detail
    # --------------------------------------------------------

    store_detail = next(
        (
            detail
            for detail in result.get(
                "details",
                []
            )
            if detail.get(
                "kind"
            ) == "STORE"
        ),
        None
    )

    # --------------------------------------------------------
    # Calculate allocations
    # --------------------------------------------------------

    market_allocated_kg = 0.0

    buyer_allocated_kg = 0.0

    storage_allocated_kg = 0.0

    for detail in result.get(
        "details",
        []
    ):

        allocated = float(
            detail.get(
                "allocated_kg",
                0
            )
        )

        kind = detail.get(
            "kind"
        )

        if kind == "MARKET":

            market_allocated_kg += allocated

        elif kind == "BUYER":

            buyer_allocated_kg += allocated

        elif kind == "STORE":

            storage_allocated_kg += allocated

    # --------------------------------------------------------
    # Actual harvest quantity
    # --------------------------------------------------------

    total_harvest_kg = float(
        harvest.quantity_kg
    )

    # --------------------------------------------------------
    # Verify allocation consistency
    # --------------------------------------------------------

    allocated_total = (
        market_allocated_kg
        + buyer_allocated_kg
        + storage_allocated_kg
    )

    allocation_difference = round(
        total_harvest_kg
        - allocated_total,
        2
    )

    # --------------------------------------------------------
    # Decide current strategy
    # --------------------------------------------------------

    if storage_allocated_kg > 0:

        decision = "STORE"

    else:

        decision = "SELL NOW"

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

    return {

        "farmer_id":
            farmer_id,

        "harvest_id":
            harvest.id,

        "crop":
            harvest.crop,

        "variety":
            harvest.variety,

        "decision":
            decision,

        "total_harvest_kg":
            round(
                total_harvest_kg,
                2
            ),

        "allocated_to_markets_kg":
            round(
                market_allocated_kg,
                2
            ),

        "allocated_to_buyers_kg":
            round(
                buyer_allocated_kg,
                2
            ),

        "allocated_to_storage_kg":
            round(
                storage_allocated_kg,
                2
            ),

        "allocation_difference_kg":
            allocation_difference,

        "storage":
            result.get(
                "storage"
            ),

        "store_analysis":
            store_detail,

        "total_expected_return":
            result.get(
                "total_expected_return"
            ),

        "risk_preference":
            result.get(
                "risk_preference"
            )
    }

# ============================================================
# STORAGE ANALYSIS FOR SELECTED HARVEST
# ============================================================

@router.get(
    "/storage/harvest/{harvest_id}"
)
def get_harvest_storage_analysis(
    harvest_id: int,
    db: Session = Depends(get_db)
):
    """
    Return storage-vs-selling analysis for one
    specific harvest.
    """

    # --------------------------------------------------------
    # Get selected harvest
    # --------------------------------------------------------

    harvest = (
        db.query(Harvest)
        .filter(
            Harvest.id == harvest_id
        )
        .first()
    )

    if not harvest:

        raise HTTPException(
            status_code=404,
            detail="Harvest not found."
        )

    # --------------------------------------------------------
    # Get farmer optimization
    # --------------------------------------------------------

    result = (
        get_farmer_optimal_strategy(
            db=db,
            farmer_id=harvest.farmer_id
        )
    )

    if not result:

        raise HTTPException(
            status_code=404,
            detail=(
                "Unable to generate optimization "
                "result."
            )
        )

    # --------------------------------------------------------
    # Find store detail
    # --------------------------------------------------------

    store_detail = next(
        (
            detail
            for detail in result.get(
                "details",
                []
            )
            if detail.get("kind") == "STORE"
        ),
        None
    )

    # --------------------------------------------------------
    # Allocation totals
    # --------------------------------------------------------

    market_allocated_kg = 0.0

    buyer_allocated_kg = 0.0

    storage_allocated_kg = 0.0

    for detail in result.get(
        "details",
        []
    ):

        allocated = float(
            detail.get(
                "allocated_kg",
                0
            )
        )

        kind = detail.get(
            "kind"
        )

        if kind == "MARKET":

            market_allocated_kg += allocated

        elif kind == "BUYER":

            buyer_allocated_kg += allocated

        elif kind == "STORE":

            storage_allocated_kg += allocated

    # --------------------------------------------------------
    # Current decision
    # --------------------------------------------------------

    decision = (
        "STORE"
        if storage_allocated_kg > 0
        else "SELL NOW"
    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {

        "farmer_id":
            harvest.farmer_id,

        "harvest_id":
            harvest.id,

        "crop":
            harvest.crop,

        "variety":
            harvest.variety,

        "decision":
            decision,

        "total_harvest_kg":
            round(
                float(
                    harvest.quantity_kg
                ),
                2
            ),

        "allocated_to_markets_kg":
            round(
                market_allocated_kg,
                2
            ),

        "allocated_to_buyers_kg":
            round(
                buyer_allocated_kg,
                2
            ),

        "allocated_to_storage_kg":
            round(
                storage_allocated_kg,
                2
            ),

        "storage":
            result.get(
                "storage"
            ),

        "store_analysis":
            store_detail,

        "total_expected_return":
            result.get(
                "total_expected_return"
            ),

        "risk_preference":
            result.get(
                "risk_preference"
            )
    }

# ============================================================
# WHAT-IF SIMULATION REQUEST
# ============================================================

class WhatIfRequest(BaseModel):

    harvest_id: Optional[int] = None

    price_change_pct: float = Field(
        default=0.0,
        ge=-100.0,
        le=100.0
    )

    transport_change_per_kg: float = Field(
        default=0.0,
        ge=-1000.0,
        le=1000.0
    )

    storage_capacity_kg: Optional[float] = Field(
        default=None,
        ge=0.0
    )

    spoilage_risk_pct: float = Field(
        default=0.0,
        ge=0.0,
        le=100.0
    )


# ============================================================
# WHAT-IF SIMULATION
# ============================================================

@router.post(
    "/what-if/{farmer_id}"
)
def what_if_simulation(
    farmer_id: int,
    request: WhatIfRequest,
    db: Session = Depends(get_db)
):

    try:

        result = simulate_farmer_what_if(

            db=db,

            farmer_id=farmer_id,

            harvest_id=(
                request.harvest_id
            ),

            price_change_pct=(
                request.price_change_pct
            ),

            transport_change_per_kg=(
                request.transport_change_per_kg
            ),

            storage_capacity_kg=(
                request.storage_capacity_kg
            ),

            spoilage_risk_pct=(
                request.spoilage_risk_pct
            )

        )

        return result

    except ValueError as err:

        raise HTTPException(
            status_code=400,
            detail=str(err)
        )

    except Exception as err:

        print(
            f"What-if simulation error: {err}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to run what-if simulation."
            )
        )

# ============================================================
# MARKET MAP / LOCATION INTELLIGENCE
# ============================================================

@router.get(
    "/map/{farmer_id}"
)
def get_market_map(
    farmer_id: int,
    harvest_id: int | None = None,
    db: Session = Depends(get_db)
):
    """
    Return farmer-to-market geographic information.

    Distance is calculated using stored coordinates.
    Travel time is an estimate and not live routing.
    """

    try:

        return get_market_map_data(
            db=db,
            farmer_id=farmer_id,
            harvest_id=harvest_id
        )

    except ValueError as err:

        raise HTTPException(
            status_code=404,
            detail=str(err)
        )

    except Exception as err:

        print(
            f"Market map error: {err}"
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to generate market map data."
        )