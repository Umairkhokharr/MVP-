import pandas as pd

def analyze_fraud(df):
    df = df.copy()

    # Normalize date column
    timestamp_col = next((col for col in df.columns if 'time' in col or 'date' in col), None)
    merchant_col = next((col for col in df.columns if 'merchant' in col.lower()), None)

    if not timestamp_col or not merchant_col:
        raise ValueError("Timestamp or Merchant column not found.")

    df[timestamp_col] = pd.to_datetime(df[timestamp_col], errors='coerce')
    df = df.dropna(subset=[timestamp_col, merchant_col])

    # Flag: transaction bursts per merchant per hour
    tx_counts = df.groupby([merchant_col, pd.Grouper(key=timestamp_col, freq='1h')]).size()
    burst_merchants = tx_counts[tx_counts > 10].reset_index()[merchant_col].unique()

    # Flag: merchant with inconsistent location records (e.g., too many distinct locations)
    if 'merchant_location' in df.columns:
        location_flags = df.groupby(merchant_col)['merchant_location'].nunique()
        flagged_locations = location_flags[location_flags > 2].index.tolist()
    else:
        flagged_locations = []

    # Assign fraud risk flags
    df['fraud_flag'] = df[merchant_col].apply(
        lambda x: 'HIGH' if x in burst_merchants or x in flagged_locations else 'LOW'
    )

    return df
