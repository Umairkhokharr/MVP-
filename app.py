import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import os

# --- Page configuration ---
st.set_page_config(page_title="MerchSentAI", page_icon="🛡️", layout="centered")

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

# --- Fraud detection logic with 10 flags ---
def run_fraud_analysis(df):
    results = {
        'high_risk_countries': ['Iran', 'North Korea', 'Syria', 'Cuba', 'Russia', 'Venezuela'],
        'high_risk_categories': ['Cryptocurrency', 'Gambling', 'Adult Content', 'Arms Dealing'],
        'pep_list': ['John Smith', 'Emma Johnson', 'Michael Brown', 'Sarah Davis'],
        'data_enrichments': ["Geolocation intelligence", "Risk scoring algorithm", "Business network mapping", "Transaction pattern analysis"]
    }

    # Screening & fraud flags
    df['SanctionedFlag'] = df['MerchantName'].isin(results['pep_list'])
    df['HighRiskCountryFlag'] = df['Country'].isin(results['high_risk_countries'])
    df['HighRiskCategoryFlag'] = df['BusinessCategory'].isin(results['high_risk_categories'])
    df['HighAmountFlag'] = df['AvgTransaction'] > 10000
    df['RegistrationDate'] = pd.to_datetime(df['RegistrationDate'], errors='coerce')
    df['RecentRegistrationFlag'] = (pd.Timestamp(datetime.today().date()) - df['RegistrationDate']).dt.days < 30

    # Additional fraud logic flags
    df['CryptoRelatedFlag'] = df['BusinessCategory'] == 'Cryptocurrency'
    df['LuxuryHighValueFlag'] = (df['BusinessCategory'] == 'Luxury Goods') & (df['AvgTransaction'] > 50000)
    df['EnergyLargeVolumeFlag'] = (df['BusinessCategory'] == 'Energy') & (df['AvgTransaction'] > 100000)
    df['OddNameLengthFlag'] = df['MerchantName'].str.len() % 2 == 1
    df['HighRiskScoreFlag'] = df.get('Enriched_RiskScore', 0) > 80

    fraud_logic_cols = [
        'SanctionedFlag', 'HighRiskCountryFlag', 'HighRiskCategoryFlag',
        'HighAmountFlag', 'RecentRegistrationFlag', 'CryptoRelatedFlag',
        'LuxuryHighValueFlag', 'EnergyLargeVolumeFlag', 'OddNameLengthFlag',
        'HighRiskScoreFlag'
    ]

    df['FraudFlagCount'] = df[fraud_logic_cols].sum(axis=1)
    df['Suspicious'] = df['FraudFlagCount'] > 0

    return df, results, fraud_logic_cols

# --- Executive summary display with table & charts ---
def display_executive_summary(df, results, fraud_logic_cols):
    total_merchants = len(df)
    sanctioned = int(df['SanctionedFlag'].sum())
    high_risk = int(df['HighRiskCountryFlag'].sum())
    suspicious = int(df['Suspicious'].sum())

    st.markdown("### Executive Summary")

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total merchants", total_merchants)
    col2.metric("Sanction matches", sanctioned)
    col3.metric("High-risk jurisdictions", high_risk)
    col4.metric("Suspicious merchants", suspicious)

    # Summary table
    summary_df = pd.DataFrame({
        'Metric': ['Total merchants', 'Sanction matches', 'High-risk jurisdictions', 'Suspicious merchants'],
        'Count': [total_merchants, sanctioned, high_risk, suspicious]
    })
    st.table(summary_df)

    # Bar chart for summary
    st.bar_chart(summary_df.set_index('Metric'))

    # Fraud logic distribution chart
    st.markdown("#### Fraud Logic Flags Distribution")
    flag_counts = df[fraud_logic_cols].sum().sort_values(ascending=False)
    st.bar_chart(flag_counts)

# --- Main page ---
def main_page():
    st.markdown(
        """<style>
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
        </style>""", unsafe_allow_html=True)

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
            df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
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

        # Data Enrichment
        with st.expander("Data Enrichment", expanded=True):
            df['Enriched_Location'] = df['Country']
            df['Enriched_RiskScore'] = np.random.randint(1, 100, len(df))
            st.success("Data enrichment applied")
            st.write(f"Enriched data ({len(df)} rows)")
            st.dataframe(df)

        # Fraud & screening
        df, results, fraud_logic_cols = run_fraud_analysis(df)

        with st.expander("Sanctions/Screening", expanded=True):
            st.success("Sanctions screening completed")
            st.dataframe(df[['MerchantName'] + [col for col in fraud_logic_cols[:3]]])

        with st.expander("Fraud Analysis", expanded=True):
            st.success("Fraud analysis completed")
            st.dataframe(df[fraud_logic_cols + ['FraudFlagCount', 'Suspicious']])

        # Executive summary
        display_executive_summary(df, results, fraud_logic_cols)

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Full Risk Report", data=csv, file_name='risk_report.csv')

    if st.button("Back to Main"):
        st.session_state.page = 'main'
        safe_rerun()

# --- Routing ---
if st.session_state.page == 'main':
    main_page()
else:
    analysis_page()
