# src/config.py
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# load the .env from the project root
load_dotenv(dotenv_path=BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
LOGS_DIR = BASE_DIR / "logs"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

RENTCAST_API_KEY = os.getenv("RENTCAST_API_KEY", "").strip()
RENTCAST_BASE_URL = "https://api.rentcast.io/v1/listings/rental/long-term"

DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Miami")
DEFAULT_STATE = os.getenv("DEFAULT_STATE", "FL")
SQFT_TO_M2_FACTOR = 0.092903
