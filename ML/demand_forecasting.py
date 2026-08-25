import os
import json
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)

from xgboost import XGBClassifier


# ============================================================
# VILAINILAI - DEMAND DIRECTION FORECASTING
# ============================================================

DATA_PATH = "data/processed/tomato_forecasting_features.csv"

MODEL_DIR = "ml/models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "tomato_demand_model.pkl"
)

PREDICTIONS_PATH = os.path.join(
    MODEL_DIR,
    "tomato_demand_predictions.csv"
)

METRICS_PATH = os.path.join(
    MODEL_DIR,
    "tomato_demand_metrics.json"
)


# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n" + "=" * 65)
print("VILAINILAI - DEMAND DIRECTION FORECASTING")
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


# ============================================================
# 4. CREATE FUTURE ARRIVAL TARGET
# ============================================================
#
# The dataset does not contain direct consumer-demand data.
#
# Therefore, we use future market arrivals as a
# demand-pressure proxy.
#
# We compare tomorrow's arrival quantity with today's
# arrival quantity for the same market.
# ============================================================

df["next_arrival_quantity"] = (
    df.groupby("Market")[
        "Arrival Quantity Kg"
    ].shift(-1)
)

df["arrival_change_future_pct"] = (
    (
        df["next_arrival_quantity"]
        - df["Arrival Quantity Kg"]
    )
    /
    df["Arrival Quantity Kg"].replace(
        0,
        pd.NA
    )
) * 100


# ============================================================
# 5. CREATE DEMAND-DIRECTION LABEL
# ============================================================
#
# > +10%  → INCREASING
# < -10%  → DECREASING
# Otherwise → STABLE
#
# This is a demand-pressure proxy.
# ============================================================

def create_demand_label(change):

    if pd.isna(change):
        return pd.NA

    if change > 10:
        return "INCREASING"

    elif change < -10:
        return "DECREASING"

    else:
        return "STABLE"


df["demand_direction"] = (
    df["arrival_change_future_pct"]
    .apply(create_demand_label)
)


# Remove rows without a valid future target
df = df.dropna(
    subset=["demand_direction"]
).reset_index(drop=True)


print("\nDemand direction labels created.")

print(
    df["demand_direction"]
    .value_counts()
    .to_string()
)


# ============================================================
# 6. FEATURES
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

TARGET = "demand_direction"

X = df[features]

y = df[TARGET]


# ============================================================
# 7. DATE-BASED TRAIN / TEST SPLIT
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
# 8. ENCODE TARGET
# ============================================================

label_mapping = {
    "DECREASING": 0,
    "STABLE": 1,
    "INCREASING": 2
}

reverse_mapping = {
    0: "DECREASING",
    1: "STABLE",
    2: "INCREASING"
}

y_train_encoded = y_train.map(
    label_mapping
)

y_test_encoded = y_test.map(
    label_mapping
)


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
# 10. XGBOOST CLASSIFIER
# ============================================================

model = XGBClassifier(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    min_child_weight=3,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="multi:softprob",
    num_class=3,
    eval_metric="mlogloss",
    random_state=42,
    n_jobs=-1
)


# ============================================================
# 11. PIPELINE
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
# 12. TRAIN
# ============================================================

print("\n" + "-" * 65)
print("TRAINING XGBOOST DEMAND MODEL...")
print("-" * 65)

pipeline.fit(
    X_train,
    y_train_encoded
)

print("Demand model training completed!")


# ============================================================
# 13. PREDICTION
# ============================================================

predicted_labels = pipeline.predict(
    X_test
)

predicted_probabilities = (
    pipeline.predict_proba(
        X_test
    )
)


# ============================================================
# 14. EVALUATION
# ============================================================

accuracy = accuracy_score(
    y_test_encoded,
    predicted_labels
)

precision = precision_score(
    y_test_encoded,
    predicted_labels,
    average="weighted",
    zero_division=0
)

recall = recall_score(
    y_test_encoded,
    predicted_labels,
    average="weighted",
    zero_division=0
)

f1 = f1_score(
    y_test_encoded,
    predicted_labels,
    average="weighted",
    zero_division=0
)


# ============================================================
# 15. RESULTS
# ============================================================

print("\n" + "=" * 65)
print("DEMAND DIRECTION RESULTS")
print("=" * 65)

print(
    f"Accuracy  : {accuracy * 100:.2f}%"
)

print(
    f"Precision : {precision * 100:.2f}%"
)

print(
    f"Recall    : {recall * 100:.2f}%"
)

print(
    f"F1 Score  : {f1 * 100:.2f}%"
)

print("\nClassification Report:")

print(
    classification_report(
        y_test_encoded,
        predicted_labels,
        labels=[0, 1, 2],
        target_names=[
            "DECREASING",
            "STABLE",
            "INCREASING"
        ],
        zero_division=0
    )
)


# ============================================================
# 16. CREATE CORRECTLY ALIGNED PREDICTION OUTPUT
# ============================================================

# IMPORTANT:
# Use the exact test dataframe rows so that actual
# and predicted values stay aligned.

test_results = df.loc[
    test_mask,
    [
        "Arrival Date",
        "Market",
        "demand_direction"
    ]
].copy()

test_results = test_results.reset_index(
    drop=True
)

test_results["Actual Demand Direction"] = (
    test_results["demand_direction"]
)

test_results["Predicted Demand Direction"] = (
    pd.Series(
        predicted_labels
    )
    .map(reverse_mapping)
)

test_results["Prediction Confidence"] = (
    predicted_probabilities.max(
        axis=1
    ) * 100
)

test_results["Prediction Confidence"] = (
    test_results[
        "Prediction Confidence"
    ].round(2)
)

results = test_results[
    [
        "Arrival Date",
        "Market",
        "Actual Demand Direction",
        "Predicted Demand Direction",
        "Prediction Confidence"
    ]
].copy()


# ============================================================
# 17. SAVE MODEL
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

joblib.dump(
    {
        "model": pipeline,
        "label_mapping": label_mapping,
        "reverse_mapping": reverse_mapping,
        "target_type":
            "arrival-based demand direction proxy"
    },
    MODEL_PATH
)

print(
    f"\nModel saved to:"
    f"\n{MODEL_PATH}"
)


# ============================================================
# 18. SAVE PREDICTIONS
# ============================================================

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
    "model": "XGBoost Classifier",
    "task": "Demand direction classification",
    "target":
        "Arrival-based demand direction proxy",

    "training_rows":
        int(len(X_train)),

    "testing_rows":
        int(len(X_test)),

    "accuracy":
        round(float(accuracy), 4),

    "precision":
        round(float(precision), 4),

    "recall":
        round(float(recall), 4),

    "f1_score":
        round(float(f1), 4),

    "label_definition": {
        "INCREASING":
            "Future arrival quantity increases by >10%",
        "STABLE":
            "Future arrival quantity changes by -10% to +10%",
        "DECREASING":
            "Future arrival quantity decreases by >10%"
    }
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
print("SAMPLE DEMAND PREDICTIONS")
print("=" * 65)

print(
    results.head(10).to_string(
        index=False
    )
)

print("\n" + "=" * 65)
print("DEMAND FORECASTING COMPLETED")
print("=" * 65)