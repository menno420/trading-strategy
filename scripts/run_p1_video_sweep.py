#!/usr/bin/env python3
"""P1 video-strategy sweep — competing interpretations × BTC-USD × daily.

Lane: video-strategy__btcusd__multi (QUEUE item 1). Three faithful
interpretations of the DaviddTech video's under-specified rules
(docs/research/video-source-2026-07-09.md) run as competing systems vs each
other and vs buy-and-hold, all long/flat, engine cost defaults on:

* ``supertrend_flip`` — SuperTrend-flip entry, EMA + MACD as filters;
* ``macd_supertrend`` — MACD-cross entry, SuperTrend + EMA as filters;
* ``ema_crossover`` — dual-EMA control on the video's stated sweep region
  (slow 110→400 coarsened, fast 10→100 coarsened, incl. the stated winner
  slow=400 / fast=45).

Decide-and-flag (data):

* Instrument: the video trades BTCUSDT (Bybit); this lane maps it to
  Yahoo's BTC-USD index (cached via the standard loader). Same underlying,
  different venue/quote conventions.
* Timeframe: the video uses 1h/4h. Yahoo hourly caps at ~730 days, which
  leaves only ~6 months of pre-holdout hourly data — far too thin for the
  lab's train-1008/test-252 walk-forward — so this lane runs DAILY as the
  primary timeframe. Flagged deviation from the source.
* Annualization: metrics use PERIODS_PER_YEAR["daily"] = 252, but BTC
  trades ~365 days/year, so annualized Sharpe/CAGR are UNDERSTATED by a
  constant factor for strategy and benchmark alike — comparisons vs B&H
  over the same window are unaffected. Flagged, not patched (the constant
  is lab-wide).

Structure mirrors scripts/run_p1_trend_sweep.py: per family (1) full-dev
per-variant rows (bookkeeping, NOT findings), (2) walk-forward OOS vs
buy-and-hold over the exact stitched OOS window (the only finding),
(3) one ledger run for the top full-period variant. Plus untuned
default-parameter spot checks of the two new strategies on two universe
tickers (context only).

Usage: python3 scripts/run_p1_video_sweep.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import DEFAULT_PARAMS, STRATEGIES  # noqa: E402
from trading_lab.walkforward import walk_forward  # noqa: E402

TICKER = "BTC-USD"
TIMEFRAME = "daily"
TRAIN_SIZE = 1008
TEST_SIZE = 252

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / "p1-video-strategy-daily"

SPOT_CHECK_TICKERS = ["NVDA", "GLD"]
SPOT_CHECK_FAMILIES = ["supertrend_flip", "macd_supertrend"]

VARIANT_METRIC_KEYS = ("sharpe", "sortino", "cagr", "total_return",
                       "max_drawdown", "win_rate", "turnover_per_year",
                       "n_trades")


def series_metrics(returns, equity) -> dict:
    """Metrics computable from stitched OOS returns/equity alone."""
    out = {
        "sharpe": metrics.sharpe(returns, TIMEFRAME),
        "sortino": metrics.sortino(returns, TIMEFRAME),
        "cagr": metrics.cagr(equity, TIMEFRAME),
        "total_return": metrics.total_return(equity),
        "max_drawdown": metrics.max_drawdown(equity),
        "n_bars": int(len(returns)),
    }
    return {k: (None if isinstance(v, float) and v != v else v)
            for k, v in out.items()}


def main() -> None:
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    grid_sizes = sweeps.video_variants_per_family()
    print(f"grids: {grid_sizes} (total {sweeps.video_total_variants()})")

    ohlcv = load_ohlcv(TICKER, TIMEFRAME)  # holdout excluded by default
    for family in sweeps.VIDEO_STRATEGY_FAMILIES:
        variants = sweeps.video_variants(family)
        strategy_fn = STRATEGIES[family]

        # 1) full-dev-period backtest per variant (bookkeeping rows)
        rows = []
        for params in variants:
            res = run_backtest(ohlcv, strategy_fn(ohlcv, **params),
                               timeframe=TIMEFRAME)
            m = metrics.compute_all(res)
            rows.append({"params": params,
                         "metrics": {k: m[k] for k in VARIANT_METRIC_KEYS}})

        # 2) walk-forward OOS — the only reportable finding
        wf = walk_forward(ohlcv, strategy_fn, variants,
                          train_size=TRAIN_SIZE, test_size=TEST_SIZE,
                          timeframe=TIMEFRAME)
        first, last = wf["splits"][0]["split"], wf["splits"][-1]["split"]
        oos_slice = ohlcv.iloc[first.test_start:last.test_end]
        bench_oos = buy_and_hold_result(oos_slice, timeframe=TIMEFRAME)

        # 3) ledger run for the top full-period variant
        top = max(rows, key=lambda r: (r["metrics"]["sharpe"]
                                       if r["metrics"]["sharpe"] is not None
                                       else float("-inf")))
        run_path = ledger.run_and_record(
            strategy=family, instrument=TICKER, timeframe=TIMEFRAME,
            ohlcv=ohlcv, params=top["params"],
            variants_tried=len(variants),
            notes=(f"P1 video-strategy sweep ({family} interpretation of the "
                   f"DaviddTech video, BTCUSDT mapped to BTC-USD, daily not "
                   f"1h/4h — flagged): top full-dev-period variant of "
                   f"{len(variants)} tried (post-hoc selection — in-sample; "
                   f"the walk-forward OOS finding lives in experiments/sweeps/"
                   f"p1-video-strategy-daily/{family}__{TICKER}.json)"),
        )

        bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME)
        sweep_record = {
            "schema_version": 1,
            "sweep": "p1-video-strategy-daily",
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": family,
            "interpretation": {
                "supertrend_flip": ("(i) SuperTrend-flip entry + EMA trend "
                                    "filter + MACD confirmation, long/flat, "
                                    "exit on SuperTrend flip"),
                "macd_supertrend": ("(ii) MACD-cross entry + SuperTrend/EMA "
                                    "filters, long/flat, exit on MACD cross "
                                    "down"),
                "ema_crossover": ("(iii) dual-EMA crossover control on the "
                                  "video's stated sweep region (winner "
                                  "slow=400/fast=45 included)"),
            }[family],
            "instrument": TICKER,
            "instrument_note": "video instrument BTCUSDT (Bybit) mapped to Yahoo BTC-USD",
            "timeframe": TIMEFRAME,
            "timeframe_note": ("video uses 1h/4h; pre-holdout hourly depth "
                               "(~6 months) is too thin for train-1008/"
                               "test-252 walk-forward — daily flagged as "
                               "deviation"),
            "data_start": str(ohlcv.index[0]),
            "data_end": str(ohlcv.index[-1]),
            "n_bars": int(len(ohlcv)),
            "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                      "commission_bps": config.DEFAULT_COMMISSION_BPS},
            "execution": "signal at bar t fills at bar t+1 open",
            "variants_tried": len(variants),
            "lane_variants_tried": sweeps.video_total_variants(),
            "full_period_variants": {
                "note": ("single-split in-sample rows for deflated-Sharpe "
                         "bookkeeping — NOT findings"),
                "rows": rows,
            },
            "walk_forward": {
                "train_size": TRAIN_SIZE,
                "test_size": TEST_SIZE,
                "n_splits": len(wf["splits"]),
                "variants_tried": wf["variants_tried"],
                "oos_start": str(oos_slice.index[0]),
                "oos_end": str(oos_slice.index[-1]),
                "oos_metrics": series_metrics(wf["oos_returns"],
                                              wf["oos_equity"]),
                "benchmark_oos_metrics": metrics.compute_all(bench_oos),
                "per_split": [{
                    "train": [s["split"].train_start, s["split"].train_end],
                    "test": [s["split"].test_start, s["split"].test_end],
                    "params": s["params"],
                    "train_score": (None if s["train_score"] != s["train_score"]
                                    else s["train_score"]),
                    "test_sharpe": (None if s["test_sharpe"] != s["test_sharpe"]
                                    else s["test_sharpe"]),
                } for s in wf["splits"]],
            },
            "benchmark_full_period_metrics": metrics.compute_all(bench_full),
            "top_full_period_variant": {"params": top["params"],
                                        "metrics": top["metrics"],
                                        "ledger_run": run_path.name},
        }
        out = SWEEP_DIR / f"{family}__{TICKER}.json"
        out.write_text(json.dumps(sweep_record, indent=2, sort_keys=True) + "\n")
        print(f"{TICKER} {family}: oos_sharpe="
              f"{sweep_record['walk_forward']['oos_metrics']['sharpe']:.3f} "
              f"bench={sweep_record['walk_forward']['benchmark_oos_metrics']['sharpe']:.3f} "
              f"-> {out.name}")

    # Untuned default-parameter spot checks on universe tickers (context
    # only, no tuning: variants_tried=1 per run).
    for ticker in SPOT_CHECK_TICKERS:
        spot_ohlcv = load_ohlcv(ticker, TIMEFRAME)
        for family in SPOT_CHECK_FAMILIES:
            path = ledger.run_and_record(
                strategy=family, instrument=ticker, timeframe=TIMEFRAME,
                ohlcv=spot_ohlcv, params=DEFAULT_PARAMS[family],
                variants_tried=1,
                notes=("P1 video-strategy lane: untuned default-parameter "
                       "spot check on a universe ticker (context for the "
                       "BTC-USD sweep; no selection performed)"),
            )
            print(f"spot check {ticker} {family}: -> {path.name}")

    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
