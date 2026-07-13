#!/usr/bin/env python3
"""Round 4 slice R4-F — DAY-OF-WEEK SEASONALITY across the 15 daily tickers.

POST-HOLDOUT, DEV-ONLY (pre-registered in ``docs/research-round-4-plan.md``
§ R4-F, merged BEFORE any Round-4 outcome existed; owner mandate ORDER 012
night-run, "continue with some new ideas"). Promotion is CLOSED: nothing
this script produces can be an out-of-sample claim; a KEEP anywhere below
is dev-candidate only, never a finding.

The program's first *calendar* hypothesis and a classic multiple-testing
trap — pre-registered as the stress test of the round's correction
discipline. One new family (``weekday_long``: long only on bars signalled
on one chosen weekday, house signal-at-t / fill-at-t+1-open rail — the
variant labeled weekday=d is exposed to the session AFTER each day-d bar;
the five variants together tile the trading week, see the strategy module
docstring) swept across ALL 15 committed daily caches, declared in
``trading_lab.sweeps`` BEFORE this script ran.

K accounting (the point of this slice)
--------------------------------------
The lane grid handed to each ticker's walk-forward is the 5 weekday
variants, but the REGISTERED significance bar counts ALL day×ticker combos
tested: 5 weekdays × 15 tickers = **K = 75**, so the Bonferroni bar RISES
to ``min_tstat(75)`` ≈ **3.21** (vs 2.64 at the standard K=12). K is never
counted down; the bar is never lowered. Both numbers are recorded per
lane: the lane-local informational t-stat at K=5 (comparable to other
rounds' lane grades — informational only, promotion closed) and the
registered K=75 verdict. Pre-registered hypothesis: **null after
correction** — ``significant_at_k75`` is a boolean nothing is expected to
set. Pre-registered rule: a combo is an R4-F KEEP iff it clears BOTH the
Round-2 benchmark rule AND t ≥ 3.21 at K=75; everything else KILL, or
KILL-SIG at t ≤ −3.21 (R4-A's mirrored bar, ``classify_verdict``).

Rail (standard, unchanged)
--------------------------
Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded; ``data_end <= 2025-01-08`` asserted per ticker
below; the holdout is SPENT and never read). Costs: engine defaults, 5 bps
slippage + 1 bp commission per side. Execution: signal at bar t fills at
bar t+1 open. Walk-forward: train 1008 bars ≈ 4y, test 252 bars ≈ 1y,
contiguous test windows; stitched OOS vs buy-and-hold over the exact same
stitched window at the same costs. Round-2 KEEP/KILL rule: KEEP as
dev-candidate iff stitched OOS Sharpe > benchmark OOS Sharpe AND > 0;
ties/ambiguity KILL.

For every ticker this script produces (r3 schema plus the K=75 block):

1. **Per-variant full-dev-period backtests** (5 rows) — bookkeeping, NOT
   findings (single-split in-sample).
2. **A walk-forward evaluation** of the 5-variant lane grid — the stitched
   OOS result graded by the standard rule, with the lane-local K=5
   informational grade AND the registered K=75 verdict.
3. **Per-combo fixed-weekday walk-forwards** — each of the 5 registered
   day×ticker combos replayed as a fixed rule (grid of exactly that one
   variant, no selection) over the SAME walk-forward windows, so all 75
   registered combos carry their own stitched OOS t-stat against the 3.21
   bar. This is what the registered K counts.
4. **One standard ledger run file** for the lane's top full-period variant
   (these ARE new runs — new family, new configs — unlike the R4-B
   replay), followed by one ``rebuild_index()`` at the end.

Program burden: 4148 registered configs prior to this lane (2432 through
the Round-3 slices-1-8 synthesis + 288 slice 10 + 360 slice 11 + 180
slice 12 + 120 slice 13 + 384 slice 14 + 384 slice 15; the Round-4 R4-A
and R4-B re-grades searched nothing new); this lane adds 75 → program
cumulative 4223.

Usage: python3 scripts/run_r4_seasonality_sweep.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, promotion, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402
from trading_lab.walkforward import walk_forward  # noqa: E402

FAMILY = "weekday_long"
TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years
TEST_SIZE = 252    # ~1 trading year; step defaults to TEST_SIZE (contiguous)

# Dev rail: the loader's default excludes holdout bars >= 2025-01-09, so the
# last dev bar can be at most 2025-01-08 (asserted per ticker below).
DEV_DATA_END_MAX = "2025-01-08"

SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / "r4-seasonality"

# Program burden prior to this lane (see module docstring for the ledger).
PROGRAM_PRIOR_CONFIGS = 4148

VARIANT_METRIC_KEYS = ("sharpe", "sortino", "cagr", "total_return",
                       "max_drawdown", "win_rate", "turnover_per_year",
                       "n_trades")

WEEKDAY_NAMES = {0: "Mon", 1: "Tue", 2: "Wed", 3: "Thu", 4: "Fri"}


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


def _clean(x):
    """NaN -> None for JSON."""
    return None if isinstance(x, float) and x != x else x


def main() -> None:
    t0 = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    variants = sweeps.r4_seasonality_variants(FAMILY)
    lane_configs = sweeps.r4_seasonality_total_configs()
    k_registered = sweeps.R4_SEASONALITY_K
    bar_k75 = promotion.min_tstat(k_registered)
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_configs
    assert variants == [{"weekday": d} for d in range(5)] \
        and lane_configs == 75 and k_registered == 75, \
        "grid drifted from the declared Round-4 R4-F lane (trading_lab.sweeps)"
    assert round(bar_k75, 2) == 3.21, "K=75 bar drifted"
    strategy_fn = STRATEGIES[FAMILY]
    print(f"grid: {len(variants)} weekday variants × "
          f"{len(sweeps.R4_SEASONALITY_INSTRUMENTS)} instruments = "
          f"{lane_configs} registered configs; REGISTERED K = {k_registered}, "
          f"bar min_tstat({k_registered}) = {bar_k75:.3f} "
          f"(program cumulative {program_cumulative})")

    lane_rows = []
    combo_rows = []

    for ticker in sweeps.R4_SEASONALITY_INSTRUMENTS:
        ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
        data_end = str(ohlcv.index[-1])
        assert data_end[:10] <= DEV_DATA_END_MAX, \
            f"{ticker}: dev rail breached (data_end {data_end})"

        # 1) full-dev-period backtest per variant (bookkeeping rows)
        rows = []
        for params in variants:
            res = run_backtest(ohlcv, strategy_fn(ohlcv, **params),
                               timeframe=TIMEFRAME)
            m = metrics.compute_all(res)
            rows.append({"params": params,
                         "metrics": {k: m[k] for k in VARIANT_METRIC_KEYS}})

        # 2) walk-forward over the 5-variant lane grid — standard rail
        wf = walk_forward(ohlcv, strategy_fn, variants,
                          train_size=TRAIN_SIZE, test_size=TEST_SIZE,
                          timeframe=TIMEFRAME)
        first, last = wf["splits"][0]["split"], wf["splits"][-1]["split"]
        oos_slice = ohlcv.iloc[first.test_start:last.test_end]
        bench_oos = buy_and_hold_result(oos_slice, timeframe=TIMEFRAME)
        oos_m = series_metrics(wf["oos_returns"], wf["oos_equity"])
        bench_oos_m = metrics.compute_all(bench_oos)
        oos_sharpe, bench_sharpe = oos_m["sharpe"], bench_oos_m["sharpe"]

        # Round-2 KEEP/KILL rule (standard, dev-candidate semantics);
        # ties/ambiguity resolve KILL.
        keep = (oos_sharpe is not None and bench_sharpe is not None
                and oos_sharpe > bench_sharpe and oos_sharpe > 0)
        verdict = "KEEP (dev-candidate only)" if keep else "KILL"
        # Lane-local informational grade (K = 5 variants this lane's grid),
        # comparable to other rounds' lane grades — informational only.
        grade = promotion.grade_promotion(
            strategy_sharpe=oos_sharpe, benchmark_sharpe=bench_sharpe,
            n_periods=oos_m["n_bars"], timeframe=TIMEFRAME,
            variants_tried=len(variants))
        # REGISTERED K=75 verdict: KEEP iff standard rule AND t >= 3.21;
        # KILL-SIG at t <= -3.21 (classify_verdict, R4-A bar mirrored).
        t = grade["tstat"]
        significant = bool(t == t and t >= bar_k75)
        verdict_k75 = promotion.classify_verdict(keep and significant,
                                                 t, bar_k75)

        # 3) per-combo fixed-weekday walk-forwards — the 5 registered
        # day×ticker combos this lane contributes to K=75. Grid of exactly
        # one variant: no selection happens, the walk-forward degenerates
        # to an honest stitched OOS replay of the fixed rule over the SAME
        # test windows as the lane grid above.
        combos = []
        for params in variants:
            cwf = walk_forward(ohlcv, strategy_fn, [params],
                               train_size=TRAIN_SIZE, test_size=TEST_SIZE,
                               timeframe=TIMEFRAME)
            assert len(cwf["splits"]) == len(wf["splits"]), \
                f"{ticker}: combo windows drifted from the lane windows"
            c_m = series_metrics(cwf["oos_returns"], cwf["oos_equity"])
            c_sharpe = c_m["sharpe"]
            c_keep = (c_sharpe is not None and bench_sharpe is not None
                      and c_sharpe > bench_sharpe and c_sharpe > 0)
            if c_sharpe is None:
                c_t = None
            else:
                c_t = promotion.sharpe_delta_tstat(
                    c_sharpe, bench_sharpe, c_m["n_bars"], TIMEFRAME)
            c_sig = bool(c_t is not None and c_t == c_t and c_t >= bar_k75)
            combo = {
                "weekday": params["weekday"],
                "weekday_name": WEEKDAY_NAMES[params["weekday"]],
                "instrument": ticker,
                "oos_metrics": c_m,
                "benchmark_oos_sharpe": _clean(bench_sharpe),
                "keep_standard_rule": bool(c_keep),
                "tstat": _clean(c_t),
                "min_tstat_k75": bar_k75,
                "significant_at_k75": c_sig,
                # Pre-registered R4-F rule: KEEP iff standard rule AND
                # t >= 3.21 at K=75; KILL-SIG at t <= -3.21.
                "verdict_r4f_registered": promotion.classify_verdict(
                    c_keep and c_sig, c_t, bar_k75),
            }
            combos.append(combo)
            combo_rows.append(combo)

        # 4) ledger run for the top full-period variant (new runs — new
        # family, new configs — so they DO go on the ledger, unlike R4-B)
        top = max(rows, key=lambda r: (r["metrics"]["sharpe"]
                                       if r["metrics"]["sharpe"] is not None
                                       else float("-inf")))
        run_path = ledger.run_and_record(
            strategy=FAMILY, instrument=ticker, timeframe=TIMEFRAME,
            ohlcv=ohlcv, params=top["params"],
            variants_tried=len(variants),
            notes=(f"Round 4 R4-F day-of-week seasonality sweep "
                   f"(post-holdout DEV-ONLY, promotion closed — "
                   f"pre-registered docs/research-round-4-plan.md § R4-F, "
                   f"ORDER 012): top full-dev-period variant of "
                   f"{len(variants)} tried (post-hoc selection — "
                   f"in-sample; REGISTERED significance K = "
                   f"{k_registered} across all day×ticker combos, bar "
                   f"min_tstat({k_registered}) ≈ {bar_k75:.2f}; the "
                   f"walk-forward OOS number lives in experiments/sweeps/"
                   f"r4-seasonality/{FAMILY}__{ticker}.json)"),
        )

        bench_full = buy_and_hold_result(ohlcv, timeframe=TIMEFRAME)
        sweep_record = {
            "schema_version": 1,
            "sweep": "r4-seasonality",
            "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": FAMILY,
            "instrument": ticker,
            "instrument_status": ("committed daily cache (full committed "
                                  "daily surface — all 15 caches swept, no "
                                  "post-hoc instrument selection)"),
            "family_status": ("NEW strategy family (weekday_long) — the "
                              "program's first calendar rule; registered in "
                              "trading_lab.sweeps before this script ran"),
            "timeframe": TIMEFRAME,
            "post_holdout_dev_only": True,
            "order": "ORDER 012 night-run (control/inbox.md)",
            "pre_registration": "docs/research-round-4-plan.md § R4-F",
            "data_start": str(ohlcv.index[0]),
            "data_end": data_end,
            "n_bars": int(len(ohlcv)),
            "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                      "commission_bps": config.DEFAULT_COMMISSION_BPS},
            "execution": "signal at bar t fills at bar t+1 open",
            "variants_tried": len(variants),
            "lane_variants_tried": lane_configs,
            "program_variants_tried": program_cumulative,
            "k_registered": k_registered,
            "k_registered_note": ("the REGISTERED significance K for this "
                                  "slice counts ALL day×ticker combos: 5 "
                                  "weekdays × 15 tickers = 75; the bar "
                                  "RISES to min_tstat(75) ≈ 3.21 — never "
                                  "lowered, never counted down"),
            "min_tstat_k75": bar_k75,
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
                    "train_score": _clean(s["train_score"]),
                    "test_sharpe": _clean(s["test_sharpe"]),
                } for s in wf["splits"]],
            },
            "combos": {
                "note": ("the 5 registered day×ticker combos this lane "
                         "contributes to K=75 — each a FIXED single-weekday "
                         "rule (no selection) replayed over the same "
                         "walk-forward test windows; the pre-registered "
                         "R4-F rule (KEEP iff Round-2 rule AND t >= 3.21 "
                         "at K=75) applies to these rows"),
                "rows": combos,
            },
            "benchmark_full_period_metrics": metrics.compute_all(bench_full),
            "top_full_period_variant": {"params": top["params"],
                                        "metrics": top["metrics"],
                                        "ledger_run": run_path.name},
            "verdict": verdict,
            "verdict_k75": {
                "note": ("REGISTERED verdict at K=75 (pre-registered R4-F "
                         "rule; KILL-SIG at t <= -3.21 per R4-A's mirrored "
                         "bar)"),
                "k": k_registered,
                "min_tstat": bar_k75,
                "tstat": _clean(t),
                "significant_at_k75": significant,
                "verdict": verdict_k75,
            },
            "promotion_grade": {
                "note": ("lane-local ORDER 007 bar on the stitched OOS "
                         "Sharpe delta, Bonferroni K = 5 variants this "
                         "lane's grid — INFORMATIONAL ONLY (the registered "
                         "bar for this slice is K=75); promotion is CLOSED "
                         "post-holdout (nothing here is a finding)"),
                **grade,
            },
        }
        out = SWEEP_DIR / f"{FAMILY}__{ticker}.json"
        out.write_text(json.dumps(sweep_record, indent=2, sort_keys=True) + "\n")
        lane_rows.append({
            "instrument": ticker,
            "oos_sharpe": _clean(oos_sharpe),
            "benchmark_oos_sharpe": _clean(bench_sharpe),
            "tstat": _clean(t),
            "verdict": verdict,
            "significant_at_k75": significant,
            "verdict_k75": verdict_k75,
            "file": out.name,
        })
        print(f"{ticker} {FAMILY}: oos_sharpe={oos_sharpe:.3f} "
              f"bench={bench_sharpe:.3f} t={t:.2f} "
              f"(lane bar {grade['min_tstat']:.2f}, K75 bar {bar_k75:.2f}) "
              f"{verdict} / K75 {verdict_k75} -> {out.name}")

    runtime_s = time.monotonic() - t0

    # Rollup — the K=75 accounting lives here, first-class.
    n_keep = sum(1 for r in lane_rows if r["verdict"].startswith("KEEP"))
    n_kill_sig = sum(1 for r in lane_rows if r["verdict_k75"]
                     == promotion.SWEEP_KILL_SIG)
    n_sig = sum(1 for r in lane_rows if r["significant_at_k75"])
    combo_keep = sum(1 for c in combo_rows
                     if c["verdict_r4f_registered"] == promotion.SWEEP_KEEP)
    combo_kill_sig = sum(1 for c in combo_rows
                         if c["verdict_r4f_registered"]
                         == promotion.SWEEP_KILL_SIG)
    combo_sig = sum(1 for c in combo_rows if c["significant_at_k75"])
    combo_ts = [c["tstat"] for c in combo_rows if c["tstat"] is not None]
    best_combo = max(combo_rows,
                     key=lambda c: (c["tstat"] if c["tstat"] is not None
                                    else float("-inf")))
    worst_combo = min(combo_rows,
                      key=lambda c: (c["tstat"] if c["tstat"] is not None
                                     else float("inf")))
    summary = {
        "schema_version": 1,
        "sweep": "r4-seasonality",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": ledger.git_sha(),
        "pre_registration": "docs/research-round-4-plan.md § R4-F",
        "order": "ORDER 012 night-run (control/inbox.md)",
        "post_holdout_dev_only": True,
        "hypothesis": ("null after correction — no day×ticker combo clears "
                       "the Bonferroni bar at the honestly-counted K"),
        "k_registered": k_registered,
        "min_tstat_k75": bar_k75,
        "lane_grid": len(variants),
        "instruments": list(sweeps.R4_SEASONALITY_INSTRUMENTS),
        "registered_configs": lane_configs,
        "program_variants_tried": program_cumulative,
        "runtime_seconds": round(runtime_s, 1),
        "lanes": {
            "note": ("per-ticker walk-forward over the 5-variant lane grid, "
                     "graded by the standard Round-2 rule (dev-candidate "
                     "semantics) with lane-local informational t at K=5 and "
                     "the registered K=75 verdict"),
            "n": len(lane_rows),
            "keep_standard_rule": n_keep,
            "kill": len(lane_rows) - n_keep,
            "kill_sig_at_k75": n_kill_sig,
            "significant_at_k75": n_sig,
            "rows": lane_rows,
        },
        "combos": {
            "note": ("the 75 registered day×ticker combos K counts — fixed "
                     "single-weekday rules over the same walk-forward "
                     "windows; pre-registered R4-F rule applied"),
            "n": len(combo_rows),
            "keep_r4f_registered": combo_keep,
            "kill_sig_at_k75": combo_kill_sig,
            "significant_at_k75": combo_sig,
            "keep_standard_rule": sum(1 for c in combo_rows
                                      if c["keep_standard_rule"]),
            "best_tstat": _clean(max(combo_ts)) if combo_ts else None,
            "worst_tstat": _clean(min(combo_ts)) if combo_ts else None,
            "best_combo": {k: best_combo[k] for k in
                           ("instrument", "weekday", "weekday_name", "tstat")},
            "worst_combo": {k: worst_combo[k] for k in
                            ("instrument", "weekday", "weekday_name", "tstat")},
            "rows": combo_rows,
        },
    }
    (SWEEP_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n")

    print(f"\nlanes: {n_keep} KEEP (standard rule) / "
          f"{len(lane_rows) - n_keep} KILL / {n_kill_sig} KILL-SIG at K=75; "
          f"significant_at_k75: {n_sig}")
    print(f"combos (K={k_registered}): {combo_keep} KEEP / "
          f"{len(combo_rows) - combo_keep - combo_kill_sig} KILL / "
          f"{combo_kill_sig} KILL-SIG; significant_at_k75: {combo_sig}; "
          f"best t = {max(combo_ts):.3f} vs bar {bar_k75:.3f} "
          f"({best_combo['instrument']} {best_combo['weekday_name']}); "
          f"worst t = {min(combo_ts):.3f} "
          f"({worst_combo['instrument']} {worst_combo['weekday_name']})")
    print(f"runtime: {runtime_s:.1f}s")
    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
