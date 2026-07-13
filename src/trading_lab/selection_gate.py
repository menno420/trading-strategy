"""Selection-fair replay standing gate — round-6+ dev-lane KEEP verdicts.

Replay semantics lifted from ``scripts/run_r5d_selection_fair.py`` (R5-D,
PR #110); that historical script stays byte-untouched — this module is the
standing home of its machinery. Standing doc (binding, with the recorded
semantic choices): ``docs/selection-fair-gate.md``.

From research round 6 onward a dev-lane KEEP verdict additionally requires
that a SELECTION-FREE fixed-config replay of the lane's committed top
variant — one fixed config, no training pick, over the lane's exact
committed walk-forward test windows at the lane's costs — beats
same-window buy-and-hold. R5-D measured why: on the program's five best
lanes ``selection_gap > 0`` held on only 3/5, and two searched
walk-forwards LOST to their own fixed config (SLV −0.313, META hourly
−0.396) — in-window re-selection can flatter the searched number.

Deliberate strictness increases over the R5-D experiment slice (each
recorded in the standing doc):

* UNGRADEABLE (missing ``per_split`` windows, fidelity-guard failure,
  cache drift / missing data, non-contiguous windows) = gate **FAIL**,
  never a neutral skip — R5-D's SKIPPED was experiment-report semantics.
* The pass rule adds ``fixed_sharpe > 0`` (r3-rule alignment R5-D lacked);
  ties and NaN fail.

The gate is invoked explicitly by round-6+ runners; nothing here
retroactively re-labels existing results (round ≤5 verdicts stand as
published). ``selection_gap = searched − fixed`` stays informational —
no registered threshold.
"""

from __future__ import annotations

import math

import pandas as pd

from . import metrics, promotion
from .engine import buy_and_hold_result, run_backtest

# Gate outcomes. There is deliberately no SKIPPED/UNGRADEABLE outcome:
# an ungradeable lane FAILs with a verbatim reason (strict standing-gate
# semantics; see module docstring).
GATE_PASS = "PASS"
GATE_FAIL = "FAIL"

# Fidelity-guard tolerance on the searched-arm replay, verbatim from R5-D
# (itself the R4-B standing-rail precedent).
REPLAY_TOL = 1e-8


def _clean(x):
    """NaN → None so gate results serialize machine-readably (R5-D)."""
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def stitched_replay(ohlcv, strategy_fn, rows, timeframe, *, costs):
    """Replay per-split positions ([t0, t1] windows + params per row) at
    ``costs`` and stitch the OOS returns. Signals for a test window may use
    trailing history before test_start (indicators are causal) but never
    anything >= test_end. No selection of any kind happens here.

    Lifted from ``scripts/run_r5d_selection_fair.py`` with the lane's
    ``costs`` dict (``slippage_bps``/``commission_bps``) parametrized in
    place of that script's pinned baseline.
    """
    rets, per = [], []
    for row in rows:
        t0, t1 = int(row["test"][0]), int(row["test"][1])
        pos = strategy_fn(ohlcv.iloc[:t1], **row["params"]).iloc[t0:t1]
        res = run_backtest(ohlcv.iloc[t0:t1], pos, timeframe=timeframe,
                           **costs)
        rets.append(res.returns)
        per.append({"test": [t0, t1], "params": row["params"],
                    "test_sharpe": _clean(metrics.sharpe(res.returns,
                                                         timeframe))})
    return pd.concat(rets), per


def gate_decision(*, fixed_sharpe, bench_sharpe) -> bool:
    """Pure pass rule, no I/O: both Sharpes non-NaN AND
    ``fixed_sharpe > bench_sharpe`` AND ``fixed_sharpe > 0``.

    The ``> 0`` conjunct is the deliberate strictness increase over R5-D
    (r3-rule alignment). Ties and NaN fail. Total by design: None or
    non-numeric inputs fail rather than raise.
    """
    try:
        fixed = float(fixed_sharpe)
        bench = float(bench_sharpe)
    except (TypeError, ValueError):
        return False
    if math.isnan(fixed) or math.isnan(bench):
        return False
    return fixed > bench and fixed > 0.0


def _fail(reason: str, **fields) -> dict:
    """A FAIL gate result with every schema key present (None when the
    failure happened before the value could be computed)."""
    result = {"gate": GATE_FAIL, "reason": reason, "fixed_sharpe": None,
              "bench_sharpe": None, "searched_sharpe": None,
              "selection_gap": None, "n_periods": None,
              "fixed_per_split": None}
    result.update(fields)
    return result


