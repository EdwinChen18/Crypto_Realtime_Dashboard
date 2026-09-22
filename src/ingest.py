"""Fetch current market data for tracked coins from CoinGecko and store it in Supabase."""
import sys
import requests
from src.config import COINGECKO_API_URL, COINS, PRICE_CHANGE_PERCENTAGES, VS_CURRENCY
from src.db import insert_price_rows
from dotenv import load_dotenv
load_dotenv()

def fetch_market_data():
    params = {
        "vs_currency": VS_CURRENCY,
        "ids": ",".join(COINS),
        "price_change_percentage": PRICE_CHANGE_PERCENTAGES,
    }
    response = requests.get(COINGECKO_API_URL, params=params, timeout=15)
    response.raise_for_status()
    return response.json()


def parse_rows(raw_data):
    rows = []
    for coin in raw_data:
        rows.append({
            "coin_id": coin.get("id"),
            "symbol": coin.get("symbol"),
            "current_price_usd": coin.get("current_price"),
            "market_cap": coin.get("market_cap"),
            "market_cap_rank": coin.get("market_cap_rank"),
            "total_volume_24h": coin.get("total_volume"),
            "high_24h": coin.get("high_24h"),
            "low_24h": coin.get("low_24h"),
            "price_change_pct_1h": coin.get("price_change_percentage_1h_in_currency"),
            "price_change_pct_24h": coin.get("price_change_percentage_24h_in_currency"),
            "price_change_pct_7d": coin.get("price_change_percentage_7d_in_currency"),
            "circulating_supply": coin.get("circulating_supply"),
            "ath_usd": coin.get("ath"),
            "ath_change_pct": coin.get("ath_change_percentage"),
        })
    return rows

def main():
    raw_data = fetch_market_data()
    rows = parse_rows(raw_data)
    insert_price_rows(rows)
    print(f"Inserted {len(rows)} rows for coins: {', '.join(COINS)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Ingest failed: {exc}", file=sys.stderr)
        sys.exit(1)


