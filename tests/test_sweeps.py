"""Sweep-grid tests: bounded counts, constraint filtering, runnable variants."""

import numpy as np
import pandas as pd
import pytest

from trading_lab import sweeps
from trading_lab.strategies import (STRATEGIES, TREND_FOLLOWING_FAMILY,
                                    VIDEO_STRATEGY_FAMILY)


class TestTrendFollowingGrids:
    def test_families_match_strategy_registry(self):
        assert set(sweeps.TREND_FOLLOWING_FAMILIES) == set(TREND_FOLLOWING_FAMILY)
        for fam in sweeps.TREND_FOLLOWING_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the variant counts reported in ledger
        # records and docs/p1-trend-following-results.md must match these.
        counts = sweeps.variants_per_family()
        assert counts == {"sma_crossover": 44, "ema_crossover": 44,
                          "macd": 48, "donchian": 41}
        assert sweeps.total_variants() == 177
        for fam, n in counts.items():
            assert 40 <= n <= 80, f"{fam} grid out of the bounded range"

    def test_constraints_filtered(self):
        for params in sweeps.variants("sma_crossover"):
            assert params["fast"] < params["slow"]
        for params in sweeps.variants("macd"):
            assert params["fast"] < params["slow"]
        for params in sweeps.variants("donchian"):
            assert params["exit"] <= params["entry"]

    def test_every_variant_runs(self, random_walk):
        # Every grid point must be accepted by its strategy (no ValueError)
        # and emit valid positions.
        for fam in sweeps.TREND_FOLLOWING_FAMILIES:
            for params in sweeps.variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.variants("astrology")

    def test_deterministic_order(self):
        assert sweeps.variants("donchian") == sweeps.variants("donchian")


class TestVideoStrategyGrids:
    def test_families_match_strategy_registry(self):
        assert set(sweeps.VIDEO_STRATEGY_FAMILIES) == set(VIDEO_STRATEGY_FAMILY)
        for fam in sweeps.VIDEO_STRATEGY_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and docs/p1-video-strategy-results.md must match these.
        counts = sweeps.video_variants_per_family()
        assert counts == {"supertrend_flip": 36, "macd_supertrend": 36,
                          "ema_crossover": 20}
        assert sweeps.video_total_variants() == 92

    def test_control_grid_contains_video_winner(self):
        # The video's stated best dual-EMA setting (slow=400, fast=45) must be
        # a grid point of the control interpretation.
        assert {"fast": 45, "slow": 400} in sweeps.video_variants("ema_crossover")
        for params in sweeps.video_variants("ema_crossover"):
            assert params["fast"] < params["slow"]

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.VIDEO_STRATEGY_FAMILIES:
            for params in sweeps.video_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.video_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.video_variants("supertrend_flip")
                == sweeps.video_variants("supertrend_flip"))


class TestMeanReversionGrids:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import MEAN_REVERSION_FAMILY
        assert set(sweeps.MEAN_REVERSION_FAMILIES) == set(MEAN_REVERSION_FAMILY)
        for fam in sweeps.MEAN_REVERSION_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and docs/p1-mean-reversion-results.md must match these.
        counts = sweeps.mean_reversion_variants_per_family()
        assert counts == {"rsi_mean_reversion": 48,
                          "bollinger_reversion": 48,
                          "pullback": 48}
        assert sweeps.mean_reversion_total_variants() == 144
        for fam, n in counts.items():
            assert 40 <= n <= 80, f"{fam} grid out of the bounded range"

    def test_constraints_filtered(self):
        for params in sweeps.mean_reversion_variants("rsi_mean_reversion"):
            assert params["oversold"] < params["overbought"]
        for params in sweeps.mean_reversion_variants("bollinger_reversion"):
            assert params["z_exit"] > -params["z_entry"]

    def test_pullback_grid_includes_unfiltered_and_filtered(self):
        # The pullback sub-family must probe both with and without the
        # long-term trend filter (trend_len=0 disables it).
        trend_lens = {p["trend_len"]
                      for p in sweeps.mean_reversion_variants("pullback")}
        assert 0 in trend_lens and 200 in trend_lens

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.MEAN_REVERSION_FAMILIES:
            for params in sweeps.mean_reversion_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.mean_reversion_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.mean_reversion_variants("pullback")
                == sweeps.mean_reversion_variants("pullback"))