def run_selection_gate(*, ohlcv, strategy, per_split, top_variant,
                       timeframe, costs,
                       recorded_searched_sharpe=None) -> dict:
    """Run the full standing gate for one lane. Never raises on lane
    defects — every ungradeable condition is a FAIL with a verbatim reason.

    Arguments mirror a committed lane source JSON (R5-D shapes): ``ohlcv``
    is the lane's dev-rail frame (the CALLER owns the cache-drift check of
    ``data_start``/``data_end``/``n_bars`` against the source JSON, exactly
    as R5-D's ``prepare_lane`` did — on drift, do not call this function;
    record gate FAIL with the drift reason); ``strategy`` is the family's
    ``generate`` callable; ``per_split`` is the committed
    ``walk_forward.per_split`` list; ``top_variant`` the committed top
    full-period params; ``costs`` the lane's committed costs dict.
    ``recorded_searched_sharpe``, when given, arms the R5-D fidelity guard:
    the searched-arm replay must reproduce it within :data:`REPLAY_TOL`.

    Returns a machine-readable dict: ``gate`` (:data:`GATE_PASS` /
    :data:`GATE_FAIL`), ``reason``, ``fixed_sharpe``, ``bench_sharpe``,
    ``searched_sharpe``, ``selection_gap`` (informational — searched minus
    fixed, no registered threshold), ``n_periods``, ``fixed_per_split``.
    NaN values are serialized as None.
    """
    if not per_split:
        return _fail("ungradeable: lane has no committed "
                     "walk_forward.per_split test windows — the gate "
                     "cannot replay what was never committed")
    windows = [[int(r["test"][0]), int(r["test"][1])] for r in per_split]
    n = int(len(ohlcv))
    for t0, t1 in windows:
        if not (0 <= t0 < t1 <= n):
            return _fail(f"ungradeable: committed test window [{t0}, {t1}] "
                         f"does not fit the loaded data ({n} bars) — "
                         f"positional windows would misalign (missing "
                         f"data / cache drift)")
    for prev, nxt in zip(windows, windows[1:]):
        if nxt[0] != prev[1]:
            return _fail(f"ungradeable: committed test windows are not "
                         f"contiguous ({prev} then {nxt}) — the "
                         f"same-window benchmark slice "
                         f"[{windows[0][0]}:{windows[-1][1]}] would not "
                         f"equal the stitched OOS coverage")

    # Searched arm: always replayed (it prices selection_gap); with a
    # recorded Sharpe it is also the R5-D fidelity guard.
    searched, _ = stitched_replay(ohlcv, strategy, per_split, timeframe,
                                  costs=costs)
    searched_sharpe = metrics.sharpe(searched, timeframe)
    if recorded_searched_sharpe is not None:
        if (math.isnan(searched_sharpe)
                or not (abs(searched_sharpe - recorded_searched_sharpe)
                        <= REPLAY_TOL)):
            return _fail(f"ungradeable: fidelity guard failed — replayed "
                         f"searched stitched OOS Sharpe {searched_sharpe!r} "
                         f"vs recorded {recorded_searched_sharpe!r} (tol "
                         f"{REPLAY_TOL}) — refusing to grade an "
                         f"unreproduced lane",
                         searched_sharpe=_clean(searched_sharpe))

    # Fixed arm: the committed top variant, selection-free, on the
    # identical windows; benchmark is same-window B&H at the same costs
    # over the contiguous slice (exactly R5-D).
    fixed_rows = [{"test": w, "params": top_variant} for w in windows]
    fixed, fixed_per = stitched_replay(ohlcv, strategy, fixed_rows,
                                       timeframe, costs=costs)
    fixed_sharpe = metrics.sharpe(fixed, timeframe)
    oos_slice = ohlcv.iloc[windows[0][0]:windows[-1][1]]
    bench = buy_and_hold_result(oos_slice, timeframe=timeframe, **costs)
    bench_sharpe = metrics.sharpe(bench.returns, timeframe)
    fields = {
        "fixed_sharpe": _clean(fixed_sharpe),
        "bench_sharpe": _clean(bench_sharpe),
        "searched_sharpe": _clean(searched_sharpe),
        "selection_gap": _clean(searched_sharpe - fixed_sharpe),
        "n_periods": int(len(fixed)),
        "fixed_per_split": fixed_per,
    }
    if math.isnan(fixed_sharpe) or math.isnan(bench_sharpe):
        return _fail("ungradeable: fixed or benchmark stitched Sharpe is "
                     "NaN (degenerate returns) — NaN never passes",
                     **fields)
    if gate_decision(fixed_sharpe=fixed_sharpe, bench_sharpe=bench_sharpe):
        return {"gate": GATE_PASS,
                "reason": (f"fixed-config replay beats same-window B&H "
                           f"({fixed_sharpe:.6f} > {bench_sharpe:.6f}) and "
                           f"is positive"),
                **fields}
    return _fail(f"fixed-config replay does not beat same-window B&H with "
                 f"a positive Sharpe (fixed {fixed_sharpe:.6f}, bench "
                 f"{bench_sharpe:.6f}) — the searched edge does not "
                 f"survive selection-free", **fields)


def apply_gate(verdict: str, gate_result: dict) -> str:
    """Fold a gate result into a lane verdict.

    A KEEP verdict (:data:`promotion.VERDICT_KEEP_DEV` — promotion is
    CLOSED post-holdout, so KEEP-dev is the ceiling — or the sweep-vocab
    :data:`promotion.SWEEP_KEEP`) demotes to :data:`promotion.SWEEP_KILL`
    on gate FAIL. KILL / KILL-SIG (and anything else non-KEEP) pass
    through unchanged — the gate only ever demotes, never upgrades and
    never invents verdict strings.
    """
    if gate_result["gate"] == GATE_PASS:
        return verdict
    if verdict in (promotion.VERDICT_KEEP_DEV, promotion.SWEEP_KEEP):
        return promotion.SWEEP_KILL
    return verdict
