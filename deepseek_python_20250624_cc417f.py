import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time  # Added for fallback rerun

# Page configuration
st.set_page_config(
    page_title="MerchSentAI",
    layout="centered",
    page_icon="🛡️"
)

# Session state setup
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'data' not in st.session_state:
    st.session_state.data = None
if 'results' not in st.session_state:
    st.session_state.results = {}
if 'rerun_count' not in st.session_state:  # Added for rerun protection
    st.session_state.rerun_count = 0

# Rerun function with safety measures
def safe_rerun():
    try:
        st.rerun()  # Modern method (v1.12+)
    except AttributeError:
        try:
            st.experimental_rerun()  # Legacy method
        except:
            # Ultimate fallback
            st.experimental_set_query_params(rerun=time.time())
            st.experimental_rerun()

# Main page
def main_page():
    st.markdown(
        f"""
        <style>
        .main {{
            background-color: #f0f2f6;
            padding: 2rem;
            border-radius: 10px;
        }}
        .title {{
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            margin-bottom: 1.5rem;
            color: #1e3a8a;
        }}
        .logo {{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 60%;
        }}
        .stButton>button {{
            background-color: #4f46e5;
            color: white;
            font-weight: bold;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            margin-top: 1.5rem;
            width: 100%;
            transition: all 0.3s;
        }}
        .stButton>button:hover {{
            background-color: #3730a3;
            transform: scale(1.05);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div class="main">', unsafe_allow_html=True)
    # FIX 1: Replaced use_column_width with use_container_width
    st.image("https://via.placeholder.com/600x200?text=MerchSentAI+Logo", 
             width=300, 
             use_container_width=True,  # Updated parameter
             output_format='auto')
    
    st.markdown('<h1 class="title">Merchant Risk Intelligence Platform</h1>', unsafe_allow_html=True)
    
    if st.button("Enter the Data World", key="enter_button"):
        st.session_state.page = "analysis"
        # FIX 2: Using safe rerun with protection
        st.session_state.rerun_count = 0
        safe_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Fraud detection logic (simplified)
def run_fraud_analysis(df):
    results = {
        'high_risk_countries': ['Iran', 'North Korea', 'Syria', 'Cuba'],
        'high_risk_categories': ['Cryptocurrency', 'Gambling', 'Adult'],
        'pep_list': ['John Smith', 'Emma Johnson', 'Michael Brown']
    }
    
    # Screening flags
    df['Sanctioned'] = df['MerchantName'].isin(results['pep_list'])
    df['HighRiskCountry'] = df['Country'].isin(results['high_risk_countries'])
    df['HighRiskCategory'] = df['BusinessCategory'].isin(results['high_risk_categories'])
    
    # Fraud flags
    df['HighAmount'] = df['AvgTransaction'] > 10000
    df['RecentRegistration'] = (pd.to_datetime('today') - pd.to_datetime(df['RegistrationDate'])).dt.days < 30
    df['Suspicious'] = df['HighAmount'] | df['RecentRegistration']
    
    return df, results

# Analysis page
def analysis_page():
    st.markdown(
        f"""
        <style>
        .tab {{
            background-color: #eef2ff;
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
        }}
        .tab-header {{
            color: #4f46e5;
            font-weight: bold;
            font-size: 1.2rem;
        }}
        .summary-box {{
            background-color: #f8fafc;
            border-left: 4px solid #4f46e5;
            padding: 1rem;
            margin-top: 1.5rem;
            border-radius: 4px;
        }}
        .metric {{
            font-size: 1.1rem;
            margin-bottom: 0.5rem;
        }}
        .metric-value {{
            font-weight: bold;
            color: #1e3a8a;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.title("Merchant Risk Analysis")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Merchant Data (Excel)", type=["xlsx", "csv"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.session_state.data = df
        except Exception as e:
            st.error(f"Error reading file: {e}")
            st.session_state.data = None
    elif st.session_state.data is None:
        st.info("Using sample dataset for demo")
        try:
            # FIX 3: Added error handling for sample data
            st.session_state.data = pd.read_excel("sample_merchants.xlsx")
        except Exception as e:
            st.error(f"Could not load sample data: {e}")
            st.session_state.data = pd.DataFrame({
                'MerchantID': [1, 2, 3],
                'MerchantName': ['Test1', 'Test2', 'Test3'],
                'Country': ['USA', 'Canada', 'UK'],
                'Region': ['West', 'East', 'North'],
                'BusinessCategory': ['Retail', 'Services', 'Tech'],
                'AvgTransaction': [5000, 15000, 8000],
                'RegistrationDate': ['2023-01-01', '2024-05-01', '2022-12-15']
            })
    
    if st.session_state.data is not None:
        df = st.session_state.data.copy()
        
        # Ensure required columns exist (FIX 4: Added column validation)
        required_columns = ['MerchantName', 'Country', 'BusinessCategory', 'AvgTransaction', 'RegistrationDate']
        for col in required_columns:
            if col not in df.columns:
                df[col] = f"Missing {col}"
        
        # Data Enrichment Tab
        with st.expander("📊 Data Enrichment", expanded=True):
            st.markdown('<div class="tab">', unsafe_allow_html=True)
            st.markdown('<div class="tab-header">Data Enrichment</div>', unsafe_allow_html=True)
            
            # Add enrichment columns
            df['Enriched_Location'] = df['Country'] + " | " + df.get('Region', 'N/A')
            df['Enriched_RiskScore'] = np.random.randint(1, 100, size=len(df))
            
            st.success("✅ Data enrichment completed")
            st.write("Added columns: Enriched_Location, Enriched_RiskScore")
            st.dataframe(df.head(3))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Sanctions/Screening Tab
        with st.expander("🔍 Sanctions/Screening", expanded=True):
            st.markdown('<div class="tab">', unsafe_allow_html=True)
            st.markdown('<div class="tab-header">Sanctions & Screening</div>', unsafe_allow_html=True)
            
            df, results = run_fraud_analysis(df)
            
            st.success("✅ Screening completed")
            st.write(f"Flagged {df['Sanctioned'].sum()} sanctioned merchants")
            st.write(f"Flagged {df['HighRiskCountry'].sum()} high-risk country merchants")
            st.dataframe(df[['MerchantID', 'MerchantName', 'Sanctioned', 'HighRiskCountry']].head(3))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Fraud Analysis Tab
        with st.expander("🕵️ Fraud Analysis", expanded=True):
            st.markdown('<div class="tab">', unsafe_allow_html=True)
            st.markdown('<div class="tab-header">Fraud Detection</div>', unsafe_allow_html=True)
            
            # FIX 5: Ensure date conversion
            try:
                df['RegistrationDate'] = pd.to_datetime(df['RegistrationDate'])
                today = pd.Timestamp(datetime.today().date())
                df['RecentRegistration'] = (today - df['RegistrationDate']).dt.days < 30
                df['Suspicious'] = df['HighAmount'] | df['RecentRegistration']
            except Exception as e:
                st.error(f"Date processing error: {e}")
                df['RecentRegistration'] = False
                df['Suspicious'] = df['HighAmount']
            
            st.success("✅ Fraud analysis completed")
            st.write(f"Flagged {df['Suspicious'].sum()} suspicious merchants")
            st.write(f"Identified {df['HighAmount'].sum()} high-value transactions")
            st.dataframe(df[['MerchantID', 'MerchantName', 'Suspicious', 'HighAmount']].head(3))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Executive Summary
        st.markdown("### Executive Summary")
        st.markdown('<div class="summary-box">', unsafe_allow_html=True)
        
        total_merchants = len(df)
        sanctioned = df['Sanctioned'].sum()
        high_risk = df['HighRiskCountry'].sum()
        suspicious = df['Suspicious'].sum()
        
        st.markdown(f'<div class="metric">Total Merchants Analyzed: <span class="metric-value">{total_merchants}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric">Sanction Matches: <span class="metric-value">{sanctioned}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric">High-Risk Country Flags: <span class="metric-value">{high_risk}</span></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric">Suspicious Activity Flags: <span class="metric-value">{suspicious}</span></div>', unsafe_allow_html=True)
        
        st.markdown("**Analysis Performed:**")
        st.markdown("- Data enrichment with location and risk scoring")
        st.markdown("- PEP and sanctions screening")
        st.markdown("- High-risk country identification")
        st.markdown("- Fraud pattern detection (high-value transactions, new registrations)")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download results
        st.download_button(
            label="Download Full Report",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name='merchant_risk_report.csv',
            mime='text/csv'
        )
    
    if st.button("Back to Main"):
        st.session_state.page = 'main'
        st.session_state.data = None
        # FIX 6: Safe rerun with counter
        if st.session_state.rerun_count < 3:
            st.session_state.rerun_count += 1
            safe_rerun()
        else:
            st.session_state.rerun_count = 0
            st.experimental_rerun = lambda: None  # Prevent infinite loop

# Page routing
if st.session_state.page == 'main':
    main_page()
elif st.session_state.page == 'analysis':
    analysis_page()