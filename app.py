import sys
from pathlib import Path

# Add project root to sys.path (app.py is in root → parents[0])
project_root = Path(__file__).resolve().parents[0]
sys.path.insert(0, str(project_root))
print(f"[DEBUG app] Added root: {project_root}")

import streamlit as st
from src.scorer import get_wallet_risk
import time

# ────────────────────────────────────────────────────────────────
# Page Config & Title
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Wallet Risk Scorer",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("🛡️ Wallet Risk Scorer")
st.markdown("**Crypto Credit Score** — Powered by real blockchain data + graph ML")

# ────────────────────────────────────────────────────────────────
# Sidebar – Info & Links
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("About")
    st.markdown("""
    **ETH Wallet Risk Scorer**  
    Detects suspicious patterns like draining, exfiltration, and early massive outflows.  
    Trained unsupervised on 141+ legitimate wallets (Binance, Uniswap, etc.).
    """)

    st.markdown("**Current Model**")
    st.info("Isolation Forest – only normal data used for training")

    st.markdown("**GitHub**")
    st.markdown("[View Source Code →](https://github.com/NITHISH-2006/ETH-Wallet-Risk-Scorer)")

    st.markdown("**Built by**")
    st.markdown("Nithish – part of 12-month zkML DeFi Security roadmap")

    st.markdown("---")
    st.caption("Disclaimer: This is a prototype for educational/research use. Not financial/security advice.")

# ────────────────────────────────────────────────────────────────
# Main Input
# ────────────────────────────────────────────────────────────────
st.markdown("### Enter Ethereum Address (0x...)")
address = st.text_input(
    label="",
    placeholder="e.g. 0x218c572b1ab6065d74bebcb708a3f523d14f7719",
    key="address_input",
    help="Paste any Ethereum wallet address to get its risk score"
)

# Quick examples
# Quick examples - use callbacks to safely update the input
st.caption("Quick test examples:")

def set_bad1():
    st.session_state.address_input = "0x218c572b1ab6065d74bebcb708a3f523d14f7719"

def set_bad2():
    st.session_state.address_input = "0x6c8ec8f14be7c01672d31cfa5f2cefeab2562b50"

def set_normal():
    st.session_state.address_input = "0x28c6c06298d514db089934071355e5743bf21d60"

col_ex1, col_ex2, col_ex3 = st.columns(3)
col_ex1.button("Test Bad #1", on_click=set_bad1)
col_ex2.button("Test Bad #2", on_click=set_bad2)
col_ex3.button("Test Normal (Binance)", on_click=set_normal)

# ────────────────────────────────────────────────────────────────
# Run Scoring
# ────────────────────────────────────────────────────────────────
if st.button("🔍 Get Risk Score", type="primary", use_container_width=True):
    if not address:
        st.warning("Please enter an Ethereum address")
        st.stop()

    if not address.startswith("0x") or len(address) != 42:
        st.error("Invalid Ethereum address (must be 42 characters starting with 0x)")
        st.stop()

    with st.spinner("Analyzing on-chain behavior... (5–15 seconds first time)"):
        start_time = time.time()
        try:
            score, reasons, tx_df = get_wallet_risk(address)
            elapsed = time.time() - start_time

            col1, col2 = st.columns([1, 2])

            with col1:
                if score > 70:
                    delta = "HIGH RISK 🔥"
                elif score > 40:
                    delta = "MEDIUM ⚠️"
                else:
                    delta = "LOW RISK ✅"

                st.metric("Risk Score", f"{score}/100", delta=delta)

                st.caption(f"Processed in {elapsed:.1f} seconds")

            with col2:
                st.subheader("Why this score?")
                if reasons:
                    for r in reasons:
                        st.markdown(f"• {r}")
                else:
                    st.info("No specific risk signals detected")

            if not tx_df.empty:
                with st.expander("Raw Transaction Preview (first 10 txs)"):
                    st.dataframe(tx_df.head(10))

            st.success("Analysis complete!")

        except ValueError as e:
            st.error(f"Error processing wallet: {str(e)}")
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            st.info("Check console or try again.")

# Footer
st.markdown("---")
st.caption("Prototype v0.1 – Built as part of zkML DeFi Security roadmap")