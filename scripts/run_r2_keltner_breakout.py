#!/usr/bin/env python3
"""Round 2 slice R2 — `keltner_breakout` × {BTC-USD, META, AMZN, SLV} × daily.

POST-HOLDOUT, DEV-ONLY (docs/research-round-2.md — BINDING pre-registration,
merged before any Round 2 number existed). Promotion is closed: nothing this
script produces can be an out-of-sample claim; KEEPs are dev-candidates only.

Family (§3b): long when close > EMA(n) + m * ATR(n); exit (flat) when
close < EMA(n). Long/flat. Grid frozen at n ∈ {20, 50}, m ∈ {1.5, 2.0, 2.5}
→ 6 variants/instrument × 4 instruments = 24 registered configs.
Round-2 lane cumulative after this slice: 48 (R1) + 24 = 72; program
cumulative: 590 + 72 = 662.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded). Costs: engine defaults, 5 bps slippage + 1 bp
commission per side. Execution: signal at bar t fills at bar t+1 open.

For every instrument this script produces (same shape as slice R1):

1. **Per-variant full-dev-period backtests** for every grid point —
   bookkeeping rows, NOT findings (single-split in-sample).
2. **A walk-forward evaluation** of the grid (train 1008 bars ≈ 4y, test
   252 bars ≈ 1y, contiguous test windows) — the stitched OOS result is the
   only reportable number, benchmarked against buy-and-hold over the exact
   same stitched OOS period. KEEP/KILL per §6: KEEP as dev-candidate iff
   stitched OOS Sharpe > benchmark OOS Sharpe AND > 0; ties/ambiguity KILL.
3. **One standard ledger run file** for the instrument's top full-period
   variant, so the lane shows up in ``experiments/index.jsonl``.

Usage: python3 scripts/run_r2_keltner_breakout.py
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
TRAIN_SIZE = 1008  # ~4 trading years (pre-registration §5)
TEST_SIZE = 252    # ~1 trading year; step defaults to TEST_SIZE (contiguous)

FAMILY = "keltner_breakout"
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / "r2-keltner_breakout"

# Round-2 lane configs already spent before this slice (R1, merged in #47).
ROUND2_PRIOR_CONFIGS = 48
PROGRAM_PRIOR_CONFIGS = 590  # pre-Round-2 program burden (pre-reg §2)

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
    variants = sweeps.r2_keltner_variants(FAMILY)
    family_configs = sweeps.r2_keltner_total_configs()
    lane_cumulative = ROUND2_PRIOR_CONFIGS + family_configs
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_cumulative
    assert len(variants) == 6 and family_configs == 24, \
        "grid drifted from the pre-registration (docs/research-round-2.md §3b)"
    print(f"grid: {len(variants)} variants/instrument × "
          f"{len(sweeps.R2_KELTNER_INSTRUMENTS)} instruments = "
          f"{family_configs} registered configs "
          f"(Round-2 lane cumulative {lane_cumulative}, "
          f"program cumulative {program_cumulative})")
    strategy_fn = STRATEGIES[FAMILY]

    for ticker in sweeps.R2_KELTNER_INSTRUMENTS:
        ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default

        # 1) full-dev-period backtest per variant (bookkeeping rows)
        rows = []
        for params in variants:
            res = run_backtest(ohlcv, strategy_fn(ohlcv, **params),
                               timeframe=TIMEFRAME)
            m = metrics.compute_all(res)
            rows.append({"params": params,
                         "metrics": {k: m[k] for k in VARIANT_METRIC_KEYS}})

        # 2) walk-forward OOS — the only reportable number (dev-only)
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
            strategy=FAMILY, instrument=ticker, timeframe=TIMEFRAME,
            ohlcv=ohlcv, params=top["params"],
            variants_tried=len(variants),
            notes=(f"Round 2 slice R2 (post-holdout DEV-ONLY, promotion "
                   f"closed — docs/research-round-2.md): top full-dev-period "
                   f"variant of {len(variants)} tried (post-hoc selection — "
                   f"in-sample; the walk-forward OOS number lives in "
                   f"experiments/sweeps/r2-keltner_breakout/"
                   f"{FAMILY}__{ticker}.json)"),
        )

        bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME)
        sweep_record = {
            "schema_version": 1,
            "sweep": "r2-keltner_breakout",
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": FAMILY,
            "instrument": ticker,
            "timeframe": TIMEFRAME,
            "preregistration": "docs/research-round-2.md",
            "post_holdout_dev_only": True,
            "data_start": str(ohlcv.index[0]),
            "data_end": str(ohlcv.index[-1]),
            "n_bars": int(len(ohlcv)),
            "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                      "commission_bps": config.DEFAULT_COMMISSION_BPS},
            "execution": "signal at bar t fills at bar t+1 open",
            "variants_tried": len(variants),
            "family_variants_tried": family_configs,
            "lane_variants_tried": lane_cumulative,
            "program_variants_tried": program_cumulative,
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
        out = SWEEP_DIR / f"{FAMILY}__{ticker}.json"
        out.write_text(json.dumps(sweep_record, indent=2, sort_keys=True) + "\n")
        oos_sharpe = sweep_record["walk_forward"]["oos_metrics"]["sharpe"]
        bench_sharpe = sweep_record["walk_forward"]["benchmark_oos_metrics"]["sharpe"]
        verdict = ("KEEP (dev-candidate only)"
                   if oos_sharpe is not None and bench_sharpe is not None
                   and oos_sharpe > bench_sharpe and oos_sharpe > 0
                   else "KILL")
        print(f"{ticker} {FAMILY}: oos_sharpe="
              f"{oos_sharpe:.3f} bench={bench_sharpe:.3f} {verdict} "
              f"-> {out.name}")

    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
