import os
import joblib
import numpy as np
import pandas as pd

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ============================================================
# VILAINILAI - SUPPLY / PRICE SHOCK DETECTION
# ============================================================

DATA_PATH = "data/processed/tomato_forecasting_features.csv"

MODEL_DIR = "ml/models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "tomato_shock_detector.pkl"
)

RESULTS_PATH = os.path.join(
    MODEL_DIR,
    "tomato_shock_results.csv"
)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n" + "=" * 65)
print("VILAINILAI - SUPPLY / PRICE SHOCK DETECTION")
print("=" * 65)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")
print(f"Rows: {len(df):,}")


# ============================================================
# 2. DATE PROCESSING
# ============================================================

df["Arrival Date"] = pd.to_datetime(
    df["Arrival Date"],
    errors="coerce"
)

df = df.dropna(
    subset=["Arrival Date"]
)

df = df.sort_values(
    ["Market", "Arrival Date"]
).reset_index(drop=True)


# ============================================================
# 3. NUMERIC CONVERSION
# ============================================================

numeric_columns = [
    "Modal Price Per Kg",
    "Arrival Quantity Kg",
    "price_lag_1",
    "price_lag_7",
    "price_lag_14",
    "rolling_price_7",
    "rolling_price_14"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ============================================================
# 4. CREATE SHOCK FEATURES
# ============================================================

print("\nCreating shock features...")

# Percentage change in arrival quantity
df["arrival_change_pct"] = (
    df.groupby("Market")["Arrival Quantity Kg"]
    .pct_change()
    * 100
)

# Percentage change in price
df["price_change_pct"] = (
    df.groupby("Market")["Modal Price Per Kg"]
    .pct_change()
    * 100
)

# Difference between current price and 7-day rolling price
df["price_deviation_pct"] = (
    (
        df["Modal Price Per Kg"]
        - df["rolling_price_7"]
    )
    / df["rolling_price_7"].replace(0, np.nan)
) * 100


# Difference between current arrivals and recent average
df["arrival_deviation_pct"] = (
    (
        df["Arrival Quantity Kg"]
        - df.groupby("Market")[
            "Arrival Quantity Kg"
        ].transform(
            lambda x: x.rolling(
                window=7,
                min_periods=3
            ).mean()
        )
    )
    /
    df.groupby("Market")[
        "Arrival Quantity Kg"
    ].transform(
        lambda x: x.rolling(
            window=7,
            min_periods=3
        ).mean()
    ).replace(0, np.nan)
) * 100


# ============================================================
# 5. CLEAN SHOCK FEATURES
# ============================================================

shock_features = [
    "arrival_change_pct",
    "price_change_pct",
    "price_deviation_pct",
    "arrival_deviation_pct"
]

df_model = df.dropna(
    subset=shock_features
).copy()

print(
    f"Rows available for shock detection: "
    f"{len(df_model):,}"
)


# ============================================================
# 6. PREPARE FEATURES
# ============================================================

X = df_model[shock_features].copy()

# Limit extreme percentage values so that
# a single extreme observation doesn't dominate.
X = X.replace(
    [np.inf, -np.inf],
    np.nan
)

X = X.dropna()

df_model = df_model.loc[
    X.index
].copy()


# ============================================================
# 7. STANDARDIZATION
# ============================================================

scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)


# ============================================================
# 8. ISOLATION FOREST
# ============================================================

print("\n" + "-" * 65)
print("TRAINING ISOLATION FOREST...")
print("-" * 65)

detector = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42,
    n_jobs=-1
)

detector.fit(X_scaled)

print("Shock detection model trained!")


# ============================================================
# 9. ANOMALY PREDICTION
# ============================================================

predictions = detector.predict(
    X_scaled
)

anomaly_scores = detector.decision_function(
    X_scaled
)

df_model["anomaly_prediction"] = predictions

df_model["anomaly_score"] = anomaly_scores


# Isolation Forest:
# +1 = normal
# -1 = anomaly

