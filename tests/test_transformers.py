import pytest
import pandas as pd
from src.transformers import clean_rental_data


@pytest.fixture
def sample_raw_payload():
    """
    Controlled payload:
    - 1 valid listing (rent_01)
    - 1 exact duplicate (rent_01 again)
    - 1 listing with null squareFootage (rent_02)
    - 1 listing with an unrealistic zero price (rent_03)
    """
    return [
        {
            "id": "rent_01",
            "formattedAddress": "1000 Brickell Ave, Miami, FL 33131",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33131",
            "price": 3000,
            "squareFootage": 1000,
            "bedrooms": 2,
            "bathrooms": 2,
            "propertyType": "condo ",
            "daysOnMarket": 10,
            "status": "Active",
        },
        {
            # exact duplicate of the first record
            "id": "rent_01",
            "formattedAddress": "1000 Brickell Ave, Miami, FL 33131",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33131",
            "price": 3000,
            "squareFootage": 1000,
            "bedrooms": 2,
            "bathrooms": 2,
            "propertyType": "condo ",
            "daysOnMarket": 10,
            "status": "Active",
        },
        {
            # invalid: null squareFootage (can't compute $/sqft)
            "id": "rent_02",
            "formattedAddress": "450 NW 24th St, Miami, FL 33127",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33127",
            "price": 2500,
            "squareFootage": None,
            "bedrooms": 1,
            "bathrooms": 1,
            "propertyType": "apartment",
            "daysOnMarket": 5,
            "status": "Active",
        },
        {
            # invalid: price below the sanity floor (100 USD)
            "id": "rent_03",
            "formattedAddress": "2801 Florida Ave, Miami, FL 33133",
            "city": "Miami",
            "state": "FL",
            "zipCode": "33133",
            "price": 0,
            "squareFootage": 850,
            "bedrooms": 2,
            "bathrooms": 1.5,
            "propertyType": "townhouse",
            "daysOnMarket": 12,
            "status": "Active",
        },
    ]


def test_clean_rental_data_filters_invalid_and_duplicates(sample_raw_payload):
    """Duplicates, nulls and zero prices must be dropped."""
    df = clean_rental_data(sample_raw_payload)

    # only the unique rent_01 should survive out of the 4 raw records
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.iloc[0]["id"] == "rent_01"


def test_clean_rental_data_metrics_calculation(sample_raw_payload):
    """Checks $/sqft math, m² conversion and label normalization."""
    df = clean_rental_data(sample_raw_payload)
    row = df.iloc[0]

    # 3000 USD / 1000 sqft = 3.00 USD/sqft
    assert row["price_per_sqft"] == 3.00

    # 1000 sqft * 0.092903 = 92.90 m²
    assert row["area_m2"] == 92.90

    # 3000 USD / 92.90 m² = 32.29 USD/m²
    assert row["price_per_m2"] == 32.29

    # string normalization ("condo " -> "Condo")
    assert row["propertyType"] == "Condo"


def test_clean_rental_data_empty_input():
    """Pipeline shouldn't blow up on an empty API response."""
    df = clean_rental_data([])

    assert isinstance(df, pd.DataFrame)
    assert df.empty
