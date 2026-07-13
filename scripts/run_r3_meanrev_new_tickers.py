#!/usr/bin/env python3
"""Round 3 slice 11 — MEAN-REVERSION FAMILIES on the 6 new instruments × daily.

POST-HOLDOUT, DEV-ONLY (ORDER 012 night-run: "expand the backtest surface —
new strategies, new stocks/tickers, new indicators — every result recorded
honestly"). Promotion is closed: nothing this script produces can be an
out-of-sample claim; KEEPs are dev-candidates only. This slice lands AFTER
the Round-3 synthesis (``docs/research-round-3-results.md``, PR #89, which
aggregates slices 1-8 only) and EXTENDS the round — the synthesis doc is
not rewritten; this lane's delta is recorded in its session card and PR.

Slice 3 (r3-new-tickers, PR #83) cached six new instruments — SPY, QQQ,
TSLA, JPM, XOM, TLT — but probed them with only 6-variant grids of three
families; slice 10 (r3-trend-new-tickers, PR #90) completed the TREND-family
coverage of that surface. This slice completes the MEAN-REVERSION coverage
with the five existing mean-reversion families (``rsi_mean_reversion``,
``bollinger_reversion``, ``pullback``, ``stochastic_reversion``,
``williams_r_reversion``) over 12-variant sub-grids of their published
axes, declared in ``trading_lab.sweeps`` BEFORE this script ran: 12
variants × 5 families × 6 instruments = 360 registered configs. Program
burden prior to this lane: 2720 (2432 through the slices-1-8 synthesis
+ 288 slice 10); program cumulative after: 3080. NO new strategy code and
NO new parameter territory (subset relations pinned in
``tests/test_sweeps.py``); the rsi_mean_reversion sub-grid is disjoint
from the slice-3 probe grid on the same instruments so no config is
registered twice (slice 10's donchian precedent). The instruments stay
lane-local (``config.UNIVERSE`` frozen); caches are the committed slice-3
ones.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded; asserted per ticker below). Costs: engine defaults,
5 bps slippage + 1 bp commission per side. Execution: signal at bar t fills
at bar t+1 open.

For every family × ticker this script produces (same shape as Round 2 and
the earlier Round-3 lanes):

1. **Per-variant full-dev-period backtests** for every grid point —
   bookkeeping rows, NOT findings (single-split in-sample).
2. **A walk-forward evaluation** of the grid (train 1008 bars ≈ 4y, test
   252 bars ≈ 1y, contiguous test windows) — the stitched OOS result is the
   only reportable number, benchmarked against buy-and-hold over the exact
   same stitched OOS period. KEEP/KILL per the Round-2 rule: KEEP as
   dev-candidate iff stitched OOS Sharpe > benchmark OOS Sharpe AND > 0;
   ties/ambiguity KILL. The ORDER 007 promotion-bar arithmetic
   (``trading_lab.promotion.grade_promotion``, Bonferroni K = 12 variants
   this lane) is recorded alongside — informational only, promotion closed.
3. **One standard ledger run file** for the family's top full-period
   variant, so the lane shows up in ``experiments/index.jsonl``.

No new buy-and-hold ledger rows: the six per-instrument B&H baselines
already sit on the ledger from slice 3 (they are benchmarks, not searched
configs); the walk-forward benchmark is recomputed in-window here as
always.

Usage: python3 scripts/run_r3_meanrev_new_tickers.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, promotion, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402
from trading_lab.walkforward import walk_forward  # noqa: E402

TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years
TEST_SIZE = 252    # ~1 trading year; step defaults to TEST_SIZE (contiguous)

# Dev rail: the loader's default excludes holdout bars >= 2025-01-09, so the
# last dev bar can be at most 2025-01-08 (asserted per ticker below).
DEV_DATA_END_MAX = "2025-01-08"

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / "r3-meanrev-new-tickers"

# Program burden prior to this lane: 2720 = 2432 through the Round-3
# slices-1-8 synthesis (docs/research-round-3-results.md budget ledger)
# + 288 slice 10 (r3-trend-new-tickers, PR #90).
PROGRAM_PRIOR_CONFIGS = 2720

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
    grid_sizes = sweeps.r3_meanrev_new_tickers_variants_per_family()
    lane_configs = sweeps.r3_meanrev_new_tickers_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_configs
    assert grid_sizes == {"rsi_mean_reversion": 12,
                          "bollinger_reversion": 12,
                          "pullback": 12,
                          "stochastic_reversion": 12,
                          "williams_r_reversion": 12} \
        and lane_configs == 360, \
        "grid drifted from the declared Round-3 slice-11 lane (trading_lab.sweeps)"
    assert not (set(sweeps.R3_MEANREV_NEW_TICKERS_INSTRUMENTS)
                & set(config.UNIVERSE)), \
        "slice-11 instruments must stay disjoint from the frozen universe"
    print(f"grids: {grid_sizes} × {len(sweeps.R3_MEANREV_NEW_TICKERS_INSTRUMENTS)} "
          f"instruments = {lane_configs} registered configs "
          f"(program cumulative {program_cumulative})")
    verdicts = []

    for ticker in sweeps.R3_MEANREV_NEW_TICKERS_INSTRUMENTS:
        ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
        data_end = str(ohlcv.index[-1])
        assert data_end[:10] <= DEV_DATA_END_MAX, \
            f"{ticker}: dev rail breached (data_end {data_end})"

        for family in sweeps.R3_MEANREV_NEW_TICKERS_FAMILIES:
            variants = sweeps.r3_meanrev_new_tickers_variants(family)
            strategy_fn = STRATEGIES[family]

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
                strategy=family, instrument=ticker, timeframe=TIMEFRAME,
                ohlcv=ohlcv, params=top["params"],
                variants_tried=len(variants),
                notes=(f"Round 3 meanrev-new-tickers sweep (post-holdout "
                       f"DEV-ONLY, promotion closed — ORDER 012 night-run, "
                       f"slice 11, extends R3 after the slices-1-8 "
                       f"synthesis): top full-dev-period variant of "
                       f"{len(variants)} tried (post-hoc selection — "
                       f"in-sample; the walk-forward OOS number lives in "
                       f"experiments/sweeps/r3-meanrev-new-tickers/"
                       f"{family}__{ticker}.json)"),
            )

            oos_m = series_metrics(wf["oos_returns"], wf["oos_equity"])
            bench_oos_m = metrics.compute_all(bench_oos)
            oos_sharpe, bench_sharpe = oos_m["sharpe"], bench_oos_m["sharpe"]
            # Round-2 KEEP/KILL rule; ties/ambiguity resolve KILL.
            keep = (oos_sharpe is not None and bench_sharpe is not None
                    and oos_sharpe > bench_sharpe and oos_sharpe > 0)
            verdict = "KEEP (dev-candidate only)" if keep else "KILL"
            # ORDER 007 promotion-bar arithmetic — informational only:
            # promotion is CLOSED post-holdout, nothing here can promote.
            grade = promotion.grade_promotion(
                strategy_sharpe=oos_sharpe, benchmark_sharpe=bench_sharpe,
                n_periods=oos_m["n_bars"], timeframe=TIMEFRAME,
                variants_tried=len(variants))

            bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME)
            sweep_record = {
                "schema_version": 1,
                "sweep": "r3-meanrev-new-tickers",
                "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "git_sha": ledger.git_sha(),
                "family": family,
                "instrument": ticker,
                "instrument_status": ("slice-3 lane-local instrument (not in "
                                      "the frozen config.UNIVERSE); committed "
                                      "PR #83 cache reused"),
                "family_status": ("existing strategy, no new code; slice 3 "
                                  "already probed this family on these "
                                  "instruments with a 6-variant grid — this "
                                  "12-variant sub-grid is DISJOINT from that "
                                  "probe (pinned by test)"
                                  if family == "rsi_mean_reversion" else
                                  "existing strategy, no new code"),
                "timeframe": TIMEFRAME,
                "post_holdout_dev_only": True,
                "order": "ORDER 012 night-run (control/inbox.md)",
                "data_start": str(ohlcv.index[0]),
                "data_end": data_end,
                "n_bars": int(len(ohlcv)),
                "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                          "commission_bps": config.DEFAULT_COMMISSION_BPS},
                "execution": "signal at bar t fills at bar t+1 open",
                "variants_tried": len(variants),
                "family_variants_tried": (grid_sizes[family]
                                          * len(sweeps.R3_MEANREV_NEW_TICKERS_INSTRUMENTS)),
                "lane_variants_tried": lane_configs,
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
                    "oos_metrics": oos_m,
                    "benchmark_oos_metrics": bench_oos_m,
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
                "verdict": verdict,
                "promotion_grade": {
                    "note": ("ORDER 007 bar on the stitched OOS Sharpe delta, "
                             "Bonferroni K = variants this lane — "
                             "INFORMATIONAL ONLY, promotion is CLOSED "
                             "post-holdout (nothing here is a finding)"),
                    **grade,
                },
            }
            out = SWEEP_DIR / f"{family}__{ticker}.json"
            out.write_text(json.dumps(sweep_record, indent=2, sort_keys=True) + "\n")
            verdicts.append((ticker, family, oos_sharpe, bench_sharpe,
                             grade["tstat"], verdict))
            print(f"{ticker} {family}: oos_sharpe={oos_sharpe:.3f} "
                  f"bench={bench_sharpe:.3f} t={grade['tstat']:.2f} "
                  f"(min {grade['min_tstat']:.2f}) {verdict} -> {out.name}")

    kills = sum(1 for v in verdicts if v[5] == "KILL")
    print(f"\nsummary: {len(verdicts) - kills} KEEP / {kills} KILL "
          f"of {len(verdicts)} lanes")
    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
