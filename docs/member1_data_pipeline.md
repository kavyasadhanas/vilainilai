# VilaiNilai — Member 1 Data Pipeline

## 1. Role

Member 1 is responsible for:

- Agricultural data collection
- Data cleaning
- Data validation
- Exploratory Data Analysis
- Feature engineering
- ML-ready dataset preparation

---

## 2. Data Source

Primary source:

AGMARKNET Daily Price and Arrival Report

Domain:

Tamil Nadu Tomato Markets

---

## 3. Raw Dataset

File:

`data/raw/tomato_market_raw.csv`

Records:

43,719

Coverage:

2025-11-07 to 2026-08-24

Markets:

187

Districts:

36

Commodity:

Tomato

---

## 4. Clean Dataset

File:

`data/processed/tomato_market_clean.csv`

Records:

43,719

Columns:

18

Cleaning performed:

- Corrected AGMARKNET CSV header
- Removed unwanted whitespace
- Converted price fields to numeric
- Converted arrival date to datetime
- Converted arrival quantity to kilograms
- Converted prices from Rs./Quintal to Rs./kg
- Checked invalid price relationships
- Checked duplicate records
- Sorted records chronologically

---

## 5. Unit Conversion

### Price

AGMARKNET:

`Rs./Quintal`

Conversion:

`Price per kg = Price per Quintal / 100`

### Arrival

AGMARKNET:

`Metric Tonnes`

Conversion:

`Arrival kg = Metric Tonnes × 1000`

---

## 6. Important Cleaned Columns

| Column | Description |
|---|---|
| State/UT | State |
| District | District |
| Market | Agricultural market |
| Commodity | Crop |
| Variety | Tomato variety |
| Grade | Product grade |
| Min Price Per Kg | Minimum tomato price per kg |
| Max Price Per Kg | Maximum tomato price per kg |
| Modal Price Per Kg | Modal tomato price per kg |
| Arrival Quantity Kg | Market arrival quantity in kg |
| Arrival Date | Market observation date |

---

## 7. Exploratory Analysis

The following analyses were performed:

- Overall tomato price statistics
- Market-wise average price
- District-wise average price
- Price trend over time
- Arrival quantity versus price
- Price volatility
- Price shock detection
- Market stability analysis

---

## 8. Forecasting Feature Dataset

File:

`data/processed/tomato_forecasting_features.csv`

Records:

41,110

Columns:

15

---

## 9. Forecasting Features

| Feature | Description |
|---|---|
| Arrival Date | Market observation date |
| Market | Market identifier |
| District | District |
| Variety | Tomato variety |
| Modal Price Per Kg | Current observed modal price |
| Arrival Quantity Kg | Market arrival quantity |
| day_of_week | Day of week |
| day_of_month | Day of month |
| month | Month |
| week_of_year | Week of year |
| price_lag_1 | Previous market observation price |
| price_lag_7 | Price from previous 7 observations |
| price_lag_14 | Price from previous 14 observations |
| rolling_price_7 | 7-observation rolling mean |
| rolling_price_14 | 14-observation rolling mean |

---

## 10. Important Note About Lag Features

`price_lag_7` and `price_lag_14` represent previous observations, not necessarily exactly 7 or 14 calendar days.

This is because market reporting may not occur every calendar day.

The forecasting member should account for this when building the final time-series model.

---

## 11. Handoff to Member 2

The primary handoff file is:

`data/processed/tomato_forecasting_features.csv`

The forecasting member can use this dataset to build the tomato price forecasting model.

The target variable is:

`Modal Price Per Kg`

---

## 12. Data Pipeline

AGMARKNET

↓

Raw Tomato Market Dataset

↓

Data Cleaning

↓

Unit Conversion

↓

Validation

↓

Exploratory Data Analysis

↓

Feature Engineering

↓

ML-Ready Forecasting Dataset

↓

Price Forecasting Model