from pathlib import Path
import pandas as pd
from src.config import PROCESSED_DATA_DIR


def export_data(
    df: pd.DataFrame,
    csv_filename: str = "clean_listings.csv",
    json_filename: str = "clean_listings.json",
) -> dict[str, Path]:

    if df.empty:
        print("[EXPORT] Empty DataFrame - nothing exported.")
        return {}

    csv_path = PROCESSED_DATA_DIR / csv_filename
    json_path = PROCESSED_DATA_DIR / json_filename

    # 1. CSV export
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"[EXPORT] CSV saved: {csv_path} ({len(df)} rows)")

    # 2. JSON export
    df.to_json(json_path, orient="records", indent=2, force_ascii=False)
    print(f"[EXPORT] JSON saved: {json_path}")

    return {"csv": csv_path, "json": json_path}


if __name__ == "__main__":
    # quick manual test
    sample_df = pd.DataFrame([{"address": "Test Ave", "price": 2500, "sqft": 750}])
    export_data(
        sample_df, csv_filename="test_export.csv", json_filename="test_export.json"
    )
