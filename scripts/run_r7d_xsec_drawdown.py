#!/usr/bin/env python3
"""Round 7D slice R7-D — cross-sectional DRAWDOWN-ranking lane on the
14-instrument basket (`xsec_drawdown`) × daily.

POST-HOLDOUT, DEV-ONLY (owner GO 2026-07-18, executing the binding
docs/research-round-7d-plan.md). Promotion is CLOSED: nothing this script
produces can be an out-of-sample claim; KEEPs are dev-candidates only.

A PORTFOLIO-level lane, mirroring the Round-3 slice-7 xsec lane
(scripts/run_r3_xsec_expanded.py) exactly in methodology: each config is
ONE fixed portfolio rule over the whole basket — rank the aligned common
date index by DRAWDOWN DEPTH (close / trailing-L-bar close-peak − 1, ≤ 0),
hold the deepest-k equal-weight, rebalance on the frozen monthly cadence
(21 bars), long/flat, no leverage. Ranking on a drawdown STATE is
structurally distinct from the trailing point-to-point RETURN ranking of
`xsec_momentum` (long winners) / `xsec_reversal` (long losers). Basket
`XSEC-14`: the 14 daily equity/ETF instruments (frozen 8-ticker universe
minus BTC-USD, plus the six slice-3 instruments SPY/QQQ/TSLA/JPM/XOM/TLT).
Grid declared in ``trading_lab.sweeps`` BEFORE this script ran: 6
registered configs (portfolio lane: configs are grid points, NOT ×
instruments). Program burden prior to this lane: 5595; program cumulative
after: 5601.

Runtime cap (pre-registered): ≤ 900 s wall-clock for the whole slice. The
cap is checked before each family; a would-be overrun STOPS the slice,
records the partial state and reports CAP-HIT — no silent truncation.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded), aligned on the instruments' COMMON date index —
the SAME short-history handling the Round-2 lane used for BTC-USD's 2014
start: the intersection simply begins at the latest-starting instrument.
Here that is META (first bar 2012-05-18), not TSLA (2010-06-29) — both
truncate the common window below the other 12 instruments' 2010-01-04
history, and META truncates furthest. Recorded honestly in every summary.
Costs: engine defaults, 5 bps slippage + 1 bp commission per side, charged
on every rebalance trade. Execution: decision at bar t fills at bar t+1
open. Benchmark: equal-weight buy & hold of the 14-instrument basket,
same window, same costs (the Round-2 lane's benchmark construction).

Per family this script produces ONE portfolio sweep file (same shape as
the Round-2 R3 lane):

1. **Per-config full-dev-period backtests** for every grid point —
   bookkeeping rows, NOT findings (single-split in-sample).
2. **A per-config walk-forward evaluation** (train 1008 bars ≈ 4y, test
   252 bars ≈ 1y, contiguous test windows, identical split scheme applied
   to the aligned common index). Each config is one FIXED portfolio rule —
   nothing to fit per split — so its stitched OOS result is the §6
   decision number. KEEP/KILL per the Round-2 rule: KEEP as dev-candidate
   iff stitched OOS Sharpe > benchmark (basket B&H) OOS Sharpe AND > 0;
   ties/ambiguity KILL. The ORDER 007 promotion-bar arithmetic
   (``trading_lab.promotion.grade_promotion``, Bonferroni K = 6 variants
   per family) is recorded alongside — informational only, promotion
   closed.
3. **A select-on-train walk-forward over the family's grid** —
   bookkeeping only, mirroring the prior lanes' machinery; NOT a
   registered config, NO verdict.
4. **One ledger run file** for the family's top full-period config
   (instrument ``XSEC-14``), so the lane shows up in
   ``experiments/index.jsonl``.

Usage: python3 scripts/run_r7d_xsec_drawdown.py
"""

