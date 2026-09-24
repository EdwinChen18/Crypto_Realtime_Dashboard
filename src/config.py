#Configuration for the crypto real-time project.

# CoinGecko coin IDs -> display label
COIN_LABELS = {
    "bitcoin": "Bitcoin (BTC)",
    "ethereum": "Ethereum (ETH)",
    "solana": "Solana (SOL)",
    "binancecoin": "BNB (BNB)",
    "ripple": "XRP (XRP)",
    "cardano": "Cardano (ADA)",
}
COINS = list(COIN_LABELS.keys())

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/coins/markets"
VS_CURRENCY = "usd"
PRICE_CHANGE_PERCENTAGES = "1h,24h,7d"
TABLE_NAME = "crypto_prices"