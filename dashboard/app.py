#Streamlit dashboard for the crypto real-time pipeline.

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import psycopg2
import streamlit as st
from plotly.subplots import make_subplots
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import COIN_LABELS

load_dotenv()

st.set_page_config(page_title="Crypto Real-Time Dashboard", layout="wide")

st.cache_data(ttl=300)
def load_data(hours: int = 48) -> pd.DataFrame:
    db_url = os.environ.get("SUPABASE_DB_URL")
    if not db_url:
        st.error("SUPABASE_DB_URL is not set. Check .env file")
        st.stop()

    since = datetime.utcnow() - timedelta(hours=hours)
    query = """
            select coin_id, symbol, current_price_usd, market_cap, market_cap_rank,
               total_volume_24h, high_24h, low_24h, price_change_pct_1h,
               price_change_pct_24h, price_change_pct_7d, circulating_supply,
               ath_usd, ath_change_pct, fetched_at
        from crypto_prices
        where fetched_at >= %s
        order by fetched_at asc
    """
    with psycopg2.connect(db_url) as conn:
        df = pd.read_sql(query, conn, params=(since,))
    return df

df = load_data()

if df.empty:
    st.warning("No data yet. Wait for the GitHub Actions workflow to run a few times.")
    st.stop()

st.title("Crypto Real-Time Dashboard")
st.caption("Live pipeline: CoinGecko API → GitHub Actions → Supabase → Streamlit")

latest = df.sort_values("fetched_at").groupby("coin_id").tail(1)

# --- KPI cards ---
cols = st.columns(len(COIN_LABELS))
for col, (coin_id, label) in zip(cols, COIN_LABELS.items()):
    row = latest[latest["coin_id"] ==  coin_id]
    if row.empty:
        continue
    row = row.iloc[0]
    col.metric(
        label= label,
        value= f"${row['current_price_usd']:,.2f} ",
        delta= f"${row['price_change_pct_24h']:,.2f}% (24h)",
    )

st.divider()

selected_coins = st.multiselect(
    "Coins to show", options=list(COIN_LABELS.keys()),
    default=list(COIN_LABELS.keys()), format_func=lambda c: COIN_LABELS[c],
)

# --- Indexed trend chart ---
st.subheader("Price Trend (Indexed to 100 at Start)")

fig1 = go.Figure()
for coin_id in selected_coins:
    coin_df = df[df["coin_id"] == coin_id].sort_values("fetched_at")
    if coin_df.empty:
        continue
    base_price = coin_df["current_price_usd"].iloc[0]
    indexed = coin_df["current_price_usd"] / base_price * 100
    fig1.add_trace(go.Scatter(
        x = coin_df["fetched_at"], y = indexed,
        mode = "lines", name=COIN_LABELS[coin_id],
        hovertemplate ="%{y:.2f}<extra></extra>",
    ))

fig1.update_layout(
    template = "plotly_dark", hovermode ="x unified",
    yaxis_title = "Indexed price (start = 100)", xaxis_title = "",
    legend=dict(orientation="h", y=-0.25),
    margin=dict(t=20),
)

st.plotly_chart(fig1, use_container_width=True)

# --- Raw price, small multiples (one panel per coin) ---
st.subheader("Raw Price per Coin")

n = max(len(selected_coins), 1)
fig2 = make_subplots(rows=1, cols=n, subplot_titles=[COIN_LABELS[c] for c in selected_coins])
for i, coin_id in enumerate(selected_coins, start=1):
    coin_df = df[df["coin_id"] == coin_id].sort_values("fetched_at")
    fig2.add_trace(
        go.Scatter(x=coin_df["fetched_at"], y=coin_df["current_price_usd"],
                   mode="lines", showlegend=False),
                   row= 1, col= i,
    )
fig2.update_layout(template="plotly_dark", height=320, margin= dict(t=40))
st.plotly_chart(fig2,use_container_width=True)

st.divider()

# --- ATH distance + Volume, side by side ---
c1, c2 = st.columns(2)
with c1:
    st.subheader("Distance from All-Time High")
    ath_df = latest[latest["coin_id"].isin(selected_coins)].sort_values("ath_change_pct")
    fig3 = go.Figure(go.Bar(
        x=ath_df["ath_change_pct"],
        y=[COIN_LABELS[c] for c in ath_df["coin_id"]],
        orientation="h",
        marker=dict(color=ath_df["ath_change_pct"], colorscale="RdYlGn"),
    ))
    fig3.update_layout(template="plotly_dark", xaxis_title="% from ATH", margin=dict(t=10))
    st.plotly_chart(fig3, use_container_width=True)

with c2:
    st.subheader("24h Trading Volume (log scale)")
    vol_df = latest[latest["coin_id"].isin(selected_coins)].sort_values("total_volume_24h", ascending=False)
    fig4 = go.Figure(go.Bar(
        x=[COIN_LABELS[c] for c in vol_df["coin_id"]],
        y=vol_df["total_volume_24h"],
    ))
    fig4.update_layout(template="plotly_dark", yaxis_type="log", yaxis_title="Volume (USD)", margin=dict(t=10))
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
st.subheader("Latest Snapshot")

display_cols = [
    "coin_id", "current_price_usd", "market_cap_rank", "total_volume_24h",
    "price_change_pct_1h", "price_change_pct_24h", "price_change_pct_7d",
    "ath_usd", "ath_change_pct", "fetched_at",
]

st.dataframe(
    latest[display_cols].sort_values("market_cap_rank"),
    use_container_width=True,
    hide_index=True,
)

