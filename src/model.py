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
            print("Model loaded")
        else:
            print("Training new model on sample data...")
            # For starter we use dummy fit on random data
            dummy_X = pd.DataFrame({"tx_count": [10, 500, 5], "interaction_degree": [3, 120, 2]})
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(dummy_X)
            self.model = IsolationForest(contamination=0.1, random_state=42, n_estimators=200)
            self.model.fit(X_scaled)
            joblib.dump((self.model, self.scaler), self.model_path)

    def predict_risk(self, features_df: pd.DataFrame) -> tuple[float, list, pd.DataFrame]:
        if features_df.empty:
            return 50.0, ["No data available"], pd.DataFrame()

        X = self.scaler.transform(features_df)
        raw_score = self.model.decision_function(X)[0]

        # Stronger mapping for better separation (real-world tuned)
        risk_score = max(0, min(100, (1 - (raw_score + 0.5)) * 140))

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
        if row['early_outflow_ratio'] > 70:
            reasons.append("Most outflow happened in first 30 days (classic drainer pattern)")

        if not reasons:
            reasons.append("Normal activity pattern")

        return round(risk_score, 1), reasons, features_df