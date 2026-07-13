#!/usr/bin/env python3
"""Round 5 slice R5-C — moving-block bootstrap of the Sharpe-delta t for
the top-5 KEEP-dev lanes.

POST-HOLDOUT, DEV-ONLY. Promotion is CLOSED: nothing this script produces
can be an out-of-sample claim; a lane that keeps its status is a
dev-candidate only, never a finding.

Pre-registration: ``docs/research-round-5-plan.md`` § R5-C, merged BEFORE
this script existed. Registered method: from each lane's
fidelity-guarded frozen replay, take the stitched OOS per-bar strategy
and benchmark return series; moving-block bootstrap the PAIRED series —
the SAME resampled block indices applied to both series, preserving the
strategy/benchmark pairing bar by bar — with block length 21 bars (daily)
/ 63 bars (hourly), 1,000 resamples, RNG seed fixed to 20260713 in this
runner (a fresh ``numpy.random.default_rng(20260713)`` per lane, so each
lane's draw is reproducible independently of processing order). Reported
per lane: the bootstrap distribution of the annualized Sharpe delta and
of the ORDER 007 t, plus ``P(delta <= 0)``.

Pre-registered decision rule (per lane):
- DEMOTED to KILL iff ``P(delta <= 0) >= 0.60``;
- ESCALATE-TO-OWNER iff ``P(delta <= 0) <= 0.10`` — an owner-gated
  proposal doc under ``docs/proposals/`` recommending a new
  pre-registered protocol on post-2026 data; the verdict itself stays
  KEEP-dev, nothing is scheduled or run;
- otherwise KEEP-dev, unchanged.

FIDELITY GUARD (standing rail, R4-B precedent): each lane's baseline
replay must reproduce its committed stitched OOS Sharpe within 1e-8; an
irreproducible lane is recorded SKIPPED with the verbatim reason.

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail
(``data_end <= 2025-01-08`` asserted per lane); ``unlock_holdout`` is
never passed; no new bars are consumed (resampling of committed replays).
All ``experiments/sweeps/r3-*/`` files stay byte-untouched; this slice
writes ``experiments/sweeps/r5-bootstrap/``.

LEDGER DECISION (deliberate, R4-B precedent): report-only, NOT ledgered —
0 new registered configs; ``experiments/index.jsonl`` untouched.

Runtime cap (pre-registered): <= 10 minutes wall-clock for the slice.

Usage: python3 scripts/run_r5c_bootstrap.py
"""

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, promotion, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import buy_and_hold_result, run_backtest  # noqa: E402
from trading_lab.strategies import STRATEGIES  # noqa: E402

SWEEP_NAME = "r5-bootstrap"
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SWEEP_NAME

DEV_DATA_END_MAX = "2025-01-08"

BASELINE_COSTS = {"slippage_bps": float(config.DEFAULT_SLIPPAGE_BPS),
                  "commission_bps": float(config.DEFAULT_COMMISSION_BPS)}
assert BASELINE_COSTS == {"slippage_bps": 5.0, "commission_bps": 1.0}

REPLAY_TOL = 1e-8

# Pre-registered bootstrap parameters (plan § R5-C, verbatim).
BLOCK_LENGTH = {"daily": 21, "hourly": 63}
N_RESAMPLES = 1000
RNG_SEED = 20260713

# Pre-registered thresholds on P(delta <= 0).
P_KILL = 0.60      # DEMOTED to KILL iff P >= this
P_ESCALATE = 0.10  # ESCALATE-TO-OWNER iff P <= this (verdict stays KEEP)

VERDICT_KEEP = "KEEP (dev-candidate only)"
VERDICT_KILL = "KILL"
STATUS_SKIPPED = "SKIPPED"

RUNTIME_CAP_SECONDS = 600  # pre-registered: <= 10 minutes wall-clock

PCTS = [2.5, 5.0, 25.0, 50.0, 75.0, 95.0, 97.5]


class LaneSkip(Exception):
    """Lane cannot be reproduced exactly — recorded verbatim, never
    approximated silently (pre-registered honesty rule)."""


