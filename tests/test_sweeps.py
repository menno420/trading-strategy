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


class TestR3NewTickersGrid:
    def test_families_are_existing_registered_strategies(self):
        # Slice 3 expands the instrument surface, not the strategy library:
        # every family must already exist in the registry.
        for fam in sweeps.R3_NEW_TICKERS_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-new-tickers sweep files must match these. 6 variants
        # per family × 3 families × 6 new instruments = 108 registered
        # configs.
        counts = sweeps.r3_new_tickers_variants_per_family()
        assert counts == {"donchian": 6, "sma_crossover": 6,
                          "rsi_mean_reversion": 6}
        assert len(sweeps.R3_NEW_TICKERS_INSTRUMENTS) == 6
        assert sweeps.r3_new_tickers_total_configs() == 108

    def test_instruments_disjoint_from_frozen_universe(self):
        # config.UNIVERSE is frozen (other sweeps depend on it); the new
        # instruments are lane-local and must not overlap it.
        from trading_lab import config
        assert not (set(sweeps.R3_NEW_TICKERS_INSTRUMENTS)
                    & set(config.UNIVERSE))
        assert sweeps.R3_NEW_TICKERS_INSTRUMENTS == ("SPY", "QQQ", "TSLA",
                                                     "JPM", "XOM", "TLT")

    def test_grids_are_subsets_of_published_family_axes(self):
        # Each slice-3 grid point must be a valid point of the family's
        # existing published grid (P1 trend / P1 mean-reversion axes) —
        # no new parameter territory is opened by this slice.
        for params in sweeps.r3_new_tickers_variants("donchian"):
            assert params in sweeps.variants("donchian")
        for params in sweeps.r3_new_tickers_variants("sma_crossover"):
            assert params in sweeps.variants("sma_crossover")
        for params in sweeps.r3_new_tickers_variants("rsi_mean_reversion"):
            assert params in sweeps.mean_reversion_variants("rsi_mean_reversion")

    def test_constraints_filtered_and_nothing_else_swept(self):
        for params in sweeps.r3_new_tickers_variants("donchian"):
            assert params["exit"] <= params["entry"]
            assert set(params) == {"entry", "exit"}
        for params in sweeps.r3_new_tickers_variants("sma_crossover"):
            assert params["fast"] < params["slow"]
            assert set(params) == {"fast", "slow"}
        for params in sweeps.r3_new_tickers_variants("rsi_mean_reversion"):
            assert params["oversold"] < params["overbought"]
            assert set(params) == {"period", "oversold", "overbought"}

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_NEW_TICKERS_FAMILIES:
            for params in sweeps.r3_new_tickers_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_new_tickers_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_new_tickers_variants("donchian")
                == sweeps.r3_new_tickers_variants("donchian"))


class TestR3AroonCciGrid:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R3_AROON_CCI_FAMILY
        assert set(sweeps.R3_AROON_CCI_FAMILIES) == set(R3_AROON_CCI_FAMILY)
        for fam in sweeps.R3_AROON_CCI_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-aroon-cci sweep files must match these. 12 variants per
        # family over the 12-ticker mixed set = 288 registered configs.
        counts = sweeps.r3_aroon_cci_variants_per_family()
        assert counts == {"aroon_trend": 12, "cci_reversion": 12}
        assert len(sweeps.R3_AROON_CCI_INSTRUMENTS) == 12
        assert sweeps.r3_aroon_cci_total_configs() == 288

    def test_instruments_universe_plus_four_new(self):
        # The mixed set is exactly the frozen 8-ticker universe (in
        # config.UNIVERSE order) followed by four of the slice-3 new
        # instruments — config.UNIVERSE itself stays frozen at 8.
        from trading_lab import config
        assert sweeps.R3_AROON_CCI_INSTRUMENTS[:8] == tuple(config.UNIVERSE)
        assert sweeps.R3_AROON_CCI_INSTRUMENTS[8:] == ("SPY", "QQQ", "TSLA",
                                                       "TLT")
        assert (set(sweeps.R3_AROON_CCI_INSTRUMENTS[8:])
                <= set(sweeps.R3_NEW_TICKERS_INSTRUMENTS))
        assert len(config.UNIVERSE) == 8

    def test_aroon_grid_includes_the_classic_control_arm(self):
        # Slice-2 card convention: a banded/gated grid must commit its
        # neutral arm. entry == exit == 0 IS the classic Aroon-Up/Aroon-Down
        # cross, so every period is paired with the pure-cross control.
        variants = sweeps.r3_aroon_cci_variants("aroon_trend")
        for period in (14, 25, 50):
            assert {"period": period, "entry": 0.0, "exit": 0.0} in variants

    def test_constraints_filtered_and_nothing_else_swept(self):
        for params in sweeps.r3_aroon_cci_variants("aroon_trend"):
            assert params["exit"] <= params["entry"]
            assert set(params) == {"period", "entry", "exit"}
        for params in sweeps.r3_aroon_cci_variants("cci_reversion"):
            assert params["buy_below"] < params["sell_above"]
            assert set(params) == {"period", "buy_below", "sell_above"}

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_AROON_CCI_FAMILIES:
            for params in sweeps.r3_aroon_cci_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_aroon_cci_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_aroon_cci_variants("aroon_trend")
                == sweeps.r3_aroon_cci_variants("aroon_trend"))


