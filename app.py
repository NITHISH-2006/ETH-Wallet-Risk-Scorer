import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[0]  # app.py is in root → parents[0]
sys.path.insert(0, str(project_root))
print(f"[DEBUG app] Added root: {project_root}")

import streamlit as st
from src.scorer import get_wallet_risk

st.set_page_config(page_title="Wallet Risk Scorer", page_icon="🛡️", layout="centered")
st.title("🛡️ Wallet Risk Scorer")
st.markdown("**Crypto Credit Score** — Powered by real blockchain data + graph ML")

address = st.text_input("Enter Ethereum Address (0x...)", placeholder="0x742d35Cc6634C0532925a3b844Bc454e4438f44e")
if st.button("🔍 Get Risk Score", type="primary"):
    with st.spinner("Analyzing on-chain behavior..."):
        try:
            score, reasons, tx_df = get_wallet_risk(address)
        except ValueError as e:
            st.error(f"Error processing wallet: {e}")
            st.stop()

    col1, col2 = st.columns([1, 2])
    with col1:
        delta = "HIGH RISK 🔥" if score > 70 else "MEDIUM ⚠️" if score > 40 else "LOW RISK ✅"
        st.metric("Risk Score", f"{score}/100", delta=delta)

    with col2:
        st.subheader("Why this score?")
        for r in reasons:
            st.write(f"• {r}")

    if not tx_df.empty:
        with st.expander("Raw Transaction Preview (first 10)"):
            st.dataframe(tx_df.head(10))