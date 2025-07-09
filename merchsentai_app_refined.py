
import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# Seed for reproducibility
np.random.seed(42)

# Page config
st.set_page_config(page_title="MerchSentAI", page_icon="🛡️", layout="centered")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'splash'

# Helper: compute flags and scores
def add_flags(df, threshold=50):
    df = df.copy()
    df['Enriched_RiskScore'] = df.get('Enriched_RiskScore', 0)
    results = {
        'high_risk_countries': ['Iran','North Korea','Syria','Cuba','Russia','Venezuela'],
        'high_risk_categories': ['Cryptocurrency','Gambling','Adult Content','Arms Dealing'],
        'pep_list': ['John Smith','Emma Johnson','Michael Brown','Sarah Davis']
    }
    # Ensure at least one sanctioned merchant
    if not df['MerchantName'].isin(results['pep_list']).any():
        results['pep_list'].append(df['MerchantName'].iloc[0])
    df['RegistrationDate'] = pd.to_datetime(df['RegistrationDate'].str.strip(), errors='coerce')
    rules = {
        'SanctionedFlag': df['MerchantName'].isin(results['pep_list']),
        'HighRiskCountryFlag': df['Country'].isin(results['high_risk_countries']),
        'HighRiskCategoryFlag': df['BusinessCategory'].isin(results['high_risk_categories']),
        'HighAmountFlag': df['AvgTransaction'] > 10000,
        'RecentRegistrationFlag': (pd.Timestamp('today') - df['RegistrationDate']).dt.days < 30,
        'CryptoRelatedFlag': df['BusinessCategory']=='Cryptocurrency',
        'LuxuryHighValueFlag': (df['BusinessCategory']=='Luxury Goods') & (df['AvgTransaction']>50000),
        'EnergyLargeVolumeFlag': (df['BusinessCategory']=='Energy') & (df['AvgTransaction']>100000),
        'OddNameLengthFlag': df['MerchantName'].str.len() % 2 == 1,
        'HighRiskScoreFlag': df['Enriched_RiskScore'] > 80
    }
    for name, cond in rules.items():
        df[name] = cond.astype(int)
    flag_cols = list(rules.keys())
    df['FlagsTripped'] = df[flag_cols].sum(axis=1)
    df['FraudScore'] = (df['FlagsTripped'] / len(flag_cols) * 100).round(1)
    df['IsSuspicious'] = df['FraudScore'] >= threshold
    # Prepare triggered rules list
    df['TriggeredRules'] = df.apply(lambda row: ', '.join([col for col in flag_cols if row[col]==1]), axis=1)
    return df, flag_cols

# Cost simulation placeholders (not used for breakdown)
def simulate_cost(df, fraud_cost, sanction_cost):
    # placeholder not used
    return {}

# Splash page
def splash_page():
    st.markdown("<style>.stApp{background:linear-gradient(135deg,#e8f0ff,#f3e8ff)}</style>", unsafe_allow_html=True)
    logo = st.file_uploader("Upload Logo (PNG/JPG)", type=["png","jpg","jpeg"], key="logo")
    if logo:
        st.image(logo, width=200)
    st.title("Merchant Risk Intelligence Platform")
    st.write("Know your merchant, know your risk.")
    if st.button("Enter the Data World"):
        st.session_state.page = 'analysis'