class TestR3MeanrevHourlyGrid:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R3_MEANREV_HOURLY_FAMILY
        assert (set(sweeps.R3_MEANREV_HOURLY_FAMILIES)
                == set(R3_MEANREV_HOURLY_FAMILY))
        for fam in sweeps.R3_MEANREV_HOURLY_FAMILIES:
            assert fam in STRATEGIES

    def test_no_new_strategies(self):
        # Slice 5 is a TIMEFRAME expansion: every family must already be
        # swept by an earlier daily lane (no new strategy code).
        earlier = (set(sweeps.MEAN_REVERSION_FAMILIES)
                   | set(sweeps.R3_STOCH_WILLR_FAMILIES))
        assert set(sweeps.R3_MEANREV_HOURLY_FAMILIES) <= earlier

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-meanrev-hourly sweep files must match these. 12
        # variants per family over the full 8-ticker universe = 384
        # registered configs.
        from trading_lab import config
        counts = sweeps.r3_meanrev_hourly_variants_per_family()
        assert counts == {"rsi_mean_reversion": 12,
                          "bollinger_reversion": 12,
                          "stochastic_reversion": 12,
                          "williams_r_reversion": 12}
        assert sweeps.R3_MEANREV_HOURLY_INSTRUMENTS == tuple(config.UNIVERSE)
        assert len(sweeps.R3_MEANREV_HOURLY_INSTRUMENTS) == 8
        assert sweeps.r3_meanrev_hourly_total_configs() == 384

    def test_grids_are_subsets_of_the_published_daily_axes(self):
        # The p1-trend-hourly convention: bar-denominated grids reused
        # as-is on hourly bars — no new parameter values. Every hourly
        # variant must already exist in its family's daily grid.
        daily = {
            "rsi_mean_reversion":
                sweeps.mean_reversion_variants("rsi_mean_reversion"),
            "bollinger_reversion":
                sweeps.mean_reversion_variants("bollinger_reversion"),
            "stochastic_reversion":
                sweeps.r3_stoch_willr_variants("stochastic_reversion"),
            "williams_r_reversion":
                sweeps.r3_stoch_willr_variants("williams_r_reversion"),
        }
        for fam in sweeps.R3_MEANREV_HOURLY_FAMILIES:
            for params in sweeps.r3_meanrev_hourly_variants(fam):
                assert params in daily[fam], (fam, params)

    def test_constraints_filtered_and_nothing_else_swept(self):
        # The stochastic d_period smoothing (3) stays frozen at the
        # strategy default and is NOT swept (as in r3-stoch-willr).
        for params in sweeps.r3_meanrev_hourly_variants("rsi_mean_reversion"):
            assert params["oversold"] < params["overbought"]
            assert set(params) == {"period", "oversold", "overbought"}
        for params in sweeps.r3_meanrev_hourly_variants("bollinger_reversion"):
            assert params["z_exit"] > -params["z_entry"]
            assert set(params) == {"lookback", "z_entry", "z_exit"}
        for params in sweeps.r3_meanrev_hourly_variants("stochastic_reversion"):
            assert params["buy_below"] < params["sell_above"]
            assert set(params) == {"k_period", "buy_below", "sell_above"}
        for params in sweeps.r3_meanrev_hourly_variants("williams_r_reversion"):
            assert params["buy_below"] < params["sell_above"]
            assert set(params) == {"period", "buy_below", "sell_above"}

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_MEANREV_HOURLY_FAMILIES:
            for params in sweeps.r3_meanrev_hourly_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_meanrev_hourly_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_meanrev_hourly_variants("bollinger_reversion")
                == sweeps.r3_meanrev_hourly_variants("bollinger_reversion"))


