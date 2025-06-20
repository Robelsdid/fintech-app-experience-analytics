import os
import pandas as pd

PROCESSED_DIR = "data/processed"
OUTPUT_FILE = "cleaned_reviews.csv"

def test_cleaned_file_exists():
    path = os.path.join(PROCESSED_DIR, OUTPUT_FILE)
    assert os.path.exists(path), f"{path} does not exist"

def test_cleaned_file_not_empty():
    path = os.path.join(PROCESSED_DIR, OUTPUT_FILE)
    df = pd.read_csv(path)
    assert len(df) > 100, "Cleaned data has too few rows"

def test_required_columns():
    path = os.path.join(PROCESSED_DIR, OUTPUT_FILE)
    df = pd.read_csv(path)
    expected_cols = {"review", "rating", "date", "bank", "source"}
    assert expected_cols.issubset(set(df.columns)), "Missing required columns"

def test_no_empty_reviews():
    path = os.path.join(PROCESSED_DIR, OUTPUT_FILE)
    df = pd.read_csv(path)
    assert not df["review"].isnull().any(), "Some reviews are null"
    assert (df["review"].str.strip() != "").all(), "Some reviews are empty strings"

def test_date_format():
    path = os.path.join(PROCESSED_DIR, OUTPUT_FILE)
    df = pd.read_csv(path)
    # Quick check: date strings are 10 chars long (YYYY-MM-DD)
    assert df["date"].str.len().eq(10).all(), "Date format is incorrect"