df_model["overall_shock"] = np.where(
    df_model["anomaly_prediction"] == -1,
    "SHOCK",
    "NORMAL"
)


# ============================================================
# 10. SUPPLY SHOCK DETECTION
# ============================================================

# Large positive arrival deviation
# indicates unusually high supply.

df_model["supply_shock"] = np.where(
    df_model["arrival_deviation_pct"] >= 30,
    "SUPPLY SHOCK",
    "NORMAL"
)


# ============================================================
# 11. PRICE SHOCK DETECTION
# ============================================================

# Large price movement compared with
# the previous observation.

df_model["price_shock"] = np.where(
    df_model["price_change_pct"].abs() >= 15,
    "PRICE SHOCK",
    "NORMAL"
)


# ============================================================
# 12. COMBINED DECISION
# ============================================================

def determine_shock(row):

    if (
        row["supply_shock"] == "SUPPLY SHOCK"
        and
        row["price_shock"] == "PRICE SHOCK"
    ):
        return "SUPPLY + PRICE SHOCK"

    elif row["supply_shock"] == "SUPPLY SHOCK":
        return "SUPPLY SHOCK"

    elif row["price_shock"] == "PRICE SHOCK":
        return "PRICE SHOCK"

    elif row["overall_shock"] == "SHOCK":
        return "ANOMALY"

    return "NORMAL"


df_model["shock_status"] = (
    df_model.apply(
        determine_shock,
        axis=1
    )
)


# ============================================================
# 13. SUMMARY
# ============================================================

print("\n" + "=" * 65)
print("SHOCK DETECTION SUMMARY")
print("=" * 65)

print(
    "\nOverall Isolation Forest anomalies:"
)

print(
    df_model["overall_shock"]
    .value_counts()
    .to_string()
)

print(
    "\nSupply shocks:"
)

print(
    df_model["supply_shock"]
    .value_counts()
    .to_string()
)

print(
    "\nPrice shocks:"
)

print(
    df_model["price_shock"]
    .value_counts()
    .to_string()
)

print(
    "\nFinal shock status:"
)

print(
    df_model["shock_status"]
    .value_counts()
    .to_string()
)


# ============================================================
# 14. SHOW EXAMPLES
# ============================================================

shock_examples = df_model[
    df_model["shock_status"] != "NORMAL"
].copy()

print("\n" + "-" * 65)
print("SAMPLE DETECTED SHOCKS")
print("-" * 65)

if len(shock_examples) > 0:

    display_columns = [
        "Arrival Date",
        "Market",
        "Modal Price Per Kg",
        "Arrival Quantity Kg",
        "arrival_change_pct",
        "price_change_pct",
        "shock_status"
    ]

    print(
        shock_examples[
            display_columns
        ]
        .head(15)
        .to_string(index=False)
    )

else:

    print("No shocks detected.")


# ============================================================
# 15. SAVE MODEL + SCALER
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    {
        "detector": detector,
        "scaler": scaler,
        "features": shock_features
    },
    MODEL_PATH
)

print(
    f"\nModel saved to:"
    f"\n{MODEL_PATH}"
)


# ============================================================
# 16. SAVE RESULTS
# ============================================================

output_columns = [
    "Arrival Date",
    "Market",
    "District",
    "Modal Price Per Kg",
    "Arrival Quantity Kg",
    "arrival_change_pct",
    "price_change_pct",
    "price_deviation_pct",
    "arrival_deviation_pct",
    "anomaly_score",
    "overall_shock",
    "supply_shock",
    "price_shock",
    "shock_status"
]

df_model[
    output_columns
].to_csv(
    RESULTS_PATH,
    index=False
)

print(
    f"Results saved to:"
    f"\n{RESULTS_PATH}"
)


# ============================================================
# 17. FINAL
# ============================================================

print("\n" + "=" * 65)
print("SHOCK DETECTION COMPLETED")
print("=" * 65)