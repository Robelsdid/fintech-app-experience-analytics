import os
import json
import pandas as pd
from datetime import datetime

# Paths
RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
OUTPUT_CSV = os.path.join(PROCESSED_DIR, "cleaned_reviews.csv")

# Map file name → bank name
BANK_MAP = {
    "cbe_reviews.json": "CBE",
    "boa_reviews.json": "BOA",
    "dashen_reviews.json": "Dashen"
}

def clean_review_data():
    all_reviews = []

    for filename in os.listdir(RAW_DIR):
        if filename.endswith(".json") and filename in BANK_MAP:
            filepath = os.path.join(RAW_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                reviews_json = json.load(f)

            for entry in reviews_json:
                review_text = entry.get("content", "").strip()
                rating = entry.get("score", None)
                date_raw = entry.get("at", None)

                # Convert datetime to YYYY-MM-DD
                if date_raw:
                    date_clean = pd.to_datetime(date_raw).strftime("%Y-%m-%d")
                else:
                    date_clean = None

                all_reviews.append({
                    "review": review_text,
                    "rating": rating,
                    "date": date_clean,
                    "bank": BANK_MAP[filename],
                    "source": "Google Play"
                })

    # Create DataFrame
    df = pd.DataFrame(all_reviews)

    # Drop rows with missing reviews or ratings
    df.dropna(subset=["review", "rating", "date"], inplace=True)

    # Save as CSV
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f" Cleaned data saved to: {OUTPUT_CSV}")
    print(f" Total cleaned reviews: {len(df)}")

if __name__ == "__main__":
    clean_review_data()
