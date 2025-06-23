import pandas as pd
from rapidfuzz import fuzz, process

# Define sanction list and risk keywords
SANCTION_LIST = [
    "Walmart", "Best Buy", "Target", "Amazon", "Shopify", "eBay", "Costco",
    "Evil Corp", "Fraudulent Co", "Scammy Store", "Sanctioned Entity", "Money Laundering Services"
]

HIGH_RISK_CATEGORIES = [
    'Cryptocurrency', 'Gambling', 'Adult Entertainment', 'Firearms',
    'Explosives', 'Unlicensed Pharma', 'Luxury Goods', 'Pawn Shop'
]

HIGH_RISK_COUNTRIES = [
    'North Korea', 'Iran', 'Syria', 'Russia', 'Venezuela', 'Myanmar'
]

ADVERSE_KEYWORDS = [
    'fraud', 'scam', 'money laundering', 'illegal', 'bribery', 'corruption',
    'smuggling', 'black market', 'embezzlement', 'pyramid', 'lawsuit', 'arrest'
]

def fuzzy_match(name, name_list, threshold=80):
    matches = process.extract(name, name_list, scorer=fuzz.token_sort_ratio, limit=1)
    if matches:
        best_match, score, _ = matches[0]
        return score >= threshold
    return False

def screen_merchants(df):
    flags = []
    for _, row in df.iterrows():
        name = row.get("merchant_name", "")
        category = row.get("merchant_category", "")
        country = row.get("merchant_country", "CA")
        website = row.get("merchant_website", "").lower()

        reasons = []

        if name in SANCTION_LIST:
            reasons.append("Exact match: sanction list")
        elif fuzzy_match(name, SANCTION_LIST):
            reasons.append("Fuzzy match: sanction list")

        if category in HIGH_RISK_CATEGORIES:
            reasons.append(f"High risk category: {category}")

        if country in HIGH_RISK_COUNTRIES:
            reasons.append(f"High risk country: {country}")

        if any(keyword in website for keyword in ADVERSE_KEYWORDS):
            reasons.append("Adverse media keywords in website")

        df.at[_, 'screening_flag'] = "; ".join(reasons) if reasons else "Clear"

    return df