import json
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import (config, ledger, metrics,  # noqa: E402
                         promotion, selection_gate, sweeps)
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.portfolio import (align_common_index,  # noqa: E402
                                   basket_buy_and_hold_result,
                                   portfolio_metrics, portfolio_walk_forward,
                                   run_portfolio_backtest)
from trading_lab.strategies import PORTFOLIO_STRATEGIES  # noqa: E402

TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years (Round-2 R3 lane scheme, reused)
TEST_SIZE = 252    # ~1 trading year; step defaults to TEST_SIZE (contiguous)

BASKET = "XSEC-14"  # portfolio pseudo-instrument label (XSEC-9 convention)
SLICE = "r7d-xsec-drawdown"
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SLICE
CAP_SECONDS = 900  # pre-registered: <= 15 min wall-clock for the slice

# Program burden prior to this lane: 5595 registered configs (Round 7C
# closed the program at 5595; see docs/current-state.md).
PROGRAM_PRIOR_CONFIGS = 5595


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


def split_rows(wf: dict) -> list[dict]:
    return [{
        "train": [s["split"].train_start, s["split"].train_end],
        "test": [s["split"].test_start, s["split"].test_end],
        "params": s["params"],
        "train_score": (None if s["train_score"] != s["train_score"]
                        else s["train_score"]),
        "test_sharpe": (None if s["test_sharpe"] != s["test_sharpe"]
                        else s["test_sharpe"]),
    } for s in wf["splits"]]


#: Honest note stamped on every lane's gate block: this is a
#: 1-config-per-lane portfolio slice, so the standing gate is DEGENERATE.
_GATE_NOTE = (
    "standing selection-fair gate [D-0002] (docs/selection-fair-gate.md), "
    "standing rule 1 of docs/research-round-7d-plan.md — run + recorded on "
    "EVERY Round-7D lane, folded through selection_gate.apply_gate BEFORE the "
    "verdict is written. 1-config-per-lane PORTFOLIO slice: this lane runs "
    "portfolio_walk_forward with a ONE-config grid, so there is NO within-lane "
    "variant selection — fixed_sharpe == searched_sharpe (the lane's own "
    "stitched OOS Sharpe) and selection_gap == 0.0 BY CONSTRUCTION. The gate "
    "is therefore degenerate here and coincides with the §6 KEEP rule; it is "
    "exercised to honor standing rule 1 and would bite a future MULTI-variant "
    "portfolio lane. Doubles as the R5-D fixed-config row (standing rule 2) — "
    "selection_gap informational, no registered threshold; report-only "
    "(R4-B precedent), not ledgered. run_selection_gate is single-instrument "
    "shaped (ohlcv+strategy) so it cannot grade a portfolio lane; the "
    "decision is selection_gate.gate_decision and the block mirrors the "
    "module's own result shape and reuses its constants."
)


