from sqlalchemy.orm import Session

from database.models import (
    Farmer,
    Harvest,
    BuyerOffer,
    Buyer,
    Market,
)

from src.negotiation_engine import make_decision
from src.explainability import generate_explanation


# ============================================================
# RISK ADJUSTMENT
# ============================================================

RISK_ADJUSTMENTS = {
    "LOW": 0.02,
    "MEDIUM": 0.05,
    "HIGH": 0.10,
}


# ============================================================
# NORMALIZE RISK PREFERENCE
# ============================================================

def normalize_risk_preference(
    risk_preference: str | None
) -> str:

    value = (
        risk_preference
        or "MEDIUM"
    ).strip().upper()

    if value == "MODERATE":
        return "MEDIUM"

    if value in RISK_ADJUSTMENTS:
        return value

    return "MEDIUM"


# ============================================================
# CALCULATE RESERVATION PRICE
# ============================================================

def calculate_fairdeal_reservation_price(
    net_price_per_kg: float,
    risk_preference: str | None
) -> dict:

    risk_level = normalize_risk_preference(
        risk_preference
    )

    risk_factor = RISK_ADJUSTMENTS[
        risk_level
    ]

    risk_adjustment = (
        net_price_per_kg
        * risk_factor
    )

    reservation_price = (
        net_price_per_kg
        + risk_adjustment
    )

    return {
        "alternative_value_per_kg":
            round(
                net_price_per_kg,
                2
            ),

        "risk_preference":
            risk_level,

        "risk_factor":
            risk_factor,

        "risk_adjustment":
            round(
                risk_adjustment,
                2
            ),

        "reservation_price":
            round(
                reservation_price,
                2
            )
    }


# ============================================================
# EVALUATE BUYER OFFERS
# ============================================================

def evaluate_buyer_offers(
    db: Session,
    harvest: Harvest,
    reservation_result: dict
) -> list[dict]:

    offers = (
        db.query(BuyerOffer)
        .filter(
            BuyerOffer.harvest_id
            == harvest.id
        )
        .filter(
            BuyerOffer.status
            == "PENDING"
        )
        .all()
    )

    results = []

    for offer in offers:

        # ----------------------------------------------------
        # Negotiation decision
        # ----------------------------------------------------
        buyer = (
            db.query(Buyer)
            .filter(
            Buyer.id == offer.buyer_id
            )
            .first()
        )

        decision_result = make_decision(
            offer_price=float(
                offer.offered_price_per_kg
            ),

            reservation_price=float(
                reservation_result[
                    "reservation_price"
                ]
            )
        )

        # ----------------------------------------------------
        # Explanation
        # ----------------------------------------------------

        explanation = generate_explanation(
            decision_result,
            reservation_result
        )

        # ----------------------------------------------------
        # Store buyer result
        # ----------------------------------------------------

        results.append({

            "buyer_offer_id":
                offer.id,

            "buyer_id":
                offer.buyer_id,

            "buyer_name":
                buyer.name
                if buyer
                else f"Buyer #{offer.buyer_id}",

            "offered_quantity_kg":
                float(
                    offer.quantity_kg
                ),

            "decision":
                decision_result[
                "decision"
                ],

            "offer_price":
                decision_result[
                "offer_price"
                ],

            "reservation_price":
                decision_result[
                "reservation_price"
                ],

            "counteroffer":
                decision_result[
                "counteroffer"
                ],

            "price_difference":
                decision_result[
                "price_difference"
                ],

            "explanation":
                explanation
        })
    return results


# ============================================================
# FIND BEST NON-BUYER ALTERNATIVE
# ============================================================

