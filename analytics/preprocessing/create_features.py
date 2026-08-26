import pandas as pd

INPUT_FILE = "data/processed/tomato_market_clean.csv"
OUTPUT_FILE = "data/processed/tomato_forecasting_features.csv"


def create_features():

    # Load cleaned dataset
    df = pd.read_csv(INPUT_FILE)

    # Convert date
    df["Arrival Date"] = pd.to_datetime(df["Arrival Date"])

    # Select required columns
    forecast_df = df[
        [
            "Arrival Date",
            "Market",
            "District",
            "Variety",
            "Modal Price Per Kg",
            "Arrival Quantity Kg",
        ]
    ].copy()

    # Sort observations by market and date
    forecast_df = forecast_df.sort_values(
        ["Market", "Arrival Date"]
    ).reset_index(drop=True)

    # Calendar features
    forecast_df["day_of_week"] = (
        forecast_df["Arrival Date"].dt.dayofweek
    )

    forecast_df["day_of_month"] = (
        forecast_df["Arrival Date"].dt.day
    )

    forecast_df["month"] = (
        forecast_df["Arrival Date"].dt.month
    )

    forecast_df["week_of_year"] = (
        forecast_df["Arrival Date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    # Historical price features
    forecast_df["price_lag_1"] = (
        forecast_df
        .groupby("Market")["Modal Price Per Kg"]
        .shift(1)
    )

    forecast_df["price_lag_7"] = (
        forecast_df
        .groupby("Market")["Modal Price Per Kg"]
        .shift(7)
    )

    forecast_df["price_lag_14"] = (
        forecast_df
        .groupby("Market")["Modal Price Per Kg"]
        .shift(14)
    )

    # Rolling price features
    forecast_df["rolling_price_7"] = (
        forecast_df
        .groupby("Market")["Modal Price Per Kg"]
        .transform(
            lambda x: x.rolling(
                7,
                min_periods=3
            ).mean()
        )
    )

    forecast_df["rolling_price_14"] = (
        forecast_df
        .groupby("Market")["Modal Price Per Kg"]
        .transform(
            lambda x: x.rolling(
                14,
                min_periods=5
            ).mean()
        )
    )

    # Remove rows without enough historical observations
    forecast_df = forecast_df.dropna().reset_index(drop=True)

    # Save final ML-ready dataset
    forecast_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("===== FEATURE ENGINEERING COMPLETE =====")
    print("Rows:", len(forecast_df))
    print("Columns:", len(forecast_df.columns))
    print("Output:", OUTPUT_FILE)

    print("\nColumns:")
    for column in forecast_df.columns:
        print("-", column)


if __name__ == "__main__":
    create_features()