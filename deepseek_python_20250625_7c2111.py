import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import time
import base64

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
if 'rerun_count' not in st.session_state:
    st.session_state.rerun_count = 0

# Function to display local image
def get_image_base64(path):
    with open(path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode()
    return f"data:image/png;base64,{encoded_string}"

# Rerun function with safety measures
def safe_rerun():
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except:
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
        .logo-container {{
            display: flex;
            justify-content: center;
            margin-bottom: 2rem;
        }}
        .logo {{
            max-width: 80%;
            height: auto;
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
    
    # Fixed logo display
    try:
        # Attempt to display local image
        logo_base64 = get_image_base64("image.png")
        st.markdown(
            f'<div class="logo-container">'
            f'<img src="{logo_base64}" class="logo">'
            f'</div>',
            unsafe_allow_html=True
        )
    except Exception as e:
        # Fallback to direct file reference
        st.markdown(
            '<div class="logo-container">'
            '<img src="app/static/image.png" class="logo">'
            '</div>',
            unsafe_allow_html=True
        )
    
    st.markdown('<h1 class="title">Merchant Risk Intelligence Platform</h1>', unsafe_allow_html=True)
    
    if st.button("Enter the Data World", key="enter_button"):
        st.session_state.page = "analysis"
        st.session_state.rerun_count = 0
        safe_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Fraud detection logic (enhanced for demo)
def run_fraud_analysis(df):
    # Demo data for investor showcase
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
    
    # Screening flags
    df['Sanctioned'] = df['MerchantName'].isin(results['pep_list'])
    df['HighRiskCountry'] = df['Country'].isin(results['high_risk_countries'])
    df['HighRiskCategory'] = df['BusinessCategory'].isin(results['high_risk_categories'])
    
    # Fraud flags
    df['HighAmount'] = df['AvgTransaction'] > 10000
    df['RecentRegistration'] = (pd.to_datetime('today') - pd.to_datetime(df['RegistrationDate'])).dt.days < 30
    df['Suspicious'] = df['HighAmount'] | df['RecentRegistration']
    
    return df, results

# Professional executive summary for investors
def display_executive_summary(df, results):
    st.markdown("### Executive Summary")
    st.markdown("""
    <div style='background-color: #f8fafc; border-left: 4px solid #4f46e5; 
                padding: 1.5rem; border-radius: 8px; margin-top: 1.5rem;'>
        <h4 style='color: #1e3a8a; margin-top: 0;'>Comprehensive Risk Intelligence</h4>
        <p>This MVP demonstrates our AI-powered merchant risk assessment platform that combines:</p>
        <ul>
            <li><strong>Data enrichment</strong> with proprietary algorithms</li>
            <li><strong>Real-time sanctions screening</strong> against global watchlists</li>
            <li><strong>Fraud pattern detection</strong> using behavioral analytics</li>
        </ul>
        
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin: 1.5rem 0;'>
            <div style='background: #eef2ff; padding: 1rem; border-radius: 8px;'>
                <div style='font-size: 1.8rem; font-weight: bold; color: #4f46e5; text-align: center;'>
                    {enrichments}
                </div>
                <div style='text-align: center;'>Data Enrichment Features</div>
            </div>
            <div style='background: #eef2ff; padding: 1rem; border-radius: 8px;'>
                <div style='font-size: 1.8rem; font-weight: bold; color: #4f46e5; text-align: center;'>
                    {fraud_patterns}
                </div>
                <div style='text-align: center;'>Fraud Detection Algorithms</div>
            </div>
            <div style='background: #eef2ff; padding: 1rem; border-radius: 8px;'>
                <div style='font-size: 1.8rem; font-weight: bold; color: #4f46e5; text-align: center;'>
                    {sources}
                </div>
                <div style='text-align: center;'>Data Sources Integrated</div>
            </div>
        </div>
        
        <h4 style='color: #1e3a8a;'>Key Risk Metrics</h4>
        <div style='display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem;'>
            <div style='background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;'>
                <div>Total Merchants</div>
                <div style='font-size: 1.5rem; font-weight: bold; color: #1e3a8a;'>{total_merchants}</div>
            </div>
            <div style='background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;'>
                <div>Sanction Matches</div>
                <div style='font-size: 1.5rem; font-weight: bold; color: #dc2626;'>{sanctioned}</div>
            </div>
            <div style='background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;'>
                <div>High-Risk Jurisdictions</div>
                <div style='font-size: 1.5rem; font-weight: bold; color: #dc2626;'>{high_risk}</div>
            </div>
            <div style='background: white; padding: 1rem; border-radius: 8px; border: 1px solid #e2e8f0;'>
                <div>Suspicious Activity</div>
                <div style='font-size: 1.5rem; font-weight: bold; color: #dc2626;'>{suspicious}</div>
            </div>
        </div>
        
        <h4 style='color: #1e3a8a; margin-top: 1.5rem;'>Technology Showcase</h4>
        <p>This MVP demonstrates our capabilities in:</p>
        <ul>
            <li><strong>Data enrichment pipeline:</strong> {enrichment_details}</li>
            <li><strong>Sanctions screening:</strong> Real-time PEP and watchlist matching</li>
            <li><strong>Fraud detection:</strong> Pattern recognition across {fraud_patterns} behavioral dimensions</li>
            <li><strong>Scalable architecture:</strong> Cloud-native deployment with enterprise-grade security</li>
        </ul>
    </div>
    """.format(
        total_merchants=len(df),
        sanctioned=df['Sanctioned'].sum(),
        high_risk=df['HighRiskCountry'].sum(),
        suspicious=df['Suspicious'].sum(),
        enrichments=len(results['data_enrichments']),
        fraud_patterns=len(results['fraud_patterns']),
        sources=len(results['high_risk_countries']) + len(results['pep_list']),
        enrichment_details=", ".