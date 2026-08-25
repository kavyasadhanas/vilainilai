import os
import json
import joblib
import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    mean_absolute_percentage_error,
    r2_score
)

from xgboost import XGBRegressor


# ============================================================
# VILAINILAI - XGBOOST TOMATO PRICE FORECASTING
# ============================================================

DATA_PATH = "data/processed/tomato_forecasting_features.csv"

MODEL_DIR = "ml/models"
MODEL_PATH = os.path.join(
    MODEL_DIR,
    "xgboost_tomato_price_model.pkl"
)

PREDICTIONS_PATH = os.path.join(
    MODEL_DIR,
    "xgboost_test_predictions.csv"
)

METRICS_PATH = os.path.join(
    MODEL_DIR,
    "xgboost_metrics.json"
)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n" + "=" * 65)
print("VILAINILAI - XGBOOST PRICE FORECASTING")
print("=" * 65)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"Dataset shape: {df.shape}")
print(f"Rows: {len(df):,}")
print(f"Columns: {len(df.columns)}")


# ============================================================
# 2. REQUIRED COLUMNS
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
        f"Missing columns: {missing_columns}"
    )

print("Required columns: OK")


# ============================================================
# 3. DATE PROCESSING
# ============================================================

df["Arrival Date"] = pd.to_datetime(
    df["Arrival Date"],
    dayfirst=True,
    errors="coerce"
)

df = df.dropna(
    subset=["Arrival Date"]
)

df = df.sort_values(
    "Arrival Date"
).reset_index(drop=True)


# ============================================================
# 4. NUMERIC DATA CLEANING
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

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

df = df.dropna(
    subset=numeric_columns + [
        "Market",
        "District",
        "Variety"
    ]
).reset_index(drop=True)

print(
    f"Rows after cleaning: {len(df):,}"
)


# ============================================================
# 5. FEATURES + TARGET
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
# 6. PROPER DATE-BASED TRAIN / TEST SPLIT
# ============================================================

# Get unique dates
unique_dates = sorted(
    df["Arrival Date"].dt.date.unique()
)

# 80% of dates for training
split_position = int(
    len(unique_dates) * 0.80
)

cutoff_date = unique_dates[split_position]

train_mask = (
    df["Arrival Date"].dt.date < cutoff_date
)

test_mask = (
    df["Arrival Date"].dt.date >= cutoff_date
)

X_train = X.loc[train_mask]
X_test = X.loc[test_mask]

y_train = y.loc[train_mask]
y_test = y.loc[test_mask]

train_dates = df.loc[
    train_mask,
    "Arrival Date"
]

test_dates = df.loc[
    test_mask,
    "Arrival Date"
]


print("\n" + "-" * 65)
print("DATE-BASED TRAIN / TEST SPLIT")
print("-" * 65)

print(
    f"Training rows : {len(X_train):,}"
)

print(
    f"Testing rows  : {len(X_test):,}"
)

print(
    f"Training period: "
    f"{train_dates.min().date()} → "
    f"{train_dates.max().date()}"
)

print(
    f"Testing period : "
    f"{test_dates.min().date()} → "
    f"{test_dates.max().date()}"
)

print(
    f"Cutoff date    : {cutoff_date}"
)


# ============================================================
# 7. BASELINE
# ============================================================

baseline_predictions = X_test[
    "price_lag_1"
].values

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

baseline_mape = (
    mean_absolute_percentage_error(
        y_test,
        baseline_predictions
    ) * 100
)

baseline_r2 = r2_score(
    y_test,
    baseline_predictions
)


print("\n" + "-" * 65)
print("BASELINE - PREVIOUS PRICE")
print("-" * 65)

print(
    f"MAE  : ₹{baseline_mae:.2f}/kg"
)

print(
    f"RMSE : ₹{baseline_rmse:.2f}/kg"
)

print(
    f"MAPE : {baseline_mape:.2f}%"
)

print(
    f"R²   : {baseline_r2:.4f}"
)


# ============================================================
# 8. PREPROCESSING
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
# 9. XGBOOST MODEL
# ============================================================

xgb_model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.05,
    max_depth=8,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="reg:squarederror",
    eval_metric="rmse",
    random_state=42,
    n_jobs=-1
)


