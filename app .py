
import streamlit as st
import pandas as pd
import numpy as np

def show_splash():
    st.markdown("<h2 style='text-align:center;'>MerchSentAI</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>Know your merchant. Know your risk.</p>", unsafe_allow_html=True)
    if st.button("🚀 Let’s Enter the Data World"):
        st.session_state.stage = "stage1"

def enrich_data(df):
    if 'merchant_id' not in df.columns:
        df['merchant_id'] = range(1, len(df) + 1)
    df['category'] = np.where(df['merchant_id'] % 2 == 0, 'Retail', 'Services')
    df['region'] = np.where(df['merchant_id'] % 3 == 0, 'North America', 'EMEA')
    df['enriched'] = True
    return df

def screen_sanctions(df):
    df['flag_sanction'] = df['merchant_name'].str.contains("Ltd|Corp|Banned", case=False)
    return df

def apply_fraud_logic(df):
    needed = ['transaction_volume', 'transaction_region', 'mcc_code', 'days_since_last_txn', 'region']
    for col in needed:
        if col not in df.columns:
            st.warning(f"Missing column: {col}")
            return None
    df['high_txn_vol'] = df['transaction_volume'] > 10000
    df['geo_mismatch'] = df['region'] != df['transaction_region']
    df['mcc_mismatch'] = df['mcc_code'].astype(str).str.startswith('9')
    df['inactive_spike'] = df['days_since_last_txn'] > 30
    df['fraud_risk_score'] = df[['high_txn_vol', 'geo_mismatch', 'mcc_mismatch', 'inactive_spike']].sum(axis=1)
    df['risk_level'] = pd.cut(df['fraud_risk_score'], [-1, 1, 2, 4], labels=['Low', 'Medium', 'High'])
    return df

def show_summary(df):
    st.subheader("📊 Executive Summary")
    st.metric("High Risk Merchants", (df['risk_level'] == 'High').sum())
    st.metric("Medium Risk Merchants", (df['risk_level'] == 'Medium').sum())
    st.metric("Low Risk Merchants", (df['risk_level'] == 'Low').sum())
    with st.expander("🔧 Backend API Diagnostic Panel"):
        st.code("""
POST /api/fraud-analysis/run
Payload: Merchant dataset
Modules: Velocity, Geo Mismatch, BIN Scan, Dormancy Spike
Runtime: ~1.5s
""")

def main():
    st.set_page_config(page_title="MerchSentAI", layout="centered")
    if 'stage' not in st.session_state:
        st.session_state.stage = 'splash'

    if st.session_state.stage == 'splash':
        show_splash()

    elif st.session_state.stage == 'stage1':
        st.title("🔍 Stage 1: Data Enrichment")
        uploaded = st.file_uploader("Upload merchant dataset", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            st.session_state.df_raw = df
            st.dataframe(df.head())
            if st.button("Hit Enrich Data"):
                st.session_state.df_enriched = enrich_data(df)
                st.session_state.stage = 'stage2'
        if st.button("🔙 Back to Splash"):
            st.session_state.stage = 'splash'

    elif st.session_state.stage == 'stage2':
        st.title("🛡️ Stage 2: Sanctions Screening")
        df = screen_sanctions(st.session_state.df_enriched)
        st.session_state.df_screened = df
        st.dataframe(df[['merchant_name', 'flag_sanction']])
        if st.button("Proceed to Fraud Analysis"):
            st.session_state.stage = 'stage3'
        if st.button("🔙 Back to Stage 1"):
            st.session_state.stage = 'stage1'

    elif st.session_state.stage == 'stage3':
        st.title("💣 Stage 3: Fraud Analysis")
        result = apply_fraud_logic(st.session_state.df_screened)
        if result is not None and 'fraud_risk_score' in result.columns:
            st.dataframe(result[['merchant_name', 'fraud_risk_score', 'risk_level']])
            show_summary(result)
        else:
            st.warning("Fraud analysis could not run.")
        if st.button("🔙 Back to Stage 2"):
            st.session_state.stage = 'stage2'

if __name__ == '__main__':
    main()
