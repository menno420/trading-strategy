#!/usr/bin/env python3
"""P2 validation — frozen P1 candidates on unconsumed pre-holdout data.

Lane: p2-validation (QUEUE item 4). Protocol (binding, see
docs/p2-validation-results.md):

* Validation data must lie OUTSIDE each candidate's P1 selection window
  AND strictly before HOLDOUT_START (2025-01-09). P1 consumed each
  candidate's ENTIRE dev range (walk-forward train+OOS both count as
  consumed).
* Parameters are FROZEN. P1 recorded no single deployed vector (the
  candidates were per-split re-selection processes), so the frozen vector
  is the one recorded "selected" vector per candidate: the
  ``top_full_period_variant`` in
  ``experiments/sweeps/<sweep>/<family>__<ticker>.json``. Zero re-tuning,
  zero new variants; ``variants_tried = 1`` per P2 run.
* Verdict (amended by ORDER 007, 2026-07-10 — the original rule promoted on
  any positive Sharpe delta with no statistics at all): promotion now goes
  through ``trading_lab.promotion.grade_promotion`` — PROMOTED-TO-FINDING
  requires strategy Sharpe > buy-and-hold Sharpe on the P2 window (net of
  engine default costs, 5+1 bps/side, t+1-open fills) AND a Sharpe-delta
  t-stat clearing the significance bar (Lo 2002 SE, Bonferroni-adjusted for
  variants tried); a positive-but-insignificant delta is RULE-PASS
  (candidate, never a finding); no beat is KILLED. Candidates with zero
  unconsumed pre-holdout bars are UNVALIDATABLE-PRE-HOLDOUT (the data math
  lives in the results doc).

Only 2 of the 14 open candidates have an unconsumed pre-holdout window:
AAPL-donchian and GOOGL-pullback (P1 consumed from 2010-01-04 only because
the committed daily cache starts there; earlier daily history exists).
Their P2 windows PRE-DATE the P1 selection window — this tests regime
generalization, not forward deployability.

Pre-2010 extension data lives in ``data/p2ext/daily/`` (fetched via the
repo's own proxy-safe fetch path; the committed ``data/daily/`` cache is
untouched). This script re-fetches only if the files are missing.

Usage: python3 scripts/run_p2_validation.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, data, ledger, metrics, promotion  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402

P2EXT_DIR = config.REPO_ROOT / "data" / "p2ext"
SWEEPS_DIR = config.EXPERIMENTS_DIR / "sweeps"

# (ticker, fetch_start): fetch end 2012-01-01 keeps a 2010–2011 overlap with
# the committed cache for the adjustment-consistency check while staying far
# from the holdout boundary.
FETCH_SPECS = [("AAPL", "1980-01-01"), ("GOOGL", "2004-01-01")]
FETCH_END = "2012-01-01"

# The two validatable candidates. P2 window end is EXCLUSIVE (load_ohlcv
# slices ``index < end``): 2010-01-04 is the first consumed bar, so the P2
# window is every available bar strictly before it.
P2_RUNS = [
    {
        "family": "donchian",
        "ticker": "AAPL",
        "sweep": "p1-trend-following-daily",
        "window_end": "2010-01-04",
    },
    {
        "family": "pullback",
        "ticker": "GOOGL",
        "sweep": "p1-mean-reversion-daily",
        "window_end": "2010-01-04",
    },
]


def ensure_p2ext() -> None:
    """Fetch the pre-2010 extension files if missing (never overwrites)."""
    for ticker, start in FETCH_SPECS:
        path = data.cache_path(ticker, "daily", P2EXT_DIR)
        if path.exists():
            continue
        df = data.fetch_ohlcv(ticker, "daily", start=start, end=FETCH_END)
        data.save_cache(df, ticker, "daily", data_dir=P2EXT_DIR)
        print(f"fetched {ticker}: {len(df)} bars {df.index[0]} -> {df.index[-1]}")


def adjustment_discrepancy(ticker: str) -> dict:
    """Max relative close discrepancy vs committed cache on the 2010–2011 overlap."""
    ext = load_ohlcv(ticker, "daily", data_dir=P2EXT_DIR)
    ref = load_ohlcv(ticker, "daily")
    overlap = ext.index.intersection(ref.index)
    rel = ((ext.loc[overlap, "close"] - ref.loc[overlap, "close"]).abs()
           / ref.loc[overlap, "close"])
    return {"ticker": ticker, "overlap_bars": int(len(overlap)),
            "overlap_start": str(overlap[0]), "overlap_end": str(overlap[-1]),
            "max_rel_close_discrepancy": float(rel.max()),
            "mean_rel_close_discrepancy": float(rel.mean())}


def frozen_params(sweep: str, family: str, ticker: str) -> dict:
    rec = json.loads((SWEEPS_DIR / sweep / f"{family}__{ticker}.json").read_text())
    return rec["top_full_period_variant"]["params"]


def run_candidate(spec: dict) -> dict:
    family, ticker = spec["family"], spec["ticker"]
    params = frozen_params(spec["sweep"], family, ticker)
    ohlcv = load_ohlcv(ticker, "daily", data_dir=P2EXT_DIR, end=spec["window_end"])
    positions = STRATEGIES[family](ohlcv, **params)
    result = run_backtest(ohlcv, positions,
                          slippage_bps=config.DEFAULT_SLIPPAGE_BPS,
                          commission_bps=config.DEFAULT_COMMISSION_BPS,
                          timeframe="daily")
    benchmark = buy_and_hold_result(ohlcv,
                                    slippage_bps=config.DEFAULT_SLIPPAGE_BPS,
                                    commission_bps=config.DEFAULT_COMMISSION_BPS,
                                    timeframe="daily")
    notes = (f"P2 validation of P1 candidate {family}__{ticker}; params frozen "
             f"from experiments/sweeps/{spec['sweep']}/{family}__{ticker}.json "
             "(top_full_period_variant); window pre-dates the P1 selection "
             "window (regime-generalization test); data from data/p2ext/daily/.")
    record = ledger.build_record(strategy=family, params=params,
                                 instrument=ticker, timeframe="daily",
                                 ohlcv=ohlcv, result=result,
                                 benchmark=benchmark, variants_tried=1,
                                 notes=notes)
    run_path = ledger.write_run(record)
    m, b = metrics.compute_all(result), metrics.compute_all(benchmark)
    # ORDER 007 promotion rule: beat B&H net of costs AND clear the
    # significance bar. variants_tried=1 here matches the ledger row (the P2
    # run itself froze one vector, zero re-tuning); the P1 lane burden behind
    # each candidate (92-177 configs) would only RAISE the bar, so a K=1
    # verdict of RULE-PASS/KILLED is already final.
    grade = promotion.grade_promotion(
        strategy_sharpe=m["sharpe"], benchmark_sharpe=b["sharpe"],
        n_periods=int(len(ohlcv)), timeframe="daily", variants_tried=1)
    return {"family": family, "ticker": ticker, "params": params,
            "window": [str(ohlcv.index[0]), str(ohlcv.index[-1])],
            "n_bars": int(len(ohlcv)), "strategy_metrics": m,
            "benchmark_metrics": b, "verdict": grade["verdict"],
            "significance": grade,
            "run_file": str(run_path.relative_to(config.REPO_ROOT))}


def main() -> None:
    ensure_p2ext()
    out = {"discrepancy_checks": [adjustment_discrepancy(t) for t, _ in FETCH_SPECS],
           "runs": [run_candidate(spec) for spec in P2_RUNS]}
    ledger.rebuild_index()
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
