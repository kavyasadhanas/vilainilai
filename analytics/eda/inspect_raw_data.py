import pandas as pd

FILE_PATH = "data/raw/tomato_market_raw.csv"

# AGMARKNET export contains the real column names in the first row
df = pd.read_csv(FILE_PATH, header=1)

print("\n===== DATASET SHAPE =====")
print(df.shape)

print("\n===== COLUMNS =====")
print(df.columns.tolist())

print("\n===== FIRST 5 ROWS =====")
print(df.head().to_string())

print("\n===== DATA TYPES =====")
print(df.dtypes)

print("\n===== MISSING VALUES =====")
print(df.isnull().sum())

print("\n===== UNIQUE COUNTS =====")

for column in ["State/UT", "District", "Market", "Commodity", "Variety", "Grade"]:
    if column in df.columns:
        print(f"\n{column}: {df[column].nunique()} unique values")
        print(df[column].dropna().unique()[:20])

print("\n===== DATE RANGE =====")

if "Arrival Date" in df.columns:
    dates = pd.to_datetime(
        df["Arrival Date"],
        format="%d-%m-%Y",
        errors="coerce"
    )

    print("Minimum:", dates.min())
    print("Maximum:", dates.max())

print("\n===== DUPLICATE ROWS =====")
print(df.duplicated().sum())