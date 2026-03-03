import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))
print(f"[DEBUG train] Added root: {project_root}")

import pandas as pd
import joblib
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from src.data_fetcher import fetch_transactions
from src.feature_engineer import engineer_features
from config import MODEL_PATH

LABELED_DIR = Path("data/labeled")
BAD_CSV = LABELED_DIR / "bad_wallets.csv"
NORMAL_CSV = LABELED_DIR / "normal_wallets.csv"
MODEL_PATH = Path(MODEL_PATH)

print(f"[DEBUG] BAD_CSV path: {BAD_CSV.absolute()} → exists? {BAD_CSV.exists()}")
print(f"[DEBUG] NORMAL_CSV path: {NORMAL_CSV.absolute()} → exists? {NORMAL_CSV.exists()}")

def collect_features(wallets_list: list) -> pd.DataFrame:
    all_features = []
    for addr in wallets_list:
        try:
            print(f"[FETCH] {addr}")
            df = fetch_transactions(addr.strip())
            feat_df = engineer_features(df, addr.strip())
            if not feat_df.empty:
                feat_df['address'] = addr.strip()
                all_features.append(feat_df)
            else:
                print(f"[WARN] Empty features for {addr}")
        except Exception as e:
            print(f"[ERROR] {addr}: {str(e)}")
    if all_features:
        return pd.concat(all_features, ignore_index=True)
    return pd.DataFrame()

def main():
    print("=== Training Real Wallet Risk Model ===")
    
    if not BAD_CSV.exists() or not NORMAL_CSV.exists():
        print("ERROR: One or both CSV files missing!")
        return

    bad_df = pd.read_csv(BAD_CSV)
    normal_df = pd.read_csv(NORMAL_CSV)
    
    bad_addrs = bad_df['address'].dropna().tolist()
    normal_addrs = normal_df['address'].dropna().tolist()
    
    print(f"Bad wallets: {len(bad_addrs)} | Normal: {len(normal_addrs)}")
    
    print("\nCollecting features for bad wallets...")
    bad_features = collect_features(bad_addrs)
    
    print("\nCollecting features for normal wallets...")
    normal_features = collect_features(normal_addrs)
    
    if normal_features.empty:
        print("ERROR: No normal features collected. Add more normal wallets!")
        return
    
    # ==================== TRAIN ONLY ON NORMAL WALLET DATA ====================
    print("\nTraining Isolation Forest ONLY on normal wallets (best practice)...")
    feature_cols = [col for col in normal_features.columns if col not in ['address']]
    normal_X = normal_features[feature_cols].fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(normal_X)
    
    model = IsolationForest(
        n_estimators=3000,          # more trees = more stable & accurate
        contamination=0.005,        # very strict - expect almost zero anomalies in normal data
        max_samples=1024,
        random_state=42
    )
    model.fit(X_scaled)
    
    joblib.dump((model, scaler), MODEL_PATH)
    print(f"Model trained on {len(normal_X)} normal wallets and saved to {MODEL_PATH}")
    
    # ==================== VALIDATION ON BAD WALLETS ====================
    if not bad_features.empty:
        bad_scaled = scaler.transform(bad_features[feature_cols].fillna(0))
        bad_scores = model.decision_function(bad_scaled)
        
        print("\nDecision scores on known bad wallets (lower = more anomalous):")
        for addr, sc in zip(bad_addrs, bad_scores):
            # Stronger mapping for better separation
            risk = max(0, min(100, (1 - (sc + 0.5)) * 180))  # ← from 140 → 190
            print(f"{addr[:10]}...: {risk:.1f}/100 (raw {sc:.3f})")
    else:
        print("No bad wallets to validate.")

if __name__ == "__main__":
    main()