
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
    # Define rule conditions
    results = {
        'high_risk_countries': ['Iran','North Korea','Syria','Cuba','Russia','Venezuela'],
        'high_risk_categories': ['Cryptocurrency','Gambling','Adult Content','Arms Dealing'],
        'pep_list': ['John Smith','Emma Johnson','Michael Brown','Sarah Davis']
    }
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
    return df, flag_cols

# Cost simulation
def simulate_cost(df, fraud_cost, sanction_cost):
    sanction_count = int(df['SanctionedFlag'].sum())
    fraud_count = int(df['IsSuspicious'].sum())
    sanction_cost_total = sanction_count * sanction_cost
    fraud_cost_total = fraud_count * fraud_cost
    total_loss = sanction_cost_total + fraud_cost_total
    return {
        'Sanction Hits': sanction_count,
        'Suspicious Incidents': fraud_count,
        'Sanction Cost': sanction_cost_total,
        'Fraud Cost': fraud_cost_total,
        'Total Loss': total_loss
    }

# Splash page
def splash_page():
    st.markdown("<style>.stApp{background:linear-gradient(135deg,#e8f0ff,#f3e8ff)}</style>", unsafe_allow_html=True)
    logo = st.file_uploader("Upload Logo (PNG/JPG)", type=["png","jpg","jpeg"], key="logo")
    if logo:
        st.image(logo, use_column_width=True)
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
        df['Enriched_Location'] = df.get('Country', np.nan)
        df['Enriched_RiskScore'] = np.random.randint(1,101,len(df))
        st.session_state.df = df
        st.session_state.enriched = True
        st.success("Data enriched")
    if st.session_state.enriched:
        st.table(df.head())

    # Stage 2: Sanctions Screening
    st.subheader("Stage 2: Perform Data Sanctions Screening")
    if st.session_state.enriched and not st.session_state.screened and st.button("Perform Data Sanctions Screening"):
        peps = ['John Smith','Emma Johnson','Michael Brown','Sarah Davis']
        df['SanctionedFlag'] = df['MerchantName'].isin(peps).astype(int)
        st.session_state.df = df
        st.session_state.screened = True
        st.success("Screening complete")
    if st.session_state.screened:
        count = int(df['SanctionedFlag'].sum())
        st.table(pd.DataFrame([{'Issue':'Sanction Hits','Count':count}]))

    # Stage 3: Fraud Analysis
    st.subheader("Stage 3: Run Fraud Analysis")
    threshold = st.slider("Suspicious Threshold (%)", 0, 100, 50, step=5)
    if st.session_state.screened and not st.session_state.fraud_done and st.button("Run Fraud Analysis"):
        df, flag_cols = add_flags(df, threshold)
        st.session_state.df = df
        st.session_state.flag_cols = flag_cols
        st.session_state.fraud_done = True
        st.success("Fraud analysis complete")
    if st.session_state.fraud_done:
        total = len(df)
        susp = int(df['IsSuspicious'].sum())
        st.table(pd.DataFrame([
            {'Metric':'Total Merchants','Value':total},
            {'Metric':'Suspicious Merchants','Value':susp}
        ]))
        detail = df[df['IsSuspicious']][['MerchantName','FraudScore','FlagsTripped']+st.session_state.flag_cols]
        st.subheader("Suspicious Merchants Detail")
        st.table(detail)

    # Stage 4: Payment Processor Impact with two tables
    st.subheader("Stage 4: Payment Processor Impact")
    fraud_cost = st.number_input("Cost per fraud incident ($)", min_value=0, value=200, step=50)
    sanction_cost = st.number_input("Cost per sanction hit ($)", min_value=0, value=5000, step=500)
    if st.session_state.fraud_done and not st.session_state.processor_done and st.button("Simulate Processor Impact"):
        raw_df = st.session_state.raw_df.copy()
        raw_df, _ = add_flags(raw_df, threshold)
        raw_metrics = simulate_cost(raw_df, fraud_cost, sanction_cost)
        ref_metrics = simulate_cost(df, fraud_cost, sanction_cost)
        st.session_state.raw_metrics = raw_metrics
        st.session_state.ref_metrics = ref_metrics
        st.session_state.processor_done = True
        st.success("Processor impact simulated")

    if st.session_state.processor_done:
        rm = st.session_state.raw_metrics
        ref = st.session_state.ref_metrics
        # Table 1: cost incurred by raw processor
        incurred = pd.DataFrame([
            {'Issue':'Sanction Hits','Raw Count':rm['Sanction Hits'],'Raw Cost ($)':rm['Sanction Cost']},
            {'Issue':'Suspicious Incidents','Raw Count':rm['Suspicious Incidents'],'Raw Cost ($)':rm['Fraud Cost']},
            {'Issue':'Total Loss','Raw Count':'','Raw Cost ($)':rm['Total Loss']}
        ])
        st.markdown("**Cost Incurred (Raw Data Processor)**")
        st.table(incurred)

        # Table 2: cost saved with MerchSentAI
        saved = pd.DataFrame([
            {'Issue':'Sanction Hits','Raw Cost ($)':rm['Sanction Cost'],'Refined Cost ($)':ref['Sanction Cost'],'Savings ($)':rm['Sanction Cost']-ref['Sanction Cost']},
            {'Issue':'Suspicious Incidents','Raw Cost ($)':rm['Fraud Cost'],'Refined Cost ($)':ref['Fraud Cost'],'Savings ($)':rm['Fraud Cost']-ref['Fraud Cost']},
            {'Issue':'Total Loss','Raw Cost ($)':rm['Total Loss'],'Refined Cost ($)':ref['Total Loss'],'Savings ($)':rm['Total Loss']-ref['Total Loss']}
        ])
        st.markdown("**Cost Saved with MerchSentAI**")
        st.table(saved)

        total_saved = rm['Total Loss'] - ref['Total Loss']
        st.markdown(f"**MerchSentAI Impact Summary:** By enriching and screening, the processor avoids **${total_saved:,}** in potential losses.")

    if st.button("Back to Splash"):
        st.session_state.page = 'splash'

# Run app
if st.session_state.page == 'splash':
    splash_page()
else:
    analysis_page()