class TestR2VolFilteredTrendGrid:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R2_VOL_TREND_FAMILY
        assert set(sweeps.R2_VOL_TREND_FAMILIES) == set(R2_VOL_TREND_FAMILY)
        for fam in sweeps.R2_VOL_TREND_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_match_preregistration(self):
        # docs/research-round-2.md §3a is BINDING: 12 variants/instrument
        # (fast ∈ {10,20} × slow ∈ {50,100,200} × filter ∈ {on,off}) over
        # exactly 4 instruments = 48 registered configs.
        counts = sweeps.r2_vol_trend_variants_per_family()
        assert counts == {"vol_filtered_trend": 12}
        assert sweeps.R2_VOL_TREND_INSTRUMENTS == ("AAPL", "MSFT", "NVDA",
                                                   "GLD")
        assert sweeps.r2_vol_trend_total_configs() == 48

    def test_constraints_filtered_and_both_arms_present(self):
        variants = sweeps.r2_vol_trend_variants("vol_filtered_trend")
        for params in variants:
            assert params["fast"] < params["slow"]
        arms = {p["vol_filter"] for p in variants}
        assert arms == {True, False}  # filter-on + filter-off baseline

    def test_windows_not_swept(self):
        # The 20/252 vol-filter windows are frozen by the pre-registration:
        # no variant may override the strategy defaults.
        for params in sweeps.r2_vol_trend_variants("vol_filtered_trend"):
            assert "vol_window" not in params
            assert "med_window" not in params

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R2_VOL_TREND_FAMILIES:
            for params in sweeps.r2_vol_trend_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r2_vol_trend_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r2_vol_trend_variants("vol_filtered_trend")
                == sweeps.r2_vol_trend_variants("vol_filtered_trend"))


class TestR2KeltnerBreakoutGrid:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R2_KELTNER_FAMILY
        assert set(sweeps.R2_KELTNER_FAMILIES) == set(R2_KELTNER_FAMILY)
        for fam in sweeps.R2_KELTNER_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_match_preregistration(self):
        # docs/research-round-2.md §3b is BINDING: 6 variants/instrument
        # (n ∈ {20, 50} × m ∈ {1.5, 2.0, 2.5}) over exactly 4 instruments
        # = 24 registered configs.
        counts = sweeps.r2_keltner_variants_per_family()
        assert counts == {"keltner_breakout": 6}
        assert sweeps.R2_KELTNER_INSTRUMENTS == ("BTC-USD", "META", "AMZN",
                                                 "SLV")
        assert sweeps.r2_keltner_total_configs() == 24

    def test_grid_is_exactly_the_registered_product(self):
        variants = sweeps.r2_keltner_variants("keltner_breakout")
        assert ({(p["n"], p["m"]) for p in variants}
                == {(n, m) for n in (20, 50) for m in (1.5, 2.0, 2.5)})
        for params in variants:
            assert set(params) == {"n", "m"}  # nothing else is swept

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R2_KELTNER_FAMILIES:
            for params in sweeps.r2_keltner_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r2_keltner_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r2_keltner_variants("keltner_breakout")
                == sweeps.r2_keltner_variants("keltner_breakout"))


class TestR2XsecMomentumGrid:
    def test_family_in_portfolio_registry_not_single_instrument(self):
        from trading_lab.strategies import PORTFOLIO_STRATEGIES, R2_XSEC_FAMILY
        assert set(sweeps.R2_XSEC_FAMILIES) == set(R2_XSEC_FAMILY)
        for fam in sweeps.R2_XSEC_FAMILIES:
            assert fam in PORTFOLIO_STRATEGIES
            assert fam not in STRATEGIES  # panel interface, not per-ticker

    def test_counts_match_preregistration(self):
        # docs/research-round-2.md §3c is BINDING: L ∈ {63, 126, 252} ×
        # k ∈ {2, 3} = 6 configs over ONE portfolio of all 9 cached daily
        # instruments — portfolio lane, so configs are NOT multiplied by
        # instruments.
        counts = sweeps.r2_xsec_variants_per_family()
        assert counts == {"xsec_momentum": 6}
        assert sweeps.R2_XSEC_INSTRUMENTS == ("AAPL", "AMZN", "BTC-USD",
                                              "GLD", "GOOGL", "META",
                                              "MSFT", "NVDA", "SLV")
        assert len(sweeps.R2_XSEC_INSTRUMENTS) == 9
        assert sweeps.r2_xsec_total_configs() == 6

    def test_grid_is_exactly_the_registered_product(self):
        variants = sweeps.r2_xsec_variants("xsec_momentum")
        assert ({(p["L"], p["k"]) for p in variants}
                == {(L, k) for L in (63, 126, 252) for k in (2, 3)})
        for params in variants:
            assert set(params) == {"L", "k"}  # nothing else is swept

    def test_rebalance_interval_frozen_not_swept(self):
        assert sweeps.R2_XSEC_REBALANCE_EVERY == 21
        for params in sweeps.r2_xsec_variants("xsec_momentum"):
            assert "rebalance_every" not in params

    def test_every_variant_runs(self):
        from trading_lab.strategies import PORTFOLIO_STRATEGIES
        rng = np.random.default_rng(17)
        idx = pd.bdate_range("2020-01-01", periods=300)
        closes = pd.DataFrame(
            {t: 100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.02, 300)))
             for t in sweeps.R2_XSEC_INSTRUMENTS}, index=idx)
        for fam in sweeps.R2_XSEC_FAMILIES:
            for params in sweeps.r2_xsec_variants(fam):
                w = PORTFOLIO_STRATEGIES[fam](
                    closes, rebalance_every=sweeps.R2_XSEC_REBALANCE_EVERY,
                    **params)
                rows = w.dropna(how="all")
                assert len(rows) > 0
                assert np.allclose(rows.sum(axis=1), 1.0)

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r2_xsec_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r2_xsec_variants("xsec_momentum")
                == sweeps.r2_xsec_variants("xsec_momentum"))