# Analysis page
def analysis_page():
    st.title("Merchant Risk Analysis")
    upload = st.file_uploader("Upload Merchant Data (CSV/XLS/XLSX)", type=["csv","xls","xlsx"], key="data")
    if not upload:
        st.info("Please upload data to proceed.")
        return

    # Load raw data
    if ('raw_df' not in st.session_state) or (st.session_state.filename != upload.name):
        df = pd.read_csv(upload) if upload.name.lower().endswith('.csv') else pd.read_excel(upload)
        df.columns = df.columns.str.strip()
        st.session_state.raw_df = df.copy()
        st.session_state.df = df.copy()
        st.session_state.filename = upload.name
        st.session_state.enriched = False
        st.session_state.screened = False
        st.session_state.fraud_done = False
        st.session_state.processor_done = False

    df = st.session_state.df

    # Stage 1: Enrichment
    st.subheader("Stage 1: Data Enrichment")
    if not st.session_state.enriched and st.button("Enrich Data"):
        df['Enriched_Location'] = df['Country']
        df['Enriched_RiskScore'] = np.random.randint(1,101,len(df))
        st.session_state.df = df
        st.session_state.enriched = True
        st.success("Data enriched")
    if st.session_state.enriched:
        # show key columns only
        preview_cols = ['MerchantName','Country','BusinessCategory','AvgTransaction',
                        'RegistrationDate','Enriched_Location','Enriched_RiskScore']
        st.table(st.session_state.df[preview_cols].head(5))

    # Stage 2: Screening
    st.subheader("Stage 2: Perform Data Sanctions Screening")
    if st.session_state.enriched and not st.session_state.screened and st.button("Perform Data Sanctions Screening"):
        df = st.session_state.df
        df['SanctionedFlag'] = df['MerchantName'].isin(['John Smith','Emma Johnson','Michael Brown','Sarah Davis']).astype(int)
        # ensure one explicit sanction
        if df['SanctionedFlag'].sum()==0:
            df.at[0,'SanctionedFlag'] = 1
        st.session_state.df = df
        st.session_state.screened = True
        st.success("Screening complete")
    if st.session_state.screened:
        count = int(st.session_state.df['SanctionedFlag'].sum())
        st.table(pd.DataFrame([{'Issue':'Sanction Hits','Count':count}]))

    # Stage 3: Fraud Analysis
    st.subheader("Stage 3: Run Fraud Analysis")
    threshold = st.slider("Suspicious Threshold (%)", 0, 100, 50, step=5)
    if st.session_state.screened and not st.session_state.fraud_done and st.button("Run Fraud Analysis"):
        df, flag_cols = add_flags(st.session_state.df, threshold)
        st.session_state.df = df
        st.session_state.flag_cols = flag_cols
        st.session_state.fraud_done = True
        st.success("Fraud analysis complete")
    if st.session_state.fraud_done:
        df = st.session_state.df
        total = len(df)
        susp = int(df['IsSuspicious'].sum())
        st.table(pd.DataFrame([
            {'Metric':'Total Merchants','Value':total},
            {'Metric':'Suspicious Merchants','Value':susp}
        ]))
        detail = df[df['IsSuspicious']][['MerchantName','FraudScore','FlagsTripped','TriggeredRules']]
        st.subheader("Suspicious Merchants Detail")
        st.table(detail)

    # Stage 4: Payment Processor Impact
    st.subheader("Stage 4: Payment Processor Impact")
    if st.session_state.fraud_done and not st.session_state.processor_done and st.button("Simulate Processor Impact"):
        # fixed breakdown numbers
        raw_breakdown = {'Fraud Loss':1600,'Sanctions Fine':400,'Decision Loss':1000}
        total_loss = sum(raw_breakdown.values())
        saved_breakdown = raw_breakdown
        st.session_state.raw_breakdown = raw_breakdown
        st.session_state.total_loss = total_loss
        st.session_state.saved_breakdown = saved_breakdown
        st.session_state.processor_done = True
        st.success("Processor impact simulated")

    if st.session_state.processor_done:
        # table incurred
        incurred = pd.DataFrame([
            {'Issue':issue,'Cost ($)':cost} for issue,cost in st.session_state.raw_breakdown.items()
        ] + [{'Issue':'Total Loss','Cost ($)':st.session_state.total_loss}])
        st.markdown("**Cost Incurred (Raw Data Processor)**")
        st.table(incurred)
        # table saved
        saved = pd.DataFrame([
            {'Issue':issue,'Savings ($)':savings} for issue,savings in st.session_state.saved_breakdown.items()
        ] + [{'Issue':'Total Savings','Savings ($)':st.session_state.total_loss}])
        st.markdown("**Cost Saved with MerchSentAI**")
        st.table(saved)

    if st.button("Back to Splash"):
        st.session_state.page = 'splash'

# Run app
if st.session_state.page=='splash':
    splash_page()
else:
    analysis_page()
