"""R4-E `crossasset_gate` — cross-asset momentum exposure gate with its
MANDATORY ungated control arm (docs/research-round-4-plan.md § R4-E).

Pinned here, in the pre-declaration commit BEFORE the sweep runs:

* gate-momentum arithmetic (trailing on the GATE calendar, warm-up NaN);
* NO LOOKAHEAD in the cross-calendar alignment — the program's first
  two-instrument strategy: the gate value applied at equity bar t is the
  most recent gate-asset value with timestamp <= t (shifting the gate
  series by one bar moves the position change by exactly one bar; a gate
  bar stamped AFTER t can never influence positions[t]; prefix invariance
  in the gate series holds exactly);
* gate routing on synthetic data: position == the frozen trend component
  where the gate is open, 0 where it is closed or undefined;
* the control arm is STRICTLY the same component with the gate removed:
  gated=False == the plain ema_crossover trend component, invariant to
  `gate_asset`, `gate_lookback` and `gate_close`;
* parameter validation and registration.

All synthetic — no cache reads in this file (the gate series is always
injected via `gate_close`).
"""

import numpy as np
import pandas as pd
import pytest

from trading_lab.strategies import STRATEGIES, crossasset_gate, ema_crossover

from conftest import make_ohlcv

# Frozen equity component used throughout (the registered R4-E component).
COMPONENTS = dict(trend_fast=20, trend_slow=100)


def _trending_equity(n=300) -> pd.DataFrame:
    """Deterministic rising equity so the trend component is long for a
    long stretch (the gate, not the component, decides exposure)."""
    t = np.arange(n)
    close = 100 * 1.003 ** t + np.sin(2 * np.pi * t / 15)
    return make_ohlcv(close)


def _gate_series(values, index) -> pd.Series:
    return pd.Series(np.asarray(values, dtype=float), index=index,
                     name="close")


class TestGateMomentum:
    def test_trailing_arithmetic(self):
        idx = pd.bdate_range("2024-01-01", periods=10)
        g = _gate_series(np.arange(1, 11), idx)
        mom = crossasset_gate.gate_momentum(g, 3)
        assert mom.iloc[:3].isna().all()             # warm-up undefined
        assert mom.iloc[3] == pytest.approx(4 / 1 - 1)
        assert mom.iloc[9] == pytest.approx(10 / 7 - 1)

    def test_rejects_bad_lookback(self):
        idx = pd.bdate_range("2024-01-01", periods=5)
        with pytest.raises(ValueError, match="gate_lookback"):
            crossasset_gate.gate_momentum(_gate_series(np.ones(5), idx), 0)


class TestNoLookaheadAlignment:
    """The engine/rail point of this slice: gate signal at equity bar t
    uses gate-asset data <= t ONLY (the engine then fills at t+1)."""

    def test_same_calendar_alignment_is_exact(self):
        oh = _trending_equity()
        # gate momentum flips positive exactly at a known bar
        n = len(oh)
        vals = np.concatenate([np.linspace(100, 80, 150),
                               np.linspace(80, 120, n - 150)])
        g = _gate_series(vals, oh.index)
        open_ = crossasset_gate.gate_signal(oh.index, g, 21)
        mom = g / g.shift(21) - 1.0
        pd.testing.assert_series_equal(open_, mom > 0, check_names=False)

    def test_gate_bar_after_t_never_influences_t(self):
        """Prefix invariance in the GATE series: truncating the gate
        series to timestamps <= t leaves the position at every bar <= t
        unchanged — future gate bars are invisible."""
        oh = _trending_equity()
        rng = np.random.default_rng(7)
        g = _gate_series(
            100 * np.exp(np.cumsum(rng.normal(0, 0.02, len(oh)))), oh.index)
        full = crossasset_gate.generate(oh, gate_close=g, gate_lookback=21,
                                        **COMPONENTS)
        for cut in (100, 200, 280):
            t = oh.index[cut - 1]
            truncated = crossasset_gate.generate(
                oh, gate_close=g[g.index <= t], gate_lookback=21,
                **COMPONENTS)
            pd.testing.assert_series_equal(full.iloc[:cut],
                                           truncated.iloc[:cut])

    def test_shifting_gate_series_shifts_the_signal_one_bar(self):
        """Delaying the gate series by one gate bar moves every gate
        decision one bar later — the signature of a strictly-backward
        alignment (a lookahead join would leave it unchanged)."""
        oh = _trending_equity()
        n = len(oh)
        vals = np.concatenate([np.linspace(100, 80, 150),
                               np.linspace(80, 120, n - 150)])
        g = _gate_series(vals, oh.index)
        open_now = crossasset_gate.gate_signal(oh.index, g, 21)
        g_delayed = g.shift(1)
        open_delayed = crossasset_gate.gate_signal(oh.index, g_delayed, 21)
        assert not open_now.equals(open_delayed)
        pd.testing.assert_series_equal(open_delayed.iloc[1:],
                                       open_now.shift(1).iloc[1:]
                                       .astype(bool), check_names=False)

    def test_misaligned_calendars_use_most_recent_gate_bar(self):
        """Gate on a sparser calendar: the value applied at equity bar t
        is the most recent gate bar <= t (ffill), never the next one."""
        oh = _trending_equity(60)
        # gate trades only every 5th equity day
        gate_idx = oh.index[::5]
        g = _gate_series(np.linspace(100, 120, len(gate_idx)), gate_idx)
        open_ = crossasset_gate.gate_signal(oh.index, g, 2)
        mom = (g / g.shift(2) - 1.0)
        expected = (mom.reindex(oh.index, method="ffill") > 0)
        pd.testing.assert_series_equal(open_, expected, check_names=False)
        # between gate bars the applied value is constant (held, not
        # interpolated, not from the future)
        assert bool(open_.loc[oh.index[11]]) == bool(open_.loc[oh.index[10]])

    def test_equity_bars_before_first_gate_bar_are_flat(self):
        oh = _trending_equity(120)
        gate_idx = oh.index[60:]  # gate history starts mid-sample
        g = _gate_series(np.linspace(100, 200, len(gate_idx)), gate_idx)
        pos = crossasset_gate.generate(oh, gate_close=g, gate_lookback=5,
                                       **COMPONENTS)
        assert (pos.iloc[:60] == 0.0).all()


