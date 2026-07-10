# Lane claim: p4-transfer__multi__daily-hourly

- session: p4-transfer lane (session/2026-07-10-p4-transfer)
- started-at: 2026-07-10T04:29:59Z
- scope: P4 cross-instrument transfer validation of the 13 P2 subjects
  (12 UNVALIDATABLE-PRE-HOLDOUT + the promoted AAPL-donchian). Params
  frozen verbatim from the P1 sweep JSONs (`top_full_period_variant`);
  zero re-tuning, zero new variants (`variants_tried = 1` per run).
  - Daily subjects (8): donchian×AAPL, sma_crossover×META,
    ema_crossover×META, donchian×META, supertrend_flip×BTC-USD,
    macd_supertrend×BTC-USD, rsi_mean_reversion×META, pullback×META —
    each run on the other 8 of
    {AAPL,MSFT,NVDA,GOOGL,AMZN,META,GLD,SLV,BTC-USD}.
  - Hourly subjects (5): sma_crossover×GOOGL, ema_crossover×GOOGL,
    donchian×GOOGL, donchian×AMZN, macd×META — each run on the other 7
    UNIVERSE tickers (no BTC-USD hourly cache exists).
  - Full pre-holdout window per instrument via `load_ohlcv`; engine
    defaults (5+1 bps/side, t+1-open fills) vs buy-and-hold.
