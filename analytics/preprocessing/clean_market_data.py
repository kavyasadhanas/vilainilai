import pandas as pd

RAW_FILE = "data/raw/tomato_market_raw.csv"
OUTPUT_FILE = "data/processed/tomato_market_clean.csv"


def clean_market_data():
    # Read AGMARKNET CSV.
    # The first row contains the actual column names.
    df = pd.read_csv(RAW_FILE, header=1)

    # Remove accidental spaces from column names
    df.columns = df.columns.str.strip()

    # Standardize text columns
    text_columns = [
        "State/UT",
        "District",
        "Market",
        "Commodity Group",
        "Commodity",
        "Variety",
        "Grade",
        "Price Unit",
        "Arrival Unit",
    ]

    for column in text_columns:
        df[column] = df[column].astype(str).str.strip()

    # Convert prices from strings such as "5,400.00" to numbers
    price_columns = [
        "Min Price",
        "Max Price",
        "Modal Price",
    ]

    for column in price_columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.strip()
        )

        df[column] = pd.to_numeric(df[column], errors="coerce")

    # Convert arrival date
    df["Arrival Date"] = pd.to_datetime(
        df["Arrival Date"],
        format="%d-%m-%Y",
        errors="coerce",
    )

    # Convert arrival quantity from Metric Tonnes to kilograms
    df["Arrival Quantity"] = pd.to_numeric(
        df["Arrival Quantity"],
        errors="coerce",
    )

    df["Arrival Quantity Kg"] = df["Arrival Quantity"] * 1000

    # Convert prices from Rs./Quintal to Rs./Kg
    df["Min Price Per Kg"] = df["Min Price"] / 100
    df["Max Price Per Kg"] = df["Max Price"] / 100
    df["Modal Price Per Kg"] = df["Modal Price"] / 100

    # Remove records where essential numeric/date values could not be converted
    df = df.dropna(
        subset=[
            "Arrival Date",
            "Min Price Per Kg",
            "Max Price Per Kg",
            "Modal Price Per Kg",
            "Arrival Quantity Kg",
        ]
    )

    # Validate price relationships
    invalid_prices = (
        (df["Min Price Per Kg"] > df["Modal Price Per Kg"])
        | (df["Modal Price Per Kg"] > df["Max Price Per Kg"])
    )

    print(f"Invalid price records found: {invalid_prices.sum()}")

    # Remove invalid price records
    df = df[~invalid_prices].copy()

    # Remove exact duplicate records
    before_duplicates = len(df)

    df = df.drop_duplicates()

    duplicates_removed = before_duplicates - len(df)

    print(f"Duplicate records removed: {duplicates_removed}")

    # Sort chronologically
    df = df.sort_values(
        by=["Arrival Date", "Market", "Variety"]
    ).reset_index(drop=True)

    # Save cleaned dataset
    df.to_csv(OUTPUT_FILE, index=False)

    print("\n===== CLEANING COMPLETE =====")
    print(f"Rows: {len(df)}")
    print(f"Columns: {len(df.columns)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    clean_market_data()