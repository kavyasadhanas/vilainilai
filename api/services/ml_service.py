import os
import joblib
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "ML",
    "models",
    "xgboost_tomato_price_model.pkl"
)

FEATURES_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "tomato_forecasting_features.csv"
)


# ============================================================
# LOAD MODEL
# ============================================================

price_model = joblib.load(
    MODEL_PATH
)


# ============================================================
# LOAD HISTORICAL FEATURES
# ============================================================

historical_features = pd.read_csv(
    FEATURES_PATH
)

historical_features["Arrival Date"] = pd.to_datetime(
    historical_features["Arrival Date"]
)


# ============================================================
# PRICE PREDICTION
# ============================================================

def predict_market_price(
    market: str,
    district: str,
    variety: str,
    arrival_quantity: float,
    prediction_date=None
):
    """
    Predict tomato price using the trained XGBoost model.

    Historical lag and rolling features are obtained from
    Member 1's preprocessed forecasting dataset.
    """

    # --------------------------------------------------------
    # Filter historical data for the requested market
    # --------------------------------------------------------

    market_history = historical_features[
        (historical_features["Market"] == market)
        &
        (historical_features["District"] == district)
    ].copy()

    if market_history.empty:
        raise ValueError(
            f"No historical data found for market: {market}"
        )

    # --------------------------------------------------------
    # Use the latest historical record
    # --------------------------------------------------------

    latest = (
        market_history
        .sort_values("Arrival Date")
        .iloc[-1]
    )

    # --------------------------------------------------------
    # Determine prediction date
    # --------------------------------------------------------

    if prediction_date is None:

        prediction_date = (
            latest["Arrival Date"]
            + pd.Timedelta(days=1)
        )

    else:

        prediction_date = pd.to_datetime(
            prediction_date
        )

    # --------------------------------------------------------
    # Calendar features
    # --------------------------------------------------------

    day_of_week = prediction_date.dayofweek

    day_of_month = prediction_date.day

    month = prediction_date.month

    week_of_year = (
        prediction_date.isocalendar().week
    )

    # --------------------------------------------------------
    # Historical features
    # --------------------------------------------------------

    input_data = pd.DataFrame([{

        "Market":
            market,

        "District":
            district,

        "Variety":
            variety,

        "Arrival Quantity Kg":
            arrival_quantity,

        "day_of_week":
            day_of_week,

        "day_of_month":
            day_of_month,

        "month":
            month,

        "week_of_year":
            int(week_of_year),

        "price_lag_1":
            latest["price_lag_1"],

        "price_lag_7":
            latest["price_lag_7"],

        "price_lag_14":
            latest["price_lag_14"],

        "rolling_price_7":
            latest["rolling_price_7"],

        "rolling_price_14":
            latest["rolling_price_14"]
    }])

    # --------------------------------------------------------
    # Predict
    # --------------------------------------------------------

    prediction = price_model.predict(
        input_data
    )[0]

    return round(
        float(prediction),
        2
    )