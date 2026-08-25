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
# VILAINILAI - HYBRID XGBOOST PRICE FORECASTING
# ============================================================

DATA_PATH = "data/processed/tomato_forecasting_features.csv"

MODEL_DIR = "ml/models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "hybrid_xgboost_tomato_model.pkl"
)

PREDICTIONS_PATH = os.path.join(
    MODEL_DIR,
    "hybrid_xgboost_predictions.csv"
)

METRICS_PATH = os.path.join(
    MODEL_DIR,
    "hybrid_xgboost_metrics.json"
)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n" + "=" * 65)
print("VILAINILAI - HYBRID XGBOOST PRICE FORECASTING")
print("=" * 65)

df = pd.read_csv(DATA_PATH)

print(f"\nDataset shape: {df.shape}")
print(f"Rows: {len(df):,}")


# ============================================================
# 2. DATE PROCESSING
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
# 3. NUMERIC CLEANING
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
# 4. CREATE RESIDUAL TARGET
# ============================================================

# Instead of predicting the complete price,
# XGBoost predicts the correction needed
# over the previous price.

df["price_change"] = (
    df["Modal Price Per Kg"]
    - df["price_lag_1"]
)

print("\nResidual target created.")

print(
    f"Average price correction: "
    f"₹{df['price_change'].mean():.2f}/kg"
)


# ============================================================
# 5. FEATURES
# ============================================================

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

TARGET = "price_change"

X = df[features]

y = df[TARGET]


# ============================================================
# 6. DATE-BASED TRAIN / TEST SPLIT
# ============================================================

unique_dates = sorted(
    df["Arrival Date"].dt.date.unique()
)

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
    f"{df.loc[train_mask, 'Arrival Date'].min().date()}"
    f" → "
    f"{df.loc[train_mask, 'Arrival Date'].max().date()}"
)

print(
    f"Testing period : "
    f"{df.loc[test_mask, 'Arrival Date'].min().date()}"
    f" → "
    f"{df.loc[test_mask, 'Arrival Date'].max().date()}"
)


# ============================================================
# 7. BASELINE
# ============================================================

baseline_predictions = (
    df.loc[test_mask, "price_lag_1"]
    .values
)

actual_prices = (
    df.loc[test_mask, "Modal Price Per Kg"]
    .values
)


baseline_mae = mean_absolute_error(
    actual_prices,
    baseline_predictions
)

baseline_rmse = np.sqrt(
    mean_squared_error(
        actual_prices,
        baseline_predictions
    )
)

baseline_mape = (
    mean_absolute_percentage_error(
        actual_prices,
        baseline_predictions
    ) * 100
)

baseline_r2 = r2_score(
    actual_prices,
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
# 9. XGBOOST RESIDUAL MODEL
# ============================================================

model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.03,
    max_depth=6,
    min_child_weight=5,
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
            model
        )
    ]
)


# ============================================================
# 11. TRAIN
# ============================================================

print("\n" + "-" * 65)
print("TRAINING HYBRID XGBOOST...")
print("-" * 65)

pipeline.fit(
    X_train,
    y_train
)

print("Training completed!")


# ============================================================
# 12. PREDICT PRICE CORRECTION
# ============================================================

predicted_change = pipeline.predict(
    X_test
)


# ============================================================
# 13. CONVERT CORRECTION INTO PRICE
# ============================================================

previous_prices = (
    df.loc[test_mask, "price_lag_1"]
    .values
)

hybrid_predictions = (
    previous_prices
    + predicted_change
)


# ============================================================
# 14. EVALUATION
# ============================================================

mae = mean_absolute_error(
    actual_prices,
    hybrid_predictions
)

rmse = np.sqrt(
    mean_squared_error(
        actual_prices,
        hybrid_predictions
    )
)

mape = (
    mean_absolute_percentage_error(
        actual_prices,
        hybrid_predictions
    ) * 100
)

r2 = r2_score(
    actual_prices,
    hybrid_predictions
)


# ============================================================
# 15. RESULTS
# ============================================================

print("\n" + "=" * 65)
print("HYBRID XGBOOST RESULTS")
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
# 16. COMPARE WITH BASELINE
# ============================================================

print("\n" + "-" * 65)
print("HYBRID XGBOOST VS BASELINE")
print("-" * 65)

print(
    f"Baseline MAE : ₹{baseline_mae:.2f}/kg"
)

print(
    f"Hybrid MAE   : ₹{mae:.2f}/kg"
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
        "✅ HYBRID MODEL BEATS BASELINE!"
    )

else:

    difference = (
        (mae - baseline_mae)
        / baseline_mae
    ) * 100

    print(
        f"MAE difference: {difference:.2f}% worse"
    )

    print(
        "⚠️ Baseline remains better."
    )


# ============================================================
# 17. SAVE MODEL
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
# 18. SAVE PREDICTIONS
# ============================================================

results = pd.DataFrame({
    "Arrival Date":
        df.loc[
            test_mask,
            "Arrival Date"
        ].values,

    "Market":
        df.loc[
            test_mask,
            "Market"
        ].values,

    "Actual Price":
        actual_prices,

    "Previous Price":
        previous_prices,

    "Predicted Change":
        predicted_change,

    "Hybrid Predicted Price":
        hybrid_predictions
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
# 19. SAVE METRICS
# ============================================================

metrics = {
    "model": "Hybrid XGBoost",
    "target": "Modal Price Per Kg",
    "method": "Previous Price + XGBoost Predicted Correction",

    "training_rows":
        int(len(X_train)),

    "testing_rows":
        int(len(X_test)),

    "baseline_mae":
        round(float(baseline_mae), 4),

    "baseline_rmse":
        round(float(baseline_rmse), 4),

    "baseline_mape":
        round(float(baseline_mape), 4),

    "hybrid_mae":
        round(float(mae), 4),

    "hybrid_rmse":
        round(float(rmse), 4),

    "hybrid_mape":
        round(float(mape), 4),

    "hybrid_r2":
        round(float(r2), 4)
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
# 20. SAMPLE PREDICTIONS
# ============================================================

print("\n" + "=" * 65)
print("SAMPLE HYBRID PREDICTIONS")
print("=" * 65)

print(
    results.head(10).to_string(
        index=False
    )
)

print("\n" + "=" * 65)
print("HYBRID FORECASTING COMPLETED")
print("=" * 65)