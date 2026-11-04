# Analysis behind the README Key Findings (daily frequency). Read-only.
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

LABELS = {
    "bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL",
    "binancecoin": "BNB", "ripple": "XRP", "cardano": "ADA",
}

with psycopg2.connect(os.environ["SUPABASE_DB_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "select coin_id, current_price_usd, fetched_at "
            "from crypto_prices order by fetched_at"
        )
        rows = cur.fetchall()

df = pd.DataFrame(rows, columns=["coin_id", "price", "fetched_at"])
df["price"] = df["price"].astype(float)
df["fetched_at"] = pd.to_datetime(df["fetched_at"], utc=True)
df["coin"] = df["coin_id"].map(LABELS)

# Common window: from the first moment all six coins have data
start = df.groupby("coin")["fetched_at"].min().max()
wide = df[df["fetched_at"] >= start].pivot_table(
    index="fetched_at", columns="coin", values="price"
)
days = (wide.index.max() - wide.index.min()).days
print(f"\nWindow: {wide.index.min()} to {wide.index.max()}")
print(f"Snapshots: {len(wide)} (about {len(wide) / max(days, 1):.1f} per day)")

# Daily close = last snapshot of each UTC day
daily = wide.resample("1D").last()
ret = daily / daily.shift(1) - 1
print(f"Daily return observations per coin (min): {int(ret.notna().sum().min())}")

print("\n=== VOLATILITY (std of daily returns, %) ===")
print((ret.std() * 100).sort_values(ascending=False).round(2))

print("\n=== CORRELATION (daily returns) ===")
corr = ret.corr()
print(corr.round(2))
pairs = corr.stack()
pairs = pairs[pairs.index.get_level_values(0) < pairs.index.get_level_values(1)]
print("Highest pair:", pairs.idxmax(), round(pairs.max(), 2))
print("Lowest pair: ", pairs.idxmin(), round(pairs.min(), 2))

print("\n=== PERFORMANCE (sampled snapshots) ===")
perf = pd.DataFrame({
    "total_change_%": ((wide.iloc[-1] / wide.iloc[0] - 1) * 100).round(1),
    "max_drawdown_%": ((wide / wide.cummax() - 1).min() * 100).round(1),
})
print(perf.sort_values("total_change_%", ascending=False))