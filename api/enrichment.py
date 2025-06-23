import pandas as pd
import random
import uuid
from faker import Faker

fake = Faker()

# Sample merchant pool
MERCHANT_POOL = [
    {"name": "Walmart", "category": "Department Store", "website": "https://www.walmart.com", "domain": "walmart.com"},
    {"name": "Amazon", "category": "Online Retail", "website": "https://www.amazon.com", "domain": "amazon.com"},
    {"name": "Starbucks", "category": "Coffee Shops", "website": "https://www.starbucks.com", "domain": "starbucks.com"},
    {"name": "Loblaws", "category": "Grocery Store", "website": "https://www.loblaws.ca", "domain": "loblaws.ca"},
    {"name": "Netflix", "category": "Streaming Services", "website": "https://www.netflix.com", "domain": "netflix.com"},
    {"name": "Tim Hortons", "category": "Coffee Shops", "website": "https://www.timhortons.ca", "domain": "timhortons.ca"},
    {"name": "Best Buy", "category": "Electronics", "website": "https://www.bestbuy.ca", "domain": "bestbuy.ca"},
    {"name": "Apple", "category": "Technology", "website": "https://www.apple.com", "domain": "apple.com"},
    {"name": "Indigo", "category": "Bookstore", "website": "https://www.chapters.indigo.ca", "domain": "indigo.ca"},
    {"name": "Uber", "category": "Transportation", "website": "https://www.uber.com", "domain": "uber.com"}
]

def enrich_merchants(df):
    enriched_data = []
    for _, row in df.iterrows():
        merchant = random.choice(MERCHANT_POOL)
        enriched_data.append({
            "transaction_id": row.get("transaction_id", str(uuid.uuid4())),
            "transaction_date": row.get("timestamp"),
            "merchant_name": merchant["name"],
            "merchant_category": merchant["category"],
            "merchant_location": fake.street_address() + ", " + fake.city() + ", " + fake.state_abbr() + ", Canada",
            "merchant_country": "CA",
            "amount": row.get("amount", round(random.uniform(5.0, 500.0), 2)),
            "merchant_logo_url": f"https://logo.clearbit.com/{merchant['domain']}",
            "merchant_website": merchant["website"],
            "is_recurring": random.choice([True, False]),
            "risk_score": round(random.uniform(0.0, 1.0), 2),
            "is_high_value": row.get("amount", 0) > 250
        })
    return pd.DataFrame(enriched_data)
