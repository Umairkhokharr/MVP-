
import streamlit as st
import pandas as pd
import numpy as np
import base64
import time

# -------------------------------
# Splash Setup & Branding
# -------------------------------
def get_base64_logo():
    return "{LOGO_B64}"

def show_splash():
    st.markdown(f"""
        <div style='text-align:center;padding-top:10%;'>
            <img src='data:image/png;base64,{get_base64_logo()}' width='160'/>
            <h1 style='font-size:2em;margin-top:30px;'>Know your merchant. Know your risk.</h1>
        </div>
    """, unsafe_allow_html=True)
    if st.button("Let’s Enter the Data World"):
        st.session_state.stage = "stage1"

# -------------------------------
# Stage 1: Data Enrichment
# -------------------------------
def enrich_data(df):
    df['category'] = np.where(df['merchant_id'] % 2 == 0, 'Retail', 'Services')
    df['region'] = np.where(df['merchant_id'] % 3 == 0, 'North America', 'EMEA')
    df['enriched'] = True
    st.session_state.df_enriched = df
    st.session_state.summary['enriched_count'] = len(df)
    return df

# -------------------------------
# Stage 2: Sanctions Screening
# -------------------------------
def screen_sanctions(df):
    df['flag_sanction'] = df['merchant_name'].str.contains("Ltd|Corp|Banned", case=False)
    flagged = df[df['flag_sanction']]
    st.session_state.df_screened = df
    st.session_state.summary['sanctions_flagged'] = len(flagged)
    st.session_state.summary['sanctions_total'] = len(df)
    return df

# -------------------------------
# Stage 3: Fraud Analysis (Inspired by Feedzai, LexisNexis, etc.)
# -------------------------------
def apply_fraud_logic(df):
    df['high_txn_vol'] = df['transaction_volume'] > 10000
    df['geo_mismatch'] = df['region'] != df['transaction_region']
    df['mcc_mismatch'] = df['mcc_code'].astype(str).str.startswith('9')  # Example high-risk code
    df['inactive_spike'] = df['days_since_last_txn'] > 30
    df['fraud_risk_score'] = df[['high_txn_vol', 'geo_mismatch', 'mcc_mismatch', 'inactive_spike']].sum(axis=1)

    df['risk_level'] = pd.cut(df['fraud_risk_score'], bins=[-1, 1, 2, 4], labels=['Low', 'Medium', 'High'])
    st.session_state.df_fraud = df

    st.session_state.summary['fraud_total'] = len(df)
    st.session_state.summary['high_risk'] = (df['risk_level'] == 'High').sum()
    st.session_state.summary['medium_risk'] = (df['risk_level'] == 'Medium').sum()
    st.session_state.summary['low_risk'] = (df['risk_level'] == 'Low').sum()
    return df

# -------------------------------
# Summary Dashboard
# -------------------------------
def show_summary():
    st.subheader("📊 Executive Summary")

    with st.expander("Processing Overview"):
        st.write("### Enrichment Summary")
        st.write({
            "Records Enriched": st.session_state.summary.get("enriched_count", 0)
        })
        st.write("### Sanctions Screening")
        st.write({
            "Total Screened": st.session_state.summary.get("sanctions_total", 0),
            "Flagged Matches": st.session_state.summary.get("sanctions_flagged", 0)
        })
        st.write("### Fraud Risk Assessment")
        st.write({
            "Total Analyzed": st.session_state.summary.get("fraud_total", 0),
            "High Risk": st.session_state.summary.get("high_risk", 0),
            "Medium Risk": st.session_state.summary.get("medium_risk", 0),
            "Low Risk": st.session_state.summary.get("low_risk", 0)
        })

    with st.expander("🔍 Backend API Interface Preview"):
        st.code("""
POST /api/fraud/check
Payload: 1,239 merchant records
Modules Triggered: Velocity, GeoMismatch, MCC Check, Dormancy
Runtime: 1.42 seconds
Output: 8 High Risk, 22 Medium, 60 Low
        """, language='text')

# -------------------------------
# App Controller
# -------------------------------
def main():
    st.set_page_config(page_title="MerchSentAI", layout="wide")

    if "stage" not in st.session_state:
        st.session_state.stage = "splash"
    if "df_raw" not in st.session_state:
        st.session_state.df_raw = None
    if "summary" not in st.session_state:
        st.session_state.summary = {}

    if st.session_state.stage == "splash":
        show_splash()

    elif st.session_state.stage == "stage1":
        st.header("🔍 Stage 1: Data Enrichment")
        uploaded = st.file_uploader("Upload merchant CSV", type="csv")
        if uploaded:
            df = pd.read_csv(uploaded)
            st.session_state.df_raw = df
            st.dataframe(df.head())
            if st.button("Hit Enrich Data"):
                with st.spinner("Enriching..."):
                    enriched = enrich_data(df)
                    st.dataframe(enriched.head())
                    st.session_state.stage = "stage2"

    elif st.session_state.stage == "stage2":
        st.header("🛡️ Stage 2: Sanctions/Screening")
        if st.button("Initiate Screening/Sanctions Check"):
            with st.spinner("Running checks..."):
                screened = screen_sanctions(st.session_state.df_enriched)
                st.dataframe(screened[['merchant_name', 'flag_sanction']])
                st.session_state.stage = "stage3"

    elif st.session_state.stage == "stage3":
        st.header("💣 Stage 3: Fraud Analysis")
        if st.button("Perform Data Analysis"):
            with st.spinner("Applying fraud rules..."):
                fraud_df = apply_fraud_logic(st.session_state.df_screened)
                st.dataframe(fraud_df[['merchant_name', 'fraud_risk_score', 'risk_level']])
                show_summary()

if __name__ == "__main__":
    main()
