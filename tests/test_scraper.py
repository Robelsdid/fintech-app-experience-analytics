import os
import json

RAW_DIR = "data/raw"
BANKS = ["cbe", "boa", "dashen"]

def test_files_exist():
    for bank in BANKS:
        path = os.path.join(RAW_DIR, f"{bank}_reviews.json")
        assert os.path.exists(path), f"{path} does not exist"

def test_json_is_valid():
    for bank in BANKS:
        path = os.path.join(RAW_DIR, f"{bank}_reviews.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        assert isinstance(data, list), "Expected a list of reviews"
        assert len(data) > 100, "Too few reviews scraped"

def test_review_fields_exist():
    required_fields = {"content", "score", "at"}
    for bank in BANKS:
        path = os.path.join(RAW_DIR, f"{bank}_reviews.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for review in data:
            for field in required_fields:
                assert field in review, f"Missing '{field}' in review"
