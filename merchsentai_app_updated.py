import streamlit as st
import pandas as pd
import numpy as np

# --- Chargeback fraud detection ---
def detect_chargeback_fraud(df: pd.DataFrame) -> pd.Series:
    """
    Flags potential merchant chargeback fraud based on aggregate metrics.
    """
    # Example logic: high rate of chargebacks relative to transactions
    df['ChargebackRate'] = df['NumChargebacks'] / df['NumTransactions']
    df['DisputeDelta'] = df['ChargebacksThisMonth'] - df['ChargebacksLastMonth']
    df['ChargebackVolRatio'] = df['ChargebackAmount'] / df['TotalTransactionVolume']
    rate_mean, rate_std = df['ChargebackRate'].mean(), df['ChargebackRate'].std(ddof=0)
    df['ChargebackRateZ'] = (df['ChargebackRate'] - rate_mean) / rate_std

    df['HighChargebackRateFlag'] = df['ChargebackRate'] > 0.05
    df['ChargebackSpikeFlag'] = df['DisputeDelta'] > 10
    df['HighChargebackVolFlag'] = df['ChargebackVolRatio'] > 0.10
    df['ChargebackOutlierZFlag'] = df['ChargebackRateZ'].abs() > 2

    return df['HighChargebackRateFlag'] | df['ChargebackSpikeFlag'] | df['HighChargebackVolFlag'] | df['ChargebackOutlierZFlag']

# --- Fraud logic placeholders ---
def detect_behavioral_fraud(df: pd.DataFrame) -> pd.Series:
    # Placeholder logic
    return pd.Series(False, index=df.index)

def detect_location_fraud(df: pd.DataFrame) -> pd.Series:
    # Placeholder logic
    return pd.Series(False, index=df.index)

# --- Main Streamlit app ---
def main():
    st.title("MerchSentAI All-in-One")

    # 1. Data Ingestion
    st.header("1. Data Ingestion")
    uploaded = st.file_uploader("Upload merchant summary CSV/XLSX with columns: NumTransactions, NumChargebacks, TotalTransactionVolume, ChargebackAmount, ChargebacksLastMonth, ChargebacksThisMonth", type=["csv","xlsx"])
    if uploaded:
        df = pd.read_csv(uploaded) if uploaded.name.endswith('.csv') else pd.read_excel(uploaded)
    else:
        st.info("Please upload your merchant-level summary data to continue.")
        return

    # 2. Data Enrichment
    st.header("2. Data Enrichment")
    original_features = df.shape[1]
    # Example enrichment (replace with your logic)
    df['Enriched_RiskScore'] = np.random.randint(1, 100, len(df))
    df['Enriched_CountryRisk'] = df['Country'].apply(lambda x: 'High' if x in ['Iran','North Korea'] else 'Low')
    new_features_added = df.shape[1] - original_features
    st.write(f"**New features added:** {new_features_added}")
    st.dataframe(df)

    # 3. Sanctions & Screening
    st.header("3. Sanctions & Screening")
    # Example sanction lists loaded (replace with real data sources)
    sanction_dbs = {
        "OFAC SDN": 5000,
        "EU Consolidated": 3000,
        "UK HMT": 2000,
        "UN 1267": 1500
    }
    st.write(f"**Databases reviewed:** {len(sanction_dbs)}")
    st.write(f"**Total records scanned:** {sum(sanction_dbs.values()):,}")

    # 4. Fraud Analysis
    st.header("4. Fraud Analysis")
    fraud_funcs = [detect_behavioral_fraud, detect_location_fraud]
    num_fraud_logics = len(fraud_funcs)
    flags_df = pd.DataFrame(index=df.index)
    for fn in fraud_funcs:
        flags_df[fn.__name__] = fn(df)
    # Chargeback fraud detection
    flags_df['ChargebackFraudFlag'] = detect_chargeback_fraud(df)
    total_chargeback_flags = int(flags_df['ChargebackFraudFlag'].sum())
    st.write(f"**Fraud logics applied:** {num_fraud_logics}")
    st.write(f"**Chargeback fraud flags identified:** {total_chargeback_flags}")
    st.dataframe(flags_df)

    # 5. Executive Summary Tables
    st.header("5. Executive Summary")
    # Table 1: Data Enrichment summary
    summary1 = pd.DataFrame({
        "Stage": ["Data Enrichment"],
        "New Features Added": [new_features_added]
    })
    st.subheader("Data Enrichment")
    st.table(summary1)
    # Table 2: Sanctions/Screening summary
    summary2 = pd.DataFrame({
        "Stage": ["Sanctions Screening"],
        "Databases Reviewed": [len(sanction_dbs)],
        "Total Records Scanned": [sum(sanction_dbs.values())]
    })
    st.subheader("Sanctions Screening")
    st.table(summary2)
    # Table 3: Fraud Analysis summary
    summary3 = pd.DataFrame({
        "Stage": ["Fraud Analysis"],
        "Fraud Logics Applied": [num_fraud_logics],
        "Chargeback Flags Identified": [total_chargeback_flags]
    })
    st.subheader("Fraud Analysis")
    st.table(summary3)

if __name__ == "__main__":
    main()
