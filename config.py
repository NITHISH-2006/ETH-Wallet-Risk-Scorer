import os
from dotenv import load_dotenv

load_dotenv()
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")
CACHE_DIR = os.getenv("CACHE_DIR", "data/cache")
MODEL_PATH = os.getenv("MODEL_PATH", "models/isolation_forest_v1.pkl")
MAX_TXS = 10000
API_SLEEP = 0.35  # 0.35s sleep → ~2.85 calls/sec [safer than 3 calls/sec limit]



