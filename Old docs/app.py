
# MerchSentAI Streamlit MVP with session state and charts
import streamlit as st
import pandas as pd
import plotly.express as px
from api.enrichment import enrich_merchants
from api.screening import screen_merchants
from api.analysis import analyze_fraud

st.set_page_config(page_title="MerchSentAI MVP", layout="wide")
st.title("🛡️ MerchSentAI - Merchant Risk & Fraud Detection")

# Step 1: File Upload
st.header("Step 1: Upload Raw Transaction Data")
uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.session_state["raw_df"] = df
    st.success("✅ File uploaded successfully.")
    st.dataframe(df.head())

# Step 2: Data Enrichment
if "raw_df" in st.session_state:
    st.header("Step 2: Data Enrichment")
    if st.button("Run Enrichment") or "enriched_df" in st.session_state:
        if "enriched_df" not in st.session_state:
            enriched_df = enrich_merchants(st.session_state["raw_df"])
            st.session_state["enriched_df"] = enriched_df
        else:
            enriched_df = st.session_state["enriched_df"]

        st.success("✅ Data enrichment complete.")
        st.dataframe(enriched_df.head())

        # Enrichment Stats
        st.subheader("🔍 Enrichment Insights")
        col1, col2 = st.columns(2)
        with col1:
            cat_count = enriched_df["merchant_category"].value_counts()
            fig = px.bar(cat_count, x=cat_count.index, y=cat_count.values, labels={"x": "Category", "y": "Count"}, title="Merchant Categories")
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.metric("Total Transactions Enriched", len(enriched_df))

# Step 3: Screening
if "enriched_df" in st.session_state:
    st.header("Step 3: Sanctions & Risk Screening")
    if st.button("Run Screening") or "screened_df" in st.session_state:
        if "screened_df" not in st.session_state:
            screened_df = screen_merchants(st.session_state["enriched_df"])
            st.session_state["screened_df"] = screened_df
        else:
            screened_df = st.session_state["screened_df"]

        st.success("✅ Screening complete.")
        st.dataframe(screened_df.head())

        # Screening Stats
        st.subheader("🔍 Screening Insights")
        flagged = screened_df[screened_df['screening_flag'] != "Clear"]
        st.metric("Flagged Merchants", len(flagged))
        st.metric("Screened Clean Merchants", len(screened_df) - len(flagged))

# Step 4: Fraud Analysis
if "screened_df" in st.session_state:
    st.header("Step 4: Fraud Risk Analysis")
    if st.button("Run Fraud Analysis") or "analyzed_df" in st.session_state:
        if "analyzed_df" not in st.session_state:
            clean_df = st.session_state["screened_df"]
            clean_df = clean_df[clean_df['screening_flag'] == "Clear"]
            analyzed_df = analyze_fraud(clean_df)
            st.session_state["analyzed_df"] = analyzed_df
        else:
            analyzed_df = st.session_state["analyzed_df"]

        st.success("✅ Fraud analysis complete.")
        st.dataframe(analyzed_df.head())

        # Fraud Insights
        st.subheader("📊 Fraud Risk Breakdown")
        risk_chart = analyzed_df['fraud_flag'].value_counts().reset_index()
        risk_chart.columns = ['Risk Level', 'Count']
        fig = px.pie(risk_chart, names='Risk Level', values='Count', title='Fraud Risk Distribution')
        st.plotly_chart(fig, use_container_width=True)

        # Final Download Option
        st.download_button("Download Final Output", analyzed_df.to_csv(index=False), "merchant_risk_results.csv")
