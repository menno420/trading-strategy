#!/usr/bin/env python3
"""P4 cross-instrument transfer validation — frozen P2 subjects on foreign
instruments.

Lane: p4-transfer (QUEUE item 7). Protocol, PRE-REGISTERED before any run
was executed (see docs/p4-transfer-results.md):

* Subjects: the 13 P2 subjects — the 12 UNVALIDATABLE-PRE-HOLDOUT
  candidates plus the one PROMOTED-TO-FINDING (AAPL-donchian; the plan
  requires survivors to transfer too). GOOGL-pullback was KILLED at P2 and
  is excluded.
* Parameters are FROZEN verbatim from each subject's P1 sweep JSON
  (``top_full_period_variant`` in
  ``experiments/sweeps/<sweep>/<family>__<ticker>.json``). Zero re-tuning,
  zero new variants: ``variants_tried = 1`` per run.
* Transfer instruments: every OTHER instrument with a committed cache in
  the subject's timeframe. Daily: the other 8 of
  {AAPL, MSFT, NVDA, GOOGL, AMZN, META, GLD, SLV, BTC-USD}. Hourly: the
  other 7 UNIVERSE tickers (no BTC-USD hourly cache exists).
* Window: the FULL pre-holdout series per transfer instrument, loaded via
  ``trading_lab.data.load_ohlcv`` (holdout rail: bars >= 2025-01-09 are
  excluded; ``unlock_holdout`` is never passed). Since the params are
  frozen and the transfer instrument never participated in the subject's
  selection, the entire period is out-of-selection. Walk-forward is
  degenerate here (a single-variant grid has no per-split selection to
  do), so this full-period frozen-param protocol follows the P2 precedent
  — a deliberate, recorded deviation from a brief that said
  "walk-forward".
* Costs/execution: engine defaults (5 bps slippage + 1 bps commission per
  side, t+1-open fills), benchmark = buy-and-hold on the same series.
* PRE-REGISTERED VERDICT RULE (per subject, fixed before running): count
  the transfer instruments where strategy Sharpe > B&H Sharpe.
  TRANSFER-SUPPORTED if the count is >= 2/3 of that subject's transfer
  instruments; TRANSFER-WEAK if >= 1/3 and < 2/3; TRANSFER-FAILED if
  < 1/3. These semantics are defined by this P4 lane (the founding plan
  defines P4 in one line only). A transfer verdict NEVER promotes a
  candidate to finding — it only sharpens the prior for the sealed-holdout
  P5 test.

Outputs: one ledger row per subject x transfer instrument
(``experiments/runs/``, ``variants_tried = 1``), regenerated
``experiments/index.jsonl``, and one machine-readable per-subject summary
JSON under ``experiments/sweeps/p4-transfer/``.

Usage: python3 scripts/run_p4_transfer.py
"""

import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402

SWEEPS_DIR = config.EXPERIMENTS_DIR / "sweeps"
OUT_DIR = SWEEPS_DIR / "p4-transfer"

DAILY_INSTRUMENTS = list(config.UNIVERSE) + ["BTC-USD"]
HOURLY_INSTRUMENTS = list(config.UNIVERSE)  # no BTC-USD hourly cache exists

# The 13 P4 subjects (family, home ticker, timeframe, P1 sweep). The
# expected_params column is the pre-registered cross-check against the
# sweep JSON's top_full_period_variant; on any mismatch the sweep file
# wins and the mismatch is recorded in the summary.
SUBJECTS = [
    ("donchian", "AAPL", "daily", "p1-trend-following-daily",
     {"entry": 15, "exit": 5}),
    ("sma_crossover", "META", "daily", "p1-trend-following-daily",
     {"fast": 15, "slow": 75}),
    ("ema_crossover", "META", "daily", "p1-trend-following-daily",
     {"fast": 25, "slow": 50}),
    ("donchian", "META", "daily", "p1-trend-following-daily",
     {"entry": 55, "exit": 55}),
    ("supertrend_flip", "BTC-USD", "daily", "p1-video-strategy-daily",
     {"st_period": 14, "st_mult": 2.0, "ema_len": 200,
      "macd_fast": 12, "macd_slow": 26, "macd_signal": 9}),
    ("macd_supertrend", "BTC-USD", "daily", "p1-video-strategy-daily",
     {"st_period": 14, "st_mult": 2.0, "ema_len": 100,
      "macd_fast": 12, "macd_slow": 26, "macd_signal": 9}),
    ("rsi_mean_reversion", "META", "daily", "p1-mean-reversion-daily",
     {"period": 2, "oversold": 10, "overbought": 50}),
    ("pullback", "META", "daily", "p1-mean-reversion-daily",
     {"entry_lookback": 7, "exit_len": 7, "trend_len": 100}),
    ("sma_crossover", "GOOGL", "hourly", "p1-trend-hourly",
     {"fast": 10, "slow": 75}),
    ("ema_crossover", "GOOGL", "hourly", "p1-trend-hourly",
     {"fast": 20, "slow": 50}),
    ("donchian", "GOOGL", "hourly", "p1-trend-hourly",
     {"entry": 40, "exit": 40}),
    ("donchian", "AMZN", "hourly", "p1-trend-hourly",
     {"entry": 40, "exit": 40}),
    ("macd", "META", "hourly", "p1-trend-hourly",
     {"fast": 5, "slow": 26, "signal": 5}),
]


