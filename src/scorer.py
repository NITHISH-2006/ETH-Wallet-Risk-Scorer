import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
print(f"[DEBUG scorer] Added root: {project_root}")

from src.data_fetcher import fetch_transactions
from src.feature_engineer import engineer_features
from src.model import WalletRiskModel
from config import MODEL_PATH

model = WalletRiskModel(MODEL_PATH)

def get_wallet_risk(address: str):
    print(f"[DEBUG] Scoring wallet: {address}")
    df = fetch_transactions(address)
    features_df = engineer_features(df, address)
    score, reasons, df_raw = model.predict_risk(features_df)
    return score, reasons, df_raw