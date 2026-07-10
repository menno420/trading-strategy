#!/usr/bin/env python3
"""P1 known-indicator sweep — mean-reversion family × all 8 tickers × daily.

Lane: mean-reversion (rsi_mean_reversion, bollinger_reversion, pullback) on
the full universe, daily bars, pre-holdout dev data only, realistic costs on
(engine defaults: 5 bps slippage + 1 bp commission per side).

For every family × ticker this script produces:

1. **Per-variant full-dev-period backtests** for every grid point in
   ``trading_lab.sweeps`` — recorded as rows in ONE aggregate sweep file
   (``experiments/sweeps/p1-mean-reversion-daily/<family>__<ticker>.json``).
   These rows are multiple-testing bookkeeping (the raw material for deflated
   Sharpe analysis), NOT findings: each row is a single-split in-sample
   backtest.
2. **A walk-forward evaluation** of the family grid
   (``trading_lab.walkforward.walk_forward``, train 1008 bars ≈ 4y, test 252
   bars ≈ 1y, contiguous test windows) — the stitched out-of-sample result is
   the only number reported as a finding, benchmarked against buy-and-hold
   over the exact same stitched OOS period.
3. **One standard ledger run file** for the family's top full-period variant
   (``variants_tried`` = family grid size — it was selected post hoc from the
   whole grid), so the family shows up in ``experiments/index.jsonl``.

Decide-and-flag (aggregation): same convention as the trend lane — one
aggregate sweep file per family × ticker with per-variant rows plus a single
ledger run for its top variant, instead of ~1,150 one-file-per-variant runs.

Usage: python3 scripts/run_p1_meanrev_sweep.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402
from trading_lab.walkforward import walk_forward  # noqa: E402

TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years
TEST_SIZE = 252    # ~1 trading year; step defaults to TEST_SIZE (contiguous)

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / "p1-mean-reversion-daily"

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
    grid_sizes = sweeps.mean_reversion_variants_per_family()
    print(f"grids: {grid_sizes} (total {sweeps.mean_reversion_total_variants()})")

    for ticker in config.UNIVERSE:
        ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
        for family in sweeps.MEAN_REVERSION_FAMILIES:
            variants = sweeps.mean_reversion_variants(family)
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
                strategy=family, instrument=ticker, timeframe=TIMEFRAME,
                ohlcv=ohlcv, params=top["params"],
                variants_tried=len(variants),
                notes=(f"P1 mean-reversion sweep: top full-dev-period variant "
                       f"of {len(variants)} tried (post-hoc selection — "
                       f"in-sample; the walk-forward OOS finding lives in "
                       f"experiments/sweeps/p1-mean-reversion-daily/"
                       f"{family}__{ticker}.json)"),
            )

            bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME)
            sweep_record = {
                "schema_version": 1,
                "sweep": "p1-mean-reversion-daily",
                "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "git_sha": ledger.git_sha(),
                "family": family,
                "instrument": ticker,
                "timeframe": TIMEFRAME,
                "data_start": str(ohlcv.index[0]),
                "data_end": str(ohlcv.index[-1]),
                "n_bars": int(len(ohlcv)),
                "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                          "commission_bps": config.DEFAULT_COMMISSION_BPS},
                "execution": "signal at bar t fills at bar t+1 open",
                "variants_tried": len(variants),
                "lane_variants_tried": sweeps.mean_reversion_total_variants(),
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
            out = SWEEP_DIR / f"{family}__{ticker}.json"
            out.write_text(json.dumps(sweep_record, indent=2, sort_keys=True) + "\n")
            print(f"{ticker} {family}: oos_sharpe="
                  f"{sweep_record['walk_forward']['oos_metrics']['sharpe']:.3f} "
                  f"bench={sweep_record['walk_forward']['benchmark_oos_metrics']['sharpe']:.3f} "
                  f"-> {out.name}")

    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