def _clean(x):
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def frozen_stitched_returns(ohlcv, strategy_fn, per_split, timeframe):
    """Replay the committed frozen per-split params on the committed
    positional test windows at baseline costs and stitch the OOS returns.
    No selection of any kind happens here."""
    rets = []
    for row in per_split:
        t0, t1 = int(row["test"][0]), int(row["test"][1])
        pos = strategy_fn(ohlcv.iloc[:t1], **row["params"]).iloc[t0:t1]
        res = run_backtest(ohlcv.iloc[t0:t1], pos, timeframe=timeframe,
                           **BASELINE_COSTS)
        rets.append(res.returns)
    return pd.concat(rets)


def prepare_lane(lane: dict):
    """Load data, replay the lane frozen, run the fidelity guard, and
    return the paired stitched strategy/benchmark per-bar return arrays.
    Raises LaneSkip with a verbatim reason on any mismatch."""
    source = json.loads((config.REPO_ROOT / lane["source_file"]).read_text())
    fam, tick, tf = source["family"], source["instrument"], source["timeframe"]
    if fam not in STRATEGIES:
        raise LaneSkip(f"strategy {fam!r} not in trading_lab.strategies."
                       f"STRATEGIES — original rail cannot be rebuilt")
    ohlcv = load_ohlcv(tick, tf)  # dev rail: holdout excluded by default
    data_end = str(ohlcv.index[-1])
    assert data_end[:10] <= DEV_DATA_END_MAX, \
        f"{tick}: dev rail breached (data_end {data_end})"
    for field, got in (("data_start", str(ohlcv.index[0])),
                       ("data_end", data_end),
                       ("n_bars", int(len(ohlcv)))):
        if got != source[field]:
            raise LaneSkip(f"cache drift vs committed lane "
                           f"{lane['source_file']}: {field} recorded "
                           f"{source[field]!r}, loaded {got!r} — positional "
                           f"windows would misalign")
    per_split = source["walk_forward"]["per_split"]
    strat = frozen_stitched_returns(ohlcv, STRATEGIES[fam], per_split, tf)
    got_sharpe = metrics.sharpe(strat, tf)
    rec_sharpe = source["walk_forward"]["oos_metrics"]["sharpe"]
    if not (abs(got_sharpe - rec_sharpe) <= REPLAY_TOL):
        raise LaneSkip(f"baseline replay mismatch for {lane['source_file']}: "
                       f"replayed stitched OOS Sharpe {got_sharpe!r} vs "
                       f"recorded {rec_sharpe!r} (tol {REPLAY_TOL}) — "
                       f"refusing to grade an unreproduced lane")
    oos_lo = int(per_split[0]["test"][0])
    oos_hi = int(per_split[-1]["test"][1])
    bench = buy_and_hold_result(ohlcv.iloc[oos_lo:oos_hi], timeframe=tf,
                                **BASELINE_COSTS)
    if len(bench.returns) != len(strat):
        raise LaneSkip(f"benchmark alignment failure for "
                       f"{lane['source_file']}: strategy {len(strat)} bars "
                       f"vs benchmark {len(bench.returns)} — cannot pair")
    return source, strat.to_numpy(), bench.returns.to_numpy(), got_sharpe


def np_sharpe(values: np.ndarray, timeframe: str) -> float:
    """Annualized Sharpe on a numpy array — the exact
    trading_lab.metrics.sharpe formula (ddof=1, zero risk-free)."""
    sd = values.std(ddof=1)
    if sd == 0 or math.isnan(sd):
        return float("nan")
    ppy = metrics.periods_per_year(timeframe)
    return float(values.mean() / sd * math.sqrt(ppy))


def moving_block_bootstrap(strat, bench, timeframe):
    """The pre-registered paired moving-block bootstrap: identical block
    start indices for both series (pairing preserved bar by bar)."""
    n = len(strat)
    block = BLOCK_LENGTH[timeframe]
    n_blocks = math.ceil(n / block)
    rng = np.random.default_rng(RNG_SEED)
    deltas = np.empty(N_RESAMPLES)
    tstats = np.empty(N_RESAMPLES)
    offsets = np.arange(block)
    for b in range(N_RESAMPLES):
        starts = rng.integers(0, n - block + 1, size=n_blocks)
        idx = (starts[:, None] + offsets[None, :]).ravel()[:n]
        s_sh = np_sharpe(strat[idx], timeframe)
        b_sh = np_sharpe(bench[idx], timeframe)
        deltas[b] = s_sh - b_sh
        tstats[b] = promotion.sharpe_delta_tstat(s_sh, b_sh, n, timeframe)
    return deltas, tstats