class TestR3StochWillrGrid:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R3_STOCH_WILLR_FAMILY
        assert (set(sweeps.R3_STOCH_WILLR_FAMILIES)
                == set(R3_STOCH_WILLR_FAMILY))
        for fam in sweeps.R3_STOCH_WILLR_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-stoch-willr sweep files must match these. 12 variants
        # per family over the full 8-ticker universe = 192 registered
        # configs.
        from trading_lab import config
        counts = sweeps.r3_stoch_willr_variants_per_family()
        assert counts == {"stochastic_reversion": 12,
                          "williams_r_reversion": 12}
        assert sweeps.R3_STOCH_WILLR_INSTRUMENTS == tuple(config.UNIVERSE)
        assert len(sweeps.R3_STOCH_WILLR_INSTRUMENTS) == 8
        assert sweeps.r3_stoch_willr_total_configs() == 192

    def test_constraints_filtered_and_nothing_else_swept(self):
        # The stochastic d_period smoothing (3) is frozen at the strategy
        # default and NOT swept.
        for params in sweeps.r3_stoch_willr_variants("stochastic_reversion"):
            assert params["buy_below"] < params["sell_above"]
            assert set(params) == {"k_period", "buy_below", "sell_above"}
        for params in sweeps.r3_stoch_willr_variants("williams_r_reversion"):
            assert params["buy_below"] < params["sell_above"]
            assert set(params) == {"period", "buy_below", "sell_above"}

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_STOCH_WILLR_FAMILIES:
            for params in sweeps.r3_stoch_willr_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_stoch_willr_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_stoch_willr_variants("stochastic_reversion")
                == sweeps.r3_stoch_willr_variants("stochastic_reversion"))


class TestR3RocAdxGrid:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R3_ROC_ADX_FAMILY
        assert set(sweeps.R3_ROC_ADX_FAMILIES) == set(R3_ROC_ADX_FAMILY)
        for fam in sweeps.R3_ROC_ADX_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-roc-adx sweep files must match these. 12 variants per
        # family over the full 8-ticker universe = 192 registered configs.
        from trading_lab import config
        counts = sweeps.r3_roc_adx_variants_per_family()
        assert counts == {"roc_momentum": 12, "adx_filtered_sma": 12}
        assert sweeps.R3_ROC_ADX_INSTRUMENTS == tuple(config.UNIVERSE)
        assert len(sweeps.R3_ROC_ADX_INSTRUMENTS) == 8
        assert sweeps.r3_roc_adx_total_configs() == 192

    def test_constraints_filtered_and_nothing_else_swept(self):
        # The ADX period (Wilder default 14) is frozen at the strategy
        # default and NOT swept.
        for params in sweeps.r3_roc_adx_variants("roc_momentum"):
            assert params["exit"] <= params["entry"]
            assert set(params) == {"lookback", "entry", "exit"}
        for params in sweeps.r3_roc_adx_variants("adx_filtered_sma"):
            assert params["fast"] < params["slow"]
            assert set(params) == {"fast", "slow", "adx_min"}

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_ROC_ADX_FAMILIES:
            for params in sweeps.r3_roc_adx_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_roc_adx_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_roc_adx_variants("roc_momentum")
                == sweeps.r3_roc_adx_variants("roc_momentum"))
