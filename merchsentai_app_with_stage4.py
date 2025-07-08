
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import matplotlib.pyplot as plt
from pptx import Presentation
from pptx.util import Inches

# Seed for reproducibility
np.random.seed(42)

# Page config
st.set_page_config(page_title="MerchSentAI", page_icon="🛡️", layout="centered")

# Session state initialization
if 'page' not in st.session_state:
    st.session_state.page = 'splash'

# Cost simulation function
def simulate_processor_cost(df, flags, fraud_cost, sanction_cost):
    sanction_misses = int(df.get('SanctionedFlag', pd.Series([0]*len(df))).sum())
    fraud_misses = int(df[flags].any(axis=1).sum())
    sanction_total = sanction_misses * sanction_cost
    fraud_total = fraud_misses * fraud_cost
    total = sanction_total + fraud_total
    return sanction_misses, sanction_total, fraud_misses, fraud_total, total

# Fraud analysis logic
def run_fraud_analysis(df):
    if 'Enriched_RiskScore' not in df:
        st.warning("Enriched_RiskScore missing—defaulting to 0")
        df['Enriched_RiskScore'] = 0
    results = {
        'high_risk_countries': ['Iran', 'North Korea', 'Syria', 'Cuba', 'Russia', 'Venezuela'],
        'high_risk_categories': ['Cryptocurrency', 'Gambling', 'Adult Content', 'Arms Dealing'],
        'pep_list': ['John Smith', 'Emma Johnson', 'Michael Brown', 'Sarah Davis']
    }
    df['RegistrationDate'] = pd.to_datetime(df['RegistrationDate'].str.strip(), errors='coerce')
    df['SanctionedFlag'] = df['MerchantName'].isin(results['pep_list'])
    df['HighRiskCountryFlag'] = df['Country'].isin(results['high_risk_countries'])
    df['HighRiskCategoryFlag'] = df['BusinessCategory'].isin(results['high_risk_categories'])
    df['HighAmountFlag'] = df['AvgTransaction'] > 10000
    df['RecentRegistrationFlag'] = (pd.Timestamp('today') - df['RegistrationDate']).dt.days < 30
    df['CryptoRelatedFlag'] = df['BusinessCategory']=='Cryptocurrency'
    df['LuxuryHighValueFlag'] = (df['BusinessCategory']=='Luxury Goods') & (df['AvgTransaction']>50000)
    df['EnergyLargeVolumeFlag'] = (df['BusinessCategory']=='Energy') & (df['AvgTransaction']>100000)
    df['OddNameLengthFlag'] = df['MerchantName'].str.len() % 2 == 1
    df['HighRiskScoreFlag'] = df['Enriched_RiskScore'] > 80
    flags = [
        'SanctionedFlag', 'HighRiskCountryFlag', 'HighRiskCategoryFlag',
        'HighAmountFlag', 'RecentRegistrationFlag', 'CryptoRelatedFlag',
        'LuxuryHighValueFlag', 'EnergyLargeVolumeFlag', 'OddNameLengthFlag', 'HighRiskScoreFlag'
    ]
    total = len(df)
    sanctioned = int(df['SanctionedFlag'].sum())
    high_risk = int(df['HighRiskCountryFlag'].sum())
    suspicious = int(df[flags].any(axis=1).sum())
    summary = pd.DataFrame({
        'Metric': ['Total merchants', 'Sanction matches', 'High-risk jurisdictions', 'Suspicious merchants'],
        'Count': [total, sanctioned, high_risk, suspicious]
    })
    st.table(summary)
    st.bar_chart(summary.set_index('Metric'))
    st.markdown("#### Fraud Logic Flags Distribution")
    flag_counts = df[flags].sum().sort_values(ascending=False)
    st.bar_chart(flag_counts)
    return df, summary, flags

# Splash page
def splash_page():
    st.markdown("""
    <style>
    .stApp {background: linear-gradient(135deg, #e8f0ff, #f3e8ff);}
    .stButton>button {background-color:#4f46e5; color:white; font-weight:bold; border-radius:8px; padding:.75rem; width:100%;}
    </style>
    """, unsafe_allow_html=True)
    logo = st.file_uploader("Upload Logo (PNG/JPG)", type=["png","jpg","jpeg"], key="logo")
    if logo:
        st.image(logo, use_column_width=True)
    st.title("Merchant Risk Intelligence Platform")
    st.write("Know your merchant, know your risk.")
    if st.button("Enter the Data World"):
        st.session_state.page = 'analysis'

