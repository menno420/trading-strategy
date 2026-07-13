#!/usr/bin/env python3
"""Round 3 slice 13 — the TEN Round-3 single-instrument families on BTC-USD.

POST-HOLDOUT, DEV-ONLY (ORDER 012 night-run: "expand the backtest surface —
new strategies, new stocks/tickers, new indicators — every result recorded
honestly"). Promotion is closed: nothing this script produces can be an
out-of-sample claim; KEEPs are dev-candidates only. This slice lands AFTER
the Round-3 synthesis (``docs/research-round-3-results.md``, PR #89, which
aggregates slices 1-8 only) and EXTENDS the round — the synthesis doc is
not rewritten; this lane's delta is recorded in its session card and PR.

The committed BTC-USD daily cache (P1 video lane; dev rail 2014-09-17 →
2025-01-08) has only ever been swept by the video-lane families
(``supertrend_flip``, ``macd_supertrend``, the dual-EMA control), the R2
§3b ``keltner_breakout`` arm and the P4 transfer spot checks. The ten
single-instrument families Round 3 added — ``stochastic_reversion``,
``williams_r_reversion``, ``roc_momentum``, ``adx_filtered_sma``,
``aroon_trend``, ``cci_reversion``, ``bollinger_breakout``,
``atr_trailing``, ``trix_momentum``, ``ichimoku_trend`` — have NEVER run
on BTC-USD. This slice completes that coverage: each family's declared
Round-3 grid is reused VERBATIM (``trading_lab.sweeps`` delegates to the
source lane's generator; equality pinned in ``tests/test_sweeps.py``), so
NO new strategy code and NO new parameter territory: 12 variants × 10
families × 1 instrument = 120 registered configs. Program burden prior to
this lane: 3260 (through slice 12, PR #92); program cumulative after:
3380. The cross-sectional family (``xsec_momentum``) is out of scope — a
basket strategy whose expanded lane (slice 9) deliberately excludes
BTC-USD over the calendar-mixing problem.

Calendar/annualization note (the P1 video-lane convention, followed here
verbatim): BTC-USD trades ~365 days/year (7 days/week — the dev cache has
3767 daily bars over ~10.3 calendar years), but metrics use the lab-wide
``PERIODS_PER_YEAR["daily"] = 252``, so annualized Sharpe/CAGR are
UNDERSTATED by a constant factor for strategy and benchmark alike —
same-window comparisons vs B&H are unaffected. Flagged, not patched. The
walk-forward windows (train 1008 / test 252 BARS) therefore span ~2.8 and
~0.7 calendar years on BTC rather than ~4 and ~1 — same bar counts as
every daily lane, shorter calendar span, as in the video lane.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded; asserted below). Costs: engine defaults, 5 bps
slippage + 1 bp commission per side. Execution: signal at bar t fills at
bar t+1 open.

For every family this script produces (same shape as Round 2 and the
earlier Round-3 lanes):

1. **Per-variant full-dev-period backtests** for every grid point —
   bookkeeping rows, NOT findings (single-split in-sample).
2. **A walk-forward evaluation** of the grid (train 1008 bars, test 252
   bars, contiguous test windows) — the stitched OOS result is the only
   reportable number, benchmarked against buy-and-hold over the exact
   same stitched OOS period. KEEP/KILL per the Round-2 rule: KEEP as
   dev-candidate iff stitched OOS Sharpe > benchmark OOS Sharpe AND > 0;
   ties/ambiguity KILL. The ORDER 007 promotion-bar arithmetic
   (``trading_lab.promotion.grade_promotion``, Bonferroni K = 12 variants
   this lane) is recorded alongside — informational only, promotion
   closed. Per the slice-11 convention, any lane whose t-stat crosses the
   NEGATIVE bar (t <= -min_tstat) is flagged loudly: significantly WORSE
   than B&H at the very bar a winner would have had to clear.
3. **One standard ledger run file** for the family's top full-period
   variant, so the lane shows up in ``experiments/index.jsonl``.

Plus exactly ONE buy-and-hold baseline ledger row for BTC-USD
(variants_tried=1): unlike the slice-3 instruments, BTC-USD has NO B&H
row on the ledger — the P1 video lane predates the slice-3 baseline
convention — so this lane records it once (a benchmark, not a searched
config); the walk-forward benchmark is recomputed in-window as always.

Usage: python3 scripts/run_r3_btc_coverage.py
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
TRAIN_SIZE = 1008  # bars (~4 trading years on equities; ~2.8 calendar years on BTC)
TEST_SIZE = 252    # bars; step defaults to TEST_SIZE (contiguous)

# Dev rail: the loader's default excludes holdout bars >= 2025-01-09, so the
# last dev bar can be at most 2025-01-08 (asserted below).
DEV_DATA_END_MAX = "2025-01-08"

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / "r3-btc-coverage"

# Program burden prior to this lane: 3260 = 3080 through slice 11 + 180
# slice 12 (r3-gated-new-tickers, PR #92 session card).
PROGRAM_PRIOR_CONFIGS = 3260

ANNUALIZATION_NOTE = (
    "P1 video-lane convention followed verbatim: BTC-USD trades ~365 "
    "days/year but metrics use the lab-wide PERIODS_PER_YEAR['daily'] = "
    "252, so annualized Sharpe/CAGR are UNDERSTATED by a constant factor "
    "for strategy and benchmark alike; same-window comparisons vs B&H are "
    "unaffected. Flagged, not patched.")

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
    grid_sizes = sweeps.r3_btc_coverage_variants_per_family()
    lane_configs = sweeps.r3_btc_coverage_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_configs
    assert grid_sizes == {fam: 12 for fam in sweeps.R3_BTC_COVERAGE_FAMILIES} \
        and lane_configs == 120, \
        "grid drifted from the declared Round-3 slice-13 lane (trading_lab.sweeps)"
    assert not (set(sweeps.R3_BTC_COVERAGE_INSTRUMENTS)
                & set(config.UNIVERSE)), \
        "slice-13 instrument must stay disjoint from the frozen universe"
    print(f"grids: {grid_sizes} × {len(sweeps.R3_BTC_COVERAGE_INSTRUMENTS)} "
          f"instrument = {lane_configs} registered configs "
          f"(program cumulative {program_cumulative})")
    verdicts = []

    for ticker in sweeps.R3_BTC_COVERAGE_INSTRUMENTS:
        ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
        data_end = str(ohlcv.index[-1])
        assert data_end[:10] <= DEV_DATA_END_MAX, \
            f"{ticker}: dev rail breached (data_end {data_end})"

        # Buy-and-hold baseline ledger run — BTC-USD has no B&H row on the
        # ledger (the P1 video lane predates the slice-3 baseline
        # convention); recorded ONCE here (benchmark, not a searched
        # config — variants_tried=1).
        ledger.run_and_record(
            strategy="buy_and_hold", instrument=ticker, timeframe=TIMEFRAME,
            ohlcv=ohlcv, params={}, variants_tried=1,
            notes=("Round 3 btc-coverage lane (post-holdout DEV-ONLY, "
                   "promotion closed — ORDER 012 night-run, slice 13): "
                   "passive buy-and-hold baseline for BTC-USD, absent from "
                   "the ledger until now (the P1 video lane predates the "
                   "slice-3 baseline convention); committed cache reused, "
                   "nothing fetched. " + ANNUALIZATION_NOTE),
        )

        for family in sweeps.R3_BTC_COVERAGE_FAMILIES:
            variants = sweeps.r3_btc_coverage_variants(family)
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
                notes=(f"Round 3 btc-coverage sweep (post-holdout DEV-ONLY, "
                       f"promotion closed — ORDER 012 night-run, slice 13, "
                       f"extends R3 after the slices-1-8 synthesis): first "
                       f"ever {family} run on BTC-USD; top full-dev-period "
                       f"variant of {len(variants)} tried (post-hoc "
                       f"selection — in-sample; the walk-forward OOS number "
                       f"lives in experiments/sweeps/r3-btc-coverage/"
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
                "schema_version": 1,
                "sweep": "r3-btc-coverage",
                "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "git_sha": ledger.git_sha(),
                "family": family,
                "instrument": ticker,
                "instrument_status": ("lane-local instrument (not in the "
                                      "frozen config.UNIVERSE); committed P1 "
                                      "video-lane cache reused, nothing "
                                      "fetched"),
                "family_status": (f"existing strategy, no new code; first "
                                  f"ever {family} run on BTC-USD (the "
                                  f"family's Round-3 lane covered "
                                  f"equities/ETFs only)"),
                "annualization_note": ANNUALIZATION_NOTE,
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
                                          * len(sweeps.R3_BTC_COVERAGE_INSTRUMENTS)),
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
                "negative_bar_crossed": bool(neg_flag),
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
                             grade["tstat"], verdict, neg_flag))
            flag_txt = "  ** NEGATIVE BAR CROSSED **" if neg_flag else ""
            print(f"{ticker} {family}: oos_sharpe={oos_sharpe:.3f} "
                  f"bench={bench_sharpe:.3f} t={grade['tstat']:.2f} "
                  f"(min {grade['min_tstat']:.2f}) {verdict} -> {out.name}"
                  f"{flag_txt}")

    kills = sum(1 for v in verdicts if v[5] == "KILL")
    neg = sum(1 for v in verdicts if v[6])
    print(f"\nsummary: {len(verdicts) - kills} KEEP / {kills} KILL "
          f"of {len(verdicts)} lanes ({neg} crossed the negative bar)")
    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
