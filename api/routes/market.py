from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.core.database import get_db

from api.schemas.comparison import (
    MarketComparisonRequest,
    MarketComparisonResponse
)

from api.schemas.market import (
    MarketCreate,
    MarketResponse,
    MarketPriceCreate,
    MarketPriceResponse
)

from api.services.market_service import (
    compare_markets
)

from database.models import (
    Market,
    MarketPrice
)


router = APIRouter(
    prefix="/markets",
    tags=["Markets"]
)


# ============================================================
# CREATE MARKET
# ============================================================

@router.post(
    "/",
    response_model=MarketResponse
)
def create_market(
    market_data: MarketCreate,
    db: Session = Depends(get_db)
):

    market = Market(
        name=market_data.name,
        district=market_data.district,
        latitude=market_data.latitude,
        longitude=market_data.longitude
    )

    db.add(market)

    db.commit()

    db.refresh(market)

    return market


# ============================================================
# COMPARE MARKETS
# ============================================================

@router.post(
    "/compare",
    response_model=MarketComparisonResponse
)
def compare_market_options(
    request: MarketComparisonRequest,
    db: Session = Depends(get_db)
):

    result = compare_markets(
        db=db,

        crop=request.crop,

        variety=request.variety,

        quantity_kg=request.quantity_kg,

        market_costs=request.market_costs,

        prediction_date=request.prediction_date
    )

    if not result:

        raise HTTPException(
            status_code=404,

            detail=(
                "No valid market prediction "
                "data found for the requested crop."
            )
        )

    return result


# ============================================================
# GET MARKET
# ============================================================

@router.get(
    "/{market_id}",
    response_model=MarketResponse
)
def get_market(
    market_id: int,
    db: Session = Depends(get_db)
):

    market = (
        db.query(Market)
        .filter(
            Market.id == market_id
        )
        .first()
    )

    if not market:

        raise HTTPException(
            status_code=404,
            detail="Market not found"
        )

    return market


# ============================================================
# CREATE MARKET PRICE
# ============================================================

@router.post(
    "/prices",
    response_model=MarketPriceResponse
)
def create_market_price(
    price_data: MarketPriceCreate,
    db: Session = Depends(get_db)
):

    market = (
        db.query(Market)
        .filter(
            Market.id
            == price_data.market_id
        )
        .first()
    )

    if not market:

        raise HTTPException(
            status_code=404,
            detail="Market not found"
        )

    price = MarketPrice(
        market_id=price_data.market_id,

        crop=price_data.crop,

        price_per_kg=price_data.price_per_kg,

        arrival_quantity_kg=
            price_data.arrival_quantity_kg
    )

    db.add(price)

    db.commit()

    db.refresh(price)

    return price


# ============================================================
# GET MARKET PRICES
# ============================================================

@router.get(
    "/{market_id}/prices",
    response_model=list[MarketPriceResponse]
)
def get_market_prices(
    market_id: int,
    db: Session = Depends(get_db)
):

    prices = (
        db.query(MarketPrice)
        .filter(
            MarketPrice.market_id
            == market_id
        )
        .all()
    )

    return prices