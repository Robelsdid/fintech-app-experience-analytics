import pandas as pd
import oracledb
import os

# --- Database Credentials (Replace with your actual credentials) ---
# It's recommended to use environment variables for sensitive data
DB_USER = os.environ.get("ORACLE_USER", "SYSTEM")
DB_PASSWORD = os.environ.get("ORACLE_PASSWORD", "Oracle123!")
# For Oracle XE, the connect string is often 'localhost:1521/XEPDB1'
DB_DSN = os.environ.get("ORACLE_DSN", "localhost:1521/XEPDB1")

# --- Data and Configuration ---
CSV_PATH = 'data/processed/reviews_with_themes.csv'
# This should match the app names and packages from my scraper
BANK_MAPPING = {
    "cbe": {"name": "Commercial Bank of Ethiopia", "package": "com.combanketh"},
    "boa": {"name": "Bank of Abyssinia", "package": "com.bankofabyssinia.boaapp"},
    "dashen": {"name": "Dashen Bank", "package": "com.tekln.dashentab"}
}

def load_data_to_oracle():
    """Connects to Oracle, populates banks, and inserts review data."""
    try:
        with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
            with connection.cursor() as cursor:
                print("Successfully connected to Oracle Database")

                # 1. Populate the 'banks' table
                print("Populating 'banks' table...")
                bank_ids = {}
                for key, info in BANK_MAPPING.items():
                    # Use MERGE to insert if not exists, avoiding duplicates
                    merge_sql = """
                        MERGE INTO banks b
                        USING (SELECT :name AS bank_name, :pkg AS app_package_id FROM dual) s
                        ON (b.bank_name = s.bank_name)
                        WHEN NOT MATCHED THEN
                            INSERT (bank_name, app_package_id) VALUES (s.bank_name, s.app_package_id)
                    """
                    cursor.execute(merge_sql, name=info['name'], pkg=info['package'])
                    
                    # Fetch the bank_id
                    cursor.execute("SELECT bank_id FROM banks WHERE bank_name = :name", name=info['name'])
                    bank_ids[key] = cursor.fetchone()[0]
                
                print(f"Bank IDs fetched: {bank_ids}")
                connection.commit()

                # 2. Prepare and insert data into the 'reviews' table
                print("Loading review data from CSV...")
                df = pd.read_csv(CSV_PATH)
                df['review_date'] = pd.to_datetime(df['date']).dt.date
                # Map bank names (cbe, boa, dashen) to their new integer IDs
                df['bank_id'] = df['bank'].map(bank_ids)
                
                # Generate unique review IDs
                df['review_id'] = range(1, len(df) + 1)

                # --- FIX: Convert pandas NaN to None for Oracle ---
                # Oracle driver cannot handle pandas.NA or numpy.nan for number columns.
                numeric_cols = ['bank_id', 'rating', 'sentiment_score']
                for col in numeric_cols:
                    # Using .astype(object) allows for `None` to be placed in the series.
                    df[col] = df[col].astype(object).where(df[col].notna(), None)

                # Prepare data for insertion
                # Ensure columns match the 'reviews' table structure
                reviews_to_insert = df[[
                    'review_id', 'bank_id', 'review', 'rating', 'review_date', 
                    'sentiment_label', 'sentiment_score', 'identified_theme(s)', 'source'
                ]].copy()
                # Rename columns to match table definition
                reviews_to_insert.rename(columns={'review': 'review_text'}, inplace=True)
                
                # Convert DataFrame to list of tuples for executemany
                data_tuples = [tuple(x) for x in reviews_to_insert.to_numpy()]

                print(f"Inserting {len(data_tuples)} reviews into 'reviews' table...")
                cursor.executemany("""
                    INSERT INTO reviews (review_id, bank_id, review_text, rating, review_date, 
                                         sentiment_label, sentiment_score, identified_themes, source)
                    VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
                """, data_tuples)
                
                connection.commit()
                print(f"Successfully inserted {cursor.rowcount} reviews.")

    except oracledb.Error as e:
        print(f"Oracle Database error: {e}")
    except FileNotFoundError:
        print(f"Error: The file '{CSV_PATH}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    load_data_to_oracle() 