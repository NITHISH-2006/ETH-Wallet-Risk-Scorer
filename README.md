# ETH Wallet Risk Scorer

**Side Quest 1** 
**Goal**: Give any Ethereum wallet a 0–100 risk score + reasons (like a crypto credit score)

## Current Status (March 2026)
- Trained **Isolation Forest** unsupervised — only on 89 normal / legitimate wallets (Binance, Uniswap, Coinbase, etc.)
- Tested on 12 known bad wallets from real 2025–2026 exploits (rekt.news)
- Bad wallets now flagged **56–74/100** (medium-high risk)
- Normal wallets ~30–40/100 (low risk)
- Real-time Etherscan V2 API + caching + graph features (networkx)

## Features Detected
- High transfers to unseen addresses (draining/exfiltration)
- Massive early outflow (classic drainer pattern)
- Sudden recent activity bursts
- High transaction density

## Demo (Streamlit)
Run locally:
```bash
streamlit run app.py