import math

from sqlalchemy.orm import Session

from database.models import (
    Farmer,
    Harvest,
    Market,
    MarketCost
)


# ============================================================
# APPROXIMATE LOCATION COORDINATES
# ============================================================
#
# Farmer currently stores a textual location rather than
# exact farm latitude/longitude.
#
# These are therefore APPROXIMATE city/district reference
# points, not exact farm coordinates.
#
# When Farmer.latitude / longitude are added later, this
# mapping can be replaced by the farmer's actual coordinates.
# ============================================================

LOCATION_COORDINATES = {

    "salem": {
        "name": "Salem, Tamil Nadu",
        "latitude": 11.6643,
        "longitude": 78.1460
    },

    "dindigul": {
        "name": "Dindigul, Tamil Nadu",
        "latitude": 10.3673,
        "longitude": 77.9803
    },

    "madurai": {
        "name": "Madurai, Tamil Nadu",
        "latitude": 9.9252,
        "longitude": 78.1198
    },

    "coimbatore": {
        "name": "Coimbatore, Tamil Nadu",
        "latitude": 11.0168,
        "longitude": 76.9558
    },

    "trichy": {
        "name": "Tiruchirappalli, Tamil Nadu",
        "latitude": 10.7905,
        "longitude": 78.7047
    },

    "tiruchirappalli": {
        "name": "Tiruchirappalli, Tamil Nadu",
        "latitude": 10.7905,
        "longitude": 78.7047
    },

    "erode": {
        "name": "Erode, Tamil Nadu",
        "latitude": 11.3410,
        "longitude": 77.7172
    },

    "theni": {
        "name": "Theni, Tamil Nadu",
        "latitude": 10.0104,
        "longitude": 77.4768
    },

    "karur": {
        "name": "Karur, Tamil Nadu",
        "latitude": 10.9601,
        "longitude": 78.0766
    }
}


# ============================================================
# NORMALIZE LOCATION TEXT
# ============================================================

def normalize_location(
    location: str | None
) -> str:

    if not location:
        return ""

    value = (
        location
        .strip()
        .lower()
    )

    # --------------------------------------------------------
    # Remove common state suffix
    # --------------------------------------------------------

    value = value.replace(
        ", tamil nadu",
        ""
    )

    value = value.replace(
        "tamil nadu",
        ""
    )

    value = value.strip()

    return value


# ============================================================
# HAVERSINE DISTANCE
# ============================================================

