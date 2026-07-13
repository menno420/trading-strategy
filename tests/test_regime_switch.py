"""R4-D `regime_switch` — trend-strength tercile regime switch with its
MANDATORY unconditional control arm (docs/research-round-4-plan.md § R4-D).

Pinned here, in the pre-declaration commit BEFORE the sweep runs:

* trailing-rank arithmetic (the tercile machinery, warm-up NaN rules);
* bucket assignment on synthetic data — a strong-trend segment routes to
  the trend component, a weak/choppy segment to the weak component, for
  BOTH registered metrics (adx, sma_slope);
* routing identity for EVERY bar: strong bucket -> trend component
  positions, weak bucket -> weak component positions, undefined -> flat;
* the control arm is STRICTLY the same components with the condition
  removed: weak_family="flat" == the plain ema_crossover trend component,
  weak_family="reversion" == the 0.5/0.5 mean of both components, and the
  control output is invariant to `metric` and `rank_window`;
* parameter validation.
"""

import numpy as np
import pandas as pd
import pytest

from trading_lab.strategies import (STRATEGIES, ema_crossover, regime_switch,
                                    rsi_mean_reversion)

from conftest import make_ohlcv

# Frozen component params used throughout (the registered R4-D components).
COMPONENTS = dict(trend_fast=20, trend_slow=100,
                  rsi_period=2, rsi_oversold=20, rsi_overbought=60)


def _three_regime_ohlcv() -> pd.DataFrame:
    """Deterministic 450-bar series: chop (0-149) -> strong exponential
    trend (150-299, constant relative slope) -> chop (300-449)."""
    t1 = np.arange(150)
    chop1 = 100 + 3 * np.sin(2 * np.pi * t1 / 12)
    trend = chop1[-1] * 1.005 ** np.arange(1, 151)
    chop2 = trend[-1] + 0.05 * trend[-1] * np.sin(2 * np.pi
                                                  * np.arange(150) / 12)
    return make_ohlcv(np.concatenate([chop1, trend, chop2]))


class TestTrailingRank:
    def test_increasing_series_ranks_top(self):
        s = pd.Series(np.arange(20, dtype=float))
        r = regime_switch.trailing_rank(s, 5)
        assert r.iloc[:4].isna().all()          # warm-up: no full window
        assert (r.iloc[4:] == 1.0).all()        # current bar is the max

    def test_decreasing_series_ranks_bottom(self):
        s = pd.Series(np.arange(20, 0, -1, dtype=float))
        r = regime_switch.trailing_rank(s, 5)
        assert (r.iloc[4:] == 0.2).all()        # only itself <= itself

    def test_leading_nans_delay_definition(self):
        s = pd.Series([np.nan] * 3 + list(np.arange(10, dtype=float)))
        r = regime_switch.trailing_rank(s, 5)
        # Full window of DEFINED values only exists from index 3 + 4.
        assert r.iloc[:7].isna().all()
        assert (r.iloc[7:] == 1.0).all()

    def test_rejects_bad_window(self):
        with pytest.raises(ValueError, match="rank_window"):
            regime_switch.trailing_rank(pd.Series([1.0, 2.0]), 1)


class TestBucketAssignment:
    """Strong-trend vs weak-trend segments route to the right bucket —
    for BOTH registered metrics (deterministic synthetic fixture; windows
    pinned with margin)."""

    def test_adx_buckets_track_regimes(self):
        oh = _three_regime_ohlcv()
        b = regime_switch.bucket_assignments(oh, "adx", 126,
                                             adx_period=7).reset_index(
                                                 drop=True)
        assert (b.iloc[170:300] == 1.0).all()   # trend segment: strong
        assert (b.iloc[310:425] == 0.0).all()   # chop segment: weak

    def test_sma_slope_buckets_track_regimes(self):
        oh = _three_regime_ohlcv()
        b = regime_switch.bucket_assignments(
            oh, "sma_slope", 126, slope_sma=20,
            slope_horizon=5).reset_index(drop=True)
        assert (b.iloc[160:300] == 1.0).mean() > 0.95   # trend: strong
        assert (b.iloc[310:400] == 0.0).all()           # chop: weak

    def test_warmup_undefined(self):
        oh = _three_regime_ohlcv()
        b = regime_switch.bucket_assignments(oh, "adx", 126, adx_period=7)
        # 2*adx_period ADX warm-up + a full 126-bar rank window first.
        assert b.iloc[:126].isna().all()

    def test_middle_tercile_holds_previous_bucket(self):
        # Hysteresis is implemented as ffill over strong/weak marks:
        # every defined bucket value equals the most recent boundary hit.
        oh = _three_regime_ohlcv()
        rank = regime_switch.trailing_rank(
            regime_switch.trend_strength(oh, "adx", adx_period=7), 126)
        raw = pd.Series(np.nan, index=oh.index)
        raw[rank >= regime_switch.STRONG_Q] = 1.0
        raw[rank <= regime_switch.WEAK_Q] = 0.0
        expected = raw.ffill()
        got = regime_switch.bucket_assignments(oh, "adx", 126, adx_period=7)
        pd.testing.assert_series_equal(got, expected)
        # and the fixture genuinely exercises middle-tercile bars:
        assert ((rank > regime_switch.WEAK_Q)
                & (rank < regime_switch.STRONG_Q)).any()


