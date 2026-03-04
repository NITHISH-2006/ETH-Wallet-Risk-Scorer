import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from pathlib import Path

class WalletRiskModel:
    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.scaler = None
        self.model = None
        self.load_or_train()

    def load_or_train(self):
        if self.model_path.exists():
            self.model, self.scaler = joblib.load(self.model_path)
            print("✅ Model loaded successfully")
        else:
            print("Training new model on sample data...")
            dummy_X = pd.DataFrame({"tx_count": [10, 500, 5], "interaction_degree": [3, 120, 2]})
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(dummy_X)
            self.model = IsolationForest(contamination=0.1, random_state=42, n_estimators=200)
            self.model.fit(X_scaled)
            joblib.dump((self.model, self.scaler), self.model_path)

    def predict_risk(self, features_df: pd.DataFrame, address: str = None) -> tuple[float, list, pd.DataFrame]:
        if features_df.empty:
            return 50.0, ["No data available"], pd.DataFrame()

        known_cex = {
        "0x28c6c06298d514db089934071355e5743bf21d60": "Binance hot wallet",
        "0x742d35cc6634c0532925a3b844bc454e4438f44e": "Coinbase hot wallet",
        "0xe592427a0aece92de3edee1f18e0157c05861564": "Uniswap V3 Router",
        "0xf977814e90da44bfa03b6295a0616a897441acec": "Binance another hot",
        "0x3fc91a3afd70395cd496c647d5a6cc9d4b2b7fad": "Uniswap Universal Router",
        "0xdef1c0ded9bec7f1a1670819833240f027b25eff": "1inch Aggregator",
        "0x00000000006c3852cbef3e08e8df289169ede581": "OpenSea Seaport",
        # Add more known legit addresses if you want
        }

        # Pass address from scorer to here (small change needed in scorer.py)
        if address and address.lower() in known_cex:
            return 20.0, [f"Known legitimate wallet: {known_cex[address.lower()]}"], features_df

        X = self.scaler.transform(features_df)
        raw_score = self.model.decision_function(X)[0]

        risk_score = max(0, min(100, (1 - (raw_score + 0.5)) * 210))  # ← changed to 210

        row = features_df.iloc[0]
        reasons = []

        if row['outgoing_to_new_ratio_pct'] > 50:
            reasons.append("High transfers to previously unseen addresses (draining/exfiltration)")
        if row['outflow_per_day'] > 300:
            reasons.append("Massive daily ETH outflow (high exfiltration risk)")
        if row['tx_density'] > 2000:
            reasons.append("Extremely high transaction density (bot/drainer behavior)")
        if row['has_recent_spike'] > 60 and row['tx_count'] > 100:
            reasons.append("Sudden recent activity burst")
        if row['interaction_degree'] > 120:
            reasons.append("Very high connectivity (possible mixer/phishing)")
        if row['wallet_age_days'] < 90 and row['tx_count'] > 500:
            reasons.append("Young wallet with massive activity (high risk)")
        if row.get('early_outflow_ratio_pct', 0) > 65:
            reasons.append("Large portion of outflow in first 30 days (classic drainer pattern)")
        if row.get('young_wallet_high_activity', 0) == 1:
            reasons.append("Young wallet with extremely high activity (classic drainer pattern)")

        if not reasons:
            reasons.append("Normal activity pattern")

        return round(risk_score, 1), reasons, features_df