import os
import time
import pandas as pd
import requests
from pathlib import Path
import joblib
from config import ETHERSCAN_API_KEY, CACHE_DIR, MAX_TXS, API_SLEEP

print("data_fetcher.py loaded successfully")

CACHE_DIR = Path(CACHE_DIR)
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def get_cache_path(address: str) -> Path:
    return CACHE_DIR / f"{address.lower()}.joblib"

def fetch_transactions(address: str) -> pd.DataFrame:
    cache_path = get_cache_path(address)
    if cache_path.exists():
        print(f"✅ Cache hit for {address}")
        return joblib.load(cache_path)

    print(f"🌐 Fetching from Etherscan V2: {address}")
    url = "https://api.etherscan.io/v2/api"  
    params = {
        "module": "account",
        "action": "txlist",
        "address": address,
        "startblock": 0,
        "endblock": 99999999,
        "sort": "asc",
        "apikey": ETHERSCAN_API_KEY,
        "page": 1,
        "offset": MAX_TXS,
        "chainid": "1"  # still needed
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") != "1":
        msg = data.get('message', 'Unknown error')
        if "No transactions found" in msg:
            print(f"No transactions found for {address} — returning empty DF")
            df = pd.DataFrame()
        else:
            raise ValueError(f"Etherscan error: {msg} - Full: {data}")
    else:
        df = pd.DataFrame(data["result"])
        if not df.empty:
            df["value"] = pd.to_numeric(df["value"], errors="coerce") / 1e18
            df["timeStamp"] = pd.to_datetime(df["timeStamp"], unit="s")
            df["is_incoming"] = df["to"].str.lower() == address.lower()

    joblib.dump(df, cache_path)
    time.sleep(API_SLEEP)
    return df