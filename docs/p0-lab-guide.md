# P0 lab guide — engine, data, holdout, ledger

> **Status:** `reference` — how to run a backtest in this lab and what the
> engine actually simulates. The binding methodology is
> [docs/founding-plan.md](founding-plan.md); this guide documents the P0
> implementation of it.

## Execution model (engine)

`trading_lab.engine.run_backtest(ohlcv, positions, ...)`:

- **t+1 open execution.** A position decided on bar *t* (signals may use
  data through bar *t*'s close) is filled at bar *t+1*'s **open**. Internally
  `held = positions.shift(1)`; the no-lookahead proof lives in
  `tests/test_engine.py::TestNoLookahead`.
- **Open-to-open accounting.** The return attributed to bar *t* is
  `open[t+1]/open[t] - 1` (final bar closes out at its close), so equity at
  index *t* is marked as of bar *t+1*'s open.
- **Costs are on by default**: `slippage_bps=5` + `commission_bps=1` per
  side of traded notional (defaults in `trading_lab/config.py`). A zero-cost
  run must be requested explicitly (`slippage_bps=0, commission_bps=0`).
- Positions may be 0/1 (long/flat), -1/0/1, or fractional weights in [-1, 1].

## Locked holdout policy

`HOLDOUT_START = "2025-01-09"` in `trading_lab/config.py` — the most recent
18 months as of the lab's founding. `data.load_ohlcv` **silently excludes
every bar `>= HOLDOUT_START`** by default. The `unlock_holdout=True` escape
hatch emits a `HoldoutViolationWarning` plus a log warning and exists ONLY
for the P5 final review. The raw cache files under `data/` do contain
holdout bars (fetch is raw; enforcement happens at load time) — no analysis
code may read them directly; always go through `load_ohlcv`.

## Running a backtest

```python
from trading_lab.data import load_ohlcv
from trading_lab.engine import run_backtest, buy_and_hold_result
from trading_lab.strategies import STRATEGIES
from trading_lab import metrics, ledger

ohlcv = load_ohlcv("AAPL", "daily")            # holdout excluded
strategy = STRATEGIES["sma_crossover"]
pos = strategy(ohlcv, fast=20, slow=50)
result = run_backtest(ohlcv, pos, timeframe="daily")
print(metrics.compute_all(result))

# or: backtest + benchmark + ledger entry in one call
ledger.run_and_record(strategy="sma_crossover", instrument="AAPL",
                      timeframe="daily", ohlcv=ohlcv,
                      params={"fast": 20, "slow": 50}, variants_tried=1)
```

Walk-forward validation (the only way findings are reported — see
founding plan): `trading_lab.walkforward.walk_forward(...)` fits a
parameter grid on each rolling train window and scores on the following
unseen test window.

## Ledger

One JSON file per run under `experiments/runs/<utc-timestamp>-<confighash>.json`
— parallel sessions never conflict. Each record carries config hash, strategy
family, params, instrument, timeframe, data range, all metrics, benchmark
buy-and-hold metrics for the same period, `variants_tried`
(multiple-testing discipline), and the git sha. The index
(`experiments/index.jsonl`) is **regenerated** from the run files with
`python3 -m trading_lab.ledger` — never hand-edited, never appended.

## Data layer

- Cache: `data/{timeframe}/{ticker}.csv.gz`; refresh with
  `python3 scripts/fetch_data.py [daily|hourly]`. Fetch order: yfinance
  (`auto_adjust=True`) → Yahoo v8 chart API via plain `requests` (same
  adjustment) → stooq (daily only, unadjusted, flagged in logs).
- Daily timestamps are exchange-local dates (tz-naive); hourly timestamps
  are UTC (tz-naive).
- Universe (in `config.py`): AAPL MSFT NVDA GOOGL AMZN META + GLD SLV.
  Metals via ETFs, not GC=F/SI=F futures: cleaner free hourly data, no
  contract rolls.
- Annualization: daily = 252 periods/year, hourly = 252 × 6.5 = 1638.

## Live-data quirks found (2026-07-09 fetch)

- **Partial last bar**: fetching mid-session leaves an in-progress bar at
  the end of the cache (e.g. daily 2026-07-09 with ~10% of typical volume).
  It sits inside the holdout so no analysis reads it; refresh the cache
  before P5.
- **META history starts 2012-05-18** (IPO) — 3554 daily bars vs 4153 for
  the rest of the universe since 2010-01-01.
- **Hourly depth exceeds the documented 730 days**: Yahoo returned ~2.9
  years of 1h bars (back to 2023-08). Sessions are 7 bars/day (13:30–20:30
  UTC, last bar a half hour); 4 half-days have only 3 bars; GLD/SLV are
  missing 1–2 scattered hourly bars vs the tech names.
- **Yahoo hourly can contain all-NaN rows** — dropped at normalize time in
  `trading_lab/data.py`.
- **Egress-proxy TLS note**: yfinance's default curl_cffi browser
  impersonation is reset by corporate TLS-reterminating proxies; `data.py`
  passes a plain curl_cffi session (with `REQUESTS_CA_BUNDLE`) instead.
