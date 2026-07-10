#!/usr/bin/env python3
"""Round 2 slice R3 — `xsec_momentum` × 9-instrument basket × daily.

POST-HOLDOUT, DEV-ONLY (docs/research-round-2.md — BINDING pre-registration,
merged before any Round 2 number existed). Promotion is closed: nothing this
script produces can be an out-of-sample claim; KEEPs are dev-candidates only.

Family (§3c): first PORTFOLIO-level lane. One strategy over all 9 cached
daily instruments as a single portfolio: rank by trailing total return over
lookback L, hold the top-k equal-weight, rebalance every 21 bars (frozen,
not swept). Grid frozen at L ∈ {63, 126, 252} × k ∈ {2, 3} → 6 registered
configs (portfolio lane: configs are grid points, NOT × instruments).
Round-2 lane cumulative after this slice: 48 (R1) + 24 (R2) + 6 = 78;
program cumulative: 590 + 78 = 668.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (bars
>= 2025-01-09 excluded), aligned on the instruments' COMMON date index
(§3c). Costs: engine defaults, 5 bps slippage + 1 bp commission per side,
charged on every rebalance trade. Execution: decision at bar t fills at
bar t+1 open. Benchmark (§5): equal-weight buy & hold of the 9-instrument
basket, same window, same costs.

This script produces ONE portfolio sweep file (§7):

1. **Per-config full-dev-period backtests** for every grid point —
   bookkeeping rows, NOT findings (single-split in-sample).
2. **A per-config walk-forward evaluation** (train 1008 bars ≈ 4y, test
   252 bars ≈ 1y, contiguous test windows, identical split scheme applied
   to the aligned common index). Each config is one FIXED portfolio rule —
   there is nothing to fit per split — so its stitched OOS result is the
   rule evaluated on the stitched test windows; that is the §6 decision
   number per config. KEEP/KILL per §6: KEEP as dev-candidate iff stitched
   OOS Sharpe > benchmark (basket B&H) OOS Sharpe AND > 0; ties/ambiguity
   KILL.
3. **A select-on-train walk-forward over the 6-config grid** — bookkeeping
   only, mirroring the prior lanes' machinery; it is NOT a registered
   config and carries NO verdict.
4. **One ledger run file** for the top full-period config (instrument
   ``XSEC-9``), so the lane shows up in ``experiments/index.jsonl``.

Usage: python3 scripts/run_r2_xsec_momentum.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.portfolio import (align_common_index,  # noqa: E402
                                   basket_buy_and_hold_result,
                                   portfolio_metrics, portfolio_walk_forward,
                                   run_portfolio_backtest)
from trading_lab.strategies import PORTFOLIO_STRATEGIES  # noqa: E402

TIMEFRAME = "daily"
TRAIN_SIZE = 1008  # ~4 trading years (pre-registration §5)
TEST_SIZE = 252    # ~1 trading year; step defaults to TEST_SIZE (contiguous)

FAMILY = "xsec_momentum"
BASKET = "XSEC-9"  # portfolio pseudo-instrument label for ledger/sweep rows
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / "r2-xsec_momentum"

# Round-2 lane configs already spent before this slice (R1 #47 + R2 #48).
ROUND2_PRIOR_CONFIGS = 48 + 24
PROGRAM_PRIOR_CONFIGS = 590  # pre-Round-2 program burden (pre-reg §2)


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


def main() -> None:
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    variants = sweeps.r2_xsec_variants(FAMILY)
    family_configs = sweeps.r2_xsec_total_configs()
    lane_cumulative = ROUND2_PRIOR_CONFIGS + family_configs
    program_cumulative = PROGRAM_PRIOR_CONFIGS + lane_cumulative
    assert len(variants) == 6 and family_configs == 6, \
        "grid drifted from the pre-registration (docs/research-round-2.md §3c)"
    print(f"grid: {len(variants)} portfolio configs over "
          f"{len(sweeps.R2_XSEC_INSTRUMENTS)} instruments "
          f"(Round-2 lane cumulative {lane_cumulative}, "
          f"program cumulative {program_cumulative})")
    weight_fn = PORTFOLIO_STRATEGIES[FAMILY]
    rebal = sweeps.R2_XSEC_REBALANCE_EVERY

    def targets_for(closes, params):
        return weight_fn(closes, rebalance_every=rebal, **params)

    # Data rail + alignment (pre-reg §1, §3c): default holdout-excluding
    # loader only; intersect the 9 date indexes (BTC-USD bars on days any
    # equity is closed are dropped).
    frames = {t: load_ohlcv(t, TIMEFRAME)
              for t in sweeps.R2_XSEC_INSTRUMENTS}
    opens, closes = align_common_index(frames)
    print(f"aligned common index: {len(opens)} bars "
          f"{opens.index[0].date()} -> {opens.index[-1].date()}")

    # 1) full-dev-period backtest per config (bookkeeping rows)
    rows = []
    for params in variants:
        res = run_portfolio_backtest(opens, closes,
                                     targets_for(closes, params),
                                     timeframe=TIMEFRAME)
        rows.append({"params": params, "metrics": portfolio_metrics(res)})
    bench_full = basket_buy_and_hold_result(opens, closes,
                                            timeframe=TIMEFRAME)

    # 2) per-config walk-forward OOS — the §6 decision numbers (dev-only).
    # A config is one fixed portfolio rule (no per-split fitting), so the
    # grid passed to the walk-forward machinery is the single config.
    per_config = []
    oos_slice_bounds = None
    for params in variants:
        wf = portfolio_walk_forward(opens, closes,
                                    lambda c, **p: targets_for(c, p),
                                    [params], train_size=TRAIN_SIZE,
                                    test_size=TEST_SIZE, timeframe=TIMEFRAME)
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
    bench_oos = basket_buy_and_hold_result(opens.iloc[a:b], closes.iloc[a:b],
                                           timeframe=TIMEFRAME)
    bench_oos_metrics = portfolio_metrics(bench_oos)

    # 3) select-on-train walk-forward over the whole grid — bookkeeping
    # only (prior lanes' machinery); NOT a registered config, NO verdict.
    wf_sel = portfolio_walk_forward(opens, closes,
                                    lambda c, **p: targets_for(c, p),
                                    variants, train_size=TRAIN_SIZE,
                                    test_size=TEST_SIZE, timeframe=TIMEFRAME)

    # 4) ledger run for the top full-period config (in-sample bookkeeping)
    top = max(rows, key=lambda r: (r["metrics"]["sharpe"]
                                   if r["metrics"]["sharpe"] is not None
                                   else float("-inf")))
    top_res = run_portfolio_backtest(opens, closes,
                                     targets_for(closes, top["params"]),
                                     timeframe=TIMEFRAME)
    cfg = {
        "strategy": FAMILY, "params": top["params"], "instrument": BASKET,
        "timeframe": TIMEFRAME,
        "slippage_bps": config.DEFAULT_SLIPPAGE_BPS,
        "commission_bps": config.DEFAULT_COMMISSION_BPS,
        "data_start": str(opens.index[0]), "data_end": str(opens.index[-1]),
    }
    record = {
        "schema_version": ledger.SCHEMA_VERSION,
        "run_id": None,  # filled by write_run
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": ledger.git_sha(),
        "config_hash": ledger.config_hash(cfg),
        "strategy": FAMILY,
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
        "notes": (f"Round 2 slice R3 (post-holdout DEV-ONLY, promotion "
                  f"closed — docs/research-round-2.md): top full-dev-period "
                  f"config of {len(variants)} tried (post-hoc selection — "
                  f"in-sample; the per-config walk-forward OOS numbers live "
                  f"in experiments/sweeps/r2-xsec_momentum/"
                  f"{FAMILY}__{BASKET}.json). Portfolio lane: instrument "
                  f"{BASKET} = equal-weight top-k basket over "
                  f"{len(sweeps.R2_XSEC_INSTRUMENTS)} instruments; "
                  f"benchmark = equal-weight basket B&H, same costs; "
                  f"win_rate is null (single-book episode metric undefined "
                  f"for a cross-sectional portfolio)."),
    }
    run_path = ledger.write_run(record)

    sweep_record = {
        "schema_version": 1,
        "sweep": "r2-xsec_momentum",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": ledger.git_sha(),
        "family": FAMILY,
        "instrument": BASKET,
        "instruments": list(sweeps.R2_XSEC_INSTRUMENTS),
        "timeframe": TIMEFRAME,
        "preregistration": "docs/research-round-2.md",
        "post_holdout_dev_only": True,
        "alignment": ("common date index = intersection of the 9 "
                      "instruments' dev-rail date indexes (BTC-USD bars on "
                      "days any equity market is closed are dropped); "
                      "lookback L counts aligned bars"),
        "rebalance_every_bars": rebal,
        "data_start": str(opens.index[0]),
        "data_end": str(opens.index[-1]),
        "n_bars": int(len(opens)),
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
            "n_splits": per_config[0]["n_splits"],
            "oos_start": str(opens.index[a]),
            "oos_end": str(opens.index[b - 1]),
            "note": ("each config is one FIXED portfolio rule — no "
                     "per-split fitting — so its stitched OOS is the rule "
                     "evaluated on the identical split scheme's test "
                     "windows (pre-reg §5, verdicts per config per §6)"),
            "benchmark_oos_metrics": bench_oos_metrics,
            "per_config": per_config,
        },
        "selection_walk_forward": {
            "note": ("select-on-train over the 6-config grid, mirroring "
                     "prior lanes' machinery — BOOKKEEPING ONLY: not a "
                     "registered config, carries no verdict"),
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
    out = SWEEP_DIR / f"{FAMILY}__{BASKET}.json"
    out.write_text(json.dumps(sweep_record, indent=2, sort_keys=True) + "\n")

    bench_sharpe = bench_oos_metrics["sharpe"]
    for entry in per_config:
        oos_sharpe = entry["oos_metrics"]["sharpe"]
        verdict = ("KEEP (dev-candidate only)"
                   if oos_sharpe is not None and bench_sharpe is not None
                   and oos_sharpe > bench_sharpe and oos_sharpe > 0
                   else "KILL")
        p = entry["params"]
        print(f"L={p['L']:>3} k={p['k']}: oos_sharpe={oos_sharpe:.3f} "
              f"bench={bench_sharpe:.3f} {verdict}")
    print(f"selection stitch (bookkeeping only): "
          f"oos_sharpe={sweep_record['selection_walk_forward']['oos_metrics']['sharpe']:.3f}")
    print(f"-> {out.name}")

    print("rebuilding index...")
    print(ledger.rebuild_index())


if __name__ == "__main__":
    main()