class TestConditionalRouting:
    """positions == the routed component on EVERY bar, both weak families."""

    @pytest.mark.parametrize("metric,kw", [
        ("adx", dict(adx_period=7)),
        ("sma_slope", dict(slope_sma=20, slope_horizon=5)),
    ])
    def test_routes_components_by_bucket(self, metric, kw):
        oh = _three_regime_ohlcv()
        bucket = regime_switch.bucket_assignments(oh, metric, 126, **kw)
        trend = ema_crossover.generate(oh, fast=20, slow=100)
        weak = rsi_mean_reversion.generate(oh, period=2, oversold=20,
                                           overbought=60)
        pos = regime_switch.generate(oh, metric=metric, rank_window=126,
                                     weak_family="reversion",
                                     regime_condition=True,
                                     **COMPONENTS, **kw)
        strong_bars, weak_bars = bucket == 1.0, bucket == 0.0
        assert strong_bars.any() and weak_bars.any()
        assert pos[strong_bars].equals(trend[strong_bars])
        assert pos[weak_bars].equals(weak[weak_bars])
        assert (pos[bucket.isna()] == 0.0).all()

    def test_flat_weak_family_is_flat_in_weak_bucket(self):
        oh = _three_regime_ohlcv()
        bucket = regime_switch.bucket_assignments(oh, "adx", 126,
                                                  adx_period=7)
        pos = regime_switch.generate(oh, metric="adx", rank_window=126,
                                     weak_family="flat",
                                     regime_condition=True,
                                     adx_period=7, **COMPONENTS)
        assert (pos[bucket == 0.0] == 0.0).all()
        trend = ema_crossover.generate(oh, fast=20, slow=100)
        assert pos[bucket == 1.0].equals(trend[bucket == 1.0])


class TestControlArm:
    """The MANDATORY unconditional control arm: strictly the same
    components with the regime condition removed — nothing else."""

    def test_flat_control_is_plain_trend_component(self, random_walk):
        ctrl = regime_switch.generate(random_walk, weak_family="flat",
                                      regime_condition=False, **COMPONENTS)
        trend = ema_crossover.generate(random_walk, fast=20, slow=100)
        pd.testing.assert_series_equal(ctrl, trend,
                                       check_names=False)

    def test_reversion_control_is_equal_weight_mean(self, random_walk):
        ctrl = regime_switch.generate(random_walk, weak_family="reversion",
                                      regime_condition=False, **COMPONENTS)
        trend = ema_crossover.generate(random_walk, fast=20, slow=100)
        weak = rsi_mean_reversion.generate(random_walk, period=2,
                                           oversold=20, overbought=60)
        pd.testing.assert_series_equal(ctrl, 0.5 * (trend + weak),
                                       check_names=False)
        # fractional disagreement positions are expected and in-range
        assert set(np.unique(ctrl)) <= {0.0, 0.5, 1.0}

    @pytest.mark.parametrize("weak_family", ["flat", "reversion"])
    def test_control_invariant_to_metric_and_window(self, random_walk,
                                                    weak_family):
        base = regime_switch.generate(random_walk, weak_family=weak_family,
                                      regime_condition=False, **COMPONENTS)
        for metric in regime_switch.METRICS:
            for rank_window in (30, 126, 504):
                other = regime_switch.generate(
                    random_walk, metric=metric, rank_window=rank_window,
                    weak_family=weak_family, regime_condition=False,
                    **COMPONENTS)
                pd.testing.assert_series_equal(base, other)

    def test_arms_share_identical_components(self):
        """Where the conditional arm is in the strong bucket its position
        IS the flat-control's position bar-for-bar — the arms differ only
        in the condition, never in the components."""
        oh = _three_regime_ohlcv()
        bucket = regime_switch.bucket_assignments(oh, "adx", 126,
                                                  adx_period=7)
        cond = regime_switch.generate(oh, metric="adx", rank_window=126,
                                      weak_family="flat",
                                      regime_condition=True,
                                      adx_period=7, **COMPONENTS)
        ctrl = regime_switch.generate(oh, weak_family="flat",
                                      regime_condition=False, **COMPONENTS)
        strong = bucket == 1.0
        assert strong.any()
        assert cond[strong].equals(ctrl[strong])


class TestValidation:
    def test_rejects_bad_metric(self, random_walk):
        with pytest.raises(ValueError, match="metric"):
            regime_switch.generate(random_walk, metric="vix")

    def test_rejects_bad_weak_family(self, random_walk):
        with pytest.raises(ValueError, match="weak_family"):
            regime_switch.generate(random_walk, weak_family="short")

    def test_rejects_bad_rank_window(self, random_walk):
        with pytest.raises(ValueError, match="rank_window"):
            regime_switch.generate(random_walk, rank_window=1)

    def test_registered_in_strategies(self):
        assert STRATEGIES["regime_switch"] is regime_switch.generate

    def test_trend_strength_rejects_bad_metric(self, random_walk):
        with pytest.raises(ValueError, match="metric"):
            regime_switch.trend_strength(random_walk, "macd")