def selection_gate_block(*, fixed_sharpe, bench_sharpe, per_split,
                         n_periods) -> dict:
    """Build the selection-fair standing-gate result block for one portfolio
    lane, in the shape :func:`selection_gate.run_selection_gate` produces
    (so :func:`selection_gate.apply_gate` folds it and rollups read it).

    KEY FACT (encoded honestly): this is a 1-config-per-lane portfolio slice
    — the lane's walk-forward grid is ONE config, so there is no within-lane
    selection to replay. Hence ``fixed_sharpe == searched_sharpe`` (the
    lane's own stitched OOS Sharpe) and ``selection_gap == 0.0`` by
    construction. The gate decision itself is the module's pure rule
    (:func:`selection_gate.gate_decision`); the ``reason_class`` follows the
    module taxonomy with the module's precedence (non-positive beats
    underperform); UNGRADEABLE_NAN only if a Sharpe is missing/NaN.
    """
    sg = selection_gate
    searched_sharpe = fixed_sharpe  # no within-lane selection to replay
    selection_gap = (None if (fixed_sharpe is None or searched_sharpe is None)
                     else searched_sharpe - fixed_sharpe)  # 0.0 by construction
    # Fixed arm == searched arm: mirror the single-name lane's per-split rows
    # ({params, test, test_sharpe}) so the R5-D fixed-config row is legible.
    fixed_per_split = [{"params": r["params"], "test": r["test"],
                        "test_sharpe": r["test_sharpe"]} for r in per_split]
    common = {"fixed_sharpe": fixed_sharpe, "bench_sharpe": bench_sharpe,
              "searched_sharpe": searched_sharpe,
              "selection_gap": selection_gap, "n_periods": n_periods,
              "fixed_per_split": fixed_per_split, "note": _GATE_NOTE}
    if fixed_sharpe is None or bench_sharpe is None:
        return {"gate": sg.GATE_FAIL,
                "reason": ("ungradeable: fixed or benchmark stitched Sharpe is "
                           "NaN (degenerate returns) — NaN never passes"),
                "reason_class": sg.REASON_UNGRADEABLE_NAN, **common}
    if sg.gate_decision(fixed_sharpe=fixed_sharpe, bench_sharpe=bench_sharpe):
        return {"gate": sg.GATE_PASS,
                "reason": (f"fixed-config replay beats same-window B&H "
                           f"({fixed_sharpe:.6f} > {bench_sharpe:.6f}) and is "
                           f"positive"),
                "reason_class": sg.REASON_PASS, **common}
    reason_class = (sg.REASON_FAIL_NONPOSITIVE if fixed_sharpe <= 0.0
                    else sg.REASON_FAIL_UNDERPERFORM)
    return {"gate": sg.GATE_FAIL,
            "reason": (f"fixed-config replay does not beat same-window B&H "
                       f"with a positive Sharpe (fixed {fixed_sharpe:.6f}, "
                       f"bench {bench_sharpe:.6f}) — the searched edge does "
                       f"not survive selection-free"),
            "reason_class": reason_class, **common}


