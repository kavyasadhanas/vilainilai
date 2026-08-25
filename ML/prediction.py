import os
import joblib
import numpy as np
import pandas as pd


# ============================================================
# VILAINILAI - ML PREDICTION FUNCTIONS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")


# ============================================================
# LOAD PRICE FORECASTING MODEL
# ============================================================

PRICE_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "xgboost_tomato_price_model.pkl"
)

price_model = joblib.load(
    PRICE_MODEL_PATH
)


# ============================================================
# LOAD SHOCK DETECTION MODEL
# ============================================================

SHOCK_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "tomato_shock_detector.pkl"
)

shock_package = joblib.load(
    SHOCK_MODEL_PATH
)

shock_detector = shock_package["detector"]
shock_scaler = shock_package["scaler"]
shock_features = shock_package["features"]


# ============================================================
# 1. PRICE PREDICTION
# ============================================================

def predict_price(
    market,
    district,
    variety,
    arrival_quantity,
    day_of_week,
    day_of_month,
    month,
    week_of_year,
    price_lag_1,
    price_lag_7,
    price_lag_14,
    rolling_price_7,
    rolling_price_14
):
    """
    Predict tomato modal price in ₹/kg.

    Returns:
        float: predicted price
    """

    input_data = pd.DataFrame([{
        "Market": market,
        "District": district,
        "Variety": variety,
        "Arrival Quantity Kg": arrival_quantity,
        "day_of_week": day_of_week,
        "day_of_month": day_of_month,
        "month": month,
        "week_of_year": week_of_year,
        "price_lag_1": price_lag_1,
        "price_lag_7": price_lag_7,
        "price_lag_14": price_lag_14,
        "rolling_price_7": rolling_price_7,
        "rolling_price_14": rolling_price_14
    }])

    prediction = price_model.predict(
        input_data
    )[0]

    return round(
        float(prediction),
        2
    )


# ============================================================
# 2. SHOCK DETECTION
# ============================================================

def detect_shock(
    arrival_change_pct,
    price_change_pct,
    price_deviation_pct,
    arrival_deviation_pct
):
    """
    Detect abnormal supply/price conditions.

    Returns:
        dictionary containing shock status
    """

    input_data = pd.DataFrame([{
        "arrival_change_pct":
            arrival_change_pct,

        "price_change_pct":
            price_change_pct,

        "price_deviation_pct":
            price_deviation_pct,

        "arrival_deviation_pct":
            arrival_deviation_pct
    }])

    # Ensure correct feature order
    input_data = input_data[
        shock_features
    ]

    scaled_input = shock_scaler.transform(
        input_data
    )

    anomaly_prediction = (
        shock_detector.predict(
            scaled_input
        )[0]
    )

    anomaly_score = (
        shock_detector.decision_function(
            scaled_input
        )[0]
    )

    # Isolation Forest:
    # +1 = normal
    # -1 = anomaly

    overall_anomaly = (
        anomaly_prediction == -1
    )

    # Rule-based supply shock
    supply_shock = (
        arrival_deviation_pct >= 30
    )

    # Rule-based price shock
    price_shock = (
        abs(price_change_pct) >= 15
    )

    # Final decision
    if supply_shock and price_shock:
        status = "SUPPLY + PRICE SHOCK"

    elif supply_shock:
        status = "SUPPLY SHOCK"

    elif price_shock:
        status = "PRICE SHOCK"

    elif overall_anomaly:
        status = "ANOMALY"

    else:
        status = "NORMAL"

    return {
        "status": status,
        "is_anomaly": bool(
            overall_anomaly
        ),
        "anomaly_score": round(
            float(anomaly_score),
            4
        ),
        "supply_shock": bool(
            supply_shock
        ),
        "price_shock": bool(
            price_shock
        )
    }


# ============================================================
# 3. TEST THE FUNCTIONS
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("VILAINILAI ML PREDICTION TEST")
    print("=" * 60)

    # --------------------------------------------------------
    # Test price prediction
    # --------------------------------------------------------

    predicted_price = predict_price(
        market="Athur(Uzhavar Sandhai )",
        district="Dindigul",
        variety="Tomato",
        arrival_quantity=3000,
        day_of_week=2,
        day_of_month=25,
        month=8,
        week_of_year=35,
        price_lag_1=25.0,
        price_lag_7=24.0,
        price_lag_14=23.5,
        rolling_price_7=24.5,
        rolling_price_14=24.0
    )

    print(
        f"\nPredicted tomato price:"
        f" ₹{predicted_price}/kg"
    )


    # --------------------------------------------------------
    # Test shock detection
    # --------------------------------------------------------

    shock_result = detect_shock(
        arrival_change_pct=45.0,
        price_change_pct=-20.0,
        price_deviation_pct=-18.0,
        arrival_deviation_pct=40.0
    )

    print("\nShock detection:")

    print(
        f"Status: "
        f"{shock_result['status']}"
    )

    print(
        f"Supply shock: "
        f"{shock_result['supply_shock']}"
    )

    print(
        f"Price shock: "
        f"{shock_result['price_shock']}"
    )

    print(
        f"Anomaly: "
        f"{shock_result['is_anomaly']}"
    )

    print(
        f"Anomaly score: "
        f"{shock_result['anomaly_score']}"
    )

    print("\n" + "=" * 60)
    print("ML PREDICTION TEST COMPLETED")
    print("=" * 60)