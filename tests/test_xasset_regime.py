"""Round-11 cross-asset regime tests (docs/research-round-11-plan.md).

The headline is the NO-LOOKAHEAD / prefix-invariance test: regime-detection
lookahead is the #1 failure mode for this class, and the load-bearing guarantee
is that the causal regime score AND the conditioned position at bar t are
identical whether computed on the full series or on the series truncated at bar
t. If ``TestNoLookahead`` ever fails, the design leaks and must be fixed, never
papered over.
"""

import numpy as np
import pandas as pd
import pytest

from trading_lab import xasset_regime as xr


# ---------------------------------------------------------------------------
# Helpers: synthetic ALIGNED daily close panels (one shared NYSE-style index)
# ---------------------------------------------------------------------------

def _series(values, start="2020-01-01") -> pd.Series:
    idx = pd.bdate_range(start, periods=len(values))
    return pd.Series(np.asarray(values, dtype=float), index=idx)


def _aligned_panel(n=420, seed=7) -> dict:
    """A panel of aligned (shared-index) random-walk closes for every ticker
    R11 reads: the four breadth legs SPY/QQQ/GLD/TLT plus the NVDA target."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2020-01-01", periods=n)
    panel = {}
    for i, ticker in enumerate(("SPY", "QQQ", "GLD", "TLT", "NVDA")):
        # distinct drift/vol per leg so the scores are non-degenerate
        drift = 0.0004 + 0.0002 * i
        rets = rng.normal(drift, 0.012 + 0.002 * i, n)
        panel[ticker] = pd.Series(100.0 * np.exp(np.cumsum(rets)), index=idx)
    return panel


# ---------------------------------------------------------------------------
# Headline: causality / no-lookahead (prefix invariance under truncation)
# ---------------------------------------------------------------------------

class TestNoLookahead:
    """The load-bearing correctness guarantee: score AND conditioned position
    at bar t are IDENTICAL on the full series vs the series truncated at bar t
    (``series.iloc[:t+1]``). Trailing windows + rolling (never full-sample)
    normalization forbid any dependence on data with timestamp > t."""

    @pytest.mark.parametrize("signal", list(xr.REGIME_SIGNALS))
    @pytest.mark.parametrize("window", [63, 126, 252])
    def test_score_is_prefix_invariant(self, signal, window):
        panel = _aligned_panel()
        full = xr.regime_score(panel, signal, window)
        n = len(full)
        # probe a spread of bars, incl. deep in the fully-warmed region
        for t in (window + 5, window + 60, 300, 350, n - 1):
            trunc_panel = {k: v.iloc[:t + 1] for k, v in panel.items()}
            trunc = xr.regime_score(trunc_panel, signal, window)
            assert len(trunc) == t + 1
            a, b = full.iloc[t], trunc.iloc[t]
            # identical (both NaN in warm-up, or bit-for-bit equal once defined)
            assert (np.isnan(a) and np.isnan(b)) or a == b, (
                f"score leak at t={t} signal={signal} W={window}: "
                f"full={a!r} trunc={b!r}")

    @pytest.mark.parametrize("signal", list(xr.REGIME_SIGNALS))
    def test_conditioned_position_is_prefix_invariant(self, signal):
        panel = _aligned_panel()
        window, pwin = 63, 252
        full = xr.regime_conditioned_positions(
            panel, target="NVDA", signal=signal, window=window,
            percentile_window=pwin)
        n = len(full)
        # bars past the (window + pwin) warm-up are the meaningful, non-zero probes
        for t in (window + pwin + 1, window + pwin + 20, n - 1):
            trunc_panel = {k: v.iloc[:t + 1] for k, v in panel.items()}
            trunc = xr.regime_conditioned_positions(
                trunc_panel, target="NVDA", signal=signal, window=window,
                percentile_window=pwin)
            assert trunc.index.equals(panel["NVDA"].index[:t + 1])
            assert full.iloc[t] == trunc.iloc[t], (
                f"position leak at t={t} signal={signal}: "
                f"full={full.iloc[t]!r} trunc={trunc.iloc[t]!r}")

    def test_percentile_rank_never_uses_future_values(self):
        # A monotone-increasing score: each bar is the max of its trailing
        # window, so the causal rank is exactly 1.0 once warmed — a full-sample
        # rank would instead assign the early bars LOW ranks (the leak).
        score = _series(np.arange(1.0, 401.0))
        ranks = xr.rolling_percentile_rank(score, window=252)
        warmed = ranks.iloc[251:]
        assert not warmed.isna().any()
        assert np.allclose(warmed.values, 1.0)


# ---------------------------------------------------------------------------
# Shape / range / alignment / NaN-freeness
# ---------------------------------------------------------------------------

class TestShapeAndRange:
    @pytest.mark.parametrize("signal", list(xr.REGIME_SIGNALS))
    @pytest.mark.parametrize("target", ["SPY", "QQQ", "NVDA"])
    def test_position_in_unit_interval_no_nan_aligned(self, signal, target):
        panel = _aligned_panel()
        pos = xr.regime_conditioned_positions(
            panel, target=target, signal=signal, window=63)
        assert pos.index.equals(panel[target].index)  # aligned to the target
        assert not pos.isna().any()                    # NaN-free (warm-up -> 0)
        assert (pos >= 0.0).all() and (pos <= 1.0).all()

    @pytest.mark.parametrize("signal", list(xr.REGIME_SIGNALS))
    def test_warmup_bars_are_flat_zero(self, signal):
        panel = _aligned_panel()
        window = 63
        pos = xr.regime_conditioned_positions(
            panel, target="NVDA", signal=signal, window=window,
            percentile_window=252)
        # the first (window + 252 - 1) bars are undefined -> resolved to 0.0
        assert (pos.iloc[:window] == 0.0).all()

    def test_position_is_non_degenerate_when_warmed(self):
        # after warm-up the continuous conditioning takes a spread of values in
        # (0, 1], not a single constant — this is continuous, not a binary gate
        panel = _aligned_panel()
        pos = xr.regime_conditioned_positions(
            panel, target="NVDA", signal="xasset_eq_bond_mom", window=63,
            percentile_window=252)
        warmed = pos.iloc[63 + 252:]
        assert warmed.nunique() > 5
        assert warmed.max() <= 1.0 and warmed.min() >= 0.0

    def test_breadth_score_is_a_fraction(self):
        panel = _aligned_panel()
        score = xr.breadth_score(panel, window=63)
        warmed = score.dropna()
        assert set(np.unique(warmed.values)) <= {0.0, 0.25, 0.5, 0.75, 1.0}

    def test_unknown_signal_rejected(self):
        panel = _aligned_panel()
        with pytest.raises(ValueError, match="unknown regime signal"):
            xr.regime_score(panel, "astrology", 63)
        with pytest.raises(ValueError, match="unknown regime signal"):
            xr.regime_conditioned_positions(
                panel, target="SPY", signal="astrology", window=63)

    def test_bad_window_rejected(self):
        with pytest.raises(ValueError, match="window"):
            xr.trailing_total_return(_series([1, 2, 3]), 0)
        with pytest.raises(ValueError, match="window"):
            xr.rolling_percentile_rank(_series([1, 2, 3]), 0)


# ---------------------------------------------------------------------------
# Hand-constructed examples: one per signal (exact arithmetic)
# ---------------------------------------------------------------------------

class TestHandConstructedSignals:
    def test_eq_bond_mom_exact(self):
        # W=2: score_t = (SPY_t/SPY_{t-2} - 1) - (TLT_t/TLT_{t-2} - 1)
        spy = _series([100.0, 100.0, 110.0, 121.0])
        tlt = _series([100.0, 100.0, 90.0, 81.0])
        panel = {"SPY": spy, "TLT": tlt}
        score = xr.eq_bond_momentum_score(panel, window=2)
        # bar 2: SPY 100->110 (+0.10), TLT 100->90 (-0.10) => +0.10 - (-0.10)
        assert score.iloc[2] == pytest.approx(0.10 - (-0.10))
        # bar 3: SPY 100->121 (+0.21), TLT 100->81 (-0.19) => 0.21 - (-0.19)
        assert score.iloc[3] == pytest.approx(0.21 - (-0.19))
        assert np.isnan(score.iloc[0]) and np.isnan(score.iloc[1])  # warm-up
        # risk-on high: equities up while bonds down -> positive score
        assert score.iloc[2] > 0.0

    def test_metals_riskoff_exact(self):
        # W=2: score_t = -(GLD_t/GLD_{t-2} - 1); gold UP => risk-OFF => score DOWN
        gld = _series([100.0, 100.0, 120.0, 150.0])
        score = xr.metals_riskoff_score({"GLD": gld}, window=2)
        assert score.iloc[2] == pytest.approx(-(120.0 / 100.0 - 1.0))  # -0.20
        assert score.iloc[3] == pytest.approx(-(150.0 / 100.0 - 1.0))  # -0.50
        assert score.iloc[2] < 0.0 and score.iloc[3] < 0.0  # gold bid -> risk-off
        assert np.isnan(score.iloc[1])

    def test_breadth_exact_fraction(self):
        # W=3. At bar 3 each leg's SMA = mean of bars 1,2,3. Construct two legs
        # ABOVE their SMA and two BELOW => breadth = 2/4 = 0.5.
        up = _series([10.0, 11.0, 12.0, 20.0])    # 20 > mean(11,12,20)=14.33 -> above
        up2 = _series([10.0, 10.0, 10.0, 30.0])   # 30 > mean(10,10,30)=16.67 -> above
        down = _series([20.0, 12.0, 11.0, 10.0])  # 10 < mean(12,11,10)=11.0  -> below
        down2 = _series([50.0, 10.0, 10.0, 10.0]) # 10 < mean(10,10,10)=10.0  -> below (not >)
        panel = {"SPY": up, "QQQ": up2, "GLD": down, "TLT": down2}
        score = xr.breadth_score(panel, window=3)
        assert score.iloc[3] == pytest.approx(0.5)
        assert np.isnan(score.iloc[1])  # warm-up (SMA(3) undefined before bar 2)

    def test_breadth_all_above_is_one_all_below_is_zero(self):
        rising = _series([10.0, 11.0, 12.0, 13.0, 20.0])
        falling = _series([20.0, 13.0, 12.0, 11.0, 5.0])
        all_up = {a: rising for a in xr.BREADTH_ASSETS}
        all_down = {a: falling for a in xr.BREADTH_ASSETS}
        assert xr.breadth_score(all_up, window=3).iloc[4] == pytest.approx(1.0)
        assert xr.breadth_score(all_down, window=3).iloc[4] == pytest.approx(0.0)