class TestR3BreakoutGrid:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R3_BREAKOUT_FAMILY
        assert set(sweeps.R3_BREAKOUT_FAMILIES) == set(R3_BREAKOUT_FAMILY)
        for fam in sweeps.R3_BREAKOUT_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-breakout sweep files must match these. 12 variants per
        # family over the 12-ticker mixed set = 288 registered configs.
        counts = sweeps.r3_breakout_variants_per_family()
        assert counts == {"bollinger_breakout": 12, "atr_trailing": 12}
        assert len(sweeps.R3_BREAKOUT_INSTRUMENTS) == 12
        assert sweeps.r3_breakout_total_configs() == 288

    def test_instruments_universe_plus_four_new(self):
        # The mixed set reuses the slice-4 (r3-aroon-cci) 12-ticker set
        # verbatim: the frozen 8-ticker universe (config.UNIVERSE order)
        # followed by four of the slice-3 new instruments —
        # config.UNIVERSE itself stays frozen at 8.
        from trading_lab import config
        assert sweeps.R3_BREAKOUT_INSTRUMENTS == sweeps.R3_AROON_CCI_INSTRUMENTS
        assert sweeps.R3_BREAKOUT_INSTRUMENTS[:8] == tuple(config.UNIVERSE)
        assert sweeps.R3_BREAKOUT_INSTRUMENTS[8:] == ("SPY", "QQQ", "TSLA",
                                                      "TLT")
        assert len(config.UNIVERSE) == 8

    def test_band_axis_reuses_the_reversion_z_entry_axis(self):
        # Declared reuse: num_std values are the daily bollinger_reversion
        # z_entry axis verbatim, so every band width already sits in the
        # multiple-testing burden ledger under the mirror-image thesis.
        breakout_widths = {p["num_std"]
                           for p in sweeps.r3_breakout_variants(
                               "bollinger_breakout")}
        reversion_entries = {p["z_entry"]
                             for p in sweeps.mean_reversion_variants(
                                 "bollinger_reversion")}
        assert breakout_widths == reversion_entries

    def test_constraints_filtered_and_nothing_else_swept(self):
        # Pure threshold grids — the slice-2/4 committed-control-arm
        # convention is not applicable (no hysteresis band, no on/off gate).
        for params in sweeps.r3_breakout_variants("bollinger_breakout"):
            assert set(params) == {"period", "num_std"}
            assert params["num_std"] > 0
        for params in sweeps.r3_breakout_variants("atr_trailing"):
            assert set(params) == {"entry_lookback", "atr_period", "k"}
            assert params["k"] > 0

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_BREAKOUT_FAMILIES:
            for params in sweeps.r3_breakout_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_breakout_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_breakout_variants("atr_trailing")
                == sweeps.r3_breakout_variants("atr_trailing"))