class TestGateRouting:
    def test_open_gate_passes_trend_component_through(self):
        oh = _trending_equity()
        g = _gate_series(np.linspace(100, 200, len(oh)), oh.index)  # mom>0
        pos = crossasset_gate.generate(oh, gate_close=g, gate_lookback=21,
                                       **COMPONENTS)
        trend = ema_crossover.generate(oh, fast=20, slow=100)
        # after gate warm-up the gate is always open -> pure component
        pd.testing.assert_series_equal(pos.iloc[21:], trend.iloc[21:],
                                       check_names=False)
        # during gate warm-up: flat regardless of the component
        assert (pos.iloc[:21] == 0.0).all()

    def test_closed_gate_is_always_flat(self):
        oh = _trending_equity()
        g = _gate_series(np.linspace(200, 100, len(oh)), oh.index)  # mom<0
        pos = crossasset_gate.generate(oh, gate_close=g, gate_lookback=21,
                                       **COMPONENTS)
        assert (pos == 0.0).all()

    def test_routing_identity_every_bar(self):
        oh = _trending_equity()
        rng = np.random.default_rng(11)
        g = _gate_series(
            100 * np.exp(np.cumsum(rng.normal(0, 0.03, len(oh)))), oh.index)
        open_ = crossasset_gate.gate_signal(oh.index, g, 21)
        trend = ema_crossover.generate(oh, fast=20, slow=100)
        pos = crossasset_gate.generate(oh, gate_close=g, gate_lookback=21,
                                       **COMPONENTS)
        assert open_.any() and (~open_).any()
        assert pos[open_].equals(trend[open_])
        assert (pos[~open_] == 0.0).all()

    def test_zero_momentum_is_closed(self):
        # strict sign rule: gate opens on mom > 0, not >= 0
        oh = _trending_equity(60)
        g = _gate_series(np.full(60, 100.0), oh.index)   # mom == 0
        pos = crossasset_gate.generate(oh, gate_close=g, gate_lookback=5,
                                       **COMPONENTS)
        assert (pos == 0.0).all()


class TestControlArm:
    """The MANDATORY ungated control arm: strictly the same component with
    the gate removed — nothing else."""

    def test_control_is_plain_trend_component(self, random_walk):
        ctrl = crossasset_gate.generate(random_walk, gated=False,
                                        **COMPONENTS)
        trend = ema_crossover.generate(random_walk, fast=20, slow=100)
        pd.testing.assert_series_equal(ctrl, trend, check_names=False)

    def test_control_invariant_to_gate_params(self, random_walk):
        base = crossasset_gate.generate(random_walk, gated=False,
                                        **COMPONENTS)
        junk_gate = _gate_series(np.linspace(1, 2, len(random_walk)),
                                 random_walk.index)
        for asset in ("TLT", "XOM", "GLD", "NOT-EVEN-REAL"):
            for lb in (0, 21, 252):
                other = crossasset_gate.generate(
                    random_walk, gate_asset=asset, gate_lookback=lb,
                    gated=False, gate_close=junk_gate, **COMPONENTS)
                pd.testing.assert_series_equal(base, other)

    def test_arms_share_identical_component(self):
        """Where the gate is open the gated arm's position IS the
        control's position bar-for-bar — the arms differ only in the
        gate, never in the component."""
        oh = _trending_equity()
        rng = np.random.default_rng(13)
        g = _gate_series(
            100 * np.exp(np.cumsum(rng.normal(0, 0.03, len(oh)))), oh.index)
        open_ = crossasset_gate.gate_signal(oh.index, g, 21)
        gated = crossasset_gate.generate(oh, gate_close=g, gate_lookback=21,
                                         **COMPONENTS)
        ctrl = crossasset_gate.generate(oh, gated=False, **COMPONENTS)
        assert open_.any()
        assert gated[open_].equals(ctrl[open_])


class TestValidation:
    def test_rejects_bad_lookback(self, random_walk):
        with pytest.raises(ValueError, match="gate_lookback"):
            crossasset_gate.generate(random_walk, gate_lookback=0,
                                     gate_close=_gate_series(
                                         np.ones(len(random_walk)),
                                         random_walk.index), **COMPONENTS)

    def test_rejects_unregistered_gate_asset_without_injection(self,
                                                               random_walk):
        # without an injected gate_close the asset must be in the
        # registered committed-cache universe
        with pytest.raises(ValueError, match="gate_asset"):
            crossasset_gate.generate(random_walk, gate_asset="VIX",
                                     **COMPONENTS)

    def test_registered_gate_universe(self):
        assert crossasset_gate.GATE_ASSETS == ("TLT", "XOM", "GLD")

    def test_registered_in_strategies(self):
        assert STRATEGIES["crossasset_gate"] is crossasset_gate.generate

    def test_positions_are_long_flat(self):
        oh = _trending_equity()
        rng = np.random.default_rng(17)
        g = _gate_series(
            100 * np.exp(np.cumsum(rng.normal(0, 0.03, len(oh)))), oh.index)
        pos = crossasset_gate.generate(oh, gate_close=g, gate_lookback=21,
                                       **COMPONENTS)
        assert not pos.isna().any()
        assert set(np.unique(pos)) <= {0.0, 1.0}
