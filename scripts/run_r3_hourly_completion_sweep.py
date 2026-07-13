#!/usr/bin/env python3
"""Round 3 slice 15 — hourly-matrix completion × all 8 tickers × HOURLY.

POST-HOLDOUT, DEV-ONLY (ORDER 012 night-run: "expand the backtest surface —
new strategies, new stocks/tickers, new indicators — every result recorded
honestly"). Promotion is closed: nothing this script produces can be an
out-of-sample claim; KEEPs are dev-candidates only. This slice lands AFTER
the Round-3 synthesis (``docs/research-round-3-results.md``, PR #89, which
aggregates slices 1-8 only) and EXTENDS the round — the synthesis doc is
not rewritten; this lane's delta is recorded in its session card and PR.

TIMEFRAME expansion, not a strategy expansion — the COMPLETION of the
Round-3 hourly matrix started by slice 5
(``scripts/run_r3_meanrev_hourly_sweep.py``, PR #85) and slice 14
(``scripts/run_r3_trend_hourly_sweep.py``, PR #94): NO new strategy code —
the four remaining Round-3 single-instrument families (``cci_reversion``,
``bollinger_breakout``, ``atr_trailing``, ``ichimoku_trend``) are re-swept
on hourly bars. After this lane every Round-3 single-instrument family has
both a daily and an hourly lane. Conventions follow the three prior hourly
lanes (``scripts/run_p1_trend_hourly_sweep.py`` /
docs/p1-trend-hourly-results.md, the slice-5 script and the slice-14
script) exactly:

* **Data:** committed hourly caches only (zero network fetches), via
  ``trading_lab.data.load_ohlcv`` on its default rail (bars >= 2025-01-09
  excluded) — dev period 2023-08-10 → 2025-01-08, ~2476 bars/ticker; this
  script additionally ASSERTS data_end < HOLDOUT_START per ticker before
  any backtest runs.
* **Grids:** bar-denominated lookbacks reused as-is — on hourly bars the
  same numbers mean hours-to-days instead of days-to-weeks (cci period 20
  is ~3 sessions; the atr_trailing turtle channel 55 is ~8.5 sessions;
  the Hosoda 9/26/52 spans ~1.4/4/8 sessions, senkou displacement frozen
  at 26 BARS). Each family's declared Round-3 12-variant daily grid is
  reused VERBATIM by delegation in ``trading_lab.sweeps`` (declared
  BEFORE this script ran): 12 variants per family × 8 tickers = 384
  registered configs. Program burden prior to this lane: 3764 (through
  slice 14, PR #94); program cumulative after: 4148.
* **Walk-forward:** the lab's 1008/252/252 BAR convention, kept
  deliberately for cross-lane comparability (decide-and-flag, as in the
  p1-trend-hourly, slice-5 and slice-14 lanes): ~7.4-month train windows,
  ~7.4-week test windows; on ~2476 bars it yields 5 splits and a stitched
  OOS of ~1260 bars ≈ 8.5 months — a single regime, and honestly labeled
  as such. Ichimoku's warmup (senkou_b 52 + displacement 26 = 78 bars)
  fits comfortably inside a 1008-bar train window — verified, not
  assumed, by the INSUFFICIENT-DATA gate below plus the runnability
  tests; any lane that cannot support the established method is recorded
  honestly rather than bent.
* **Costs:** engine defaults, 5 bps slippage + 1 bp commission per side —
  at 1638 hourly bars/year this bites harder than on daily bars; this
  lane mixes a fast oscillator (cci_reversion, reversion-grade turnover)
  with three slower breakout/cloud trend families, so it measures both
  ends of the turnover spectrum on the same rail.
* **Annualization:** hourly Sharpe/CAGR via
  ``config.PERIODS_PER_YEAR["hourly"]`` = 1638 (252 × 6.5), applied by
  ``trading_lab.metrics`` through the ``timeframe="hourly"`` argument.

For every family × ticker this script produces (same shape as the earlier
Round-3 slices):

1. **Per-variant full-dev-period backtests** for every grid point —
   bookkeeping rows, NOT findings (single-split in-sample).
2. **A walk-forward evaluation** of the grid — the stitched OOS result is
   the only reportable number, benchmarked against buy-and-hold over the
   exact same stitched OOS period. KEEP/KILL per the Round-2 rule: KEEP as
   dev-candidate iff stitched OOS Sharpe > benchmark OOS Sharpe AND > 0;
   ties/ambiguity KILL. The ORDER 007 promotion-bar arithmetic
   (``trading_lab.promotion.grade_promotion``, Bonferroni K = 12 variants
   this lane, hourly annualization) is recorded alongside — informational
   only, promotion closed. Per the slice-11 convention, any lane whose
   t-stat crosses the NEGATIVE bar (t <= -min_tstat) is flagged loudly
   (``negative_bar_crossed``, as slices 13/14 recorded it): significantly
   WORSE than B&H at the very bar a winner would have had to clear. If a
   ticker's cache cannot support even one 1008/252 split, the lane is
   recorded as a first-class ``INSUFFICIENT-DATA`` verdict row instead of
   bending the method.
3. **One standard ledger run file** for the family's top full-period
   variant, so the lane shows up in ``experiments/index.jsonl``.

Usage: python3 scripts/run_r3_hourly_completion_sweep.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from trading_lab import config, ledger, metrics, promotion, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402
from trading_lab.walkforward import walk_forward  # noqa: E402

TIMEFRAME = "hourly"
TRAIN_SIZE = 1008  # lab convention, in BARS (~7.4 months of hourly bars)
TEST_SIZE = 252    # in BARS (~7.4 weeks); step defaults to TEST_SIZE

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / "r3-hourly-completion"

# Program burden prior to this lane: 3764 = 3380 through slice 13
# (r3-btc-coverage, PR #93) + 384 slice 14 (r3-trend-hourly, PR #94).
PROGRAM_PRIOR_CONFIGS = 3764

VARIANT_METRIC_KEYS = ("sharpe", "sortino", "cagr", "total_return",
                       "max_drawdown", "win_rate", "turnover_per_year",
                       "n_trades")

VERDICT_INSUFFICIENT = "INSUFFICIENT-DATA"


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
    grid_sizes = sweeps.r3_hourly_completion_variants_per_family()
    lane_configs = sweeps.r3_hourly_completion_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_configs
    assert grid_sizes == {fam: 12
                          for fam in sweeps.R3_HOURLY_COMPLETION_FAMILIES} \
        and lane_configs == 384, \
        "grid drifted from the declared Round-3 slice-15 lane (trading_lab.sweeps)"
    print(f"grids: {grid_sizes} × {len(sweeps.R3_HOURLY_COMPLETION_INSTRUMENTS)} "
          f"instruments = {lane_configs} registered configs "
          f"(program cumulative {program_cumulative})")
    verdicts = []

    holdout = pd.Timestamp(config.HOLDOUT_START)
    for ticker in sweeps.R3_HOURLY_COMPLETION_INSTRUMENTS:
        ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
        # Holdout rail, asserted per ticker before any backtest runs
        # (p1-trend-hourly convention).
        assert ohlcv.index[-1] < holdout, (
            f"{ticker}: data_end {ohlcv.index[-1]} >= HOLDOUT_START "
            f"{config.HOLDOUT_START}")
        for family in sweeps.R3_HOURLY_COMPLETION_FAMILIES:
            variants = sweeps.r3_hourly_completion_variants(family)
            strategy_fn = STRATEGIES[family]
            base_record = {
                "schema_version": 1,
                "sweep": "r3-hourly-completion",
                "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "git_sha": ledger.git_sha(),
                "family": family,
                "instrument": ticker,
                "timeframe": TIMEFRAME,
                "post_holdout_dev_only": True,
                "order": "ORDER 012 night-run (control/inbox.md)",
                "data_start": str(ohlcv.index[0]),
                "data_end": str(ohlcv.index[-1]),
                "n_bars": int(len(ohlcv)),
                "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                          "commission_bps": config.DEFAULT_COMMISSION_BPS},
                "execution": "signal at bar t fills at bar t+1 open",
                "variants_tried": len(variants),
                "family_variants_tried": (
                    grid_sizes[family]
                    * len(sweeps.R3_HOURLY_COMPLETION_INSTRUMENTS)),
                "lane_variants_tried": lane_configs,
                "program_variants_tried": program_cumulative,
            }
            out = SWEEP_DIR / f"{family}__{ticker}.json"

            # Honest first-class insufficient-data verdict: the established
            # split needs at least TRAIN+TEST bars; do not bend the method.
            if len(ohlcv) < TRAIN_SIZE + TEST_SIZE:
                record = {**base_record,
                          "verdict": VERDICT_INSUFFICIENT,
                          "walk_forward": {
                              "train_size": TRAIN_SIZE,
                              "test_size": TEST_SIZE,
                              "n_splits": 0,
                              "note": (f"{len(ohlcv)} bars < "
                                       f"{TRAIN_SIZE + TEST_SIZE} needed for "
                                       f"one 1008/252 split — no OOS number "
                                       f"exists for this lane"),
                          }}
                out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
                verdicts.append((ticker, family, None, None, None,
                                 VERDICT_INSUFFICIENT, False))
                print(f"{ticker} {family}: n_bars={len(ohlcv)} "
                      f"{VERDICT_INSUFFICIENT} -> {out.name}")
                continue

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
                notes=(f"Round 3 hourly-completion sweep (post-holdout "
                       f"DEV-ONLY, promotion closed — ORDER 012 night-run, "
                       f"slice 15, extends R3 after the slices-1-8 "
                       f"synthesis): top full-dev-period variant of "
                       f"{len(variants)} tried (post-hoc selection — "
                       f"in-sample; the walk-forward OOS number lives in "
                       f"experiments/sweeps/r3-hourly-completion/"
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
            # Slice-11 convention: flag lanes significantly WORSE than B&H
            # at the same Bonferroni bar a winner would have had to clear.
            neg_flag = grade["tstat"] <= -grade["min_tstat"]

            bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME)
            sweep_record = {
                **base_record,
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
                "negative_bar_crossed": bool(neg_flag),
                "promotion_grade": {
                    "note": ("ORDER 007 bar on the stitched OOS Sharpe delta, "
                             "Bonferroni K = variants this lane, hourly "
                             "annualization — INFORMATIONAL ONLY, promotion "
                             "is CLOSED post-holdout (nothing here is a "
                             "finding)"),
                    **grade,
                },
            }
            out.write_text(json.dumps(sweep_record, indent=2, sort_keys=True) + "\n")
            verdicts.append((ticker, family, oos_sharpe, bench_sharpe,
                             grade["tstat"], verdict, neg_flag))
            flag_txt = "  ** NEGATIVE BAR CROSSED **" if neg_flag else ""
            print(f"{ticker} {family}: oos_sharpe={oos_sharpe:.3f} "
                  f"bench={bench_sharpe:.3f} t={grade['tstat']:.2f} "
                  f"(min {grade['min_tstat']:.2f}) {verdict} -> {out.name}"
                  f"{flag_txt}")

    kills = sum(1 for v in verdicts if v[5] == "KILL")
    insufficient = sum(1 for v in verdicts if v[5] == VERDICT_INSUFFICIENT)
    keeps = len(verdicts) - kills - insufficient
    neg = sum(1 for v in verdicts if v[6])
    print(f"\nsummary: {keeps} KEEP / {kills} KILL / "
          f"{insufficient} {VERDICT_INSUFFICIENT} of {len(verdicts)} lanes "
          f"({neg} crossed the negative bar)")
    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
