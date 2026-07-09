# trading-lab · status
updated: 2026-07-09T17:27:00Z
phase: P1 trend-following lane complete (trend-following × all8 × daily, PR #6 merged) — 7 of 32 family×ticker lanes beat buy-and-hold on walk-forward OOS Sharpe after costs; negative result is the headline, candidates (AAPL donchian, META sma/ema/donchian) carried to P2
health: green
last-shipped: #6 — P1 trend-following sweep: SMA/EMA/MACD/Donchian × 8 tickers × daily (177 variants, walk-forward, realistic costs) + claims/ lane protocol + docs/p1-trend-following-results.md
blockers: none
orders: acked=001,002,003 done=001,002,003
⚑ needs-owner: (1) verify the env setup script is actually fixed — the successor session died at 14:05Z provision on the identical error AFTER the fix was reported; exact steps + paste-ready script in docs/retro/project-review-2026-07-09.md §(e); (2) one-time: tick "Allow auto-merge" in repo Settings→General→Pull Requests; (3) optional: archive the dead "ORDER 001 successor" session (listed active, is DOA).
notes: variants-tried this lane = 177 configurations (44 SMA + 44 EMA + 48 MACD + 41 donchian) × 8 tickers = 1,416 recorded full-period backtests plus walk-forward re-selection (per-variant rows in experiments/sweeps/p1-trend-following-daily/ for P2 deflated-Sharpe). Lane claim deleted (lane complete). Suggested next lanes (unclaimed, check claims/ first): mean-reversion × all8 × daily (RSI grid + Bollinger/z-score), then trend-following × all8 × hourly — mind turnover: MACD churn lost to costs on 5/8 tickers at 6 bps/side.