class TestR3XsecExpandedGrid:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import (PORTFOLIO_STRATEGIES,
                                            R3_XSEC_EXPANDED_FAMILY,
                                            STRATEGIES)
        assert (set(sweeps.R3_XSEC_EXPANDED_FAMILIES)
                == set(R3_XSEC_EXPANDED_FAMILY))
        for fam in sweeps.R3_XSEC_EXPANDED_FAMILIES:
            assert fam in PORTFOLIO_STRATEGIES
            assert fam not in STRATEGIES  # panel interface, not per-ticker

    def test_counts_match_declaration(self):
        # Declared BEFORE the sweep ran: xsec_momentum reuses the Round-2
        # R3 axes verbatim (L ∈ {63, 126, 252} × k ∈ {2, 3} = 6);
        # xsec_reversal mirrors them at short horizons (N ∈ {5, 10, 21} ×
        # k ∈ {2, 3} = 6). Portfolio lane: configs are grid points, NOT ×
        # instruments — 12 registered configs total.
        counts = sweeps.r3_xsec_expanded_variants_per_family()
        assert counts == {"xsec_momentum": 6, "xsec_reversal": 6}
        assert sweeps.r3_xsec_expanded_total_configs() == 12

    def test_momentum_axes_are_the_round2_axes_verbatim(self):
        assert (sweeps.r3_xsec_expanded_variants("xsec_momentum")
                == sweeps.r2_xsec_variants("xsec_momentum"))

    def test_basket_is_the_14_equity_etf_instruments(self):
        # Frozen 8-ticker universe minus BTC-USD, plus the six slice-3
        # instruments — all-equity/ETF so the aligned common index stays
        # on exchange trading days. Alphabetical (panel column order =
        # ranking tie-break order).
        assert sweeps.R3_XSEC_EXPANDED_INSTRUMENTS == (
            "AAPL", "AMZN", "GLD", "GOOGL", "JPM", "META", "MSFT",
            "NVDA", "QQQ", "SLV", "SPY", "TLT", "TSLA", "XOM")
        assert len(sweeps.R3_XSEC_EXPANDED_INSTRUMENTS) == 14
        assert "BTC-USD" not in sweeps.R3_XSEC_EXPANDED_INSTRUMENTS
        assert (tuple(sorted(sweeps.R3_XSEC_EXPANDED_INSTRUMENTS))
                == sweeps.R3_XSEC_EXPANDED_INSTRUMENTS)

    def test_grids_are_exactly_the_registered_products(self):
        variants = sweeps.r3_xsec_expanded_variants("xsec_reversal")
        assert ({(p["N"], p["k"]) for p in variants}
                == {(N, k) for N in (5, 10, 21) for k in (2, 3)})
        for params in variants:
            assert set(params) == {"N", "k"}  # nothing else is swept

    def test_rebalance_cadences_frozen_not_swept(self):
        assert sweeps.R3_XSEC_EXPANDED_REBALANCE_EVERY == {
            "xsec_momentum": 21, "xsec_reversal": 5}
        for fam in sweeps.R3_XSEC_EXPANDED_FAMILIES:
            for params in sweeps.r3_xsec_expanded_variants(fam):
                assert "rebalance_every" not in params

    def test_every_variant_runs(self):
        from trading_lab.strategies import PORTFOLIO_STRATEGIES
        rng = np.random.default_rng(23)
        idx = pd.bdate_range("2020-01-01", periods=300)
        closes = pd.DataFrame(
            {t: 100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.02, 300)))
             for t in sweeps.R3_XSEC_EXPANDED_INSTRUMENTS}, index=idx)
        for fam in sweeps.R3_XSEC_EXPANDED_FAMILIES:
            rebal = sweeps.R3_XSEC_EXPANDED_REBALANCE_EVERY[fam]
            for params in sweeps.r3_xsec_expanded_variants(fam):
                w = PORTFOLIO_STRATEGIES[fam](
                    closes, rebalance_every=rebal, **params)
                rows = w.dropna(how="all")
                assert len(rows) > 0
                assert np.allclose(rows.sum(axis=1), 1.0)

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_xsec_expanded_variants("astrology")

    def test_deterministic_order(self):
        for fam in sweeps.R3_XSEC_EXPANDED_FAMILIES:
            assert (sweeps.r3_xsec_expanded_variants(fam)
                    == sweeps.r3_xsec_expanded_variants(fam))


class TestR3TrixIchimokuGrid:
    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R3_TRIX_ICHIMOKU_FAMILY
        assert (set(sweeps.R3_TRIX_ICHIMOKU_FAMILIES)
                == set(R3_TRIX_ICHIMOKU_FAMILY))
        for fam in sweeps.R3_TRIX_ICHIMOKU_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-trix-ichimoku sweep files must match these. 12 variants
        # per family over the 12-ticker mixed set = 288 registered configs.
        counts = sweeps.r3_trix_ichimoku_variants_per_family()
        assert counts == {"trix_momentum": 12, "ichimoku_trend": 12}
        assert len(sweeps.R3_TRIX_ICHIMOKU_INSTRUMENTS) == 12
        assert sweeps.r3_trix_ichimoku_total_configs() == 288

    def test_instruments_universe_plus_four_new(self):
        # The mixed set reuses the slice-4/6 12-ticker set verbatim: the
        # frozen 8-ticker universe (config.UNIVERSE order) followed by four
        # of the slice-3 new instruments — config.UNIVERSE stays frozen at 8.
        from trading_lab import config
        assert (sweeps.R3_TRIX_ICHIMOKU_INSTRUMENTS
                == sweeps.R3_AROON_CCI_INSTRUMENTS)
        assert sweeps.R3_TRIX_ICHIMOKU_INSTRUMENTS[:8] == tuple(config.UNIVERSE)
        assert sweeps.R3_TRIX_ICHIMOKU_INSTRUMENTS[8:] == ("SPY", "QQQ",
                                                           "TSLA", "TLT")
        assert len(config.UNIVERSE) == 8

    def test_trix_grid_includes_the_zero_line_control_arm(self):
        # Slice-2/4 card convention: a derived-trigger grid must commit its
        # neutral arm. signal_period == 0 IS the classic TRIX zero-line
        # rule, so every period is paired with the zero-line control.
        variants = sweeps.r3_trix_ichimoku_variants("trix_momentum")
        for period in (9, 12, 15, 21):
            assert {"period": period, "signal_period": 0} in variants

    def test_ichimoku_grid_includes_the_classic_9_26_52(self):
        variants = sweeps.r3_trix_ichimoku_variants("ichimoku_trend")
        assert {"tenkan": 9, "kijun": 26, "senkou_b": 52} in variants

    def test_constraints_filtered_and_nothing_else_swept(self):
        # The senkou displacement is frozen at the standard 26 (strategy
        # default) and must NOT appear as a swept axis.
        for params in sweeps.r3_trix_ichimoku_variants("trix_momentum"):
            assert set(params) == {"period", "signal_period"}
            assert params["signal_period"] >= 0
        for params in sweeps.r3_trix_ichimoku_variants("ichimoku_trend"):
            assert set(params) == {"tenkan", "kijun", "senkou_b"}
            assert params["tenkan"] < params["kijun"] < params["senkou_b"]

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_TRIX_ICHIMOKU_FAMILIES:
            for params in sweeps.r3_trix_ichimoku_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_trix_ichimoku_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_trix_ichimoku_variants("ichimoku_trend")
                == sweeps.r3_trix_ichimoku_variants("ichimoku_trend"))


