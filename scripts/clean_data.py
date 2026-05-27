import pandas as pd
import os

RAW_PATH   = "data/raw/air_quality.csv"
CLEAN_PATH = "data/cleaned/air_quality_cleaned.csv"


def main():
    print(f"Reading: {RAW_PATH}")
    df = pd.read_csv(RAW_PATH)

    print(f"Raw rows:   {len(df)}")
    print(f"Columns:    {list(df.columns)}")

    # Normalize column names to snake_case
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
        .str.replace(r"[^a-z0-9_]", "", regex=True)
    )
    print(f"Normalized: {list(df.columns)}")

    # Convert types
    df["unique_id"]    = pd.to_numeric(df["unique_id"],    errors="coerce")
    df["indicator_id"] = pd.to_numeric(df["indicator_id"], errors="coerce")
    df["start_date"]   = pd.to_datetime(df["start_date"],  errors="coerce")
    df["data_value"]   = pd.to_numeric(df["data_value"],   errors="coerce")

    # Remove duplicates by unique_id
    before = len(df)
    df = df.drop_duplicates(subset=["unique_id"])
    print(f"Removed {before - len(df)} duplicate rows by unique_id")

    os.makedirs(os.path.dirname(CLEAN_PATH), exist_ok=True)
    df.to_csv(CLEAN_PATH, index=False)
    print(f"Saved:      {CLEAN_PATH}")
    print(f"Final rows: {len(df)}")


if __name__ == "__main__":
    main()