def frozen_params(sweep: str, family: str, ticker: str) -> dict:
    rec = json.loads((SWEEPS_DIR / sweep / f"{family}__{ticker}.json").read_text())
    return rec["top_full_period_variant"]["params"]


def verdict_for(beats: int, total: int) -> str:
    """Pre-registered rule: >=2/3 SUPPORTED, >=1/3 WEAK, else FAILED."""
    frac = Fraction(beats, total)
    if frac >= Fraction(2, 3):
        return "TRANSFER-SUPPORTED"
    if frac >= Fraction(1, 3):
        return "TRANSFER-WEAK"
    return "TRANSFER-FAILED"


def run_subject(family: str, home: str, timeframe: str, sweep: str,
                expected: dict) -> dict:
    params = frozen_params(sweep, family, home)
    params_match = params == expected
    if not params_match:
        print(f"WARNING: sweep params for {family}__{home} differ from the "
              f"pre-registered list; sweep file wins: {params} != {expected}")
    pool = DAILY_INSTRUMENTS if timeframe == "daily" else HOURLY_INSTRUMENTS
    transfers = [t for t in pool if t != home]
    rows = []
    for ticker in transfers:
        ohlcv = load_ohlcv(ticker, timeframe)
        positions = STRATEGIES[family](ohlcv, **params)
        result = run_backtest(ohlcv, positions,
                              slippage_bps=config.DEFAULT_SLIPPAGE_BPS,
                              commission_bps=config.DEFAULT_COMMISSION_BPS,
                              timeframe=timeframe)
        benchmark = buy_and_hold_result(
            ohlcv, slippage_bps=config.DEFAULT_SLIPPAGE_BPS,
            commission_bps=config.DEFAULT_COMMISSION_BPS,
            timeframe=timeframe)
        notes = (f"p4-transfer: {family} frozen from {home} P1 {sweep} "
                 f"(top_full_period_variant); transfer instrument")
        record = ledger.build_record(strategy=family, params=params,
                                     instrument=ticker, timeframe=timeframe,
                                     ohlcv=ohlcv, result=result,
                                     benchmark=benchmark, variants_tried=1,
                                     notes=notes)
        run_path = ledger.write_run(record)
        m, b = metrics.compute_all(result), metrics.compute_all(benchmark)
        rows.append({
            "instrument": ticker,
            "window": [str(ohlcv.index[0]), str(ohlcv.index[-1])],
            "n_bars": int(len(ohlcv)),
            "strategy_metrics": m,
            "benchmark_metrics": b,
            "beats_bh_sharpe": bool(m["sharpe"] > b["sharpe"]),
            "run_file": str(run_path.relative_to(config.REPO_ROOT)),
        })
        print(f"  {family}__{home} -> {ticker} [{timeframe}]: "
              f"sharpe {m['sharpe']:.3f} vs B&H {b['sharpe']:.3f} "
              f"{'BEATS' if m['sharpe'] > b['sharpe'] else 'loses'}")
    beats = sum(r["beats_bh_sharpe"] for r in rows)
    summary = {
        "subject": f"{family}__{home}__{timeframe}",
        "family": family,
        "home_instrument": home,
        "timeframe": timeframe,
        "p1_sweep": sweep,
        "frozen_params": params,
        "params_match_preregistered_list": params_match,
        "transfer_instruments": transfers,
        "beats_bh_count": int(beats),
        "n_transfer_instruments": len(transfers),
        "verdict": verdict_for(beats, len(transfers)),
        "runs": rows,
    }
    out_path = OUT_DIR / f"{family}__{home}__{timeframe}.json"
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    for family, home, timeframe, sweep, expected in SUBJECTS:
        print(f"subject: {family}__{home}__{timeframe} (frozen from {sweep})")
        results.append(run_subject(family, home, timeframe, sweep, expected))
    ledger.rebuild_index()
    print("\n=== P4 transfer verdicts ===")
    for r in results:
        print(f"{r['subject']}: {r['beats_bh_count']}/"
              f"{r['n_transfer_instruments']} beat B&H -> {r['verdict']}")


if __name__ == "__main__":
    main()
