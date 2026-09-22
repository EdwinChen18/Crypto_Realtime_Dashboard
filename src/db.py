"""Database connection and insert helpers for Supabase (Postgres)."""
import os
import psycopg2
from psycopg2.extras import execute_values
from src.config import TABLE_NAME

COLUMNS = [
    "coin_id", "symbol", "current_price_usd", "market_cap",
    "market_cap_rank", "total_volume_24h", "high_24h", "low_24h",
    "price_change_pct_1h", "price_change_pct_24h", "price_change_pct_7d",
    "circulating_supply", "ath_usd", "ath_change_pct",
]

def get_connection():
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        raise RuntimeError("SUPABASE_DB_URL is not set.")
    return psycopg2.connect(db_url)

def insert_price_rows(rows):
    if not rows:
        return
    values = [[row.get(col) for col in COLUMNS] for row in rows]
    query = f"INSERT INTO {TABLE_NAME} ({', '.join(COLUMNS)}) VALUES %s"
    with get_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, query, values)
        conn.commit()

        

