from datetime import datetime

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text
)

from api.core.database import Base


class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    location = Column(
        String(150),
        nullable=False
    )

    risk_preference = Column(
        String(30),
        default="moderate"
    )

    storage_capacity_kg = Column(
        Float,
        default=0
    )


class Harvest(Base):
    __tablename__ = "harvests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    farmer_id = Column(
        Integer,
        ForeignKey("farmers.id"),
        nullable=False
    )

    crop = Column(
        String(100),
        nullable=False
    )

    variety = Column(
        String(50),
        default="Deshi"
    )

    quantity_kg = Column(
        Float,
        nullable=False
    )

    quality = Column(
        String(50)
    )

    harvest_date = Column(
        Date
    )

    shelf_life_days = Column(
        Integer
    )

class Market(Base):
    __tablename__ = "markets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    district = Column(
        String(100)
    )

    latitude = Column(
        Float
    )

    longitude = Column(
        Float
    )


class MarketPrice(Base):
    __tablename__ = "market_prices"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    market_id = Column(
        Integer,
        ForeignKey("markets.id"),
        nullable=False
    )

    crop = Column(
        String(100),
        nullable=False
    )

    price_per_kg = Column(
        Float,
        nullable=False
    )

    arrival_quantity_kg = Column(
        Float
    )

    recorded_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# ---------------------------------------------------------
# MARKET COST
# ---------------------------------------------------------

class MarketCost(Base):
    __tablename__ = "market_costs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    market_id = Column(
        Integer,
        ForeignKey("markets.id"),
        nullable=False
    )

    transport_cost_per_kg = Column(
        Float,
        default=0
    )

    commission_per_kg = Column(
        Float,
        default=0
    )

    expected_loss_per_kg = Column(
        Float,
        default=0
    )


class Buyer(Base):
    __tablename__ = "buyers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(150),
        nullable=False
    )

    buyer_type = Column(
        String(50)
    )

    location = Column(
        String(150)
    )


class BuyerOffer(Base):
    __tablename__ = "buyer_offers"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    buyer_id = Column(
        Integer,
        ForeignKey("buyers.id"),
        nullable=False
    )

    harvest_id = Column(
        Integer,
        ForeignKey("harvests.id"),
        nullable=False
    )

    offered_price_per_kg = Column(
        Float,
        nullable=False
    )

    quantity_kg = Column(
        Float,
        nullable=False
    )

    status = Column(
        String(30),
        default="PENDING"
    )

    counteroffer_per_kg = Column(
        Float,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    harvest_id = Column(
        Integer,
        ForeignKey("harvests.id"),
        nullable=False
    )

    # ---------------------------------------------------------
    # FINAL DECISION
    # ---------------------------------------------------------

    action = Column(
        String(30)
    )

    destination = Column(
        String(150)
    )

    quantity_kg = Column(
        Float
    )

    expected_return = Column(
        Float
    )

    # ---------------------------------------------------------
    # ML SNAPSHOT
    # ---------------------------------------------------------

    predicted_price_per_kg = Column(
        Float
    )

    net_price_per_kg = Column(
        Float
    )

    # ---------------------------------------------------------
    # FAIRDEAL SNAPSHOT
    # ---------------------------------------------------------

    risk_preference = Column(
        String(30)
    )

    reservation_price = Column(
        Float
    )

    # ---------------------------------------------------------
    # OPTIMIZATION SNAPSHOT
    # Stored as JSON text
    # ---------------------------------------------------------

    optimization_result = Column(
        Text
    )

    # ---------------------------------------------------------
    # FAIRDEAL SNAPSHOT
    # Stored as JSON text
    # ---------------------------------------------------------

    fairdeal_result = Column(
        Text
    )

    # ---------------------------------------------------------
    # EXPLANATION
    # ---------------------------------------------------------

    explanation = Column(
        Text
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )