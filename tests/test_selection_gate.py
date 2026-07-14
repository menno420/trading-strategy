"""Selection-fair replay standing gate tests (docs/selection-fair-gate.md).

Synthetic fixtures throughout, plus one read-only integration pin against
a committed R5-D artifact (local repo files only — no network).
"""

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from conftest import make_ohlcv
from trading_lab import metrics, promotion, selection_gate
from trading_lab.selection_gate import (GATE_FAIL, GATE_PASS, apply_gate,
                                        gate_decision, run_selection_gate,
                                        stitched_replay)

REPO_ROOT = Path(__file__).resolve().parents[1]

COSTS = {"slippage_bps": 5.0, "commission_bps": 1.0}


def parity_strategy(ohlcv, *, phase):
    """Deterministic test strategy: long iff bar's positional index has
    parity ``phase``. With the engine's t+1-open execution, phase=0 holds
    exactly the odd-index bars."""
    idx = np.arange(len(ohlcv))
    return pd.Series((idx % 2 == phase).astype(float), index=ohlcv.index)


def flat_strategy(ohlcv, **params):
    """Never trades — degenerate zero-variance returns (NaN Sharpe)."""
    return pd.Series(0.0, index=ohlcv.index)


def ohlcv_from_rets(rets):
    """Opens realizing the given per-bar open-to-open returns exactly
    (matching the engine's bar-return definition)."""
    rets = np.asarray(rets, dtype=float)
    opens = 100.0 * np.cumprod(np.concatenate([[1.0], 1.0 + rets[:-1]]))
    closes = np.concatenate([opens[1:], [opens[-1]]])
    return make_ohlcv(opens, closes)


def alternating_ohlcv(n=40, up=0.03, down=-0.02):
    """Bar returns alternate: odd-index bars return ``up``, even-index
    bars ``down``."""
    return ohlcv_from_rets(np.where(np.arange(n) % 2 == 1, up, down))


# Contiguous committed-style windows over the 40-bar fixture.
PER_SPLIT = [{"test": [10, 20], "params": {"phase": 0}},
             {"test": [20, 30], "params": {"phase": 0}},
             {"test": [30, 40], "params": {"phase": 0}}]
TOP_VARIANT = {"phase": 0}


class TestGateDecision:
    """The pure pass rule: non-NaN AND fixed > bench AND fixed > 0."""

    def test_pass(self):
        assert gate_decision(fixed_sharpe=1.2, bench_sharpe=0.8)

    def test_fail_fixed_below_bench(self):
        assert not gate_decision(fixed_sharpe=0.5, bench_sharpe=0.8)

    def test_tie_fails(self):
        assert not gate_decision(fixed_sharpe=0.8, bench_sharpe=0.8)

    def test_fail_beats_bench_but_not_positive(self):
        # The deliberate strictness increase over R5-D: fixed > bench is
        # not enough when fixed <= 0.
        assert not gate_decision(fixed_sharpe=-0.1, bench_sharpe=-0.5)
        assert not gate_decision(fixed_sharpe=0.0, bench_sharpe=-0.5)

    def test_nan_fails(self):
        assert not gate_decision(fixed_sharpe=float("nan"), bench_sharpe=0.1)
        assert not gate_decision(fixed_sharpe=0.5, bench_sharpe=float("nan"))

    def test_none_fails_not_raises(self):
        assert not gate_decision(fixed_sharpe=None, bench_sharpe=0.1)

    def test_boundary_barely_above(self):
        assert gate_decision(fixed_sharpe=1e-9, bench_sharpe=0.0)
        assert gate_decision(fixed_sharpe=0.8 + 1e-9, bench_sharpe=0.8)


class TestRunSelectionGate:
    def test_pass_case(self):
        # phase=0 holds exactly the +3% bars; B&H eats the -2% bars too.
        result = run_selection_gate(
            ohlcv=alternating_ohlcv(), strategy=parity_strategy,
            per_split=PER_SPLIT, top_variant=TOP_VARIANT,
            timeframe="daily", costs=COSTS)
        assert result["gate"] == GATE_PASS
        assert result["fixed_sharpe"] > result["bench_sharpe"]
        assert result["fixed_sharpe"] > 0
        assert result["n_periods"] == 30
        assert len(result["fixed_per_split"]) == 3

    def test_fail_fixed_does_not_beat_bench(self):
        # phase=1 holds exactly the -2% bars: fixed < 0 < bench.
        result = run_selection_gate(
            ohlcv=alternating_ohlcv(), strategy=parity_strategy,
            per_split=PER_SPLIT, top_variant={"phase": 1},
            timeframe="daily", costs=COSTS)
        assert result["gate"] == GATE_FAIL
        assert "ungradeable" not in result["reason"]
        assert result["fixed_sharpe"] < result["bench_sharpe"]

    def test_fail_beats_bench_but_negative(self):
        # Held (odd) bars are volatile with a slightly negative mean;
        # unheld (even) bars lose a lot — fixed beats bench on Sharpe but
        # is itself negative, so the > 0 conjunct FAILs.
        n = 40
        rets = np.full(n, -0.04)
        odd = np.arange(1, n, 2)
        rets[odd] = np.where((odd // 2) % 2 == 0, 0.03, -0.034)
        result = run_selection_gate(
            ohlcv=ohlcv_from_rets(rets), strategy=parity_strategy,
            per_split=PER_SPLIT, top_variant=TOP_VARIANT,
            timeframe="daily", costs=COSTS)
        assert result["gate"] == GATE_FAIL
        assert result["fixed_sharpe"] > result["bench_sharpe"]
        assert result["fixed_sharpe"] < 0

    def test_nan_fixed_is_ungradeable_fail(self):
        # A never-trading fixed arm has zero-variance returns: NaN Sharpe.
        result = run_selection_gate(
            ohlcv=alternating_ohlcv(), strategy=flat_strategy,
            per_split=PER_SPLIT, top_variant=TOP_VARIANT,
            timeframe="daily", costs=COSTS)
        assert result["gate"] == GATE_FAIL
        assert "ungradeable" in result["reason"]
        assert result["fixed_sharpe"] is None  # NaN serialized as None

    def test_missing_per_split_is_ungradeable_fail(self):
        for empty in ([], None):
            result = run_selection_gate(
                ohlcv=alternating_ohlcv(), strategy=parity_strategy,
                per_split=empty, top_variant=TOP_VARIANT,
                timeframe="daily", costs=COSTS)
            assert result["gate"] == GATE_FAIL
            assert "ungradeable" in result["reason"]
            assert "per_split" in result["reason"]

    def test_non_contiguous_windows_are_ungradeable_fail(self):
        gapped = [{"test": [10, 20], "params": {"phase": 0}},
                  {"test": [21, 31], "params": {"phase": 0}}]
        result = run_selection_gate(
            ohlcv=alternating_ohlcv(), strategy=parity_strategy,
            per_split=gapped, top_variant=TOP_VARIANT,
            timeframe="daily", costs=COSTS)
        assert result["gate"] == GATE_FAIL
        assert "ungradeable" in result["reason"]
        assert "contiguous" in result["reason"]

    def test_window_beyond_data_is_ungradeable_fail(self):
        oob = [{"test": [10, 20], "params": {"phase": 0}},
               {"test": [20, 50], "params": {"phase": 0}}]
        result = run_selection_gate(
            ohlcv=alternating_ohlcv(n=40), strategy=parity_strategy,
            per_split=oob, top_variant=TOP_VARIANT,
            timeframe="daily", costs=COSTS)
        assert result["gate"] == GATE_FAIL
        assert "ungradeable" in result["reason"]

    def test_fidelity_guard_mismatch_is_ungradeable_fail(self):
        result = run_selection_gate(
            ohlcv=alternating_ohlcv(), strategy=parity_strategy,
            per_split=PER_SPLIT, top_variant=TOP_VARIANT,
            timeframe="daily", costs=COSTS,
            recorded_searched_sharpe=99.0)
        assert result["gate"] == GATE_FAIL
        assert "ungradeable" in result["reason"]
        assert "fidelity" in result["reason"]

    def test_fidelity_guard_match_passes_through(self):
        ohlcv = alternating_ohlcv()
        searched, _ = stitched_replay(ohlcv, parity_strategy, PER_SPLIT,
                                      "daily", costs=COSTS)
        recorded = metrics.sharpe(searched, "daily")
        result = run_selection_gate(
            ohlcv=ohlcv, strategy=parity_strategy, per_split=PER_SPLIT,
            top_variant=TOP_VARIANT, timeframe="daily", costs=COSTS,
            recorded_searched_sharpe=recorded)
        assert result["gate"] == GATE_PASS
        assert result["searched_sharpe"] == pytest.approx(recorded)

    def test_selection_gap_sign(self):
        # Searched arm picked the bad parity on two splits: it must come
        # out BELOW the fixed config, so the informational gap < 0.
        degraded = [{"test": [10, 20], "params": {"phase": 1}},
                    {"test": [20, 30], "params": {"phase": 1}},
                    {"test": [30, 40], "params": {"phase": 0}}]
        result = run_selection_gate(
            ohlcv=alternating_ohlcv(), strategy=parity_strategy,
            per_split=degraded, top_variant=TOP_VARIANT,
            timeframe="daily", costs=COSTS)
        assert result["selection_gap"] < 0
        assert result["selection_gap"] == pytest.approx(
            result["searched_sharpe"] - result["fixed_sharpe"])


class TestReasonClass:
    """The additive machine-readable taxonomy (docs/selection-fair-gate.md
    § reason_class): one class per existing outcome path, decisions and all
    pre-existing fields unchanged."""

    def _gate(self, **overrides):
        kwargs = dict(ohlcv=alternating_ohlcv(), strategy=parity_strategy,
                      per_split=PER_SPLIT, top_variant=TOP_VARIANT,
                      timeframe="daily", costs=COSTS)
        kwargs.update(overrides)
        return run_selection_gate(**kwargs)

    def test_pass_class(self):
        result = self._gate()
        assert result["gate"] == GATE_PASS
        assert result["reason_class"] == selection_gate.REASON_PASS

    def test_fail_underperform_class(self):
        # Fixed arm (phase=0 holds the odd-index bars) earns a small
        # positive return on held bars while the unheld even bars rally
        # hard: fixed Sharpe > 0 but loses to B&H — only the
        # beat-the-benchmark conjunct fails.
        n = 40
        rets = np.where(np.arange(n) % 2 == 1, 0.005, 0.04)
        result = self._gate(ohlcv=ohlcv_from_rets(rets))
        assert result["gate"] == GATE_FAIL
        assert result["fixed_sharpe"] > 0
        assert result["fixed_sharpe"] < result["bench_sharpe"]
        assert (result["reason_class"]
                == selection_gate.REASON_FAIL_UNDERPERFORM)

    def test_fail_nonpositive_class_beats_bench(self):
        # The test_fail_beats_bench_but_negative fixture: fixed > bench
        # but fixed < 0 — the > 0 conjunct fails.
        n = 40
        rets = np.full(n, -0.04)
        odd = np.arange(1, n, 2)
        rets[odd] = np.where((odd // 2) % 2 == 0, 0.03, -0.034)
        result = self._gate(ohlcv=ohlcv_from_rets(rets))
        assert result["gate"] == GATE_FAIL
        assert result["fixed_sharpe"] > result["bench_sharpe"]
        assert result["fixed_sharpe"] < 0
        assert (result["reason_class"]
                == selection_gate.REASON_FAIL_NONPOSITIVE)

    def test_fail_nonpositive_takes_precedence_when_both_fail(self):
        # phase=1 holds exactly the -2% bars: fixed < 0 AND fixed < bench
        # — NONPOSITIVE wins over UNDERPERFORM by the documented rule.
        result = self._gate(top_variant={"phase": 1})
        assert result["gate"] == GATE_FAIL
        assert result["fixed_sharpe"] < 0
        assert result["fixed_sharpe"] < result["bench_sharpe"]
        assert (result["reason_class"]
                == selection_gate.REASON_FAIL_NONPOSITIVE)

    def test_ungradeable_missing_windows_class(self):
        for empty in ([], None):
            result = self._gate(per_split=empty)
            assert (result["reason_class"]
                    == selection_gate.REASON_UNGRADEABLE_MISSING_WINDOWS)

    def test_ungradeable_drift_class(self):
        oob = [{"test": [10, 20], "params": {"phase": 0}},
               {"test": [20, 50], "params": {"phase": 0}}]
        result = self._gate(per_split=oob)
        assert (result["reason_class"]
                == selection_gate.REASON_UNGRADEABLE_DRIFT)

    def test_ungradeable_noncontiguous_class(self):
        gapped = [{"test": [10, 20], "params": {"phase": 0}},
                  {"test": [21, 31], "params": {"phase": 0}}]
        result = self._gate(per_split=gapped)
        assert (result["reason_class"]
                == selection_gate.REASON_UNGRADEABLE_NONCONTIGUOUS)

    def test_ungradeable_fidelity_class(self):
        result = self._gate(recorded_searched_sharpe=99.0)
        assert (result["reason_class"]
                == selection_gate.REASON_UNGRADEABLE_FIDELITY)

    def test_ungradeable_nan_class(self):
        result = self._gate(strategy=flat_strategy)
        assert (result["reason_class"]
                == selection_gate.REASON_UNGRADEABLE_NAN)

    def test_taxonomy_is_closed_and_partitioned(self):
        # Every class this suite exercises is in REASON_CLASSES; the
        # ungradeable subset is exactly the UNGRADEABLE_* names.
        assert selection_gate.UNGRADEABLE_CLASSES < \
            selection_gate.REASON_CLASSES
        assert all(c.startswith("UNGRADEABLE_")
                   for c in selection_gate.UNGRADEABLE_CLASSES)
        assert len(selection_gate.REASON_CLASSES) == 8

    def test_every_result_carries_reason_class_in_taxonomy(self):
        results = [
            self._gate(),                                  # PASS
            self._gate(top_variant={"phase": 1}),          # rule fail
            self._gate(per_split=None),                    # missing windows
            self._gate(recorded_searched_sharpe=99.0),     # fidelity
            self._gate(strategy=flat_strategy),            # NaN
        ]
        for result in results:
            assert result["reason_class"] in selection_gate.REASON_CLASSES
            assert ((result["reason_class"] == selection_gate.REASON_PASS)
                    == (result["gate"] == GATE_PASS))
            assert ((result["reason_class"]
                     in selection_gate.UNGRADEABLE_CLASSES)
                    == ("ungradeable" in result["reason"]))

    def test_backward_compatible_schema_superset(self):
        # Additive only: every pre-existing key is still present on both
        # a PASS and an ungradeable FAIL result.
        legacy_keys = {"gate", "reason", "fixed_sharpe", "bench_sharpe",
                       "searched_sharpe", "selection_gap", "n_periods",
                       "fixed_per_split"}
        for result in (self._gate(), self._gate(per_split=None)):
            assert legacy_keys <= set(result)


class TestApplyGate:
    PASS_RESULT = {"gate": GATE_PASS}
    FAIL_RESULT = {"gate": GATE_FAIL}

    def test_keep_dev_demoted_on_fail(self):
        assert apply_gate(promotion.VERDICT_KEEP_DEV,
                          self.FAIL_RESULT) == promotion.SWEEP_KILL

    def test_sweep_keep_demoted_on_fail(self):
        assert apply_gate(promotion.SWEEP_KEEP,
                          self.FAIL_RESULT) == promotion.SWEEP_KILL

    def test_keep_dev_kept_on_pass(self):
        assert apply_gate(promotion.VERDICT_KEEP_DEV,
                          self.PASS_RESULT) == promotion.VERDICT_KEEP_DEV

    def test_kill_and_kill_sig_pass_through(self):
        for verdict in (promotion.SWEEP_KILL, promotion.SWEEP_KILL_SIG):
            assert apply_gate(verdict, self.FAIL_RESULT) == verdict
            assert apply_gate(verdict, self.PASS_RESULT) == verdict

    def test_keep_dev_string_pinned_to_historical_literal(self):
        # The constant must equal the literal every r2-r5 runner wrote.
        assert promotion.VERDICT_KEEP_DEV == "KEEP (dev-candidate only)"


class TestCommittedArtifactIntegration:
    """Read-only pin against a committed R5-D artifact: the gate module
    must reproduce the recorded fixed/bench Sharpes exactly (local cached
    data only — no network)."""

    ARTIFACT = (REPO_ROOT / "experiments" / "sweeps" / "r5-selection-fair"
                / "r3-btc-coverage__bollinger_breakout__BTC-USD__daily.json")

    def test_reproduces_r5d_btc_lane(self):
        if not self.ARTIFACT.exists():  # pragma: no cover
            pytest.skip("committed R5-D artifact not present")
        record = json.loads(self.ARTIFACT.read_text())
        source = json.loads((REPO_ROOT / record["source_lane"]).read_text())
        from trading_lab.data import load_ohlcv
        from trading_lab.strategies import STRATEGIES
        ohlcv = load_ohlcv(record["instrument"], record["timeframe"])
        if int(len(ohlcv)) != source["n_bars"]:  # pragma: no cover
            pytest.skip("local cache drifted from committed lane")
        result = run_selection_gate(
            ohlcv=ohlcv, strategy=STRATEGIES[record["family"]],
            per_split=source["walk_forward"]["per_split"],
            top_variant=record["fixed_config"],
            timeframe=record["timeframe"], costs=record["costs"],
            recorded_searched_sharpe=(source["walk_forward"]
                                      ["oos_metrics"]["sharpe"]))
        assert result["gate"] == GATE_PASS  # BTC lane passed R5-D's rule
        for key, recorded in (("fixed_sharpe",
                               record["fixed_stitched_sharpe"]),
                              ("bench_sharpe",
                               record["benchmark_stitched_sharpe"]),
                              ("searched_sharpe",
                               record["searched_stitched_sharpe"]),
                              ("selection_gap", record["selection_gap"])):
            assert math.isclose(result[key], recorded, abs_tol=1e-12), key

    def test_committed_r5d_windows_are_contiguous(self):
        # The gate's contiguity hard-check must hold on real committed
        # per_split layouts, not just synthetic ones.
        if not self.ARTIFACT.exists():  # pragma: no cover
            pytest.skip("committed R5-D artifact not present")
        record = json.loads(self.ARTIFACT.read_text())
        source = json.loads((REPO_ROOT / record["source_lane"]).read_text())
        windows = [r["test"]
                   for r in source["walk_forward"]["per_split"]]
        for prev, nxt in zip(windows, windows[1:]):
            assert nxt[0] == prev[1]
