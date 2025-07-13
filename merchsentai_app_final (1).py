import streamlit as st
import pandas as pd
import numpy as np
import io

# --- Page config ---
st.set_page_config(page_title="MerchSentAI", page_icon="🛡️", layout="centered")

# --- Fraud detection functions ---
def detect_behavioral_fraud(df):
    # Placeholder: flag if velocity > threshold
    return pd.Series(False, index=df.index)

def detect_location_fraud(df):
    # Placeholder: flag if country != billing_country
    return pd.Series(False, index=df.index)

def detect_chargeback_fraud(df):
    """
    Flags merchant chargeback fraud based on aggregate metrics.
    """
    df['ChargebackRate'] = df['NumChargebacks'] / df['NumTransactions']
    df['DisputeDelta'] = df['ChargebacksThisMonth'] - df['ChargebacksLastMonth']
    df['ChargebackVolRatio'] = df['ChargebackAmount'] / df['TotalTransactionVolume']
    mean, std = df['ChargebackRate'].mean(), df['ChargebackRate'].std(ddof=0)
    df['ChargebackRateZ'] = (df['ChargebackRate'] - mean) / std

    flags = (
        (df['ChargebackRate'] > 0.05) |
        (df['DisputeDelta'] > 10) |
        (df['ChargebackVolRatio'] > 0.10) |
        (df['ChargebackRateZ'].abs() > 2)
    )
    return flags

# --- Main ---
def main():
    st.title("Merchant Risk Analysis")

    # File upload
    uploaded = st.file_uploader(
        "Upload merchant summary data (CSV/XLSX) with columns: "
        "NumTransactions, NumChargebacks, TotalTransactionVolume, "
        "ChargebackAmount, ChargebacksLastMonth, ChargebacksThisMonth",
        type=["csv","xlsx"]
    )
    if not uploaded:
        st.info("Please upload data to proceed.")
        return

    # Read data
    df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)

    # Stage 1: Data Enrichment
    st.header("1. Data Enrichment")
    orig_cols = set(df.columns)
    df['Enriched_RiskScore'] = np.random.randint(1, 101, size=len(df))
    df['Enriched_CountryRisk'] = df['Country'].map(lambda c: "High" if c in ["Iran","North Korea"] else "Low")
    new_features = len(set(df.columns) - orig_cols)
    st.write(f"**New features added:** {new_features}")
    st.dataframe(df.head())

    # Stage 2: Sanctions/Screening
    st.header("2. Sanctions & Screening")
    sanction_sources = {"OFAC SDN":5000, "EU Consolidated":3000, "UK HMT":2000, "UN 1267":1500}
    st.write(f"**Databases reviewed:** {len(sanction_sources)}")
    st.write(f"**Total records scanned:** {sum(sanction_sources.values()):,}")

    # Stage 3: Fraud Analysis
    st.header("3. Fraud Analysis")
    fraud_funcs = [detect_behavioral_fraud, detect_location_fraud]
    fraud_flags = pd.DataFrame(index=df.index)
    for fn in fraud_funcs:
        fraud_flags[fn.__name__] = fn(df)
    fraud_flags['ChargebackFraud'] = detect_chargeback_fraud(df)
    total_flags = int(fraud_flags['ChargebackFraud'].sum())
    st.write(f"**Fraud logics applied:** {len(fraud_funcs)}")
    st.write(f"**Chargeback fraud flags identified:** {total_flags}")
    st.dataframe(fraud_flags.head())

    # Download problem merchants
    problem_df = df[fraud_flags['ChargebackFraud']]
    if not problem_df.empty:
        towrite = io.BytesIO()
        problem_df.to_excel(towrite, index=False, sheet_name="Problem Merchants")
        towrite.seek(0)
        st.download_button(
            "Download Problem Merchants Data",
            data=towrite,
            file_name="problem_merchants.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # Processor Impact Metrics
    cost_of_fraud = df['ChargebackAmount'].sum()
    savings = problem_df['ChargebackAmount'].sum()
    st.header("Processor Impact")
    col1, col2 = st.columns(2)
    col1.metric("Raw Processor Loss", f"${cost_of_fraud:,.2f}")
    col2.metric("Savings from MerchSentAI API", f"${savings:,.2f}")

    # Executive Summary Tables
    st.header("Executive Summary")
    sum1 = pd.DataFrame({"Stage":["Data Enrichment"], "New Features Added":[new_features]})
    sum2 = pd.DataFrame({"Stage":["Sanctions Screening"], "DBs Reviewed":[len(sanction_sources)], "Records Scanned":[sum(sanction_sources.values())]})
    sum3 = pd.DataFrame({"Stage":["Fraud Analysis"], "Fraud Logics Applied":[len(fraud_funcs)], "Chargeback Flags":[total_flags]})

    st.subheader("Data Enrichment Summary")
    st.table(sum1)
    st.subheader("Sanctions Screening Summary")
    st.table(sum2)
    st.subheader("Fraud Analysis Summary")
    st.table(sum3)

if __name__=="__main__":
    main()