def dist_stats(values: np.ndarray) -> dict:
    return {
        "mean": _clean(float(np.mean(values))),
        "std": _clean(float(np.std(values, ddof=1))),
        "percentiles": {str(p): _clean(float(np.percentile(values, p)))
                        for p in PCTS},
    }


def main() -> None:
    t_start = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    lanes = sweeps.R5A_TARGET_LANES  # the one frozen Round-5 target set
    print(f"R5-C target set: {len(lanes)} frozen lanes; block "
          f"{BLOCK_LENGTH}, {N_RESAMPLES} resamples, seed {RNG_SEED}")
    rollup_rows, skipped = [], []

    for i, lane in enumerate(lanes, 1):
        fam, tick, tf = lane["family"], lane["instrument"], lane["timeframe"]
        tag = f"{lane['sweep']} {fam} {tick} {tf}"
        row = {"lane_id": lane["lane_id"], "sweep": lane["sweep"],
               "strategy": fam, "instrument": tick, "timeframe": tf,
               "source_file": lane["source_file"]}
        try:
            source, strat, bench, base_sharpe = prepare_lane(lane)
        except LaneSkip as exc:
            row["status"] = STATUS_SKIPPED
            row["skip_reason"] = str(exc)
            skipped.append(row)
            rollup_rows.append(row)
            print(f"[{i}/{len(lanes)}] {tag}: SKIPPED — {exc}")
            continue

        row["status"] = "GRADED"
        deltas, tstats = moving_block_bootstrap(strat, bench, tf)
        p_le0 = float(np.mean(deltas <= 0.0))
        point_delta = (np_sharpe(strat, tf) - np_sharpe(bench, tf))
        point_t = promotion.sharpe_delta_tstat(np_sharpe(strat, tf),
                                               np_sharpe(bench, tf),
                                               len(strat), tf)
        bar = promotion.min_tstat(source["variants_tried"])

        if p_le0 >= P_KILL:
            verdict, escalate = VERDICT_KILL, False
        elif p_le0 <= P_ESCALATE:
            verdict, escalate = VERDICT_KEEP, True
        else:
            verdict, escalate = VERDICT_KEEP, False
        keep = verdict == VERDICT_KEEP
        sweep_verdict = promotion.classify_verdict(keep, point_t, bar)

        record = {
            "schema_version": 1,
            "sweep": SWEEP_NAME,
            "created_utc": datetime.now(timezone.utc)
                                   .isoformat(timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": fam,
            "instrument": tick,
            "timeframe": tf,
            "post_holdout_dev_only": True,
            "preregistered_in": ("docs/research-round-5-plan.md § R5-C — "
                                 "Moving-block bootstrap of the "
                                 "Sharpe-delta t"),
            "lane_id": lane["lane_id"],
            "source_lane": lane["source_file"],
            "costs": BASELINE_COSTS,
            "no_research": ("resampling of the fidelity-guarded frozen "
                            "replay's paired stitched OOS return series — "
                            "no new bars, no selection pass, 0 new "
                            "registered configs"),
            "fidelity_guard": {"replayed_oos_sharpe": base_sharpe,
                               "matches_recorded": True,
                               "tolerance": REPLAY_TOL},
            "data_start": source["data_start"],
            "data_end": source["data_end"],
            "n_bars": source["n_bars"],
            "bootstrap": {
                "method": ("paired moving-block bootstrap: identical "
                           "resampled block indices applied to strategy "
                           "and benchmark per-bar returns"),
                "block_length_bars": BLOCK_LENGTH[tf],
                "n_resamples": N_RESAMPLES,
                "rng": f"numpy.random.default_rng({RNG_SEED}) per lane",
                "n_oos_bars": int(len(strat)),
            },
            "point_estimates": {"sharpe_delta": _clean(point_delta),
                                "tstat": _clean(point_t),
                                "min_tstat": bar},
            "sharpe_delta_distribution": dist_stats(deltas),
            "tstat_distribution": dist_stats(tstats),
            "p_delta_le_0": p_le0,
            "decision_rule": (f"DEMOTED to KILL iff P(delta<=0) >= "
                              f"{P_KILL}; ESCALATE-TO-OWNER (owner-gated "
                              f"proposal doc, verdict unchanged KEEP-dev) "
                              f"iff P(delta<=0) <= {P_ESCALATE}; otherwise "
                              f"KEEP-dev unchanged"),
            "verdict": verdict,
            "escalate_to_owner": escalate,
            "sweep_verdict": sweep_verdict,
            "ledger": ("report-only slice, NOT ledgered (R4-B precedent): "
                       "0 new registered configs; experiments/index.jsonl "
                       "untouched"),
        }
        out = SWEEP_DIR / f"{lane['sweep']}__{fam}__{tick}__{tf}.json"
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        row.update({"p_delta_le_0": p_le0,
                    "point_sharpe_delta": _clean(point_delta),
                    "point_tstat": _clean(point_t),
                    "bootstrap_t_p95": record["tstat_distribution"]
                                             ["percentiles"]["95.0"],
                    "verdict": verdict, "escalate_to_owner": escalate,
                    "sweep_verdict": sweep_verdict,
                    "detail_file": str(out.relative_to(config.REPO_ROOT))})
        rollup_rows.append(row)
        print(f"[{i}/{len(lanes)}] {tag}: P(delta<=0)={p_le0:.3f}, "
              f"delta point {point_delta:+.3f} -> {verdict}"
              f"{' + ESCALATE' if escalate else ''}")

    graded = [r for r in rollup_rows if r["status"] == "GRADED"]
    counts = {
        "target_lanes": len(lanes),
        "graded": len(graded),
        "skipped": len(skipped),
        "keep": sum(1 for r in graded if r["verdict"] == VERDICT_KEEP),
        "kill": sum(1 for r in graded if r["verdict"] == VERDICT_KILL),
        "kill_sig": sum(1 for r in graded
                        if r["sweep_verdict"] == promotion.SWEEP_KILL_SIG),
        "escalate": sum(1 for r in graded if r["escalate_to_owner"]),
    }
    elapsed = time.monotonic() - t_start
    report = {
        "schema_version": 1,
        "slice": SWEEP_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": ledger.git_sha(),
        "preregistered_in": ("docs/research-round-5-plan.md § R5-C — "
                             "Moving-block bootstrap of the Sharpe-delta t"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; every "
                                  "KEEP is a dev-candidate only, never a "
                                  "finding"),
        "target_set": ("the FROZEN top-5 KEEP-dev lanes of the plan "
                       "(trading_lab.sweeps.R5A_TARGET_LANES)"),
        "rule": (f"per lane on P(delta<=0): KILL iff >= {P_KILL}; "
                 f"escalate-to-owner iff <= {P_ESCALATE} (verdict stays "
                 f"KEEP-dev, proposal doc only); else KEEP-dev"),
        "bootstrap": {"block_length_bars": BLOCK_LENGTH,
                      "n_resamples": N_RESAMPLES, "rng_seed": RNG_SEED},
        "fidelity_guard": (f"every graded lane's baseline replay reproduced "
                           f"its committed stitched OOS Sharpe within "
                           f"{REPLAY_TOL}"),
        "burden": {"new_registered_configs": 0},
        "ledger_decision": ("report-only, NOT ledgered (R4-B precedent); "
                            "experiments/index.jsonl untouched"),
        "runtime_seconds": round(elapsed, 1),
        "runtime_cap_seconds": RUNTIME_CAP_SECONDS,
        "counts": counts,
        "lanes": rollup_rows,
    }
    out = SWEEP_DIR / "summary.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\nsummary: {counts['keep']} KEEP / {counts['kill']} KILL / "
          f"{counts['escalate']} escalate / {counts['kill_sig']} KILL-SIG "
          f"of {counts['graded']} graded ({counts['skipped']} skipped, "
          f"{elapsed:.1f}s) -> {out}")
    for r in skipped:
        print(f"  SKIPPED: {r['lane_id']} — {r['skip_reason']}")
    if elapsed > RUNTIME_CAP_SECONDS:
        print(f"  RUNTIME CAP EXCEEDED: {elapsed:.1f}s > "
              f"{RUNTIME_CAP_SECONDS}s — record in the results doc")


if __name__ == "__main__":
    main()
