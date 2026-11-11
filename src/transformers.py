import json
from typing import Any
import pandas as pd
from src.config import RAW_DATA_DIR, SQFT_TO_M2_FACTOR

RAW_FILE_PATH = RAW_DATA_DIR / "sample_raw.json"


def clean_rental_data(raw_data: list[dict[str, Any]]) -> pd.DataFrame:
    """
    Clean, type and derive investment metrics from the raw payload.

    - dedupe on id + formattedAddress
    - drop rows missing price/squareFootage (can't value those)
    - strict numeric typing
    - derived metrics: price_per_sqft, area_m2, price_per_m2
    - sanity filter for outliers/zero values
    """
    total_raw = len(raw_data)
    if total_raw == 0:
        print("[WARN] Empty raw payload received for transformation.")
        return pd.DataFrame()

    df = pd.DataFrame(raw_data)

    # 1. keep only the columns I actually use
    expected_cols = [
        "id",
        "formattedAddress",
        "city",
        "state",
        "zipCode",
        "price",
        "squareFootage",
        "bedrooms",
        "bathrooms",
        "propertyType",
        "daysOnMarket",
        "status",
    ]
    existing_cols = [c for c in expected_cols if c in df.columns]
    df = df[existing_cols].copy()

    # 2. drop duplicates
    subset_dedup = [c for c in ["id", "formattedAddress"] if c in df.columns]
    df = df.drop_duplicates(subset=subset_dedup)

    # 3. enforce numeric types
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["squareFootage"] = pd.to_numeric(df["squareFootage"], errors="coerce")

    if "bedrooms" in df.columns:
        df["bedrooms"] = (
            pd.to_numeric(df["bedrooms"], errors="coerce").fillna(0).astype(int)
        )
    if "bathrooms" in df.columns:
        df["bathrooms"] = (
            pd.to_numeric(df["bathrooms"], errors="coerce").fillna(1.0).astype(float)
        )
    if "daysOnMarket" in df.columns:
        df["daysOnMarket"] = (
            pd.to_numeric(df["daysOnMarket"], errors="coerce").fillna(0).astype(int)
        )

    # 4. business sanity filter
    # no price or no size = nothing to value
    df = df.dropna(subset=["price", "squareFootage"])
    df = df[(df["price"] > 100) & (df["squareFootage"] > 50)]

    # 5. valuation metrics
    # native US metric: price per square foot
    df["price_per_sqft"] = (df["price"] / df["squareFootage"]).round(2)

    # also normalize to m² for international readers
    df["area_m2"] = (df["squareFootage"] * SQFT_TO_M2_FACTOR).round(2)
    df["price_per_m2"] = (df["price"] / df["area_m2"]).round(2)

    # 6. normalize category labels
    if "propertyType" in df.columns:
        df["propertyType"] = (
            df["propertyType"].fillna("Other").astype(str).str.strip().str.title()
        )

    total_clean = len(df)
    discarded = total_raw - total_clean
    print(
        f"[TRANSFORM] In: {total_raw} | Kept: {total_clean} | Dropped: {discarded}"
    )

    return df


if __name__ == "__main__":
    if not RAW_FILE_PATH.exists():
        print(
            f"[ERROR] {RAW_FILE_PATH} not found - run extractors.py first."
        )
    else:
        with open(RAW_FILE_PATH, "r", encoding="utf-8") as f:
            raw_records = json.load(f)

        df_cleaned = clean_rental_data(raw_records)
        print("\n--- First 3 rows of the cleaned DataFrame ---")
        print(
            df_cleaned[
                [
                    "formattedAddress",
                    "price",
                    "squareFootage",
                    "price_per_sqft",
                    "area_m2",
                ]
            ].head(3)
        )
