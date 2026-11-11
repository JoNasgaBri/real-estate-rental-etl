from pathlib import Path
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import seaborn as sns
from src.config import BASE_DIR, PROCESSED_DATA_DIR

FIGURES_DIR = BASE_DIR / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


def generate_market_report(df: pd.DataFrame, city: str = "Miami") -> Path | None:
    """
    Executive market snapshot saved as a single PNG with the 3 charts
    I care about most:

    1. scatter - sqft vs rent, colored by property type (bargain hunting)
    2. bar - avg $/sqft by ZIP code (top 8)
    3. box - rent distribution by bedroom count
    """
    if df.empty:
        print("[VISUALIZER] Empty DataFrame - no charts generated.")
        return None

    # clean, presentation-ready style
    sns.set_theme(style="whitegrid", palette="deep")
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle(
        f"Real Estate Rental Market Overview - {city} (n={len(df)} active listings)",
        fontsize=16,
        fontweight="bold",
        y=1.02,
    )

    # 1. scatter: price vs area (bargain hunter view)
    sns.scatterplot(
        data=df,
        x="squareFootage",
        y="price",
        hue="propertyType",
        size="price_per_sqft",
        sizes=(60, 250),
        alpha=0.85,
        ax=axes[0],
    )
    axes[0].set_title("Price vs. Square Footage (Bargain Hunter)", fontweight="bold")
    axes[0].set_xlabel("Square Footage (sqft)")
    axes[0].set_ylabel("Monthly Rent ($ USD)")
    axes[0].legend(title="Type / $/sqft", bbox_to_anchor=(1.0, 1), loc="upper left")

    # 2. horizontal bars: avg $/sqft by ZIP
    zip_ranking = (
        df.assign(zipCode=df["zipCode"].astype(str))
        .groupby("zipCode")["price_per_sqft"]
        .mean()
        .sort_values(ascending=False)
        .head(8)
        .reset_index()
    )
    sns.barplot(
        data=zip_ranking,
        x="price_per_sqft",
        y="zipCode",
        hue="zipCode",
        palette="viridis",
        legend=False,
        ax=axes[1],
    )
    axes[1].set_title("Avg Price per SqFt ($/sqft) by ZIP Code", fontweight="bold")
    axes[1].set_xlabel("Avg $/sqft (USD)")
    axes[1].set_ylabel("ZIP Code")

    # 3. boxplot: rent spread by bedroom count
    sns.boxplot(
        data=df,
        x="bedrooms",
        y="price",
        hue="bedrooms",
        palette="Blues_r",
        legend=False,
        ax=axes[2],
    )
    axes[2].set_title("Rent Distribution by Bedrooms", fontweight="bold")
    axes[2].set_xlabel("Bedrooms")
    axes[2].set_ylabel("Monthly Rent ($ USD)")

    plt.tight_layout()

    output_path = FIGURES_DIR / "market_overview.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print(f"[VISUALIZER] Report saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    csv_file = PROCESSED_DATA_DIR / "clean_listings.csv"
    if csv_file.exists():
        df_clean = pd.read_csv(csv_file)
        generate_market_report(df_clean)
    else:
        print(
            "[ERROR] clean_listings.csv not found - run main.py first."
        )
