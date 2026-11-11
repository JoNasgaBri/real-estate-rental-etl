from datetime import datetime
from src.config import DEFAULT_CITY, DEFAULT_STATE
from src.extractors import fetch_rental_listings
from src.transformers import clean_rental_data
from src.exporters import export_data
from src.visualizers import generate_market_report


def run_pipeline(
    city: str = DEFAULT_CITY,
    state: str = DEFAULT_STATE,
    limit: int = 50,
    use_cache: bool = True,
) -> None:
    """Run the full ETL pipeline for rental listings."""
    start_time = datetime.now()
    print("=" * 65)
    print(f"STARTING ETL PIPELINE - {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target region: {city}, {state} | Max listings requested: {limit}")
    print("=" * 65)

    # 1. Bronze layer: ingestion
    raw_listings = fetch_rental_listings(
        city=city, state=state, limit=limit, use_cache=use_cache
    )

    # 2. Silver layer: cleaning + feature engineering
    clean_df = clean_rental_data(raw_listings)

    if clean_df.empty:
        print("[PIPELINE] No listings passed the validation checks.")
        return

    # 3. Gold layer: persist + visualize
    export_data(clean_df)
    generate_market_report(clean_df, city=city)

    # 4. Quick market summary for the terminal
    median_price = clean_df["price"].median()
    avg_price_per_sqft = clean_df["price_per_sqft"].mean()
    min_sqft_price = clean_df["price_per_sqft"].min()
    max_sqft_price = clean_df["price_per_sqft"].max()

    print("\n" + "=" * 65)
    print("MARKET INSIGHTS:")
    print(f"• Qualified listings: {len(clean_df)}")
    print(f"• Median rent: ${median_price:,.2f}/mo")
    print(f"• Avg price per sqft: ${avg_price_per_sqft:.2f}/sqft")
    print(f"• $/sqft range: ${min_sqft_price:.2f} - ${max_sqft_price:.2f}")
    print(
        f"Total runtime: {(datetime.now() - start_time).total_seconds():.2f}s"
    )
    print("=" * 65)


if __name__ == "__main__":
    # reuses the local cache when it exists
    run_pipeline(use_cache=True)