def main() -> None:
    t0 = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    grid_sizes = sweeps.r7d_xsec_drawdown_variants_per_family()
    lane_configs = sweeps.r7d_total_configs()
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_configs
    assert grid_sizes == {"xsec_drawdown": 6} and lane_configs == 6, \
        "grid drifted from the declared Round-7D slice (trading_lab.sweeps)"
    print(f"grids: {grid_sizes} over "
          f"{len(sweeps.R7D_INSTRUMENTS)} instruments = "
          f"{lane_configs} registered configs "
          f"(program cumulative {program_cumulative}); cap {CAP_SECONDS} s")

    # Data rail + alignment (Round-3 xsec handling, reused): default
    # holdout-excluding loader only; intersect the 14 date indexes. The
    # common window starts at the LATEST-starting instrument — META
    # 2012-05-18 (TSLA 2010-06-29 is the second-latest); the other 12
    # reach back to 2010-01-04. Same convention as the Round-2 lane's
    # BTC-USD (2014 start) truncation. Recorded in every summary.
    frames = {}
    for t in sweeps.R7D_INSTRUMENTS:
        ohlcv = load_ohlcv(t, TIMEFRAME)  # holdout excluded by default
        assert str(ohlcv.index[-1])[:10] <= "2025-01-08", \
            f"{t}: dev rail violated (data_end {ohlcv.index[-1]})"
        frames[t] = ohlcv
    starts = {t: str(f.index[0].date()) for t, f in frames.items()}
    latest_start = max(starts.items(), key=lambda kv: kv[1])
    opens, closes = align_common_index(frames)
    assert str(opens.index[0].date()) == latest_start[1], \
        "common index must start at the latest-starting instrument"
    print(f"aligned common index: {len(opens)} bars "
          f"{opens.index[0].date()} -> {opens.index[-1].date()} "
          f"(truncated by {latest_start[0]}, first bar {latest_start[1]})")

    verdict_lines = []
    cap_hit, skipped = False, []
    for family in sweeps.R7D_XSEC_DRAWDOWN_FAMILIES:
        elapsed = time.monotonic() - t0
        if elapsed >= CAP_SECONDS:
            cap_hit = True
            skipped.append(family)
            print(f"CAP-HIT: elapsed {elapsed:.1f} s >= cap {CAP_SECONDS} s "
                  f"before family {family} — STOPPING, no silent truncation")
            break
        variants = sweeps.r7d_xsec_drawdown_variants(family)
        weight_fn = PORTFOLIO_STRATEGIES[family]
        rebal = sweeps.R7D_XSEC_DRAWDOWN_REBALANCE_EVERY[family]

        def targets_for(cl, params, _fn=weight_fn, _rebal=rebal):
            return _fn(cl, rebalance_every=_rebal, **params)

        # 1) full-dev-period backtest per config (bookkeeping rows)
        rows = []
        for params in variants:
            res = run_portfolio_backtest(opens, closes,
                                         targets_for(closes, params),
                                         timeframe=TIMEFRAME)
            rows.append({"params": params,
                         "metrics": portfolio_metrics(res)})
        bench_full = basket_buy_and_hold_result(opens, closes,
                                                timeframe=TIMEFRAME)

        # 2) per-config walk-forward OOS — the decision numbers (dev-only).
        per_config = []
        oos_slice_bounds = None
        for params in variants:
            wf = portfolio_walk_forward(opens, closes,
                                        lambda c, **p: targets_for(c, p),
                                        [params], train_size=TRAIN_SIZE,
                                        test_size=TEST_SIZE,
                                        timeframe=TIMEFRAME)
            first, last = wf["splits"][0]["split"], wf["splits"][-1]["split"]
            oos_slice_bounds = (first.test_start, last.test_end)
            per_config.append({
                "params": params,
                "oos_metrics": series_metrics(wf["oos_returns"],
                                              wf["oos_equity"]),
                "n_splits": len(wf["splits"]),
                "per_split": split_rows(wf),
            })

        a, b = oos_slice_bounds
        bench_oos = basket_buy_and_hold_result(opens.iloc[a:b],
                                               closes.iloc[a:b],
                                               timeframe=TIMEFRAME)
        bench_oos_metrics = portfolio_metrics(bench_oos)

        # 3) select-on-train walk-forward over the family grid —
        # bookkeeping only; NOT a registered config, NO verdict.
        wf_sel = portfolio_walk_forward(opens, closes,
                                        lambda c, **p: targets_for(c, p),
                                        variants, train_size=TRAIN_SIZE,
                                        test_size=TEST_SIZE,
                                        timeframe=TIMEFRAME)

        # 4) ledger run for the top full-period config (in-sample
        # bookkeeping)
        top = max(rows, key=lambda r: (r["metrics"]["sharpe"]
                                       if r["metrics"]["sharpe"] is not None
                                       else float("-inf")))
        top_res = run_portfolio_backtest(opens, closes,
                                         targets_for(closes, top["params"]),
                                         timeframe=TIMEFRAME)
        cfg = {
            "strategy": family, "params": top["params"],
            "instrument": BASKET, "timeframe": TIMEFRAME,
            "slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
            "commission_bps": config.DEFAULT_COMMISSION_BPS,
            "data_start": str(opens.index[0]),
            "data_end": str(opens.index[-1]),
        }
        record = {
            "schema_version": ledger.SCHEMA_VERSION,
            "run_id": None,  # filled by write_run
            "created_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "config_hash": ledger.config_hash(cfg),
            "strategy": family,
            "params": top["params"],
            "instrument": BASKET,
            "timeframe": TIMEFRAME,
            "data_start": str(opens.index[0]),
            "data_end": str(opens.index[-1]),
            "n_bars": int(len(opens)),
            "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                      "commission_bps": config.DEFAULT_COMMISSION_BPS},
            "execution": "signal at bar t fills at bar t+1 open",
            "metrics": portfolio_metrics(top_res),
            "benchmark_metrics": portfolio_metrics(bench_full),
            "variants_tried": len(variants),
            "notes": (f"Round 7D slice R7-D (post-holdout DEV-ONLY, promotion "
                      f"CLOSED — owner GO 2026-07-18): top full-dev-period "
                      f"config of {len(variants)} tried this family "
                      f"({lane_configs} the lane) — post-hoc selection, "
                      f"in-sample; the per-config walk-forward OOS numbers "
                      f"live in experiments/sweeps/{SLICE}/"
                      f"{family}__{BASKET}.json. Portfolio lane: instrument "
                      f"{BASKET} = equal-weight deepest-drawdown-k basket over "
                      f"{len(sweeps.R7D_INSTRUMENTS)} "
                      f"instruments; benchmark = equal-weight basket B&H, "
                      f"same costs; common index starts at META's first bar "
                      f"2012-05-18 (latest-starting instrument — the "
                      f"Round-3 xsec short-history convention); win_rate is "
                      f"null (single-book episode metric undefined for a "
                      f"cross-sectional portfolio)."),
        }
        run_path = ledger.write_run(record)

        # Verdicts: Round-2 §6 rule; ORDER 007 t-stat informational only.
        bench_sharpe = bench_oos_metrics["sharpe"]
        config_verdicts = []
        for entry in per_config:
            oos_sharpe = entry["oos_metrics"]["sharpe"]
            keep = (oos_sharpe is not None and bench_sharpe is not None
                    and oos_sharpe > bench_sharpe and oos_sharpe > 0)
            verdict_pre_gate = (promotion.VERDICT_KEEP_DEV if keep
                                else promotion.SWEEP_KILL)
            grade = promotion.grade_promotion(
                strategy_sharpe=oos_sharpe, benchmark_sharpe=bench_sharpe,
                n_periods=entry["oos_metrics"]["n_bars"],
                timeframe=TIMEFRAME, variants_tried=len(variants))
            # Standing rule 1: selection-fair gate on EVERY lane, folded
            # through apply_gate BEFORE the verdict is written (here the gate
            # only ever demotes KEEP->KILL; degenerate on this 1-config lane).
            gate_block = selection_gate_block(
                fixed_sharpe=oos_sharpe, bench_sharpe=bench_sharpe,
                per_split=entry["per_split"],
                n_periods=entry["oos_metrics"]["n_bars"])
            verdict = selection_gate.apply_gate(verdict_pre_gate, gate_block)
            entry["verdict_pre_gate"] = verdict_pre_gate
            entry["verdict"] = verdict
            entry["selection_gate"] = gate_block
            entry["promotion_grade"] = {
                "note": ("ORDER 007 bar on the stitched OOS Sharpe delta "
                         "vs the basket-B&H benchmark, Bonferroni K = "
                         "variants this family — INFORMATIONAL ONLY, "
                         "promotion is CLOSED post-holdout (nothing here "
                         "is a finding)"),
                **grade,
            }
            config_verdicts.append((entry["params"], oos_sharpe,
                                    grade["tstat"], verdict,
                                    gate_block["reason_class"]))

        sweep_record = {
            "schema_version": 1,
            "sweep": SLICE,
            "created_utc": datetime.now(timezone.utc).isoformat(
                timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": family,
            "instrument": BASKET,
            "instruments": list(sweeps.R7D_INSTRUMENTS),
            "instrument_first_bars": starts,
            "timeframe": TIMEFRAME,
            "post_holdout_dev_only": True,
            "order": "owner GO 2026-07-18 (docs/research-round-7d-plan.md)",
            "cap_seconds": CAP_SECONDS,
            "alignment": ("common date index = intersection of the 14 "
                          "instruments' dev-rail date indexes — starts at "
                          "the LATEST-starting instrument, META 2012-05-18 "
                          "(TSLA 2010-06-29 second-latest; the other 12 "
                          "reach back to 2010-01-04), the same handling "
                          "the Round-2 R3 lane used for BTC-USD's 2014 "
                          "start; lookbacks count aligned bars"),
            "rebalance_every_bars": rebal,
            "data_start": str(opens.index[0]),
            "data_end": str(opens.index[-1]),
            "n_bars": int(len(opens)),
            "costs": {"slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
                      "commission_bps": config.DEFAULT_COMMISSION_BPS},
            "execution": "signal at bar t fills at bar t+1 open",
            "variants_tried": len(variants),
            "family_variants_tried": grid_sizes[family],
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
                "n_splits": per_config[0]["n_splits"],
                "oos_start": str(opens.index[a]),
                "oos_end": str(opens.index[b - 1]),
                "note": ("each config is one FIXED portfolio rule — no "
                         "per-split fitting — so its stitched OOS is the "
                         "rule evaluated on the identical split scheme's "
                         "test windows (Round-2 R3 scheme; verdicts per "
                         "config per the Round-2 §6 rule)"),
                "benchmark_oos_metrics": bench_oos_metrics,
                "per_config": per_config,
            },
            "selection_walk_forward": {
                "note": ("select-on-train over the family's 6-config grid, "
                         "mirroring prior lanes' machinery — BOOKKEEPING "
                         "ONLY: not a registered config, carries no "
                         "verdict"),
                "variants_tried": wf_sel["variants_tried"],
                "oos_metrics": series_metrics(wf_sel["oos_returns"],
                                              wf_sel["oos_equity"]),
                "per_split": split_rows(wf_sel),
            },
            "benchmark_full_period_metrics": portfolio_metrics(bench_full),
            "top_full_period_variant": {"params": top["params"],
                                        "metrics": top["metrics"],
                                        "ledger_run": run_path.name},
        }
        out = SWEEP_DIR / f"{family}__{BASKET}.json"
        out.write_text(json.dumps(sweep_record, indent=2, sort_keys=True)
                       + "\n")

        for params, oos_sharpe, tstat, verdict, reason_class in config_verdicts:
            keyed = " ".join(f"{k}={v}" for k, v in params.items())
            print(f"{family} {keyed}: oos_sharpe={oos_sharpe:.3f} "
                  f"bench={bench_sharpe:.3f} t={tstat:.2f} {verdict} "
                  f"[gate {reason_class}]")
            verdict_lines.append((family, params, oos_sharpe, verdict,
                                  reason_class))
        print(f"{family} selection stitch (bookkeeping only): oos_sharpe="
              f"{sweep_record['selection_walk_forward']['oos_metrics']['sharpe']:.3f}")
        print(f"-> {out.name}")

    kills = sum(1 for v in verdict_lines if v[3] == "KILL")
    runtime = time.monotonic() - t0
    print(f"\nsummary: {len(verdict_lines) - kills} KEEP / {kills} KILL "
          f"of {len(verdict_lines)} configs")
    reason_rollup = Counter(v[4] for v in verdict_lines)
    ungradeable = sum(reason_rollup[c]
                      for c in selection_gate.UNGRADEABLE_CLASSES)
    alarm = "INFRASTRUCTURE ALARM" if ungradeable else "no infra alarm"
    rollup_str = ", ".join(f"{k}={reason_rollup[k]}"
                           for k in sorted(reason_rollup))
    print(f"selection-fair gate reason_class rollup: {rollup_str} "
          f"(UNGRADEABLE share {ungradeable}/{len(verdict_lines)} — {alarm})")
    print(f"runtime {runtime:.1f} s "
          f"(cap {CAP_SECONDS} s{' — CAP-HIT' if cap_hit else ' — not hit'})")
    if skipped:
        print(f"CAP-HIT: families skipped {skipped} — re-registration required")
    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
