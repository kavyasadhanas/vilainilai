import os
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error,
    r2_score
)


# ============================================================
# 1. PATHS
# ============================================================

DATA_PATH = "data/processed/tomato_forecasting_features.csv"

MODEL_DIR = "ml/models"
MODEL_PATH = os.path.join(MODEL_DIR, "tomato_price_model.pkl")
PREDICTIONS_PATH = "ml/models/test_predictions.csv"


# ============================================================
# 2. LOAD DATA
# ============================================================

print("\n" + "=" * 60)
print("VILAINILAI - TOMATO PRICE FORECASTING")
print("=" * 60)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# 3. BASIC VALIDATION
# ============================================================

required_columns = [
    "Arrival Date",
    "Market",
    "District",
    "Variety",
    "Modal Price Per Kg",
    "Arrival Quantity Kg",
    "day_of_week",
    "day_of_month",
    "month",
    "week_of_year",
    "price_lag_1",
    "price_lag_7",
    "price_lag_14",
    "rolling_price_7",
    "rolling_price_14"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

print("\nRequired columns: OK")


# ============================================================
# 4. DATE PROCESSING
# ============================================================

df["Arrival Date"] = pd.to_datetime(
    df["Arrival Date"],
    dayfirst=True,
    errors="coerce"
)

if df["Arrival Date"].isna().any():
    print("Warning: Some dates could not be parsed.")

df = df.dropna(subset=["Arrival Date"])

# Sort chronologically
df = df.sort_values("Arrival Date").reset_index(drop=True)


# ============================================================
# 5. HANDLE NUMERIC COLUMNS
# ============================================================

numeric_columns = [
    "Modal Price Per Kg",
    "Arrival Quantity Kg",
    "day_of_week",
    "day_of_month",
    "month",
    "week_of_year",
    "price_lag_1",
    "price_lag_7",
    "price_lag_14",
    "rolling_price_7",
    "rolling_price_14"
]

for col in numeric_columns:
    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# Remove rows with missing values in model columns
df = df.dropna(
    subset=numeric_columns + [
        "Market",
        "District",
        "Variety"
    ]
).reset_index(drop=True)

print(f"Rows after cleaning: {len(df):,}")


# ============================================================
# 6. FEATURES AND TARGET
# ============================================================

TARGET = "Modal Price Per Kg"

features = [
    "Market",
    "District",
    "Variety",
    "Arrival Quantity Kg",
    "day_of_week",
    "day_of_month",
    "month",
    "week_of_year",
    "price_lag_1",
    "price_lag_7",
    "price_lag_14",
    "rolling_price_7",
    "rolling_price_14"
]

X = df[features]
y = df[TARGET]


# ============================================================
# 7. TIME-BASED TRAIN / TEST SPLIT
# ============================================================

# IMPORTANT:
# We do NOT randomly shuffle time-series data.

split_index = int(len(df) * 0.80)

X_train = X.iloc[:split_index]
X_test = X.iloc[split_index:]

y_train = y.iloc[:split_index]
y_test = y.iloc[split_index:]

train_dates = df["Arrival Date"].iloc[:split_index]
test_dates = df["Arrival Date"].iloc[split_index:]

print("\n" + "-" * 60)
print("TIME-BASED SPLIT")
print("-" * 60)

print(f"Training rows : {len(X_train):,}")
print(f"Testing rows  : {len(X_test):,}")

print(
    f"Training period: "
    f"{train_dates.min().date()} → {train_dates.max().date()}"
)

print(
    f"Testing period : "
    f"{test_dates.min().date()} → {test_dates.max().date()}"
)


# ============================================================
# 8. BASELINE MODEL
# ============================================================

# A simple baseline:
# tomorrow/current price prediction = previous available price

baseline_predictions = X_test["price_lag_1"].values

baseline_mae = mean_absolute_error(
    y_test,
    baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        baseline_predictions
    )
)

baseline_mape = mean_absolute_percentage_error(
    y_test,
    baseline_predictions
) * 100

print("\n" + "-" * 60)
print("BASELINE RESULTS")
print("-" * 60)

print(f"Baseline MAE  : ₹{baseline_mae:.2f}/kg")
print(f"Baseline RMSE : ₹{baseline_rmse:.2f}/kg")
print(f"Baseline MAPE : {baseline_mape:.2f}%")


# ============================================================
# 9. PREPROCESSING
# ============================================================

categorical_features = [
    "Market",
    "District",
    "Variety"
]

numeric_features = [
    "Arrival Quantity Kg",
    "day_of_week",
    "day_of_month",
    "month",
    "week_of_year",
    "price_lag_1",
    "price_lag_7",
    "price_lag_14",
    "rolling_price_7",
    "rolling_price_14"
]

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            categorical_features
        ),
        (
            "numeric",
            "passthrough",
            numeric_features
        )
    ]
)


# ============================================================
# 10. RANDOM FOREST MODEL
# ============================================================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ============================================================
# 11. TRAIN MODEL
# ============================================================

print("\n" + "-" * 60)
print("TRAINING RANDOM FOREST...")
print("-" * 60)

pipeline.fit(
    X_train,
    y_train
)

print("Training completed!")


# ============================================================
# 12. PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

predictions = pipeline.predict(X_test)


# ============================================================
# 13. MODEL EVALUATION
# ============================================================

mae = mean_absolute_error(
    y_test,
    predictions
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        predictions
    )
)

mape = mean_absolute_percentage_error(
    y_test,
    predictions
) * 100

r2 = r2_score(
    y_test,
    predictions
)


# ============================================================
# 14. DISPLAY RESULTS
# ============================================================

print("\n" + "=" * 60)
print("RANDOM FOREST RESULTS")
print("=" * 60)

print(f"MAE  : ₹{mae:.2f}/kg")
print(f"RMSE : ₹{rmse:.2f}/kg")
print(f"MAPE : {mape:.2f}%")
print(f"R²   : {r2:.4f}")

print("\n" + "-" * 60)
print("MODEL VS BASELINE")
print("-" * 60)

print(
    f"Baseline MAE : ₹{baseline_mae:.2f}/kg"
)

print(
    f"Model MAE    : ₹{mae:.2f}/kg"
)

if mae < baseline_mae:
    improvement = (
        (baseline_mae - mae)
        / baseline_mae
    ) * 100

    print(
        f"MAE improvement: {improvement:.2f}%"
    )

    print("✅ Model beats the baseline!")
else:
    print(
        "⚠️ Model did not beat the baseline."
    )


# ============================================================
# 15. SAVE MODEL
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    pipeline,
    MODEL_PATH
)

print(
    f"\nModel saved to: {MODEL_PATH}"
)


# ============================================================
# 16. SAVE TEST PREDICTIONS
# ============================================================

results = pd.DataFrame({
    "Arrival Date": test_dates.values,
    "Market": df["Market"].iloc[split_index:].values,
    "Actual Price": y_test.values,
    "Predicted Price": predictions,
    "Baseline Price": baseline_predictions
})

results.to_csv(
    PREDICTIONS_PATH,
    index=False
)

print(
    f"Predictions saved to: {PREDICTIONS_PATH}"
)


# ============================================================
# 17. SAMPLE PREDICTIONS
# ============================================================

print("\n" + "=" * 60)
print("SAMPLE PREDICTIONS")
print("=" * 60)

print(
    results.head(10).to_string(
        index=False
    )
)

print("\n" + "=" * 60)
print("PRICE FORECASTING COMPLETED")
print("=" * 60)