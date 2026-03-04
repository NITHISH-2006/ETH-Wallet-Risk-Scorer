# 🛡️ ETH Wallet Risk Scorer

**Side Quest 1 Complete** — Part of my 12-month journey to build a zkML-powered DeFi Security System.

**Live Demo**: [https://eth-wallet-risk-scorer-by-nithish.streamlit.app](https://eth-wallet-risk-scorer-by-nithish.streamlit.app)  
**GitHub**: [NITHISH-2006/ETH-Wallet-Risk-Scorer](https://github.com/NITHISH-2006/ETH-Wallet-Risk-Scorer)

### What it does
Enter any Ethereum wallet address → get a **0–100 risk score** + clear reasons (draining, exfiltration, early outflow, high density, etc.).

### Current Performance (March 2026)
- Trained **unsupervised** on **77 carefully curated legitimate wallets** (Binance, Uniswap, Coinbase, Aave, etc.)
- Tested on **12 real attacker wallets** from 2025–2026 exploits (rekt.news)
- **Bad wallets**: 59–80.7/100 (average ~71) → strong high-risk flagging
- **Normal wallets**: ~30–45/100 → low risk
- Reasons are **explainable** and actionable

### Key Technical Highlights
- **Isolation Forest** trained **only on normal data** (correct unsupervised approach)
- Rich feature engineering: graph features (NetworkX), temporal density, early outflow ratio, unseen address ratio, etc.
- Etherscan V2 API with intelligent caching
- Streamlit UI with quick test buttons and clean explanations

### Tech Stack
- Python 3 | pandas | scikit-learn (Isolation Forest) | NetworkX
- Etherscan V2 API + joblib caching
- Streamlit for UI

### How to Run Locally
```bash
git clone https://github.com/NITHISH-2006/ETH-Wallet-Risk-Scorer.git
cd ETH-Wallet-Risk-Scorer
python -m venv venv
venv\Scripts\activate    # Windows
pip install -r requirements.txt
# Add your Etherscan API key to .env
streamlit run app.py