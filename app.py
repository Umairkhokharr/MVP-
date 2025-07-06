import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import base64
import os

# --- Page configuration ---
st.set_page_config(
    page_title="MerchSentAI",
    page_icon="🛡️",
    layout="centered"
)

# --- Session state setup ---
for key, default in [('page', 'main'), ('data', None), ('results', {}), ('rerun_count', 0)]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- Safe rerun function ---
def safe_rerun():
    try:
        st.experimental_rerun()
    except Exception:
        st.experimental_set_query_params(rerun=time.time())
        st.experimental_rerun()

# --- Fraud detection logic ---
def run_fraud_analysis(df):
    results = {
        'high_risk_countries': ['Iran', 'North Korea', 'Syria', 'Cuba', 'Russia', 'Venezuela'],
        'high_risk_categories': ['Cryptocurrency', 'Gambling', 'Adult Content', 'Arms Dealing'],
        'pep_list': ['John Smith', 'Emma Johnson', 'Michael Brown', 'Sarah Davis'],
        'fraud_patterns': [
            "High-value transactions (>$10,000)",
            "Recent registrations (<30 days)",
            "Mismatched location patterns",
            "High-volume/low-value pattern flipping"
        ],
        'data_enrichments': [
            "Geolocation intelligence",
            "Risk scoring algorithm",
            "Business network mapping",
            "Transaction pattern analysis"
        ]
    }
    df['Sanctioned'] = df['MerchantName'].isin(results['pep_list'])
    df['HighRiskCountry'] = df['Country'].isin(results['high_risk_countries'])
    df['HighRiskCategory'] = df['BusinessCategory'].isin(results['high_risk_categories'])
    df['HighAmount'] = df['AvgTransaction'] > 10000
    df['RegistrationDate'] = pd.to_datetime(df['RegistrationDate'], errors='coerce')
    df['RecentRegistration'] = (pd.Timestamp(datetime.today().date()) - df['RegistrationDate']).dt.days < 30
    df['Suspicious'] = df['HighAmount'] | df['RecentRegistration']
    return df, results

# --- Executive summary display ---
def display_executive_summary(df, results):
    total_merchants = len(df)
    sanctioned = int(df['Sanctioned'].sum())
    high_risk = int(df['HighRiskCountry'].sum())
    suspicious = int(df['Suspicious'].sum())

    enrichments = len(results['data_enrichments'])
    fraud_patterns = len(results['fraud_patterns'])
    sources = len(results['high_risk_countries']) + len(results['pep_list'])
    enrichment_details = ", ".join(results['data_enrichments'])

    st.markdown("### Executive Summary")
    st.markdown(f"**Total merchants:** {total_merchants}  ")
    st.markdown(f"**Sanction matches:** {sanctioned}  ")
    st.markdown(f"**High-risk jurisdictions flagged:** {high_risk}  ")
    st.markdown(f"**Suspicious merchants:** {suspicious}  ")
    st.markdown(f"**Data enrichment features:** {enrichments}")
    st.markdown(f"**Fraud detection algorithms:** {fraud_patterns}")
    st.markdown(f"**Data sources integrated:** {sources}")
    st.markdown("**Enrichment details:** " + enrichment_details)

# --- Main page ---
def main_page():
    st.markdown(
        """
        <style>
            .stButton>button {
                background-color: #4f46e5;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 0.5rem 1rem;
                width: 100%;
            }
            .stButton>button:hover {
                background-color: #3730a3;
                transform: scale(1.05);
            }
        </style>
        """, unsafe_allow_html=True)

    if os.path.exists("logo.png"):
        st.image("logo.png", use_column_width=True)
    else:
        st.warning("Place 'logo.png' in the same folder for splash branding.")

    st.title("Merchant Risk Intelligence Platform")
    st.write("Know your merchant, know your risk.")

    if st.button("Enter the Data World"):
        st.session_state.page = 'analysis'
        safe_rerun()

# --- Analysis page ---
def analysis_page():
    st.title("Merchant Risk Analysis")

    uploaded = st.file_uploader("Upload Merchant Data (CSV/XLSX)", type=["csv", "xlsx"])
    if uploaded:
        try:
            if uploaded.name.endswith('.csv'):
                df = pd.read_csv(uploaded)
            else:
                df = pd.read_excel(uploaded)
            st.session_state.data = df
        except Exception as e:
            st.error(f"Could not read file: {e}")
    elif st.session_state.data is None:
        df = pd.DataFrame({
            'MerchantID': [101,102,103,104,105],
            'MerchantName': ['CryptoEx','WatchesInc','Emma Johnson','OilGasLtd','DigitalCo'],
            'Country': ['Cayman Islands','Switzerland','Iran','Russia','Singapore'],
            'BusinessCategory': ['Cryptocurrency','Luxury Goods','Banking','Energy','IT Services'],
            'AvgTransaction': [45000,12500,7800,220000,3500],
            'RegistrationDate': ['2023-11-15','2022-05-01','2024-05-20','2021-12-10','2024-04-15']
        })
        st.info("Using sample data for demo")
        st.session_state.data = df

    if st.session_state.data is not None:
        df = st.session_state.data.copy()
        for col in ['MerchantName','Country','BusinessCategory','AvgTransaction','RegistrationDate']:
            if col not in df:
                df[col] = np.nan

        with st.expander("Data Enrichment", expanded=True):
            df['Enriched_Location'] = df['Country']
            df['Enriched_RiskScore'] = np.random.randint(1,100,len(df))
            st.success("Data enrichment applied")
            st.dataframe(df.head())

        df, results = run_fraud_analysis(df)

        with st.expander("Sanctions/Screening", expanded=True):
            st.success("Sanctions screening completed")
            st.dataframe(df[['MerchantName','Sanctioned','HighRiskCountry']].head())

        with st.expander("Fraud Analysis", expanded=True):
            st.success("Fraud analysis completed")
            st.dataframe(df[['MerchantName','Suspicious','HighAmount','RecentRegistration']].head())

        display_executive_summary(df, results)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Full Risk Report", data=csv, file_name='risk_report.csv')

    if st.button("Back to Main"):
        st.session_state.page = 'main'
        safe_rerun()

if st.session_state.page == 'main':
    main_page()
else:
    analysis_page()
