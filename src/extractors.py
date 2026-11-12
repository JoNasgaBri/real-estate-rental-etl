import json
from typing import Any
import httpx
from src.config import (
    DEFAULT_CITY,
    DEFAULT_STATE,
    RAW_DATA_DIR,
    RENTCAST_API_KEY,
    RENTCAST_BASE_URL,
)

RAW_FILE_PATH = RAW_DATA_DIR / "sample_raw.json"


def fetch_rental_listings(
    city: str = DEFAULT_CITY,
    state: str = DEFAULT_STATE,
    limit: int = 50,
    use_cache: bool = True,
) -> list[dict[str, Any]]:
    
    # 1. local cache check (saves API calls)
    if use_cache and RAW_FILE_PATH.exists():
        print(f"[CACHE] Loading local data from: {RAW_FILE_PATH}")
        with open(RAW_FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[CACHE] {len(data)} listings loaded from disk.")
        return data

    # 2. API key check
    if not RENTCAST_API_KEY or RENTCAST_API_KEY == "your_api_key_here":
        raise ValueError(
       
        )

    headers = {"Accept": "application/json", "X-Api-Key": RENTCAST_API_KEY}

    params = {"city": city, "state": state, "status": "Active", "limit": limit}

    # 3. HTTP request via httpx
    print(f"[HTTP] Requesting up to {limit} listings for {city}, {state}...")
    with httpx.Client(timeout=20.0) as client:
        response = client.get(RENTCAST_BASE_URL, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            print(f"[HTTP] Success: {len(data)} listings received.")

            # 4. 
            with open(RAW_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[DISK] Raw backup saved to: {RAW_FILE_PATH}")

            return data

        elif response.status_code == 401:
            raise PermissionError("Error 401: invalid or unauthorized API key.")
        elif response.status_code == 429:
            raise RuntimeError("Error 429: RentCast rate limit reached.")
        else:
            response.raise_for_status()


if __name__ == "__main__":
    # quick manual run
    records = fetch_rental_listings(limit=25, use_cache=True)
    print(f"[INFO] First listing sample:\n{records[0] if records else 'Empty'}")