def find_best_non_buyer_alternative(
    db: Session,
    optimization_result: dict
) -> dict | None:
    """
    Find the best currently active non-buyer alternative.

    A destination is considered an alternative only when the
    optimizer has actually allocated a positive quantity to it.

    This prevents an unused STORE option from becoming the
    reservation-price benchmark.
    """

    details = optimization_result.get(
        "details",
        []
    )

    # --------------------------------------------------------
    # Only use non-buyer destinations that are actually active
    # --------------------------------------------------------

    active_non_buyer_details = [
        detail
        for detail in details
        if detail.get("kind") != "BUYER"
        and float(
            detail.get(
                "allocated_kg",
                0
            )
        ) > 0
    ]

    # --------------------------------------------------------
    # No active non-buyer alternative
    # --------------------------------------------------------

    if not active_non_buyer_details:
        return None

    # --------------------------------------------------------
    # Select highest net-price active alternative
    # --------------------------------------------------------

    best_detail = max(
        active_non_buyer_details,
        key=lambda detail: float(
            detail.get(
                "net_price_per_kg",
                0
            )
        )
    )

    destination_id = (
        best_detail.get(
            "destination_id"
        )
    )

    destination_name = destination_id

    # --------------------------------------------------------
    # Resolve market name
    # --------------------------------------------------------

    if (
        destination_id
        and destination_id.startswith("market_")
    ):

        try:

            market_id = int(
                destination_id.split("_")[1]
            )

            market = (
                db.query(Market)
                .filter(
                    Market.id == market_id
                )
                .first()
            )

            if market:

                destination_name = (
                    market.name
                )

        except (
            ValueError,
            IndexError
        ):

            pass

    return {

        "destination_id":
            destination_id,

        "destination_name":
            destination_name,

        "net_price_per_kg":
            float(
                best_detail.get(
                    "net_price_per_kg",
                    0
                )
            ),

        "risk_adjusted_price_per_kg":
            float(
                best_detail.get(
                    "risk_adjusted_price_per_kg",
                    0
                )
            ),

        "allocated_kg":
            float(
                best_detail.get(
                    "allocated_kg",
                    0
                )
            ),

        "kind":
            best_detail.get(
                "kind"
            )
    }


# ============================================================
# GET FARMER FAIRDEAL RESULT
# ============================================================

def get_farmer_fairdeal(
    db: Session,
    farmer_id: int,
    optimization_result: dict
):
    """
    Generate FairDeal negotiation intelligence.

    The reservation price is based on the best
    currently active non-buyer alternative, so a buyer's
    own offer does not become its own reservation benchmark.
    """

    # ========================================================
    # VALIDATE OPTIMIZATION RESULT
    # ========================================================

    if not optimization_result:
        return None

    # ========================================================
    # GET FARMER
    # ========================================================

    farmer = (
        db.query(Farmer)
        .filter(
            Farmer.id == farmer_id
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
    # FIND BEST NON-BUYER ALTERNATIVE
    # ========================================================

    alternative = (
        find_best_non_buyer_alternative(
            db=db,
            optimization_result=optimization_result
        )
    )

    # ========================================================
    # NO ACTIVE NON-BUYER ALTERNATIVE
    # ========================================================

    if not alternative:

        return {

            "best_alternative": None,

            "best_alternative_kind": None,

            "alternative_value_per_kg": None,

            "risk_preference":
                normalize_risk_preference(
                    farmer.risk_preference
                ),

            "risk_factor": None,

            "risk_adjustment": None,

            "reservation_price": None,

            "buyer_offers": []
        }

    # ========================================================
    # CALCULATE RESERVATION PRICE
    # ========================================================

    reservation_result = (
        calculate_fairdeal_reservation_price(

            net_price_per_kg=
                alternative[
                    "net_price_per_kg"
                ],

            risk_preference=
                farmer.risk_preference
        )
    )

    # ========================================================
    # BUILD EXPLANATION INPUT
    # ========================================================

    explanation_result = {

        **reservation_result,

        "best_market":
            alternative[
                "destination_name"
            ]
    }

    # ========================================================
    # EVALUATE PENDING BUYER OFFERS
    # ========================================================

    buyer_results = (
        evaluate_buyer_offers(

            db=db,

            harvest=harvest,

            reservation_result=
                explanation_result
        )
    )

    # ========================================================
    # FINAL FAIRDEAL RESPONSE
    # ========================================================

    return {

        "best_alternative":
            alternative[
                "destination_name"
            ],

        "best_alternative_kind":
            alternative[
                "kind"
            ],

        "alternative_value_per_kg":
            reservation_result[
                "alternative_value_per_kg"
            ],

        "risk_preference":
            reservation_result[
                "risk_preference"
            ],

        "risk_factor":
            reservation_result[
                "risk_factor"
            ],

        "risk_adjustment":
            reservation_result[
                "risk_adjustment"
            ],

        "reservation_price":
            reservation_result[
                "reservation_price"
            ],

        "buyer_offers":
            buyer_results
    }