import streamlit as st
import pandas as pd
from src.config import PROCESSED_DATA_DIR

st.set_page_config(page_title="Real Estate Investor Dashboard", layout="wide")
st.title("🏠 US Real Estate Rental Valuation Dashboard")

csv_path = PROCESSED_DATA_DIR / "clean_listings.csv"

if not csv_path.exists():
    st.error("Run 'python3 main.py' first to generate the clean dataset.")
else:
    df = pd.read_csv(csv_path)

    # sidebar filters
    st.sidebar.header("Investment Filters")
    max_price = st.sidebar.slider(
        "Max Rent ($)",
        int(df["price"].min()),
        int(df["price"].max()),
        int(df["price"].max()),
    )
    selected_types = st.sidebar.multiselect(
        "Property Type",
        df["propertyType"].unique(),
        default=df["propertyType"].unique(),
    )

    filtered_df = df[
        (df["price"] <= max_price) & (df["propertyType"].isin(selected_types))
    ]

    if filtered_df.empty:
        st.warning("No listings match the selected filters.")
    else:
        # top KPIs
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Filtered Listings", len(filtered_df))
        col2.metric("Median Rent", f"${filtered_df['price'].median():,.0f}")
        col3.metric("Avg $/sqft", f"${filtered_df['price_per_sqft'].mean():.2f}")
        col4.metric(
            "Avg Area (sqft)", f"{filtered_df['squareFootage'].mean():.0f} sqft"
        )

        # table sorted by best $/sqft first
        st.subheader("🔥 Best Opportunities (sorted by lowest $/sqft)")
        st.dataframe(
            filtered_df.sort_values(by="price_per_sqft", ascending=True),
            use_container_width=True,
        )
