# VilaiNilai — Member 1 Data Pipeline

## Responsibility

Data collection, cleaning, exploratory analysis and feature engineering.

## Data Source

AGMARKNET Daily Price and Arrival Report.

## Dataset

Tamil Nadu Tomato Market Data.

## Raw Dataset

`data/raw/tomato_market_raw.csv`

## Clean Dataset

`data/processed/tomato_market_clean.csv`

## Forecasting Dataset

`data/processed/tomato_forecasting_features.csv`

## Raw Data Coverage

- State: Tamil Nadu
- Commodity: Tomato
- Date range: 2025-11-07 to 2026-08-24
- Markets: 187
- Districts: 36
- Records: 43,719

## Important Raw Fields

| Field | Meaning |
|---|---|
| State/UT | State |
| District | District |
| Market | Agricultural market |
| Commodity | Crop |
| Variety | Tomato variety |
| Grade | Product grade |
| Min Price | Minimum price in Rs./Quintal |
| Max Price | Maximum price in Rs./Quintal |
| Modal Price | Modal price in Rs./Quintal |
| Arrival Quantity | Market arrival quantity |
| Arrival Date | Observation date |

## Converted Features

| Feature | Meaning |
|---|---|
| Arrival Quantity Kg | Arrival quantity converted to kilograms |
| Min Price Per Kg | Minimum price converted to ₹/kg |
| Max Price Per Kg | Maximum price converted to ₹/kg |
| Modal Price Per Kg | Modal price converted to ₹/kg |

## Forecasting Features

| Feature | Purpose |
|---|---|
| day_of_week | Weekly pattern |
| day_of_month | Calendar pattern |
| month | Seasonal pattern |
| week_of_year | Annual seasonal pattern |
| price_lag_1 | Previous market observation |
| price_lag_7 | Previous 7 observations |
| price_lag_14 | Previous 14 observations |
| rolling_price_7 | Recent 7-observation average |
| rolling_price_14 | Recent 14-observation average |

## Unit Conversions

1 quintal = 100 kg

1 metric tonne = 1,000 kg

Therefore:

`Price per kg = Price per quintal / 100`

`Arrival quantity kg = Arrival quantity metric tonnes × 1,000`

## Handoff to ML Member

The ML member should use:

`data/processed/tomato_forecasting_features.csv`

as the starting dataset for price forecasting.

The raw dataset must not be modified.