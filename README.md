# Crypto Real-Time Dashboard

![Fetch crypto prices](https://github.com/EdwinChen18/Crypto_Realtime_Dashboard/actions/workflows/fetch_data.yml/badge.svg)

End-to-end data pipeline: a Python script pulls live market data for six major
cryptocurrencies from the CoinGecko API, stores a snapshot in a Supabase
(PostgreSQL) database every 30 minutes through GitHub Actions, and a Streamlit
dashboard visualizes price trends, correlations, and volatility over time.

**Live demo:** [add your Streamlit link here]

![Dashboard](docs/dashboard.png)

## Architecture

```
CoinGecko API → src/ingest.py → Supabase (PostgreSQL) → dashboard/app.py (Streamlit)
                      ↑
         GitHub Actions cron (every 30 min)
```

## Tracked Coins

Bitcoin (BTC), Ethereum (ETH), Solana (SOL), BNB (BNB), XRP (XRP), Cardano (ADA)

## Metrics Collected

- Current price (USD), market cap, market cap rank
- 24h trading volume, 24h high and low
- Price change % over 1h, 24h, and 7d
- Circulating supply
- All-time high (ATH) and % distance from ATH

## Dashboard Features

- KPI cards with current price and 24h change per coin
- Indexed price trend (start = 100) to compare coins fairly regardless of price scale
- Raw price per coin in separate panels
- Distance from all-time high (horizontal bar chart)
- 24h trading volume on a log scale with readable tick labels (10M to 100B)
- Price correlation matrix (heatmap of returns)
- Rolling volatility (standard deviation of returns, adjustable window)
- Latest snapshot table with all metrics
- Dark theme configured through `.streamlit/config.toml`

## Tech Stack

| Layer | Tools |
|---|---|
| Ingestion | Python 3.11, requests 2.34.2 |
| Database | Supabase (PostgreSQL), psycopg2-binary 2.9.13 |
| Automation | GitHub Actions (cron) |
| Dashboard | Streamlit 1.64.0, Plotly, pandas |
| Configuration | python-dotenv 1.2.3 |

All dependency versions are pinned in `requirements.txt`.

## Project Structure

```
Crypto_Realtime_Dashboard/
├── .github/workflows/fetch_data.yml   # Scheduled ingestion
├── .streamlit/config.toml             # Dashboard theme
├── dashboard/app.py                   # Streamlit app
├── docs/dashboard.png                 # Screenshot
├── sql/schema.sql                     # Table definition
├── src/
│   ├── config.py                      # Coins, API URL, table name
│   ├── db.py                          # Database connection and inserts
│   └── ingest.py                      # CoinGecko fetch and parse
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Design Decisions

- **Indexed prices:** Bitcoin trades at a much higher price than the other coins and
  flattens them on a shared axis. Indexing every coin to 100 at the start of the
  window shows relative performance instead.
- **Log scale for volume:** trading volumes differ by orders of magnitude, so a log
  axis with custom tick labels keeps small coins visible.
- **Connection pooler (port 6543):** suited to short-lived connections like the ones
  GitHub Actions creates on every run.
- **Least privilege:** ingestion uses a role that can write, while the public
  dashboard connects with a read-only role limited to `SELECT` on `crypto_prices`.
- **Cached queries:** the dashboard caches database reads for 5 minutes to limit load.
- **No extra tables for analytics:** correlation and volatility are computed from the
  stored price snapshots using percentage returns.

## Local Setup

1. Clone the repo and install dependencies:
   ```powershell
   git clone https://github.com/EdwinChen18/Crypto_Realtime_Dashboard.git
   cd Crypto_Realtime_Dashboard
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
   On macOS or Linux, activate with `source .venv/bin/activate`.
2. Create a free Demo API key at [coingecko.com/en/api](https://www.coingecko.com/en/api).
3. Create a Supabase project and run `sql/schema.sql` in the SQL Editor.
   Copy the Transaction pooler connection string (port 6543).
4. Copy `.env.example` to `.env` and fill in both variables:
   - `SUPABASE_DB_URL`
   - `COINGECKO_API_KEY`
5. Test the ingestion script:
   ```powershell
   python -m src.ingest
   ```
   Expected output: `Inserted 6 rows for coins: bitcoin, ethereum, solana, binancecoin, ripple, cardano`
6. Run the dashboard:
   ```powershell
   streamlit run dashboard/app.py
   ```

## Automation

`.github/workflows/fetch_data.yml` runs `src/ingest.py` every 30 minutes with
GitHub Actions. Add these repository secrets under
Settings > Secrets and variables > Actions:

- `SUPABASE_DB_URL`
- `COINGECKO_API_KEY`

To trigger a run manually and check its status:

```powershell
gh workflow run fetch_data.yml
gh run list --workflow=fetch_data.yml --limit 5
```

## Deployment

The dashboard is deployed on Streamlit Community Cloud with `dashboard/app.py` as the
main file. The only secret it needs is `SUPABASE_DB_URL`, using the read-only database
role. It does not need the CoinGecko key because it only reads from Supabase.

## Engineering Notes

- **API access changes:** CoinGecko started returning `403 Forbidden` for
  unauthenticated requests to the markets endpoint, which broke the scheduled runs.
  Fixed by sending a free Demo API key in the `x-cg-demo-api-key` header, stored as
  a GitHub secret.
- **Silent failures:** a misspelled coin ID is ignored by the API without an error and
  simply returns fewer rows. The ingestion script logs the number of inserted rows to
  make this visible.
- **Outage gap:** runs that failed during the API change left a gap in the stored
  history. Charts show the gap instead of interpolating over it.

## Limitations and Future Work

- Snapshots are taken every 30 minutes, so this is near real-time, not tick-level streaming.
- Add a validation step that fails the run if the returned row count differs from the
  number of tracked coins.
- Price alerts when a coin moves more than a set percentage.
- Forecasting and anomaly detection on the stored history.
- Historical backfill using CoinGecko's market chart endpoint.

## Status

- [x] Ingestion script and Supabase schema
- [x] GitHub Actions automation (every 30 minutes)
- [x] Streamlit dashboard with trend, ATH, volume, correlation, and volatility views
- [ ] Deployed publicly on Streamlit Community Cloud

## Author

Edwin Chen Liu | [LinkedIn](https://linkedin.com/in/edwin-chen18) | [GitHub](https://github.com/EdwinChen18)