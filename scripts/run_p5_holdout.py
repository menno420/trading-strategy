#!/usr/bin/env python3
"""P5 one-shot holdout evaluation — ORDER 008, protocol-bound.

BINDING PROTOCOL: docs/p5-holdout-protocol.md (pre-registered). This script
is the mechanical executor of §7.2: it re-verifies the §2 frozen-parameter
table against the sweep JSONs at run time, fetches fresh bars through
``trading_lab.data.fetch_ohlcv``, loads them with
``load_ohlcv(..., unlock_holdout=True)`` (the P5-only kwarg;
``HoldoutViolationWarning`` is expected and correct here, and ONLY here),
runs exactly the 13 frozen-param subject runs + 13 buy-and-hold benchmarks
of §1–§3 once each, writes every ledger row with ``holdout_unlocked=True``,
and rebuilds the index.

*** ONE SHOT — NEVER RE-RUN. *** The holdout was spent the moment
``--evaluate`` first produced numbers (2026-07-10). Re-running the
evaluation, changing parameters, adding windows, or adding subjects would
be in-sample by definition (protocol §6). The ``--evaluate`` phase refuses
to run if its output summary already exists. This file is committed as
reproduction *evidence*, not as a thing to execute again.

Mechanical interpretation decisions, fixed BEFORE any holdout number was
read (documented per protocol §5's interpretation guard):

1. **Warm-up + first fill (protocol §4).** Positions are computed over the
   FULL fetched series (indicator warm-up on pre-holdout dev bars, as §4
   permits). The evaluated slice is the holdout window plus exactly ONE
   warm-in bar (the last bar strictly before the window start). Under the
   engine's t+1-open model the warm-in bar contributes zero return and zero
   cost (``held[0] = 0``), and its only role is to let the position decided
   on the last dev bar fill at the FIRST holdout bar's open — "scored
   returns begin at the first holdout-window fill" (§4). The buy-and-hold
   benchmark runs on the exact same slice, so it too enters at the first
   holdout bar's open and pays the same entry cost. Ledger ``data_start``
   is therefore the warm-in (pre-holdout) bar; the scored window starts at
   the first bar >= the window start.
2. **Window start.** Daily subjects: 2025-01-09 (``HOLDOUT_START``). Hourly
   subjects: ``max(2025-01-09, earliest obtainable bar)`` per the §4
   contingency; if the obtainable window has < 250 hourly bars the subject
   is NOT-EVALUABLE (no backtest is run, nothing is ledgered, the fact is
   reported).
3. **Verdicts (§5), mechanical.** PRIMARY: CONFIRMED iff strategy Sharpe >
   B&H Sharpe (strict), REFUTED otherwise. SECONDARY: HOLDOUT-BEAT iff
   strategy Sharpe > B&H Sharpe (strict), else HOLDOUT-MISS. A Sharpe that
   is undefined/NaN (e.g. a strategy that never trades) counts as NOT a
   beat — the resolution less favorable to the strategy.
4. **Data path.** Fresh bars are cached under ``data/p5holdout/`` (the
   ``data/p2ext`` precedent) so the committed pre-holdout caches stay
   byte-identical; ``load_ohlcv`` applies the holdout rail regardless of
   ``data_dir`` and is the only load path used.
5. **Significance context.** Each row also carries the ORDER 007
   ``trading_lab.promotion.grade_promotion`` output at K=1 (reported
   alongside, per the order; K>=lane burden only raises the bar).

Phases (run in this order; each is idempotent-safe except the one-shot):

    python3 scripts/run_p5_holdout.py --verify-params   # §2 gate, read-only
    python3 scripts/run_p5_holdout.py --fetch           # network -> data/p5holdout
    python3 scripts/run_p5_holdout.py --smoke           # mechanics dry-run, DEV DATA
    python3 scripts/run_p5_holdout.py --evaluate        # THE one shot

``--smoke`` exercises the identical code path on pre-holdout data only
(``unlock_holdout=False``, committed caches, pseudo-window 2024-01-09,
ledger rows to a throwaway directory that is never committed) so that any
mechanical crash is found and fixed before the holdout is touched. It reads
zero holdout bars and tunes nothing (params stay frozen).
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from trading_lab import config, data, ledger, metrics, promotion  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402

SWEEPS_DIR = config.EXPERIMENTS_DIR / "sweeps"
P5_DATA_DIR = config.REPO_ROOT / "data" / "p5holdout"
OUT_DIR = SWEEPS_DIR / "p5-holdout"
OUT_PATH = OUT_DIR / "results.json"

MIN_HOURLY_BARS = 250  # protocol §4: fewer -> NOT-EVALUABLE

# The closed subject list, verbatim from docs/p5-holdout-protocol.md §1–§2.
# (id, role, family, ticker, timeframe, sweep, frozen params.)
SUBJECTS = [
    ("P",   "PRIMARY",   "donchian",           "AAPL",    "daily",  "p1-trend-following-daily",
     {"entry": 15, "exit": 5}),
    ("S1",  "SECONDARY", "sma_crossover",      "META",    "daily",  "p1-trend-following-daily",
     {"fast": 15, "slow": 75}),
    ("S2",  "SECONDARY", "ema_crossover",      "META",    "daily",  "p1-trend-following-daily",
     {"fast": 25, "slow": 50}),
    ("S3",  "SECONDARY", "donchian",           "META",    "daily",  "p1-trend-following-daily",
     {"entry": 55, "exit": 55}),
    ("S4",  "SECONDARY", "supertrend_flip",    "BTC-USD", "daily",  "p1-video-strategy-daily",
     {"ema_len": 200, "macd_fast": 12, "macd_signal": 9, "macd_slow": 26,
      "st_mult": 2.0, "st_period": 14}),
    ("S5",  "SECONDARY", "macd_supertrend",    "BTC-USD", "daily",  "p1-video-strategy-daily",
     {"ema_len": 100, "macd_fast": 12, "macd_signal": 9, "macd_slow": 26,
      "st_mult": 2.0, "st_period": 14}),
    ("S6",  "SECONDARY", "rsi_mean_reversion", "META",    "daily",  "p1-mean-reversion-daily",
     {"overbought": 50, "oversold": 10, "period": 2}),
    ("S7",  "SECONDARY", "pullback",           "META",    "daily",  "p1-mean-reversion-daily",
     {"entry_lookback": 7, "exit_len": 7, "trend_len": 100}),
    ("S8",  "SECONDARY", "sma_crossover",      "GOOGL",   "hourly", "p1-trend-hourly",
     {"fast": 10, "slow": 75}),
    ("S9",  "SECONDARY", "ema_crossover",      "GOOGL",   "hourly", "p1-trend-hourly",
     {"fast": 20, "slow": 50}),
    ("S10", "SECONDARY", "donchian",           "GOOGL",   "hourly", "p1-trend-hourly",
     {"entry": 40, "exit": 40}),
    ("S11", "SECONDARY", "donchian",           "AMZN",    "hourly", "p1-trend-hourly",
     {"entry": 40, "exit": 40}),
    ("S12", "SECONDARY", "macd",               "META",    "hourly", "p1-trend-hourly",
     {"fast": 5, "signal": 5, "slow": 26}),
]

# instrument x timeframe pairs that need bars (deduped from SUBJECTS)
FETCH_SPECS = [("AAPL", "daily"), ("META", "daily"), ("BTC-USD", "daily"),
               ("GOOGL", "hourly"), ("AMZN", "hourly"), ("META", "hourly")]


def verify_params() -> None:
    """Protocol §2 run-time gate: exact dict equality, all 13 rows, or STOP."""
    mismatches = []
    for sid, _, fam, tic, tf, sweep, expected in SUBJECTS:
        src = SWEEPS_DIR / sweep / f"{fam}__{tic}.json"
        actual = json.loads(src.read_text())["top_full_period_variant"]["params"]
        status = "MATCH" if actual == expected else "MISMATCH"
        print(f"{sid:>3} {fam}__{tic} [{tf}]: {status}")
        if actual != expected:
            mismatches.append((sid, expected, actual))
    if mismatches:
        raise SystemExit(f"PROTOCOL VIOLATION (§2): frozen-param mismatch, "
                         f"do not run: {mismatches}")
    print("13/13 frozen-param rows verified against sweep JSONs.")


def fetch() -> None:
    """Fetch fresh bars through the standard path into data/p5holdout/."""
    for ticker, tf in FETCH_SPECS:
        df = data.fetch_ohlcv(ticker, tf)
        path = data.save_cache(df, ticker, tf, data_dir=P5_DATA_DIR)
        print(f"fetched {ticker} {tf}: {len(df)} bars "
              f"{df.index[0]} -> {df.index[-1]} -> {path}")


def evaluate_subject(spec, *, window_start: str, unlock: bool,
                     data_dir, runs_dir) -> dict:
    sid, role, family, ticker, tf, sweep, expected = spec

    # §2 gate again, per subject, immediately before its run.
    src = SWEEPS_DIR / sweep / f"{family}__{ticker}.json"
    params = json.loads(src.read_text())["top_full_period_variant"]["params"]
    if params != expected:
        raise SystemExit(f"PROTOCOL VIOLATION (§2) on {sid}: {params} != {expected}")

    full = load_ohlcv(ticker, tf, unlock_holdout=unlock, data_dir=data_dir)

    ws = pd.Timestamp(window_start)
    contingency = None
    if full.index[0] > ws:  # §4 hourly contingency (moving history floor)
        contingency = (f"earliest obtainable bar {full.index[0]} is after "
                       f"{window_start}; window shortened per protocol §4")
        ws = full.index[0]

    window_index = full.index[full.index >= ws]
    n_window_bars = int(len(window_index))
    base = {
        "id": sid, "role": role, "subject": f"{family}__{ticker}__{tf}",
        "family": family, "instrument": ticker, "timeframe": tf,
        "p1_sweep": sweep, "frozen_params": params,
        "window_start_requested": window_start,
        "window_start_effective": str(ws),
        "n_window_bars": n_window_bars,
        "contingency": contingency,
    }
    if tf == "hourly" and n_window_bars < MIN_HOURLY_BARS:
        base["verdict"] = "NOT-EVALUABLE"
        base["reason"] = (f"obtainable hourly window has {n_window_bars} bars "
                          f"< {MIN_HOURLY_BARS} (protocol §4); no run performed")
        print(f"{sid}: NOT-EVALUABLE ({n_window_bars} bars)")
        return base

    # Warm-up on the full series (§4); slice = window + one warm-in bar.
    positions = STRATEGIES[family](full, **params)
    pre = full.index[full.index < ws]
    slice_start = pre[-1] if len(pre) else full.index[0]
    eval_df = full.loc[slice_start:]
    pos_eval = positions.loc[eval_df.index]

    result = run_backtest(eval_df, pos_eval,
                          slippage_bps=config.DEFAULT_SLIPPAGE_BPS,
                          commission_bps=config.DEFAULT_COMMISSION_BPS,
                          timeframe=tf)
    benchmark = buy_and_hold_result(eval_df,
                                    slippage_bps=config.DEFAULT_SLIPPAGE_BPS,
                                    commission_bps=config.DEFAULT_COMMISSION_BPS,
                                    timeframe=tf)
    notes = (f"P5 one-shot holdout evaluation (ORDER 008; binding protocol "
             f"docs/p5-holdout-protocol.md, subject {sid} {role}). Params "
             f"frozen verbatim from experiments/sweeps/{sweep}/"
             f"{family}__{ticker}.json (top_full_period_variant), verified at "
             f"run time. Scored window {window_index[0]} -> "
             f"{eval_df.index[-1]}; data_start is one pre-window warm-in bar "
             f"(zero return/zero cost by engine construction) so the position "
             f"decided on the last dev bar fills at the first window open "
             f"(protocol §4). Benchmark B&H on the identical slice. Data: "
             f"data/p5holdout/ (fresh fetch, standard path).")
    record = ledger.build_record(strategy=family, params=params,
                                 instrument=ticker, timeframe=tf,
                                 ohlcv=eval_df, result=result,
                                 benchmark=benchmark, variants_tried=1,
                                 notes=notes, holdout_unlocked=unlock)
    run_path = ledger.write_run(record, runs_dir=runs_dir)
    m, b = metrics.compute_all(result), metrics.compute_all(benchmark)

    # §5, mechanical. Undefined Sharpe counts against the strategy.
    beats = (m["sharpe"] is not None and b["sharpe"] is not None
             and m["sharpe"] > b["sharpe"])
    if role == "PRIMARY":
        verdict = "CONFIRMED" if beats else "REFUTED"
    else:
        verdict = "HOLDOUT-BEAT" if beats else "HOLDOUT-MISS"

    grade = None
    if m["sharpe"] is not None and b["sharpe"] is not None:
        grade = promotion.grade_promotion(
            strategy_sharpe=m["sharpe"], benchmark_sharpe=b["sharpe"],
            n_periods=int(len(eval_df)), timeframe=tf, variants_tried=1)

    base.update({
        "window": [str(window_index[0]), str(eval_df.index[-1])],
        "warmin_bar": str(eval_df.index[0]),
        "n_bars_incl_warmin": int(len(eval_df)),
        "strategy_metrics": m,
        "benchmark_metrics": b,
        "beats_bh_sharpe": bool(beats),
        "verdict": verdict,
        "promotion_grade_k1": grade,
        "run_file": str(run_path.relative_to(config.REPO_ROOT))
        if runs_dir is None else str(run_path),
    })
    s = "None" if m["sharpe"] is None else f"{m['sharpe']:.3f}"
    print(f"{sid} {family}__{ticker} [{tf}]: sharpe {s} vs B&H "
          f"{b['sharpe']:.3f} -> {verdict}")
    return base


def run_all(*, window_start: str, unlock: bool, data_dir, runs_dir,
            out_path: Path) -> None:
    rows = [evaluate_subject(s, window_start=window_start, unlock=unlock,
                             data_dir=data_dir, runs_dir=runs_dir)
            for s in SUBJECTS]
    secondaries = [r for r in rows if r["role"] == "SECONDARY"]
    summary = {
        "protocol": "docs/p5-holdout-protocol.md",
        "order": "ORDER 008",
        "holdout_unlocked": unlock,
        "window_start_requested": window_start,
        "primary_verdict": rows[0]["verdict"],
        "secondary_beats": sum(bool(r.get("beats_bh_sharpe")) for r in secondaries),
        "secondary_not_evaluable": sum(r["verdict"] == "NOT-EVALUABLE"
                                       for r in secondaries),
        "n_secondaries": len(secondaries),
        "selection_burden": {"p1-trend-following-daily": 177,
                             "p1-video-strategy-daily": 92,
                             "p1-mean-reversion-daily": 144,
                             "p1-trend-hourly": 177},
        "preregistered_null_base_rates": {"p1_lanes_beating_bh":
                                          ["7/32", "3/24", "5/32"],
                                          "p4_transfer": "13/99"},
        "subjects": rows,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    if runs_dir is None:
        ledger.rebuild_index()
    print(f"\nprimary: {summary['primary_verdict']}; secondaries "
          f"{summary['secondary_beats']}/{summary['n_secondaries']} "
          f"HOLDOUT-BEAT; wrote {out_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--verify-params", action="store_true")
    g.add_argument("--fetch", action="store_true")
    g.add_argument("--smoke", action="store_true",
                   help="mechanics dry-run on DEV data only (no holdout read)")
    g.add_argument("--evaluate", action="store_true",
                   help="THE one-shot holdout evaluation (refuses to re-run)")
    args = ap.parse_args()

    if args.verify_params:
        verify_params()
    elif args.fetch:
        fetch()
    elif args.smoke:
        import tempfile
        tmp = Path(tempfile.mkdtemp(prefix="p5-smoke-"))
        verify_params()
        run_all(window_start="2024-01-09", unlock=False, data_dir=None,
                runs_dir=tmp / "runs", out_path=tmp / "smoke.json")
        print(f"SMOKE ONLY (dev data, throwaway dir {tmp}) — not a result.")
    elif args.evaluate:
        if OUT_PATH.exists():
            raise SystemExit(
                f"REFUSING TO RUN: {OUT_PATH} already exists. The holdout is "
                "one-shot and has been spent (protocol §6); never re-run.")
        verify_params()
        run_all(window_start=config.HOLDOUT_START, unlock=True,
                data_dir=P5_DATA_DIR, runs_dir=None, out_path=OUT_PATH)


if __name__ == "__main__":
    main()