# ============================================================
# 10. PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor
        ),
        (
            "model",
            xgb_model
        )
    ]
)


# ============================================================
# 11. TRAIN
# ============================================================

print("\n" + "-" * 65)
print("TRAINING XGBOOST...")
print("-" * 65)

pipeline.fit(
    X_train,
    y_train
)

print("XGBoost training completed!")


# ============================================================
# 12. PREDICT
# ============================================================

print("\nGenerating predictions...")

predictions = pipeline.predict(
    X_test
)


# ============================================================
# 13. EVALUATION
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

mape = (
    mean_absolute_percentage_error(
        y_test,
        predictions
    ) * 100
)

r2 = r2_score(
    y_test,
    predictions
)


# ============================================================
# 14. RESULTS
# ============================================================

print("\n" + "=" * 65)
print("XGBOOST RESULTS")
print("=" * 65)

print(
    f"MAE  : ₹{mae:.2f}/kg"
)

print(
    f"RMSE : ₹{rmse:.2f}/kg"
)

print(
    f"MAPE : {mape:.2f}%"
)

print(
    f"R²   : {r2:.4f}"
)


# ============================================================
# 15. COMPARE WITH BASELINE
# ============================================================

print("\n" + "-" * 65)
print("XGBOOST VS BASELINE")
print("-" * 65)

print(
    f"Baseline MAE : ₹{baseline_mae:.2f}/kg"
)

print(
    f"XGBoost MAE  : ₹{mae:.2f}/kg"
)

if mae < baseline_mae:

    improvement = (
        (baseline_mae - mae)
        / baseline_mae
    ) * 100

    print(
        f"MAE improvement: {improvement:.2f}%"
    )

    print(
        "✅ XGBoost beats the baseline!"
    )

else:

    print(
        "⚠️ XGBoost did not beat the baseline."
    )


# ============================================================
# 16. SAVE MODEL
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
    f"\nModel saved to:"
    f"\n{MODEL_PATH}"
)


# ============================================================
# 17. SAVE PREDICTIONS
# ============================================================

results = pd.DataFrame({
    "Arrival Date": test_dates.values,
    "Market": df.loc[
        test_mask,
        "Market"
    ].values,
    "Actual Price": y_test.values,
    "XGBoost Predicted Price": predictions,
    "Baseline Price": baseline_predictions
})

results.to_csv(
    PREDICTIONS_PATH,
    index=False
)

print(
    f"Predictions saved to:"
    f"\n{PREDICTIONS_PATH}"
)


# ============================================================
# 18. SAVE METRICS
# ============================================================

metrics = {
    "model": "XGBoost",
    "target": "Modal Price Per Kg",
    "unit": "INR/kg",
    "training_rows": int(len(X_train)),
    "testing_rows": int(len(X_test)),
    "training_start": str(
        train_dates.min().date()
    ),
    "training_end": str(
        train_dates.max().date()
    ),
    "testing_start": str(
        test_dates.min().date()
    ),
    "testing_end": str(
        test_dates.max().date()
    ),
    "baseline_mae": round(
        float(baseline_mae), 4
    ),
    "baseline_rmse": round(
        float(baseline_rmse), 4
    ),
    "baseline_mape": round(
        float(baseline_mape), 4
    ),
    "xgboost_mae": round(
        float(mae), 4
    ),
    "xgboost_rmse": round(
        float(rmse), 4
    ),
    "xgboost_mape": round(
        float(mape), 4
    ),
    "xgboost_r2": round(
        float(r2), 4
    )
}

with open(
    METRICS_PATH,
    "w"
) as file:

    json.dump(
        metrics,
        file,
        indent=4
    )

print(
    f"Metrics saved to:"
    f"\n{METRICS_PATH}"
)


# ============================================================
# 19. SAMPLE PREDICTIONS
# ============================================================

print("\n" + "=" * 65)
print("SAMPLE XGBOOST PREDICTIONS")
print("=" * 65)

print(
    results.head(10).to_string(
        index=False
    )
)

print("\n" + "=" * 65)
print("XGBOOST PRICE FORECASTING COMPLETED")
print("=" * 65)