# Analysis page with four stages
def analysis_page():
    st.title("Merchant Risk Analysis")
    upload = st.file_uploader("Upload Merchant Data (CSV/XLS/XLSX)", type=["csv","xls","xlsx"], key="data")
    if upload:
        if ('raw_df' not in st.session_state) or (st.session_state.get('filename') != upload.name):
            try:
                name = upload.name.lower()
                if name.endswith('.csv'):
                    df = pd.read_csv(upload)
                else:
                    df = pd.read_excel(upload)
                df.columns = df.columns.str.strip()
                st.session_state.raw_df = df.copy()
                st.session_state.df = df
                st.session_state.filename = upload.name
                st.session_state.enriched = False
                st.session_state.screened = False
                st.session_state.fraud_done = False
                st.session_state.processor_done = False
            except Exception as e:
                st.error(f"Failed to read file: {e}")
                return
    else:
        st.info("Please upload data to proceed.")
        return

    df = st.session_state.df

    # Stage 1: Enrichment
    st.subheader("Stage 1: Data Enrichment")
    if not st.session_state.enriched:
        if st.button("Enrich Data"):
            df['Enriched_Location'] = df.get('Country', np.nan)
            df['Enriched_RiskScore'] = np.random.randint(1,100,len(df))
            st.session_state.df = df
            st.session_state.enriched = True
            st.success("Data enriched!")
    if st.session_state.enriched:
        st.dataframe(df.head())

    # Stage 2: Sanctions Screening
    st.subheader("Stage 2: Perform Data Sanctions Screening")
    if st.session_state.enriched and not st.session_state.screened:
        if st.button("Perform Data Sanctions Screening"):
            peps = ['John Smith','Emma Johnson','Michael Brown','Sarah Davis']
            df['SanctionedFlag'] = df['MerchantName'].isin(peps)
            st.session_state.df = df
            st.session_state.screened = True
            st.success("Sanctions screening complete!")
    if st.session_state.screened:
        checks = pd.DataFrame({
            'Check': ['Sanction hits'],
            'Hits': [int(st.session_state.df['SanctionedFlag'].sum())]
        })
        st.table(checks)

    # Stage 3: Fraud Analysis
    st.subheader("Stage 3: Run Fraud Analysis")
    if st.session_state.screened and not st.session_state.fraud_done:
        if st.button("Run Fraud Analysis"):
            df, summary, flags = run_fraud_analysis(df)
            st.session_state.df = df
            st.session_state.summary = summary
            st.session_state.flags = flags
            st.session_state.fraud_done = True
            st.success("Fraud analysis finished!")
    if st.session_state.fraud_done:
        st.markdown("### Fraud Summary")
        st.table(st.session_state.summary)
        st.bar_chart(st.session_state.summary.set_index('Metric'))
        flag_counts = df[st.session_state.flags].sum().sort_values(ascending=False)
        st.markdown("### Fraud Flags Distribution")
        st.bar_chart(flag_counts)

    # Stage 4: Payment Processor Impact
    st.subheader("Stage 4: Payment Processor Impact")
    # Cost assumptions
    fraud_cost = st.number_input("Cost per fraud incident ($)", min_value=0, value=200, step=50)
    sanction_cost = st.number_input("Cost per sanction hit ($)", min_value=0, value=5000, step=500)
    if st.session_state.fraud_done and not st.session_state.processor_done:
        if st.button("Simulate Processor on Raw Data"):
            rm = simulate_processor_cost(st.session_state.raw_df, st.session_state.flags, fraud_cost, sanction_cost)
            st.session_state.raw_metrics = rm
            st.success("Raw data cost simulation complete!")
        if st.button("Simulate Processor on Refined Data"):
            fm = simulate_processor_cost(st.session_state.df, st.session_state.flags, fraud_cost, sanction_cost)
            st.session_state.ref_metrics = fm
            st.session_state.processor_done = True
            st.success("Refined data cost simulation complete!")
    if st.session_state.processor_done:
        rm = st.session_state.raw_metrics
        fm = st.session_state.ref_metrics
        impact_df = pd.DataFrame({
            'Issue Type': ['Sanction Hit','Fraud Incident','Total'],
            'Raw Misses': [rm[0], rm[2], ''],
            'Raw Cost': [rm[1], rm[3], rm[4]],
            'Ref Misses': [fm[0], fm[2], ''],
            'Ref Cost': [fm[1], fm[3], fm[4]],
            'Savings': [rm[1]-fm[1], rm[3]-fm[3], rm[4]-fm[4]]
        })
        st.table(impact_df)
        total_savings = rm[4] - fm[4]
        total_raw = rm[4]
        pct = (total_savings/total_raw*100) if total_raw>0 else 0
        st.markdown(f"**MerchSentAI Impact Summary:** By enriching and screening the data before processing, MerchSentAI helped the payment processor avoid **${{:,}}** in losses, reducing potential costs by {pct:.1f}%.".format(total_savings))

    # Back button
    if st.button("Back to Splash"):
        st.session_state.page = 'splash'

# Run pages
if st.session_state.page == 'splash':
    splash_page()
else:
    analysis_page()