def calculate_distance_km(
    latitude_1: float,
    longitude_1: float,
    latitude_2: float,
    longitude_2: float
) -> float:

    earth_radius_km = 6371.0

    lat1 = math.radians(
        latitude_1
    )

    lon1 = math.radians(
        longitude_1
    )

    lat2 = math.radians(
        latitude_2
    )

    lon2 = math.radians(
        longitude_2
    )

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    a = (
        math.sin(delta_lat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(delta_lon / 2) ** 2
    )

    c = (
        2
        *
        math.atan2(
            math.sqrt(a),
            math.sqrt(1 - a)
        )
    )

    return round(
        earth_radius_km * c,
        2
    )


# ============================================================
# ESTIMATED TRAVEL TIME
# ============================================================

def estimate_travel_time_minutes(
    distance_km: float
) -> int:

    average_speed_kmph = 35.0

    hours = (
        distance_km
        / average_speed_kmph
    )

    minutes = hours * 60

    return max(
        1,
        round(minutes)
    )


# ============================================================
# GET FARMER REFERENCE LOCATION
# ============================================================

def get_farmer_reference_location(
    farmer: Farmer
) -> dict:

    raw_location = (
        farmer.location
        or ""
    ).strip()

    normalized_location = normalize_location(
        raw_location
    )


    # --------------------------------------------------------
    # Exact normalized lookup
    # --------------------------------------------------------

    coordinates = (
        LOCATION_COORDINATES.get(
            normalized_location
        )
    )


    # --------------------------------------------------------
    # Partial lookup
    # Example:
    # "Salem district"
    # "Salem, Tamil Nadu"
    # --------------------------------------------------------

    if coordinates is None:

        for key, value in LOCATION_COORDINATES.items():

            if (
                key in normalized_location
                or
                normalized_location in key
            ):

                coordinates = value

                break


    # --------------------------------------------------------
    # Unknown location
    #
    # Do NOT silently pretend it is Dindigul.
    # --------------------------------------------------------

    if coordinates is None:

        raise ValueError(
            "Unable to determine approximate coordinates "
            f"for farmer location: {raw_location or 'Unknown'}"
        )


    return {

        "name":
            coordinates["name"],

        "latitude":
            coordinates["latitude"],

        "longitude":
            coordinates["longitude"],

        "is_approximate":
            True

    }


# ============================================================
# BUILD MARKET MAP DATA
# ============================================================

def get_market_map_data(
    db: Session,
    farmer_id: int,
    harvest_id: int | None = None
) -> dict:

    # --------------------------------------------------------
    # FARMER
    # --------------------------------------------------------

    farmer = (
        db.query(Farmer)
        .filter(
            Farmer.id == farmer_id
        )
        .first()
    )


    if not farmer:

        raise ValueError(
            "Farmer not found."
        )


    # --------------------------------------------------------
    # HARVEST
    # --------------------------------------------------------

    if harvest_id is not None:

        harvest = (
            db.query(Harvest)
            .filter(
                Harvest.id == harvest_id,
                Harvest.farmer_id == farmer_id
            )
            .first()
        )

    else:

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

        raise ValueError(
            "No harvest found for this farmer."
        )


    # --------------------------------------------------------
    # FARMER REFERENCE LOCATION
    # --------------------------------------------------------

    farmer_location = (
        get_farmer_reference_location(
            farmer
        )
    )


    # --------------------------------------------------------
    # MARKETS
    # --------------------------------------------------------

    markets = (
        db.query(Market)
        .all()
    )


    market_data = []


    for market in markets:

        # Skip markets without coordinates.

        if (
            market.latitude is None
            or
            market.longitude is None
        ):
            continue


        # ----------------------------------------------------
        # DISTANCE
        # ----------------------------------------------------

        distance_km = (
            calculate_distance_km(

                farmer_location[
                    "latitude"
                ],

                farmer_location[
                    "longitude"
                ],

                float(
                    market.latitude
                ),

                float(
                    market.longitude
                )
            )
        )


        # ----------------------------------------------------
        # TRAVEL TIME
        # ----------------------------------------------------

        travel_time_minutes = (
            estimate_travel_time_minutes(
                distance_km
            )
        )


        # ----------------------------------------------------
        # MARKET COST
        # ----------------------------------------------------

        market_cost = (
            db.query(MarketCost)
            .filter(
                MarketCost.market_id
                == market.id
            )
            .first()
        )


        transport_cost_per_kg = 0.0


        if market_cost:

            transport_cost_per_kg = float(
                market_cost.transport_cost_per_kg
                or 0
            )


        # ----------------------------------------------------
        # TOTAL TRANSPORT COST
        # ----------------------------------------------------

        harvest_quantity = float(
            harvest.quantity_kg
            or 0
        )


        total_transport_cost = (
            transport_cost_per_kg
            * harvest_quantity
        )


        # ----------------------------------------------------
        # MARKET RESULT
        # ----------------------------------------------------

        market_data.append({

            "market_id":
                market.id,

            "market_name":
                market.name,

            "district":
                market.district,

            "latitude":
                float(
                    market.latitude
                ),

            "longitude":
                float(
                    market.longitude
                ),

            "distance_km":
                distance_km,

            "estimated_travel_time_minutes":
                travel_time_minutes,

            "transport_cost_per_kg":
                round(
                    transport_cost_per_kg,
                    2
                ),

            "estimated_total_transport_cost":
                round(
                    total_transport_cost,
                    2
                )

        })


    # --------------------------------------------------------
    # SORT NEAREST FIRST
    # --------------------------------------------------------

    market_data.sort(
        key=lambda market:
            market["distance_km"]
    )


    # --------------------------------------------------------
    # RETURN
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

        "quantity_kg":
            float(
                harvest.quantity_kg
                or 0
            ),

        "farmer_location":
            farmer_location,

        "markets":
            market_data,

        "travel_time_note":
            "Travel time is an estimate based on an "
            "assumed average speed of 35 km/h and is "
            "not live road-routing data.",

        "market_count":
            len(
                market_data
            )

    }