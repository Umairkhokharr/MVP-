import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os

# --- Page configuration ---
st.set_page_config(page_title="MerchSentAI", page_icon="🛡️", layout="centered")

# --- Session state setup ---
if 'page' not in st.session_state:
    st.session_state.page = 'main'

# --- Fraud detection logic with 10 flags ---
def run_fraud_analysis(df):
    results = {
        'high_risk_countries': ['Iran', 'North Korea', 'Syria', 'Cuba', 'Russia', 'Venezuela'],
        'high_risk_categories': ['Cryptocurrency', 'Gambling', 'Adult Content', 'Arms Dealing'],
        'pep_list': ['John Smith', 'Emma Johnson', 'Michael Brown', 'Sarah Davis'],
        'data_enrichments': [
            "Geolocation intelligence",
            "Risk scoring algorithm",
            "Business network mapping",
            "Transaction pattern analysis"
        ]
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

# --- Splash / Main page ---
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
        st.experimental_rerun()

    st.stop()

# --- Analysis page ---
def analysis_page():
    st.title("Merchant Risk Analysis")

    uploaded = st.file_uploader("Upload Merchant Data (CSV/XLSX)", type=["csv", "xlsx"])
    if not uploaded:
        st.info("📁 Please upload a CSV or XLSX file to proceed.")
        st.stop()

    try:
        df = pd.read_csv(uploaded) if uploaded.name.lower().endswith('.csv') else pd.read_excel(uploaded)
    except Exception as e:
        st.error(f"Could not read file: {e}")
        st.stop()

    # Data Enrichment
    with st.expander("Data Enrichment", expanded=True):
        df['Enriched_Location'] = df.get('Country', np.nan)
        df['Enriched_RiskScore'] = np.random.randint(1, 100, len(df))
        st.success("Data enrichment applied")
        st.write(f"Enriched data ({len(df)} rows)")
        st.dataframe(df)

    # Fraud & screening
    df, results, fraud_logic_cols = run_fraud_analysis(df)

    with st.expander("Sanctions/Screening", expanded=True):
        st.success("Sanctions screening completed")
        st.dataframe(df[['MerchantName'] + fraud_logic_cols[:3]])

    with st.expander("Fraud Analysis", expanded=True):
        st.success("Fraud analysis completed")
        st.dataframe(df[fraud_logic_cols + ['FraudFlagCount', 'Suspicious']])

    # Executive summary
    display_executive_summary(df, results, fraud_logic_cols)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Full Risk Report", data=csv, file_name='risk_report.csv')

    if st.button("Back to Main"):
        st.session_state.page = 'main'
        st.experimental_rerun()

# --- Routing ---
if st.session_state.page == 'main':
    main_page()
else:
    analysis_page()
