from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db

from database.models import (
    Buyer,
    BuyerOffer,
    Harvest,
)

from api.schemas.buyer import (
    BuyerCreate,
    BuyerResponse,
    BuyerHarvestResponse,
    BuyerOfferCreate,
    BuyerOfferResponse,
)


router = APIRouter(
    prefix="/buyers",
    tags=["Buyers"]
)


# ============================================================
# CREATE BUYER
# ============================================================

@router.post(
    "/",
    response_model=BuyerResponse
)
def create_buyer(
    buyer_data: BuyerCreate,
    db: Session = Depends(get_db)
):

    buyer = Buyer(
        name=buyer_data.name,
        buyer_type=buyer_data.buyer_type,
        location=buyer_data.location
    )

    db.add(buyer)
    db.commit()
    db.refresh(buyer)

    return buyer


# ============================================================
# GET BUYER
# ============================================================

@router.get(
    "/{buyer_id}",
    response_model=BuyerResponse
)
def get_buyer(
    buyer_id: int,
    db: Session = Depends(get_db)
):

    buyer = (
        db.query(Buyer)
        .filter(
            Buyer.id == buyer_id
        )
        .first()
    )

    if not buyer:

        raise HTTPException(
            status_code=404,
            detail="Buyer not found"
        )

    return buyer


# ============================================================
# GET AVAILABLE HARVESTS
# ============================================================

@router.get(
    "/available-harvests",
    response_model=list[BuyerHarvestResponse]
)
def get_available_harvests(
    db: Session = Depends(get_db)
):
    """
    Return harvests that buyers can make offers for.

    For now every stored harvest is considered available.
    The buyer can then choose the quantity they want to buy.

    A future version can add an explicit harvest status such
    as AVAILABLE / SOLD / CLOSED.
    """

    harvests = (
        db.query(Harvest)
        .order_by(
            Harvest.id.desc()
        )
        .all()
    )

    return harvests


# ============================================================
# CREATE BUYER OFFER
# ============================================================

@router.post(
    "/offers",
    response_model=BuyerOfferResponse
)
def create_buyer_offer(
    offer_data: BuyerOfferCreate,
    db: Session = Depends(get_db)
):

    # --------------------------------------------------------
    # CHECK BUYER
    # --------------------------------------------------------

    buyer = (
        db.query(Buyer)
        .filter(
            Buyer.id == offer_data.buyer_id
        )
        .first()
    )

    if not buyer:

        raise HTTPException(
            status_code=404,
            detail="Buyer not found"
        )


    # --------------------------------------------------------
    # CHECK HARVEST
    # --------------------------------------------------------

    harvest = (
        db.query(Harvest)
        .filter(
            Harvest.id == offer_data.harvest_id
        )
        .first()
    )

    if not harvest:

        raise HTTPException(
            status_code=404,
            detail="Harvest not found"
        )


    # --------------------------------------------------------
    # VALIDATE QUANTITY
    # --------------------------------------------------------

    if offer_data.quantity_kg <= 0:

        raise HTTPException(
            status_code=400,
            detail="Offer quantity must be greater than zero."
        )


    harvest_quantity = float(
        harvest.quantity_kg or 0
    )


    if (
        offer_data.quantity_kg
        > harvest_quantity
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "Offer quantity cannot exceed "
                "available harvest quantity."
            )
        )


    # --------------------------------------------------------
    # VALIDATE PRICE
    # --------------------------------------------------------

    if (
        offer_data.offered_price_per_kg
        <= 0
    ):

        raise HTTPException(
            status_code=400,
            detail="Offer price must be greater than zero."
        )


    # --------------------------------------------------------
    # CREATE OFFER
    # --------------------------------------------------------

    offer = BuyerOffer(

        buyer_id=(
            offer_data.buyer_id
        ),

        harvest_id=(
            offer_data.harvest_id
        ),

        offered_price_per_kg=(
            offer_data.offered_price_per_kg
        ),

        quantity_kg=(
            offer_data.quantity_kg
        ),

        status="PENDING",

        counteroffer_per_kg=None
    )


    db.add(
        offer
    )

    db.commit()

    db.refresh(
        offer
    )

    return offer


# ============================================================
# GET OFFERS FOR A HARVEST
# ============================================================

@router.get(
    "/harvests/{harvest_id}/offers",
    response_model=list[BuyerOfferResponse]
)
def get_harvest_offers(
    harvest_id: int,
    db: Session = Depends(get_db)
):

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
            detail="Harvest not found"
        )


    offers = (
        db.query(BuyerOffer)
        .filter(
            BuyerOffer.harvest_id
            == harvest_id
        )
        .order_by(
            BuyerOffer.created_at.desc()
        )
        .all()
    )

    return offers


# ============================================================
# GET ALL OFFERS FOR A HARVEST
# ============================================================

@router.get(
    "/harvests/{harvest_id}/all-offers",
    response_model=list[BuyerOfferResponse]
)
def get_all_harvest_offers(
    harvest_id: int,
    db: Session = Depends(get_db)
):

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
            detail="Harvest not found"
        )


    offers = (
        db.query(BuyerOffer)
        .filter(
            BuyerOffer.harvest_id
            == harvest_id
        )
        .order_by(
            BuyerOffer.created_at.desc()
        )
        .all()
    )

    return offers


# ============================================================
# UPDATE NEGOTIATION RESULT
# ============================================================

@router.patch(
    "/offers/{offer_id}/status",
    response_model=BuyerOfferResponse
)
def update_offer_status(
    offer_id: int,
    status: str,
    counteroffer_per_kg: float | None = None,
    db: Session = Depends(get_db)
):

    offer = (
        db.query(BuyerOffer)
        .filter(
            BuyerOffer.id
            == offer_id
        )
        .first()
    )

    if not offer:

        raise HTTPException(
            status_code=404,
            detail="Buyer offer not found"
        )


    status = (
        status
        .strip()
        .upper()
    )


    allowed_statuses = {
        "PENDING",
        "ACCEPTED",
        "NEGOTIATING",
        "REJECTED"
    }


    if status not in allowed_statuses:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid status. Use PENDING, "
                "ACCEPTED, NEGOTIATING or REJECTED."
            )
        )


    if (
        status == "NEGOTIATING"
        and (
            counteroffer_per_kg is None
            or counteroffer_per_kg <= 0
        )
    ):

        raise HTTPException(
            status_code=400,
            detail=(
                "A positive counteroffer is required "
                "when negotiating."
            )
        )


    offer.status = status


    offer.counteroffer_per_kg = (

        counteroffer_per_kg

        if status == "NEGOTIATING"

        else None
    )


    db.commit()

    db.refresh(
        offer
    )

    return offer