class TestR3TrendNewTickersGrid:
    def test_families_are_existing_registered_strategies(self):
        # Slice 10 completes the trend-family coverage of the slice-3
        # instruments with NO new strategy code: every family must already
        # exist in the registry.
        for fam in sweeps.R3_TREND_NEW_TICKERS_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-trend-new-tickers sweep files must match these. 12
        # variants per family × 4 families × 6 instruments = 288 registered
        # configs.
        counts = sweeps.r3_trend_new_tickers_variants_per_family()
        assert counts == {"donchian": 12, "ema_crossover": 12,
                          "macd": 12, "supertrend_flip": 12}
        assert len(sweeps.R3_TREND_NEW_TICKERS_INSTRUMENTS) == 6
        assert sweeps.r3_trend_new_tickers_total_configs() == 288

    def test_instruments_are_exactly_the_slice3_set(self):
        # The lane reuses the slice-3 instruments (and caches) verbatim, and
        # they stay disjoint from the frozen universe.
        from trading_lab import config
        assert (sweeps.R3_TREND_NEW_TICKERS_INSTRUMENTS
                == sweeps.R3_NEW_TICKERS_INSTRUMENTS)
        assert not (set(sweeps.R3_TREND_NEW_TICKERS_INSTRUMENTS)
                    & set(config.UNIVERSE))

    def test_grids_are_subsets_of_published_family_axes(self):
        # Each slice-10 grid point must be a valid point of the family's
        # existing published grid (P1 trend axes; the P1 video-lane
        # supertrend grid) — no new parameter territory is opened.
        for fam in ("donchian", "ema_crossover", "macd"):
            published = sweeps.variants(fam)
            for params in sweeps.r3_trend_new_tickers_variants(fam):
                assert params in published
        video_grid = sweeps.video_variants("supertrend_flip")
        for params in sweeps.r3_trend_new_tickers_variants("supertrend_flip"):
            assert params in video_grid

    def test_donchian_grid_disjoint_from_slice3_probe(self):
        # Slice 3 already registered a 6-point donchian probe on these
        # instruments; this slice must not register any of those points a
        # second time.
        probe = sweeps.r3_new_tickers_variants("donchian")
        for params in sweeps.r3_trend_new_tickers_variants("donchian"):
            assert params not in probe

    def test_constraints_filtered_and_nothing_else_swept(self):
        # The supertrend MACD triple is frozen at the classic 12/26/9 (one
        # of the two video-lane triples) and NOT swept.
        for params in sweeps.r3_trend_new_tickers_variants("donchian"):
            assert params["exit"] <= params["entry"]
            assert set(params) == {"entry", "exit"}
        for params in sweeps.r3_trend_new_tickers_variants("ema_crossover"):
            assert params["fast"] < params["slow"]
            assert set(params) == {"fast", "slow"}
        for params in sweeps.r3_trend_new_tickers_variants("macd"):
            assert params["fast"] < params["slow"]
            assert set(params) == {"fast", "slow", "signal"}
        for params in sweeps.r3_trend_new_tickers_variants("supertrend_flip"):
            assert set(params) == {"st_period", "st_mult", "ema_len",
                                   "macd_fast", "macd_slow", "macd_signal"}
            assert (params["macd_fast"], params["macd_slow"],
                    params["macd_signal"]) == (12, 26, 9)

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_TREND_NEW_TICKERS_FAMILIES:
            for params in sweeps.r3_trend_new_tickers_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_trend_new_tickers_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_trend_new_tickers_variants("supertrend_flip")
                == sweeps.r3_trend_new_tickers_variants("supertrend_flip"))
