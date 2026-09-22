CREATE TABLE IF NOT EXISTS crypto_prices (
  id                    bigserial primary key,
  coin_id               text not null,
  symbol                text not null,
  current_price_usd      numeric not null,
  market_cap            numeric,
  market_cap_rank        integer,
  total_volume_24h       numeric,
  high_24h               numeric,
  low_24h                numeric,
  price_change_pct_1h    numeric,
  price_change_pct_24h   numeric,
  price_change_pct_7d    numeric,
  circulating_supply     numeric,
  ath_usd                numeric,
  ath_change_pct         numeric,
  fetched_at             timestamptz not null default now()
);

CREATE INDEX IF NOT EXISTS idx_crypto_prices_coin_fetched
  on crypto_prices (coin_id, fetched_at desc);