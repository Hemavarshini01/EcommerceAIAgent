import pandas as pd
import sqlite3
import os

# Define file paths
DATA_DIR = "data"
AD_SALES_FILE = os.path.join(DATA_DIR, "ad_sales_metrics.csv")
TOTAL_SALES_FILE = os.path.join(DATA_DIR, "total_sales_metrics.csv")
ELIGIBILITY_FILE = os.path.join(DATA_DIR, "eligibility.csv")

# Load the CSV files
ad_sales_df = pd.read_csv(AD_SALES_FILE)
total_sales_df = pd.read_csv(TOTAL_SALES_FILE)
eligibility_df = pd.read_csv(ELIGIBILITY_FILE)

# DATE PARSING: Standardize date columns if needed
ad_sales_df['date'] = pd.to_datetime(ad_sales_df['date'])
total_sales_df['date'] = pd.to_datetime(total_sales_df['date'])
eligibility_df['eligibility_datetime_utc'] = pd.to_datetime(eligibility_df['eligibility_datetime_utc'])

# Merge datasets
# 1. Merge ad_sales_df + total_sales_df on ['date', 'item_id']
merged_df = pd.merge(
    ad_sales_df, total_sales_df, 
    on=['date', 'item_id'], how='outer'
)

# 2. Merge merged_df + eligibility_df on 'item_id'
final_df = pd.merge(
    merged_df, eligibility_df, 
    left_on='item_id',
    right_on='item_id',
    how='left'
)

# OPTIONAL: Rearrange or clean columns if needed

# Create/Connect to SQLite database
DB_FILE = os.path.join(DATA_DIR, "all_metrics.db")
conn = sqlite3.connect(DB_FILE)

# Write the final dataframe to SQL
final_df.to_sql('all_metrics', conn, if_exists='replace', index=False)

print(f"Data merged and stored as {DB_FILE} in 'all_metrics' table.")

# Close connection
conn.close()
