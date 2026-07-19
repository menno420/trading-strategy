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


class TestR3MeanrevNewTickersGrid:
    def test_families_are_existing_registered_strategies(self):
        # Slice 11 completes the mean-reversion coverage of the slice-3
        # instruments with NO new strategy code: every family must already
        # exist in the registry.
        for fam in sweeps.R3_MEANREV_NEW_TICKERS_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-meanrev-new-tickers sweep files must match these. 12
        # variants per family × 5 families × 6 instruments = 360 registered
        # configs.
        counts = sweeps.r3_meanrev_new_tickers_variants_per_family()
        assert counts == {"rsi_mean_reversion": 12,
                          "bollinger_reversion": 12,
                          "pullback": 12,
                          "stochastic_reversion": 12,
                          "williams_r_reversion": 12}
        assert len(sweeps.R3_MEANREV_NEW_TICKERS_INSTRUMENTS) == 6
        assert sweeps.r3_meanrev_new_tickers_total_configs() == 360

    def test_instruments_are_exactly_the_slice3_set(self):
        # The lane reuses the slice-3 instruments (and caches) verbatim, and
        # they stay disjoint from the frozen universe.
        from trading_lab import config
        assert (sweeps.R3_MEANREV_NEW_TICKERS_INSTRUMENTS
                == sweeps.R3_NEW_TICKERS_INSTRUMENTS)
        assert not (set(sweeps.R3_MEANREV_NEW_TICKERS_INSTRUMENTS)
                    & set(config.UNIVERSE))

    def test_grids_are_subsets_of_published_family_axes(self):
        # Each slice-11 grid point must be a valid point of the family's
        # existing published grid (P1 mean-reversion axes; the
        # r3-stoch-willr axes) — no new parameter territory is opened.
        for fam in ("rsi_mean_reversion", "bollinger_reversion", "pullback"):
            published = sweeps.mean_reversion_variants(fam)
            for params in sweeps.r3_meanrev_new_tickers_variants(fam):
                assert params in published
        for fam in ("stochastic_reversion", "williams_r_reversion"):
            # The r3-stoch-willr grids are already exactly 12 — reused
            # VERBATIM (the superset relation degenerates to equality).
            assert (sweeps.r3_meanrev_new_tickers_variants(fam)
                    == sweeps.r3_stoch_willr_variants(fam))

    def test_rsi_grid_disjoint_from_slice3_probe(self):
        # Slice 3 already registered a 6-point rsi_mean_reversion probe on
        # these instruments (oversold frozen at 30); this slice must not
        # register any of those points a second time (slice 10's donchian
        # precedent).
        probe = sweeps.r3_new_tickers_variants("rsi_mean_reversion")
        for params in sweeps.r3_meanrev_new_tickers_variants(
                "rsi_mean_reversion"):
            assert params not in probe

    def test_pullback_grid_includes_unfiltered_control_arm(self):
        # Slice-2/4 card convention: a gated grid must commit its neutral
        # arm — trend_len=0 disables the long-term trend filter, and every
        # (entry_lookback, exit_len) pair must carry it.
        variants = sweeps.r3_meanrev_new_tickers_variants("pullback")
        for entry in (3, 5):
            for exit_len in (5, 10):
                assert {"entry_lookback": entry, "exit_len": exit_len,
                        "trend_len": 0} in variants

    def test_constraints_filtered_and_nothing_else_swept(self):
        # The stochastic d_period smoothing (3) stays frozen at the
        # strategy default and is NOT swept (as in r3-stoch-willr).
        for params in sweeps.r3_meanrev_new_tickers_variants(
                "rsi_mean_reversion"):
            assert params["oversold"] < params["overbought"]
            assert set(params) == {"period", "oversold", "overbought"}
        for params in sweeps.r3_meanrev_new_tickers_variants(
                "bollinger_reversion"):
            assert params["z_exit"] > -params["z_entry"]
            assert set(params) == {"lookback", "z_entry", "z_exit"}
        for params in sweeps.r3_meanrev_new_tickers_variants("pullback"):
            assert set(params) == {"entry_lookback", "exit_len", "trend_len"}
        for params in sweeps.r3_meanrev_new_tickers_variants(
                "stochastic_reversion"):
            assert params["buy_below"] < params["sell_above"]
            assert set(params) == {"k_period", "buy_below", "sell_above"}
        for params in sweeps.r3_meanrev_new_tickers_variants(
                "williams_r_reversion"):
            assert params["buy_below"] < params["sell_above"]
            assert set(params) == {"period", "buy_below", "sell_above"}

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_MEANREV_NEW_TICKERS_FAMILIES:
            for params in sweeps.r3_meanrev_new_tickers_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_meanrev_new_tickers_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_meanrev_new_tickers_variants("pullback")
                == sweeps.r3_meanrev_new_tickers_variants("pullback"))


class TestR3GatedNewTickersGrid:
    def test_families_are_existing_registered_strategies(self):
        # Slice 12 completes the R2/gated-family coverage of the slice-3
        # instruments with NO new strategy code: every family must already
        # exist in the registry.
        for fam in sweeps.R3_GATED_NEW_TICKERS_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-gated-new-tickers sweep files must match these.
        # keltner_breakout honestly runs at 6 — its FULL published R2 grid
        # is only 6 variants and inventing new n/m values would open new
        # parameter territory. (6 + 12 + 12) × 6 instruments = 180
        # registered configs.
        counts = sweeps.r3_gated_new_tickers_variants_per_family()
        assert counts == {"keltner_breakout": 6,
                          "vol_filtered_trend": 12,
                          "macd_supertrend": 12}
        assert len(sweeps.R3_GATED_NEW_TICKERS_INSTRUMENTS) == 6
        assert sweeps.r3_gated_new_tickers_total_configs() == 180

    def test_instruments_are_exactly_the_slice3_set(self):
        # The lane reuses the slice-3 instruments (and caches) verbatim, and
        # they stay disjoint from the frozen universe.
        from trading_lab import config
        assert (sweeps.R3_GATED_NEW_TICKERS_INSTRUMENTS
                == sweeps.R3_NEW_TICKERS_INSTRUMENTS)
        assert not (set(sweeps.R3_GATED_NEW_TICKERS_INSTRUMENTS)
                    & set(config.UNIVERSE))

    def test_grids_are_subsets_of_published_family_axes(self):
        # Each slice-12 grid point must be a valid point of the family's
        # existing published grid — no new parameter territory is opened.
        # keltner_breakout and vol_filtered_trend reuse their full Round-2
        # grids VERBATIM (the subset relation degenerates to equality);
        # macd_supertrend is a proper sub-grid of the P1 video-lane grid.
        assert (sweeps.r3_gated_new_tickers_variants("keltner_breakout")
                == sweeps.r2_keltner_variants("keltner_breakout"))
        assert (sweeps.r3_gated_new_tickers_variants("vol_filtered_trend")
                == sweeps.r2_vol_trend_variants("vol_filtered_trend"))
        video_grid = sweeps.video_variants("macd_supertrend")
        for params in sweeps.r3_gated_new_tickers_variants("macd_supertrend"):
            assert params in video_grid

    def test_vol_filtered_grid_includes_filter_off_control_arm(self):
        # Slice-2/4 card convention: a gated grid must commit its neutral
        # arm — vol_filter=False disables the calm-regime gate, and every
        # (fast, slow) pair must carry it.
        variants = sweeps.r3_gated_new_tickers_variants("vol_filtered_trend")
        for fast in (10, 20):
            for slow in (50, 100, 200):
                assert {"fast": fast, "slow": slow,
                        "vol_filter": False} in variants

    def test_constraints_filtered_and_nothing_else_swept(self):
        # The macd_supertrend MACD triple is frozen at the classic 12/26/9
        # (one of the two video-lane triples) and NOT swept — slice 10's
        # supertrend_flip precedent; the vol_filtered_trend vol windows
        # (20/252) stay frozen at the strategy defaults, as in Round 2.
        for params in sweeps.r3_gated_new_tickers_variants("keltner_breakout"):
            assert set(params) == {"n", "m"}
        for params in sweeps.r3_gated_new_tickers_variants(
                "vol_filtered_trend"):
            assert params["fast"] < params["slow"]
            assert set(params) == {"fast", "slow", "vol_filter"}
        for params in sweeps.r3_gated_new_tickers_variants("macd_supertrend"):
            assert set(params) == {"st_period", "st_mult", "ema_len",
                                   "macd_fast", "macd_slow", "macd_signal"}
            assert (params["macd_fast"], params["macd_slow"],
                    params["macd_signal"]) == (12, 26, 9)

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_GATED_NEW_TICKERS_FAMILIES:
            for params in sweeps.r3_gated_new_tickers_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_gated_new_tickers_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_gated_new_tickers_variants("macd_supertrend")
                == sweeps.r3_gated_new_tickers_variants("macd_supertrend"))


class TestR3BtcCoverageGrid:
    # The declared slice-13 families, in lane order — the ten
    # single-instrument families Round 3 added, none of which had ever
    # run on BTC-USD before this slice.
    EXPECTED_FAMILIES = ("stochastic_reversion", "williams_r_reversion",
                         "roc_momentum", "adx_filtered_sma",
                         "aroon_trend", "cci_reversion",
                         "bollinger_breakout", "atr_trailing",
                         "trix_momentum", "ichimoku_trend")

    def test_families_are_exactly_the_round3_single_instrument_set(self):
        # Slice 13 completes the BTC-USD coverage of the Round-3 families
        # with NO new strategy code: every family must already exist in
        # the registry, and the set is pinned (xsec_momentum is a basket
        # strategy and deliberately out of scope — its slice-9 lane
        # excludes BTC-USD over the calendar-mixing problem).
        assert sweeps.R3_BTC_COVERAGE_FAMILIES == self.EXPECTED_FAMILIES
        for fam in sweeps.R3_BTC_COVERAGE_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger
        # records and the r3-btc-coverage sweep files must match these.
        # 12 × 10 families × 1 instrument = 120 registered configs.
        counts = sweeps.r3_btc_coverage_variants_per_family()
        assert counts == {fam: 12 for fam in self.EXPECTED_FAMILIES}
        assert sweeps.R3_BTC_COVERAGE_INSTRUMENTS == ("BTC-USD",)
        assert sweeps.r3_btc_coverage_total_configs() == 120

    def test_grids_are_the_source_lane_grids_verbatim(self):
        # The whole point of the lane: each family's Round-3 grid reused
        # VERBATIM — the subset relation degenerates to equality with the
        # declaring lane's grid (delegation makes drift impossible; this
        # pin makes it visible).
        assert (sweeps.r3_btc_coverage_variants("stochastic_reversion")
                == sweeps.r3_stoch_willr_variants("stochastic_reversion"))
        assert (sweeps.r3_btc_coverage_variants("williams_r_reversion")
                == sweeps.r3_stoch_willr_variants("williams_r_reversion"))
        assert (sweeps.r3_btc_coverage_variants("roc_momentum")
                == sweeps.r3_roc_adx_variants("roc_momentum"))
        assert (sweeps.r3_btc_coverage_variants("adx_filtered_sma")
                == sweeps.r3_roc_adx_variants("adx_filtered_sma"))
        assert (sweeps.r3_btc_coverage_variants("aroon_trend")
                == sweeps.r3_aroon_cci_variants("aroon_trend"))
        assert (sweeps.r3_btc_coverage_variants("cci_reversion")
                == sweeps.r3_aroon_cci_variants("cci_reversion"))
        assert (sweeps.r3_btc_coverage_variants("bollinger_breakout")
                == sweeps.r3_breakout_variants("bollinger_breakout"))
        assert (sweeps.r3_btc_coverage_variants("atr_trailing")
                == sweeps.r3_breakout_variants("atr_trailing"))
        assert (sweeps.r3_btc_coverage_variants("trix_momentum")
                == sweeps.r3_trix_ichimoku_variants("trix_momentum"))
        assert (sweeps.r3_btc_coverage_variants("ichimoku_trend")
                == sweeps.r3_trix_ichimoku_variants("ichimoku_trend"))

    def test_instrument_is_lane_local(self):
        # BTC-USD is not in the frozen universe; the lane reuses the
        # committed P1 video-lane cache and fetches nothing.
        from trading_lab import config
        assert not (set(sweeps.R3_BTC_COVERAGE_INSTRUMENTS)
                    & set(config.UNIVERSE))

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_BTC_COVERAGE_FAMILIES:
            for params in sweeps.r3_btc_coverage_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_btc_coverage_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_btc_coverage_variants("ichimoku_trend")
                == sweeps.r3_btc_coverage_variants("ichimoku_trend"))


class TestR3TrendHourlyGrid:
    # The declared slice-14 families, in lane order — the four Round-3
    # trend/momentum single-instrument families, the TREND-side mirror of
    # the slice-5 (r3-meanrev-hourly) timeframe expansion.
    EXPECTED_FAMILIES = ("roc_momentum", "adx_filtered_sma",
                         "aroon_trend", "trix_momentum")

    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R3_TREND_HOURLY_FAMILY
        assert sweeps.R3_TREND_HOURLY_FAMILIES == self.EXPECTED_FAMILIES
        assert (set(sweeps.R3_TREND_HOURLY_FAMILIES)
                == set(R3_TREND_HOURLY_FAMILY))
        for fam in sweeps.R3_TREND_HOURLY_FAMILIES:
            assert fam in STRATEGIES

    def test_no_new_strategies(self):
        # Slice 14 is a TIMEFRAME expansion: every family must already be
        # swept by an earlier daily lane (no new strategy code).
        earlier = (set(sweeps.R3_ROC_ADX_FAMILIES)
                   | set(sweeps.R3_AROON_CCI_FAMILIES)
                   | set(sweeps.R3_TRIX_ICHIMOKU_FAMILIES))
        assert set(sweeps.R3_TREND_HOURLY_FAMILIES) <= earlier

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-trend-hourly sweep files must match these. 12 variants
        # per family over the full 8-ticker universe = 384 registered
        # configs — the slice-5 shape, mirrored.
        from trading_lab import config
        counts = sweeps.r3_trend_hourly_variants_per_family()
        assert counts == {fam: 12 for fam in self.EXPECTED_FAMILIES}
        assert sweeps.R3_TREND_HOURLY_INSTRUMENTS == tuple(config.UNIVERSE)
        assert len(sweeps.R3_TREND_HOURLY_INSTRUMENTS) == 8
        assert sweeps.r3_trend_hourly_total_configs() == 384

    def test_grids_are_the_declared_daily_grids_verbatim(self):
        # The slice-13 delegation convention: each family's Round-3 daily
        # grid reused VERBATIM (delegation makes drift impossible; this
        # pin makes it visible).
        assert (sweeps.r3_trend_hourly_variants("roc_momentum")
                == sweeps.r3_roc_adx_variants("roc_momentum"))
        assert (sweeps.r3_trend_hourly_variants("adx_filtered_sma")
                == sweeps.r3_roc_adx_variants("adx_filtered_sma"))
        assert (sweeps.r3_trend_hourly_variants("aroon_trend")
                == sweeps.r3_aroon_cci_variants("aroon_trend"))
        assert (sweeps.r3_trend_hourly_variants("trix_momentum")
                == sweeps.r3_trix_ichimoku_variants("trix_momentum"))

    def test_grids_are_subsets_of_the_published_daily_axes(self):
        # The p1-trend-hourly / slice-5 convention: bar-denominated grids
        # reused as-is on hourly bars — no new parameter values. Every
        # hourly variant must already exist in its family's daily grid
        # (with verbatim delegation the subset degenerates to equality;
        # this is the slice-5 membership form, belt-and-braces).
        daily = {
            "roc_momentum": sweeps.r3_roc_adx_variants("roc_momentum"),
            "adx_filtered_sma": sweeps.r3_roc_adx_variants("adx_filtered_sma"),
            "aroon_trend": sweeps.r3_aroon_cci_variants("aroon_trend"),
            "trix_momentum": sweeps.r3_trix_ichimoku_variants("trix_momentum"),
        }
        for fam in sweeps.R3_TREND_HOURLY_FAMILIES:
            for params in sweeps.r3_trend_hourly_variants(fam):
                assert params in daily[fam], (fam, params)

    def test_constraints_filtered_and_nothing_else_swept(self):
        # Frozen non-swept parameters stay frozen under verbatim reuse
        # (ADX period 14 NOT swept, as in r3-roc-adx); the committed
        # control arms are inherited unchanged (aroon entry==exit==0, trix
        # signal_period==0).
        for params in sweeps.r3_trend_hourly_variants("roc_momentum"):
            assert params["exit"] <= params["entry"]
            assert set(params) == {"lookback", "entry", "exit"}
        for params in sweeps.r3_trend_hourly_variants("adx_filtered_sma"):
            assert params["fast"] < params["slow"]
            assert set(params) == {"fast", "slow", "adx_min"}
        for params in sweeps.r3_trend_hourly_variants("aroon_trend"):
            assert params["exit"] <= params["entry"]
            assert set(params) == {"period", "entry", "exit"}
        for params in sweeps.r3_trend_hourly_variants("trix_momentum"):
            assert set(params) == {"period", "signal_period"}
        assert {"period": 14, "entry": 0.0, "exit": 0.0} in \
            sweeps.r3_trend_hourly_variants("aroon_trend")
        assert any(p["signal_period"] == 0
                   for p in sweeps.r3_trend_hourly_variants("trix_momentum"))

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_TREND_HOURLY_FAMILIES:
            for params in sweeps.r3_trend_hourly_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_trend_hourly_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_trend_hourly_variants("trix_momentum")
                == sweeps.r3_trend_hourly_variants("trix_momentum"))


class TestR3HourlyCompletionGrid:
    # The declared slice-15 families, in lane order — the four Round-3
    # single-instrument families the hourly matrix still lacked after
    # slice 5 (mean-reversion) and slice 14 (classic trend/momentum);
    # this lane completes the Round-3 hourly matrix.
    EXPECTED_FAMILIES = ("cci_reversion", "bollinger_breakout",
                         "atr_trailing", "ichimoku_trend")

    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R3_HOURLY_COMPLETION_FAMILY
        assert (sweeps.R3_HOURLY_COMPLETION_FAMILIES
                == self.EXPECTED_FAMILIES)
        assert (set(sweeps.R3_HOURLY_COMPLETION_FAMILIES)
                == set(R3_HOURLY_COMPLETION_FAMILY))
        for fam in sweeps.R3_HOURLY_COMPLETION_FAMILIES:
            assert fam in STRATEGIES

    def test_no_new_strategies(self):
        # Slice 15 is a TIMEFRAME expansion: every family must already be
        # swept by an earlier daily lane (no new strategy code).
        earlier = (set(sweeps.R3_AROON_CCI_FAMILIES)
                   | set(sweeps.R3_BREAKOUT_FAMILIES)
                   | set(sweeps.R3_TRIX_ICHIMOKU_FAMILIES))
        assert set(sweeps.R3_HOURLY_COMPLETION_FAMILIES) <= earlier

    def test_completes_the_hourly_matrix(self):
        # The three hourly slices (5, 14, 15) are disjoint and together
        # cover every Round-3 single-instrument family exactly once.
        s5 = set(sweeps.R3_MEANREV_HOURLY_FAMILIES)
        s14 = set(sweeps.R3_TREND_HOURLY_FAMILIES)
        s15 = set(sweeps.R3_HOURLY_COMPLETION_FAMILIES)
        assert not (s15 & s5) and not (s15 & s14)
        round3_single_instrument = (
            set(sweeps.R3_STOCH_WILLR_FAMILIES)
            | set(sweeps.R3_ROC_ADX_FAMILIES)
            | set(sweeps.R3_AROON_CCI_FAMILIES)
            | set(sweeps.R3_BREAKOUT_FAMILIES)
            | set(sweeps.R3_TRIX_ICHIMOKU_FAMILIES))
        assert s5 | s14 | s15 >= round3_single_instrument

    def test_counts_bounded_and_stable(self):
        # Multiple-testing discipline: the counts reported in ledger records
        # and the r3-hourly-completion sweep files must match these. 12
        # variants per family over the full 8-ticker universe = 384
        # registered configs — the slice-5/14 shape, mirrored.
        from trading_lab import config
        counts = sweeps.r3_hourly_completion_variants_per_family()
        assert counts == {fam: 12 for fam in self.EXPECTED_FAMILIES}
        assert (sweeps.R3_HOURLY_COMPLETION_INSTRUMENTS
                == tuple(config.UNIVERSE))
        assert len(sweeps.R3_HOURLY_COMPLETION_INSTRUMENTS) == 8
        assert sweeps.r3_hourly_completion_total_configs() == 384

    def test_grids_are_the_declared_daily_grids_verbatim(self):
        # The slice-13/14 delegation convention: each family's Round-3
        # daily grid reused VERBATIM (delegation makes drift impossible;
        # this pin makes it visible).
        assert (sweeps.r3_hourly_completion_variants("cci_reversion")
                == sweeps.r3_aroon_cci_variants("cci_reversion"))
        assert (sweeps.r3_hourly_completion_variants("bollinger_breakout")
                == sweeps.r3_breakout_variants("bollinger_breakout"))
        assert (sweeps.r3_hourly_completion_variants("atr_trailing")
                == sweeps.r3_breakout_variants("atr_trailing"))
        assert (sweeps.r3_hourly_completion_variants("ichimoku_trend")
                == sweeps.r3_trix_ichimoku_variants("ichimoku_trend"))

    def test_grids_are_subsets_of_the_published_daily_axes(self):
        # The p1-trend-hourly / slice-5 convention: bar-denominated grids
        # reused as-is on hourly bars — no new parameter values. Every
        # hourly variant must already exist in its family's daily grid
        # (with verbatim delegation the subset degenerates to equality;
        # this is the slice-5 membership form, belt-and-braces).
        daily = {
            "cci_reversion": sweeps.r3_aroon_cci_variants("cci_reversion"),
            "bollinger_breakout":
                sweeps.r3_breakout_variants("bollinger_breakout"),
            "atr_trailing": sweeps.r3_breakout_variants("atr_trailing"),
            "ichimoku_trend":
                sweeps.r3_trix_ichimoku_variants("ichimoku_trend"),
        }
        for fam in sweeps.R3_HOURLY_COMPLETION_FAMILIES:
            for params in sweeps.r3_hourly_completion_variants(fam):
                assert params in daily[fam], (fam, params)

    def test_constraints_filtered_and_nothing_else_swept(self):
        # Frozen non-swept parameters stay frozen under verbatim reuse
        # (ichimoku senkou displacement 26 NOT swept, as in
        # r3-trix-ichimoku); the committed grid decisions are inherited
        # unchanged (Hosoda 9/26/52 stays IN the ichimoku grid; the
        # breakout grids are pure threshold families with no control arm,
        # per the slice-6 declaration).
        for params in sweeps.r3_hourly_completion_variants("cci_reversion"):
            assert params["buy_below"] < params["sell_above"]
            assert set(params) == {"period", "buy_below", "sell_above"}
        for params in sweeps.r3_hourly_completion_variants(
                "bollinger_breakout"):
            assert set(params) == {"period", "num_std"}
        for params in sweeps.r3_hourly_completion_variants("atr_trailing"):
            assert set(params) == {"entry_lookback", "atr_period", "k"}
        for params in sweeps.r3_hourly_completion_variants("ichimoku_trend"):
            assert params["tenkan"] < params["kijun"] < params["senkou_b"]
            assert set(params) == {"tenkan", "kijun", "senkou_b"}
        assert {"tenkan": 9, "kijun": 26, "senkou_b": 52} in \
            sweeps.r3_hourly_completion_variants("ichimoku_trend")

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R3_HOURLY_COMPLETION_FAMILIES:
            for params in sweeps.r3_hourly_completion_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r3_hourly_completion_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r3_hourly_completion_variants("ichimoku_trend")
                == sweeps.r3_hourly_completion_variants("ichimoku_trend"))


class TestR4SeasonalityGrid:
    def test_family_matches_strategy_registry(self):
        from trading_lab.strategies import R4_SEASONALITY_FAMILY
        assert set(sweeps.R4_SEASONALITY_FAMILIES) == set(R4_SEASONALITY_FAMILY)
        for fam in sweeps.R4_SEASONALITY_FAMILIES:
            assert fam in STRATEGIES

    def test_counts_bounded_and_stable(self):
        # Pre-registered R4-F accounting (docs/research-round-4-plan.md):
        # 5 weekday variants × 15 tickers = 75 registered configs, and for
        # THIS slice the registered significance K is the SAME number —
        # every day×ticker combo counts toward the bar.
        assert sweeps.r4_seasonality_variants_per_family() == \
            {"weekday_long": 5}
        assert len(sweeps.R4_SEASONALITY_INSTRUMENTS) == 15
        assert sweeps.r4_seasonality_total_configs() == 75
        assert sweeps.R4_SEASONALITY_K == 75
        assert sweeps.R4_SEASONALITY_K == sweeps.r4_seasonality_total_configs()

    def test_bar_rises_with_k_and_is_never_lowered(self):
        # min_tstat(75) ≈ 3.21 — strictly ABOVE the standard K=12 bar
        # (~2.64). The plan forbids counting K down.
        from trading_lab import promotion
        bar75 = promotion.min_tstat(sweeps.R4_SEASONALITY_K)
        assert bar75 > promotion.min_tstat(12)
        assert round(bar75, 2) == 3.21

    def test_instruments_are_the_full_committed_daily_surface(self):
        # All 15 committed daily caches — the frozen 8-ticker universe +
        # the six slice-3 instruments + BTC-USD — so no post-hoc instrument
        # selection is possible. Sorted, unique, no additions.
        from trading_lab import config
        instruments = sweeps.R4_SEASONALITY_INSTRUMENTS
        assert len(set(instruments)) == len(instruments)
        assert list(instruments) == sorted(instruments)
        assert set(config.UNIVERSE) <= set(instruments)
        assert set(sweeps.R3_NEW_TICKERS_INSTRUMENTS) <= set(instruments)
        assert "BTC-USD" in instruments
        assert set(instruments) == (set(config.UNIVERSE)
                                    | set(sweeps.R3_NEW_TICKERS_INSTRUMENTS)
                                    | {"BTC-USD"})

    def test_grid_is_exactly_the_five_weekdays(self):
        # Single axis, no parameter search inside a combo; weekend days
        # (5/6, BTC-only) are NOT registered — K stays 75.
        variants = sweeps.r4_seasonality_variants("weekday_long")
        assert variants == [{"weekday": d} for d in range(5)]
        for params in variants:
            assert set(params) == {"weekday"}

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R4_SEASONALITY_FAMILIES:
            for params in sweeps.r4_seasonality_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r4_seasonality_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r4_seasonality_variants("weekday_long")
                == sweeps.r4_seasonality_variants("weekday_long"))


class TestR4EnsembleRegistration:
    """R4-C survivor committees — registered constants pinned BEFORE the
    sweep runs (docs/research-round-4-plan.md § R4-C)."""

    def test_min_members_is_two(self):
        # The plan's qualifying rule: >= 2 KEEP-dev families.
        assert sweeps.R4_ENSEMBLE_MIN_MEMBERS == 2

    def test_informational_k_is_round_standard_and_bar_never_lowered(self):
        # Each committee is ONE pre-declared config, but the plan registers
        # no smaller K for this slice — so the informational t is graded at
        # the round-standard K=12 (bar ~2.638), never below it.
        from trading_lab import promotion
        assert sweeps.R4_ENSEMBLE_K == 12
        assert round(promotion.min_tstat(sweeps.R4_ENSEMBLE_K), 3) == 2.638

    def test_keep_universe_is_the_committed_r4a_surface(self):
        from trading_lab import config
        assert sweeps.R4_ENSEMBLE_KEEP_UNIVERSE == \
            "experiments/sweeps/r4-killsig-regrade/summary.json"
        assert sweeps.R4_ENSEMBLE_EXPECTED_KEEPS == 58
        assert (config.REPO_ROOT / sweeps.R4_ENSEMBLE_KEEP_UNIVERSE).exists()

    def test_ledger_strategy_name(self):
        # Committee rows are ledgered under a clear composite name that is
        # NOT a registered single-family strategy.
        from trading_lab.strategies import STRATEGIES
        assert sweeps.R4_ENSEMBLE_STRATEGY_NAME == "committee_equal_weight"
        assert sweeps.R4_ENSEMBLE_STRATEGY_NAME not in STRATEGIES


class TestR4RegimeGrid:
    """R4-D regime-conditional allocation — grid + constants pinned BEFORE
    the sweep runs (docs/research-round-4-plan.md § R4-D)."""

    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R4_REGIME_FAMILY
        assert set(sweeps.R4_REGIME_FAMILIES) == set(R4_REGIME_FAMILY)
        assert sweeps.R4_REGIME_STRATEGY_NAME in STRATEGIES

    def test_registered_counts(self):
        # Pre-registered R4-D accounting: 12 conditional + 2 control
        # variants per lane x 6 instruments = 84 registered configs.
        assert sweeps.r4_regime_variants_per_arm() == {"conditional": 12,
                                                       "control": 2}
        assert sweeps.r4_regime_total_configs() == 84
        assert len(sweeps.R4_REGIME_INSTRUMENTS) == 6

    def test_instruments_are_the_pr83_surface(self):
        # The six slice-3 tickers VERBATIM (same tuple object) — the
        # surface PR #92's vol-gate control-arm result was measured on.
        assert sweeps.R4_REGIME_INSTRUMENTS is sweeps.R3_NEW_TICKERS_INSTRUMENTS
        assert sweeps.R4_REGIME_INSTRUMENTS == ("SPY", "QQQ", "TSLA",
                                                "JPM", "XOM", "TLT")

    def test_k_counts_every_config_and_bar_never_lowered(self):
        # K = 14 counts EVERY registered config this lane tries (12
        # conditional + 2 control); the bar RISES above the round-standard
        # 2.638 — K is never counted down.
        from trading_lab import promotion
        assert sweeps.R4_REGIME_K == 14
        assert sweeps.R4_REGIME_K == sum(
            sweeps.r4_regime_variants_per_arm().values())
        assert (promotion.min_tstat(sweeps.R4_REGIME_K)
                > promotion.min_tstat(12))
        assert round(promotion.min_tstat(sweeps.R4_REGIME_K), 3) == 2.690

    def test_conditional_variants_shape(self):
        variants = sweeps.r4_regime_conditional_variants()
        assert len(variants) == 12
        # deterministic and unique
        assert variants == sweeps.r4_regime_conditional_variants()
        assert len({tuple(sorted(v.items())) for v in variants}) == 12
        for v in variants:
            assert v["regime_condition"] is True
            assert v["metric"] in ("adx", "sma_slope")
            assert v["rank_window"] in (126, 252, 504)
            assert v["weak_family"] in ("flat", "reversion")
            # frozen components baked into every variant
            for key, val in sweeps.R4_REGIME_COMPONENT_PARAMS.items():
                assert v[key] == val

    def test_control_variants_are_the_conditionless_collapse(self):
        controls = sweeps.r4_regime_control_variants()
        assert len(controls) == 2
        for v in controls:
            assert v["regime_condition"] is False
            # the control arm never computes the metric — the regime axes
            # are deliberately absent
            assert "metric" not in v and "rank_window" not in v
            for key, val in sweeps.R4_REGIME_COMPONENT_PARAMS.items():
                assert v[key] == val
        # same weak-family coverage as the conditional arm
        assert ({v["weak_family"] for v in controls}
                == {v["weak_family"]
                    for v in sweeps.r4_regime_conditional_variants()})

    def test_component_params_are_committed_r3_grid_points(self):
        # NO new parameter territory: the frozen components are grid
        # points of the committed round-3 sweeps on THESE instruments.
        comp = sweeps.R4_REGIME_COMPONENT_PARAMS
        ema_point = {"fast": comp["trend_fast"], "slow": comp["trend_slow"]}
        assert ema_point in sweeps.r3_trend_new_tickers_variants(
            "ema_crossover")
        rsi_point = {"period": comp["rsi_period"],
                     "oversold": comp["rsi_oversold"],
                     "overbought": comp["rsi_overbought"]}
        assert rsi_point in sweeps.r3_meanrev_new_tickers_variants(
            "rsi_mean_reversion")

    def test_all_variants_runnable(self, random_walk):
        strategy = STRATEGIES[sweeps.R4_REGIME_STRATEGY_NAME]
        for params in (sweeps.r4_regime_conditional_variants()
                       + sweeps.r4_regime_control_variants()):
            pos = strategy(random_walk, **params)
            assert not pos.isna().any()
            assert ((pos >= 0.0) & (pos <= 1.0)).all()


class TestR4CrossassetGrid:
    """R4-E cross-asset exposure gate — grid + constants pinned BEFORE
    the sweep runs (docs/research-round-4-plan.md § R4-E)."""

    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R4_CROSSASSET_FAMILY
        assert set(sweeps.R4_CROSSASSET_FAMILIES) == set(R4_CROSSASSET_FAMILY)
        assert sweeps.R4_CROSSASSET_STRATEGY_NAME in STRATEGIES

    def test_registered_counts(self):
        # Pre-registered R4-E accounting: 12 gated + 1 control variant
        # per lane x 2 instruments = 26 registered configs.
        assert sweeps.r4_crossasset_variants_per_arm() == {"gated": 12,
                                                           "control": 1}
        assert sweeps.r4_crossasset_total_configs() == 26
        assert sweeps.R4_CROSSASSET_INSTRUMENTS == ("SPY", "QQQ")

    def test_gate_universe_is_the_committed_r3_caches(self):
        # The plan-named gate assets, verbatim: TLT primary, XOM and GLD
        # the pre-declared alternates (committed round-3 caches only).
        from trading_lab.strategies import crossasset_gate
        assert sweeps.R4_CROSSASSET_GATE_ASSETS == ("TLT", "XOM", "GLD")
        assert (sweeps.R4_CROSSASSET_GATE_ASSETS
                == crossasset_gate.GATE_ASSETS)

    def test_k_counts_every_config_and_bar_never_lowered(self):
        # K = 13 counts EVERY registered config this lane tries (12 gated
        # + 1 control); the bar RISES above the round-standard 2.638 — K
        # is never counted down (precedent PR #104).
        from trading_lab import promotion
        assert sweeps.R4_CROSSASSET_K == 13
        assert sweeps.R4_CROSSASSET_K == sum(
            sweeps.r4_crossasset_variants_per_arm().values())
        assert (promotion.min_tstat(sweeps.R4_CROSSASSET_K)
                > promotion.min_tstat(12))
        assert round(promotion.min_tstat(sweeps.R4_CROSSASSET_K), 3) == 2.665

    def test_gated_variants_shape(self):
        variants = sweeps.r4_crossasset_gated_variants()
        assert len(variants) == 12
        # deterministic and unique
        assert variants == sweeps.r4_crossasset_gated_variants()
        assert len({tuple(sorted(v.items())) for v in variants}) == 12
        for v in variants:
            assert v["gated"] is True
            assert v["gate_asset"] in ("TLT", "XOM", "GLD")
            assert v["gate_lookback"] in (21, 63, 126, 252)
            # frozen equity component baked into every variant
            for key, val in sweeps.R4_CROSSASSET_COMPONENT_PARAMS.items():
                assert v[key] == val

    def test_control_variant_is_the_gateless_collapse(self):
        controls = sweeps.r4_crossasset_control_variants()
        assert len(controls) == 1
        (v,) = controls
        assert v["gated"] is False
        # the control arm never loads gate data — the gate axes are
        # deliberately absent
        assert "gate_asset" not in v and "gate_lookback" not in v
        for key, val in sweeps.R4_CROSSASSET_COMPONENT_PARAMS.items():
            assert v[key] == val

    def test_component_params_are_a_committed_r3_grid_point(self):
        # NO new parameter territory: the frozen equity component is a
        # grid point of the committed round-3 trend sweep on BOTH R4-E
        # instruments (the PR #104 freeze, reused verbatim).
        comp = sweeps.R4_CROSSASSET_COMPONENT_PARAMS
        ema_point = {"fast": comp["trend_fast"], "slow": comp["trend_slow"]}
        assert ema_point in sweeps.r3_trend_new_tickers_variants(
            "ema_crossover")
        # the identical freeze PR #104 used (subset of its components)
        assert comp.items() <= sweeps.R4_REGIME_COMPONENT_PARAMS.items()
        assert set(sweeps.R4_CROSSASSET_INSTRUMENTS) <= set(
            sweeps.R3_TREND_NEW_TICKERS_INSTRUMENTS)

    def test_all_variants_runnable(self, random_walk):
        # Gated variants load the committed dev-rail gate caches
        # (holdout excluded by the loader default) — offline, local only.
        strategy = STRATEGIES[sweeps.R4_CROSSASSET_STRATEGY_NAME]
        for params in (sweeps.r4_crossasset_gated_variants()
                       + sweeps.r4_crossasset_control_variants()):
            pos = strategy(random_walk, **params)
            assert not pos.isna().any()
            assert ((pos >= 0.0) & (pos <= 1.0)).all()


class TestR5ANeighborGrids:
    """R5-A parameter-neighborhood probes — pre-declared BEFORE the slice
    runs (docs/research-round-5-plan.md § R5-A). Neighbors are selection-free
    PROBES of the frozen top-5 KEEP-dev lanes, never entrants."""

    # The plan's frozen target set, verbatim (no swap-ins, no re-ranking).
    PLAN_TOP5 = [
        ("r3-btc-coverage", "bollinger_breakout", "BTC-USD", "daily",
         {"period": 10, "num_std": 1.0}),
        ("r3-stoch-willr", "williams_r_reversion", "SLV", "daily",
         {"period": 21, "buy_below": -90, "sell_above": -30}),
        ("r3-trix-ichimoku", "ichimoku_trend", "META", "daily",
         {"tenkan": 7, "kijun": 26, "senkou_b": 44}),
        ("r3-meanrev-hourly", "stochastic_reversion", "META", "hourly",
         {"k_period": 14, "buy_below": 10, "sell_above": 80}),
        ("r3-trend-new-tickers", "ema_crossover", "TLT", "daily",
         {"fast": 30, "slow": 50}),
    ]

    def test_target_lanes_are_the_frozen_plan_top5(self):
        assert len(sweeps.R5A_TARGET_LANES) == 5
        got = [(l["sweep"], l["family"], l["instrument"], l["timeframe"],
                l["top_variant"]) for l in sweeps.R5A_TARGET_LANES]
        assert got == self.PLAN_TOP5

    def test_source_files_exist_and_families_registered(self):
        from trading_lab import config
        for lane in sweeps.R5A_TARGET_LANES:
            assert (config.REPO_ROOT / lane["source_file"]).exists(), \
                lane["source_file"]
            assert lane["family"] in STRATEGIES

    def test_top_variant_is_a_committed_grid_point(self):
        # Every top variant sits on its SOURCE lane's declared Round-3 grid
        # — the neighborhood is defined on that grid, no new territory.
        source_variants = {
            "r3-btc-coverage__bollinger_breakout__BTC-USD__daily":
                sweeps.r3_breakout_variants("bollinger_breakout"),
            "r3-stoch-willr__williams_r_reversion__SLV__daily":
                sweeps.r3_stoch_willr_variants("williams_r_reversion"),
            "r3-trix-ichimoku__ichimoku_trend__META__daily":
                sweeps.r3_trix_ichimoku_variants("ichimoku_trend"),
            "r3-meanrev-hourly__stochastic_reversion__META__hourly":
                sweeps.r3_meanrev_hourly_variants("stochastic_reversion"),
            "r3-trend-new-tickers__ema_crossover__TLT__daily":
                sweeps.r3_trend_new_tickers_variants("ema_crossover"),
        }
        for lane in sweeps.R5A_TARGET_LANES:
            assert lane["top_variant"] in source_variants[lane["lane_id"]]

    def test_neighbors_are_grid_points_too(self):
        # A ±1-step single-parameter perturbation that satisfies the family
        # constraint is by construction a point of the same committed grid.
        source_variants = {
            "r3-btc-coverage__bollinger_breakout__BTC-USD__daily":
                sweeps.r3_breakout_variants("bollinger_breakout"),
            "r3-stoch-willr__williams_r_reversion__SLV__daily":
                sweeps.r3_stoch_willr_variants("williams_r_reversion"),
            "r3-trix-ichimoku__ichimoku_trend__META__daily":
                sweeps.r3_trix_ichimoku_variants("ichimoku_trend"),
            "r3-meanrev-hourly__stochastic_reversion__META__hourly":
                sweeps.r3_meanrev_hourly_variants("stochastic_reversion"),
            "r3-trend-new-tickers__ema_crossover__TLT__daily":
                sweeps.r3_trend_new_tickers_variants("ema_crossover"),
        }
        for lane in sweeps.R5A_TARGET_LANES:
            for nb in sweeps.r5a_neighbors(lane["lane_id"]):
                assert nb in source_variants[lane["lane_id"]], \
                    (lane["lane_id"], nb)

    def test_neighbors_are_single_param_one_step_perturbations(self):
        for lane in sweeps.R5A_TARGET_LANES:
            top = lane["top_variant"]
            axes = sweeps._R5A_SOURCE_AXES[lane["lane_id"]]
            for nb in sweeps.r5a_neighbors(lane["lane_id"]):
                changed = [k for k in top if nb[k] != top[k]]
                assert len(changed) == 1, (lane["lane_id"], nb)
                key = changed[0]
                values = axes[key]
                assert abs(values.index(nb[key])
                           - values.index(top[key])) == 1

    def test_neighbor_counts_bounded_and_stable(self):
        # Registered burden: the actual clipped neighborhood is 14 configs
        # (2+4+3+3+2), inside the plan's <= 8 per lane / <= 40 total bound.
        counts = sweeps.r5a_neighbors_per_lane()
        assert counts == {
            "r3-btc-coverage__bollinger_breakout__BTC-USD__daily": 2,
            "r3-stoch-willr__williams_r_reversion__SLV__daily": 4,
            "r3-trix-ichimoku__ichimoku_trend__META__daily": 3,
            "r3-meanrev-hourly__stochastic_reversion__META__hourly": 3,
            "r3-trend-new-tickers__ema_crossover__TLT__daily": 2,
        }
        for n in counts.values():
            assert 1 <= n <= sweeps.R5A_MAX_NEIGHBORS_PER_LANE
        assert sweeps.r5a_total_configs() == 14
        assert sweeps.r5a_total_configs() <= 40

    def test_no_neighbor_is_the_top_variant_and_all_unique(self):
        for lane in sweeps.R5A_TARGET_LANES:
            nbs = sweeps.r5a_neighbors(lane["lane_id"])
            assert lane["top_variant"] not in nbs
            assert len({tuple(sorted(nb.items())) for nb in nbs}) == len(nbs)

    def test_neighbors_respect_family_constraints(self):
        for lane in sweeps.R5A_TARGET_LANES:
            keep = sweeps._R5A_SOURCE_CONSTRAINTS[lane["lane_id"]]
            for nb in sweeps.r5a_neighbors(lane["lane_id"]):
                assert keep(nb)

    def test_every_neighbor_runs(self, random_walk):
        for lane in sweeps.R5A_TARGET_LANES:
            fn = STRATEGIES[lane["family"]]
            for nb in sweeps.r5a_neighbors(lane["lane_id"]):
                pos = fn(random_walk, **nb)
                assert not pos.isna().any()

    def test_unknown_lane_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r5a_neighbors("r3-astrology__tea_leaves__SPY__daily")
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r5a_lane("nope")

    def test_deterministic_order(self):
        for lane in sweeps.R5A_TARGET_LANES:
            assert (sweeps.r5a_neighbors(lane["lane_id"])
                    == sweeps.r5a_neighbors(lane["lane_id"]))


class TestR6VolumeGrids:
    """Round-6 slice R6-A pre-declaration pins (docs/research-round-6-plan.md
    § R6-A): the grids are committed BEFORE the sweep runs and these pins
    freeze them."""

    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R6_VOLUME_FAMILY
        assert set(sweeps.R6_VOLUME_FAMILIES) == set(R6_VOLUME_FAMILY)
        for fam in sweeps.R6_VOLUME_FAMILIES:
            assert fam in STRATEGIES

    def test_registered_counts(self):
        # Multiple-testing discipline: the counts reported in the plan and
        # in any Round-6 lane JSON must match these.
        assert sweeps.r6_volume_variants_per_family() == \
            {"obv_trend": 12, "mfi_reversion": 12}
        assert sweeps.r6_volume_total_configs() == 360

    def test_k_is_round_standard_and_bar_never_lowered(self):
        # Per-lane informational K = 12 variants per family grid, exactly
        # the rounds-2-5 standard; min_tstat(12) ~ 2.64, never lowered.
        from trading_lab import promotion
        assert sweeps.R6_VOLUME_K == 12
        assert all(n == sweeps.R6_VOLUME_K
                   for n in sweeps.r6_volume_variants_per_family().values())
        assert round(promotion.min_tstat(sweeps.R6_VOLUME_K), 2) == 2.64

    def test_instruments_are_the_committed_r4f_surface_verbatim(self):
        # Same tuple OBJECT as the R4-F seasonality surface — all 15
        # committed daily caches, no new caches, nothing fetched, and no
        # post-hoc instrument selection possible.
        assert sweeps.R6_VOLUME_INSTRUMENTS is sweeps.R4_SEASONALITY_INSTRUMENTS
        assert len(sweeps.R6_VOLUME_INSTRUMENTS) == 15

    def test_constraints_filtered(self):
        for p in sweeps.r6_volume_variants("mfi_reversion"):
            assert 0 < p["buy_below"] < p["sell_above"] < 100
        for p in sweeps.r6_volume_variants("obv_trend"):
            assert p["window"] >= 2

    def test_obv_pure_control_arm_committed_for_every_window(self):
        # price_confirm=False (the pure-OBV within-family control) exists
        # for every window in the SAME grid — no post-hoc arm selection.
        variants = sweeps.r6_volume_variants("obv_trend")
        for w in {p["window"] for p in variants}:
            assert {"window": w, "price_confirm": False} in variants
            assert {"window": w, "price_confirm": True} in variants

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R6_VOLUME_FAMILIES:
            for params in sweeps.r6_volume_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()
                assert set(np.unique(pos)) <= {0.0, 1.0}

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r6_volume_variants("astrology")

    def test_deterministic_order(self):
        for fam in sweeps.R6_VOLUME_FAMILIES:
            assert (sweeps.r6_volume_variants(fam)
                    == sweeps.r6_volume_variants(fam))


class TestR6GapGrid:
    """Round-6 slice R6-B pre-declaration pins (docs/research-round-6-plan.md
    § R6-B)."""

    def test_families_match_strategy_registry(self):
        from trading_lab.strategies import R6_GAP_FAMILY
        assert set(sweeps.R6_GAP_FAMILIES) == set(R6_GAP_FAMILY)
        for fam in sweeps.R6_GAP_FAMILIES:
            assert fam in STRATEGIES

    def test_registered_counts(self):
        from trading_lab import promotion
        assert sweeps.r6_gap_variants_per_family() == {"overnight_gap": 12}
        assert sweeps.r6_gap_total_configs() == 144
        assert sweeps.R6_GAP_K == 12
        assert round(promotion.min_tstat(sweeps.R6_GAP_K), 2) == 2.64

    def test_instruments_are_the_committed_slice8_set_verbatim_no_btc(self):
        # Same tuple OBJECT as the slice-8 12-ticker mixed set; BTC-USD is
        # deliberately excluded — a 24/7 market has no overnight gap.
        assert sweeps.R6_GAP_INSTRUMENTS is sweeps.R3_TRIX_ICHIMOKU_INSTRUMENTS
        assert len(sweeps.R6_GAP_INSTRUMENTS) == 12
        assert "BTC-USD" not in sweeps.R6_GAP_INSTRUMENTS

    def test_both_mirror_theses_committed_in_the_same_grid(self):
        # fade and follow each cover the full gap_atr x hold sub-grid, so
        # neither thesis can be cherry-picked after outcomes.
        variants = sweeps.r6_gap_variants("overnight_gap")
        fade = [p for p in variants if p["mode"] == "fade"]
        follow = [p for p in variants if p["mode"] == "follow"]
        assert len(fade) == len(follow) == 6
        strip = lambda p: {k: v for k, v in p.items() if k != "mode"}
        assert [strip(p) for p in fade] == [strip(p) for p in follow]

    def test_atr_period_is_frozen_not_swept(self):
        # atr_period stays at the lab-standard default 14 and is NOT a
        # grid axis (it would quadruple the burden for a nuisance param).
        from trading_lab.strategies import DEFAULT_PARAMS
        for p in sweeps.r6_gap_variants("overnight_gap"):
            assert set(p) == {"mode", "gap_atr", "hold"}
        assert DEFAULT_PARAMS["overnight_gap"]["atr_period"] == 14

    def test_every_variant_runs(self, random_walk):
        for params in sweeps.r6_gap_variants("overnight_gap"):
            pos = STRATEGIES["overnight_gap"](random_walk, **params)
            assert not pos.isna().any()
            assert set(np.unique(pos)) <= {0.0, 1.0}

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r6_gap_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r6_gap_variants("overnight_gap")
                == sweeps.r6_gap_variants("overnight_gap"))


class TestR6VolumeHourlyGrid:
    """Round-6 slice R6-C pre-declaration pins (docs/research-round-6-plan.md
    § R6-C): timeframe expansion of R6-A — grid identity is the point."""

    def test_families_and_grids_identical_to_r6a(self):
        assert sweeps.R6_VOLUME_HOURLY_FAMILIES is sweeps.R6_VOLUME_FAMILIES
        for fam in sweeps.R6_VOLUME_HOURLY_FAMILIES:
            assert (sweeps.r6_volume_hourly_variants(fam)
                    == sweeps.r6_volume_variants(fam))

    def test_registered_counts(self):
        from trading_lab import promotion
        assert sweeps.r6_volume_hourly_variants_per_family() == \
            {"obv_trend": 12, "mfi_reversion": 12}
        assert sweeps.r6_volume_hourly_total_configs() == 192
        assert sweeps.R6_VOLUME_HOURLY_K == 12
        assert round(promotion.min_tstat(sweeps.R6_VOLUME_HOURLY_K), 2) == 2.64

    def test_instruments_are_the_committed_hourly_surface_verbatim(self):
        # Same tuple OBJECT as the r3-trend-hourly 8-ticker surface — the
        # complete committed data/hourly/ cache set, nothing fetched.
        assert (sweeps.R6_VOLUME_HOURLY_INSTRUMENTS
                is sweeps.R3_TREND_HOURLY_INSTRUMENTS)
        assert len(sweeps.R6_VOLUME_HOURLY_INSTRUMENTS) == 8

    def test_round_total_configs(self):
        # The plan's burden ledger: 360 + 144 + 192 = 696 new registered
        # configs; program cumulative 4359 -> 5055.
        assert sweeps.r6_total_configs() == 696


class TestRound7:
    """Round-7 pre-declaration pins (docs/research-round-7-plan.md, ORDER
    018): the two STATE-family grids are committed BEFORE the sweep runs and
    these pins freeze them under the selection-fair standing gate [D-0002]."""

    def test_families_match_strategy_registry(self):
        for fam in sweeps.R7_FAMILIES:
            assert fam in STRATEGIES
        assert sweeps.R7_FAMILIES == ("drawdown_reversion", "high_proximity")

    def test_axes_are_exactly_the_pre_registered_grids(self):
        assert sweeps._R7_DRAWDOWN_AXES == {
            "drawdown_reversion": {"lookback": [63, 126, 252],
                                   "entry_dd": [0.10, 0.20],
                                   "exit_frac": [0.5, 1.0]}}
        assert sweeps._R7_HIGHPROX_AXES == {
            "high_proximity": {"N": [63, 126, 252],
                               "p": [0.85, 0.90, 0.95, 0.98]}}

    def test_registered_counts(self):
        assert len(sweeps.r7_drawdown_variants("drawdown_reversion")) == 12
        assert len(sweeps.r7_highprox_variants("high_proximity")) == 12
        assert sweeps.r7_variants_per_family() == \
            {"drawdown_reversion": 12, "high_proximity": 12}

    def test_k_is_round_standard_and_bar_never_lowered(self):
        from trading_lab import promotion
        assert sweeps.R7_K == 12
        assert all(n == sweeps.R7_K
                   for n in sweeps.r7_variants_per_family().values())
        assert round(promotion.min_tstat(sweeps.R7_K), 2) == 2.64

    def test_instruments_are_the_committed_r6a_surface_verbatim(self):
        # Same tuple OBJECT as the R6-A / R4-F 15-ticker daily surface — no
        # new caches, nothing fetched, no post-hoc instrument selection.
        assert sweeps.R7_INSTRUMENTS is sweeps.R6_VOLUME_INSTRUMENTS
        assert len(sweeps.R7_INSTRUMENTS) == 15

    def test_constraints_filtered(self):
        for p in sweeps.r7_drawdown_variants("drawdown_reversion"):
            assert p["lookback"] >= 2
            assert 0.0 < p["entry_dd"] < 1.0
            assert 0.0 < p["exit_frac"] <= 1.0
        for p in sweeps.r7_highprox_variants("high_proximity"):
            assert p["N"] >= 2
            assert 0.0 < p["p"] <= 1.0

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R7_FAMILIES:
            for params in sweeps.r7_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()
                assert set(np.unique(pos)) <= {0.0, 1.0}

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r7_drawdown_variants("astrology")
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r7_highprox_variants("astrology")
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r7_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r7_drawdown_variants("drawdown_reversion")
                == sweeps.r7_drawdown_variants("drawdown_reversion"))
        assert (sweeps.r7_highprox_variants("high_proximity")
                == sweeps.r7_highprox_variants("high_proximity"))

    def test_round_total_configs_and_program_ledger(self):
        # The plan's burden ledger: 24 variants x 15 tickers = 360 new
        # registered configs; program cumulative 5055 -> 5415.
        assert sweeps.r7_total_configs() == 360
        assert 5055 + sweeps.r7_total_configs() == 5415


class TestRound7C:
    """Round-7C pre-declaration pins (docs/research-round-7c-plan.md, ORDER
    018): the washout_recovery CONJUNCTION grid is committed BEFORE the sweep
    runs and these pins freeze it under the selection-fair standing gate
    [D-0002]. W_prox < W_dd is a registered constraint, not a variant."""

    def test_families_match_strategy_registry(self):
        for fam in sweeps.R7C_CONJUNCTION_FAMILIES:
            assert fam in STRATEGIES
        assert sweeps.R7C_CONJUNCTION_FAMILIES == ("washout_recovery",)

    def test_axes_are_exactly_the_pre_registered_grid(self):
        assert sweeps._R7C_CONJUNCTION_AXES == {
            "washout_recovery": {"W_dd": [252], "entry_dd": [0.10, 0.20],
                                 "W_prox": [21, 42, 63], "p": [0.90, 0.95]}}

    def test_registered_counts(self):
        assert len(sweeps.r7c_conjunction_variants("washout_recovery")) == 12
        assert sweeps.r7c_conjunction_variants_per_family() == \
            {"washout_recovery": 12}

    def test_k_is_round_standard_and_bar_never_lowered(self):
        from trading_lab import promotion
        assert sweeps.R7C_K == 12
        assert all(n == sweeps.R7C_K
                   for n in sweeps.r7c_conjunction_variants_per_family().values())
        assert round(promotion.min_tstat(sweeps.R7C_K), 2) == 2.64

    def test_instruments_are_the_r7_surface_verbatim(self):
        # Same tuple OBJECT as the R7 15-ticker daily surface — no new
        # caches, nothing fetched, no post-hoc instrument selection.
        assert sweeps.R7C_INSTRUMENTS is sweeps.R7_INSTRUMENTS
        assert len(sweeps.R7C_INSTRUMENTS) == 15

    def test_wprox_lt_wdd_constraint_enforced(self):
        # The registered constraint: every expanded variant satisfies
        # W_prox < W_dd (a single window collapses to a contradiction).
        for c in sweeps.r7c_conjunction_variants("washout_recovery"):
            assert c["W_dd"] >= 2
            assert c["W_prox"] >= 2
            assert c["W_prox"] < c["W_dd"]
            assert 0.0 < c["entry_dd"] < 1.0
            assert 0.0 < c["p"] <= 1.0

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R7C_CONJUNCTION_FAMILIES:
            for params in sweeps.r7c_conjunction_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()
                assert set(np.unique(pos)) <= {0.0, 1.0}

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r7c_conjunction_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r7c_conjunction_variants("washout_recovery")
                == sweeps.r7c_conjunction_variants("washout_recovery"))

    def test_round_total_configs_and_program_ledger(self):
        # The plan's burden ledger: 12 variants x 15 tickers = 180 new
        # registered configs; program cumulative 5415 -> 5595.
        assert sweeps.r7c_total_configs() == 180
        assert 5415 + sweeps.r7c_total_configs() == 5595


class TestR7DXsecDrawdown:
    """Round-7D pre-declaration pins (docs/research-round-7d-plan.md, owner
    GO 2026-07-18): the xsec_drawdown cross-sectional PORTFOLIO grid is
    committed BEFORE the sweep runs and these pins freeze it. PORTFOLIO lane:
    configs = variants (instruments do NOT multiply). Mirrors
    TestR3XsecExpandedGrid."""

    def test_family_registered_as_portfolio_only(self):
        from trading_lab.strategies import (PORTFOLIO_STRATEGIES,
                                            R7D_XSEC_DRAWDOWN_FAMILY)
        assert R7D_XSEC_DRAWDOWN_FAMILY == "xsec_drawdown"
        assert sweeps.R7D_XSEC_DRAWDOWN_FAMILIES == (R7D_XSEC_DRAWDOWN_FAMILY,)
        for fam in sweeps.R7D_XSEC_DRAWDOWN_FAMILIES:
            assert fam in PORTFOLIO_STRATEGIES
            assert fam not in STRATEGIES  # panel interface, not per-ticker

    def test_axes_are_exactly_the_pre_registered_grid(self):
        assert sweeps._R7D_XSEC_DRAWDOWN_AXES == {
            "xsec_drawdown": {"L": [63, 126, 252], "k": [2, 3]}}

    def test_registered_counts(self):
        # L{63,126,252} x k{2,3} = 3 x 2 = 6 variants.
        assert len(sweeps.r7d_xsec_drawdown_variants("xsec_drawdown")) == 6
        assert sweeps.r7d_xsec_drawdown_variants_per_family() == \
            {"xsec_drawdown": 6}

    def test_portfolio_config_count_is_variants_not_times_instruments(self):
        # PORTFOLIO lane: 6 configs, NOT 6 x 14 = 84.
        assert sweeps.r7d_total_configs() == 6
        assert sweeps.r7d_total_configs() == \
            len(sweeps.r7d_xsec_drawdown_variants("xsec_drawdown"))

    def test_k_is_round_standard_and_bar_never_lowered(self):
        from trading_lab import promotion
        assert sweeps.R7D_K == 6
        assert all(n == sweeps.R7D_K
                   for n in sweeps.r7d_xsec_drawdown_variants_per_family().values())
        # xsec K=6 Bonferroni bar, unchanged and never lowered (~2.39).
        assert round(promotion.min_tstat(sweeps.R7D_K), 2) == 2.39

    def test_basket_is_the_xsec14_tuple_object(self):
        assert sweeps.R7D_INSTRUMENTS is sweeps.R3_XSEC_EXPANDED_INSTRUMENTS
        assert len(sweeps.R7D_INSTRUMENTS) == 14
        assert "BTC-USD" not in sweeps.R7D_INSTRUMENTS

    def test_rebalance_cadence_frozen_not_swept(self):
        assert sweeps.R7D_XSEC_DRAWDOWN_REBALANCE_EVERY == {"xsec_drawdown": 21}
        for params in sweeps.r7d_xsec_drawdown_variants("xsec_drawdown"):
            assert "rebalance_every" not in params
            assert set(params) == {"L", "k"}  # nothing else is swept

    def test_grid_is_exactly_the_registered_product(self):
        variants = sweeps.r7d_xsec_drawdown_variants("xsec_drawdown")
        assert ({(p["L"], p["k"]) for p in variants}
                == {(L, k) for L in (63, 126, 252) for k in (2, 3)})

    def test_every_variant_runs(self):
        from trading_lab.strategies import PORTFOLIO_STRATEGIES
        rng = np.random.default_rng(714)
        idx = pd.bdate_range("2020-01-01", periods=400)
        closes = pd.DataFrame(
            {t: 100.0 * np.exp(np.cumsum(rng.normal(0.0, 0.02, 400)))
             for t in sweeps.R7D_INSTRUMENTS}, index=idx)
        rebal = sweeps.R7D_XSEC_DRAWDOWN_REBALANCE_EVERY["xsec_drawdown"]
        for params in sweeps.r7d_xsec_drawdown_variants("xsec_drawdown"):
            w = PORTFOLIO_STRATEGIES["xsec_drawdown"](
                closes, rebalance_every=rebal, **params)
            rows = w.dropna(how="all")
            assert len(rows) > 0
            assert np.allclose(rows.sum(axis=1), 1.0)

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r7d_xsec_drawdown_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r7d_xsec_drawdown_variants("xsec_drawdown")
                == sweeps.r7d_xsec_drawdown_variants("xsec_drawdown"))

    def test_round_total_configs_and_program_ledger(self):
        # Burden ledger: 6 variants = 6 new registered configs (portfolio
        # lane, configs = variants); program cumulative 5595 -> 5601.
        assert sweeps.r7d_total_configs() == 6
        assert 5595 + sweeps.r7d_total_configs() == 5601


class TestRound8Hourly:
    """Round-8 pre-declaration pins (docs/research-round-8-plan.md, owner GO
    2026-07-18T13:47Z): the HOURLY COMPANION grids for the two newest R7
    single-instrument families are committed BEFORE the sweep runs and these
    pins freeze them under the selection-fair standing gate [D-0002]. NO new
    strategy code — the IDENTICAL R7 12-variant grids re-registered on the
    committed 8-ticker hourly cache; grid identity with R7 pinned here.
    Mirrors TestRound7."""

    def test_families_match_strategy_registry(self):
        for fam in sweeps.R8_HOURLY_FAMILIES:
            assert fam in STRATEGIES
        assert sweeps.R8_HOURLY_FAMILIES == ("drawdown_reversion",
                                             "high_proximity")

    def test_axes_are_exactly_the_pre_registered_grids(self):
        assert sweeps._R8_HOURLY_DRAWDOWN_AXES == {
            "drawdown_reversion": {"lookback": [63, 126, 252],
                                   "entry_dd": [0.10, 0.20],
                                   "exit_frac": [0.5, 1.0]}}
        assert sweeps._R8_HOURLY_HIGHPROX_AXES == {
            "high_proximity": {"N": [63, 126, 252],
                               "p": [0.85, 0.90, 0.95, 0.98]}}

    def test_axes_are_value_identical_to_the_r7_daily_axes(self):
        # Pure timeframe companion: the hourly grids carry the SAME parameter
        # values as the R7 daily grids (only the bar denomination differs).
        assert (sweeps._R8_HOURLY_DRAWDOWN_AXES
                == sweeps._R7_DRAWDOWN_AXES)
        assert (sweeps._R8_HOURLY_HIGHPROX_AXES
                == sweeps._R7_HIGHPROX_AXES)

    def test_registered_counts(self):
        assert len(sweeps.r8_hourly_variants("drawdown_reversion")) == 12
        assert len(sweeps.r8_hourly_variants("high_proximity")) == 12
        assert sweeps.r8_hourly_variants_per_family() == \
            {"drawdown_reversion": 12, "high_proximity": 12}

    def test_k_is_round_standard_and_bar_never_lowered(self):
        from trading_lab import promotion
        assert sweeps.R8_K == 12
        assert all(n == sweeps.R8_K
                   for n in sweeps.r8_hourly_variants_per_family().values())
        assert round(promotion.min_tstat(sweeps.R8_K), 2) == 2.64

    def test_instruments_are_the_committed_hourly8_surface_verbatim(self):
        # Same tuple OBJECT as the R6-C / r3-trend-hourly 8-ticker hourly
        # surface — no new caches, nothing fetched, no post-hoc selection.
        assert (sweeps.R8_HOURLY_INSTRUMENTS
                is sweeps.R6_VOLUME_HOURLY_INSTRUMENTS)
        assert len(sweeps.R8_HOURLY_INSTRUMENTS) == 8
        assert set(sweeps.R8_HOURLY_INSTRUMENTS) == {
            "AAPL", "AMZN", "GLD", "GOOGL", "META", "MSFT", "NVDA", "SLV"}

    def test_constraints_filtered(self):
        for p in sweeps.r8_hourly_variants("drawdown_reversion"):
            assert p["lookback"] >= 2
            assert 0.0 < p["entry_dd"] < 1.0
            assert 0.0 < p["exit_frac"] <= 1.0
        for p in sweeps.r8_hourly_variants("high_proximity"):
            assert p["N"] >= 2
            assert 0.0 < p["p"] <= 1.0

    def test_every_variant_runs(self, random_walk):
        for fam in sweeps.R8_HOURLY_FAMILIES:
            for params in sweeps.r8_hourly_variants(fam):
                pos = STRATEGIES[fam](random_walk, **params)
                assert not pos.isna().any()
                assert set(np.unique(pos)) <= {0.0, 1.0}

    def test_unknown_family_rejected(self):
        with pytest.raises(ValueError, match="unknown"):
            sweeps.r8_hourly_variants("astrology")

    def test_deterministic_order(self):
        assert (sweeps.r8_hourly_variants("drawdown_reversion")
                == sweeps.r8_hourly_variants("drawdown_reversion"))
        assert (sweeps.r8_hourly_variants("high_proximity")
                == sweeps.r8_hourly_variants("high_proximity"))

    def test_round_total_configs_and_program_ledger(self):
        # Burden ledger: (12 + 12) variants x 8 hourly tickers = 192 new
        # registered configs; program cumulative 5601 -> 5793.
        assert sweeps.r8_total_configs() == 192
        assert 5601 + sweeps.r8_total_configs() == 5793


class TestRound9:
    """Round-9 pre-declaration pins (docs/research-round-9-plan.md, ORDER
    019): the signal-CONFLUENCE vote grid is committed BEFORE the sweep runs
    and these pins freeze it. Members run at FIXED DEFAULT_PARAMS (no
    per-member re-search); the only searched axis is (member-set, K). The
    vote itself is trading_lab.ensemble.confluence_positions (an AND/vote
    gate, distinct from the R4-C committee AVERAGE)."""

    def test_member_sets_are_exactly_the_pre_registered_panels(self):
        assert sweeps._R9_MEMBER_SET_3 == [
            "ema_crossover", "rsi_mean_reversion", "donchian"]
        assert sweeps._R9_MEMBER_SET_5 == [
            "ema_crossover", "rsi_mean_reversion", "donchian",
            "drawdown_reversion", "obv_trend"]

    def test_every_member_is_in_the_strategy_registry(self):
        from trading_lab.strategies import DEFAULT_PARAMS
        for m in sweeps._R9_MEMBER_SET_3 + sweeps._R9_MEMBER_SET_5:
            assert m in STRATEGIES
            assert m in DEFAULT_PARAMS

    def test_member_classes_are_distinct_per_set(self):
        # Distinctness is the whole point: no family repeats within a panel
        # (a vote among duplicates is one signal counted twice).
        assert len(sweeps._R9_MEMBER_SET_3) == len(set(sweeps._R9_MEMBER_SET_3))
        assert len(sweeps._R9_MEMBER_SET_5) == len(set(sweeps._R9_MEMBER_SET_5))

    def test_vote_configs_are_exactly_the_pre_registered_grid(self):
        assert sweeps.r9_vote_configs() == [
            {"set": "set3", "members": sweeps._R9_MEMBER_SET_3, "k": 2},
            {"set": "set3", "members": sweeps._R9_MEMBER_SET_3, "k": 3},
            {"set": "set5", "members": sweeps._R9_MEMBER_SET_5, "k": 2},
            {"set": "set5", "members": sweeps._R9_MEMBER_SET_5, "k": 3},
        ]
        assert len(sweeps.r9_vote_configs()) == 4

    def test_k_within_two_and_three_and_valid_for_its_set(self):
        for c in sweeps.r9_vote_configs():
            assert c["k"] in (2, 3)
            assert 2 <= c["k"] <= len(c["members"])

    def test_instruments_are_the_r7_surface_verbatim(self):
        # Same tuple OBJECT as the R7 15-ticker daily surface — no new
        # caches, nothing fetched, no post-hoc instrument selection.
        assert sweeps._R9_INSTRUMENTS is sweeps.R7_INSTRUMENTS
        assert sweeps.R9_INSTRUMENTS is sweeps.R7_INSTRUMENTS
        assert len(sweeps.R9_INSTRUMENTS) == 15

    def test_deterministic_order(self):
        assert sweeps.r9_vote_configs() == sweeps.r9_vote_configs()

    def test_members_emit_binary_positions_at_defaults(self, random_walk):
        # Every panel member, at its fixed default params, is a 0/1 long/flat
        # lane — the precondition confluence_positions enforces.
        from trading_lab.strategies import DEFAULT_PARAMS
        for m in sweeps._R9_MEMBER_SET_5:
            pos = STRATEGIES[m](random_walk, **DEFAULT_PARAMS[m])
            assert not pos.isna().any()
            assert set(np.unique(pos)) <= {0.0, 1.0}

    def test_vote_runs_end_to_end(self, random_walk):
        # The confluence compositor grades a full (member-set, K) config into
        # a binary lane on the shared index.
        from trading_lab.ensemble import confluence_positions
        from trading_lab.strategies import DEFAULT_PARAMS
        for c in sweeps.r9_vote_configs():
            members = [STRATEGIES[m](random_walk, **DEFAULT_PARAMS[m])
                       for m in c["members"]]
            vote = confluence_positions(members, c["k"])
            assert vote.index.equals(random_walk.index)
            assert set(np.unique(vote)) <= {0.0, 1.0}

    def test_round_total_configs_and_program_ledger(self):
        # Burden ledger: 4 vote configs x 15 daily tickers = 60 new
        # registered configs; program cumulative 5793 -> 5853.
        assert sweeps.r9_total_configs() == 60
        assert 5793 + sweeps.r9_total_configs() == 5853


class TestRound10:
    """Round-10 pre-declaration pins (docs/research-round-10-plan.md, ORDER
    020): the INVERSE-confluence EXIT-vote grid is committed BEFORE the sweep
    runs and these pins freeze it. It is the De Morgan DUAL of R9 -- the SAME
    member panels, SAME grid, SAME instruments, run at FIXED DEFAULT_PARAMS (no
    per-member re-search); the only searched axis is (member-set, K). The vote
    is trading_lab.ensemble.exit_confluence_positions (long by default, go flat
    when >=K members are flat -- a risk-OFF gate OUT of a hold, distinct from
    R9's confluence_positions gate INTO a long)."""

    def test_member_sets_reuse_the_r9_panels_verbatim(self):
        # Same list OBJECTS as R9 -- one identical panel, aliased not duplicated.
        assert sweeps._R10_MEMBER_SET_3 is sweeps._R9_MEMBER_SET_3
        assert sweeps._R10_MEMBER_SET_5 is sweeps._R9_MEMBER_SET_5
        assert sweeps._R10_MEMBER_SET_3 == [
            "ema_crossover", "rsi_mean_reversion", "donchian"]
        assert sweeps._R10_MEMBER_SET_5 == [
            "ema_crossover", "rsi_mean_reversion", "donchian",
            "drawdown_reversion", "obv_trend"]

    def test_every_member_is_in_the_strategy_registry(self):
        from trading_lab.strategies import DEFAULT_PARAMS
        for m in sweeps._R10_MEMBER_SET_3 + sweeps._R10_MEMBER_SET_5:
            assert m in STRATEGIES
            assert m in DEFAULT_PARAMS

    def test_member_classes_are_distinct_per_set(self):
        assert len(sweeps._R10_MEMBER_SET_3) == len(set(sweeps._R10_MEMBER_SET_3))
        assert len(sweeps._R10_MEMBER_SET_5) == len(set(sweeps._R10_MEMBER_SET_5))

    def test_vote_configs_are_exactly_the_pre_registered_grid(self):
        assert sweeps.r10_vote_configs() == [
            {"set": "set3", "members": sweeps._R10_MEMBER_SET_3, "k": 2},
            {"set": "set3", "members": sweeps._R10_MEMBER_SET_3, "k": 3},
            {"set": "set5", "members": sweeps._R10_MEMBER_SET_5, "k": 2},
            {"set": "set5", "members": sweeps._R10_MEMBER_SET_5, "k": 3},
        ]
        assert len(sweeps.r10_vote_configs()) == 4

    def test_grid_matches_r9_except_gate_direction(self):
        # R10 is R9's dual: identical (set, members, K) axes -- only the
        # compositor differs (exit_confluence_positions vs confluence_positions).
        assert sweeps.r10_vote_configs() == sweeps.r9_vote_configs()

    def test_k_within_two_and_three_and_valid_for_its_set(self):
        for c in sweeps.r10_vote_configs():
            assert c["k"] in (2, 3)
            assert 2 <= c["k"] <= len(c["members"])

    def test_instruments_are_the_r7_surface_verbatim(self):
        # Same tuple OBJECT as the R7/R9 15-ticker daily surface -- no new
        # caches, nothing fetched, no post-hoc instrument selection.
        assert sweeps._R10_INSTRUMENTS is sweeps.R7_INSTRUMENTS
        assert sweeps.R10_INSTRUMENTS is sweeps.R7_INSTRUMENTS
        assert sweeps._R10_INSTRUMENTS is sweeps._R9_INSTRUMENTS
        assert len(sweeps.R10_INSTRUMENTS) == 15

    def test_deterministic_order(self):
        assert sweeps.r10_vote_configs() == sweeps.r10_vote_configs()

    def test_members_emit_binary_positions_at_defaults(self, random_walk):
        from trading_lab.strategies import DEFAULT_PARAMS
        for m in sweeps._R10_MEMBER_SET_5:
            pos = STRATEGIES[m](random_walk, **DEFAULT_PARAMS[m])
            assert not pos.isna().any()
            assert set(np.unique(pos)) <= {0.0, 1.0}

    def test_exit_vote_runs_end_to_end(self, random_walk):
        # The exit compositor grades a full (member-set, K) config into a binary
        # long-by-default / flat-on-exit lane on the shared index.
        from trading_lab.ensemble import exit_confluence_positions
        from trading_lab.strategies import DEFAULT_PARAMS
        for c in sweeps.r10_vote_configs():
            members = [STRATEGIES[m](random_walk, **DEFAULT_PARAMS[m])
                       for m in c["members"]]
            vote = exit_confluence_positions(members, c["k"])
            assert vote.index.equals(random_walk.index)
            assert set(np.unique(vote)) <= {0.0, 1.0}

    def test_de_morgan_dual_of_the_r9_entry_vote(self, random_walk):
        # exit_confluence_positions(m, k) == 1 - confluence_positions(1-m, k)
        # over the actual R10 panels at default params, per vote config.
        from trading_lab.ensemble import (confluence_positions,
                                          exit_confluence_positions)
        from trading_lab.strategies import DEFAULT_PARAMS
        for c in sweeps.r10_vote_configs():
            members = [STRATEGIES[m](random_walk, **DEFAULT_PARAMS[m])
                       for m in c["members"]]
            exit_lane = exit_confluence_positions(members, c["k"])
            inverted = [1.0 - m.astype(float) for m in members]
            dual = 1.0 - confluence_positions(inverted, c["k"])
            pd.testing.assert_series_equal(exit_lane, dual)

    def test_round_total_configs_and_program_ledger(self):
        # Burden ledger: 4 exit-vote configs x 15 daily tickers = 60 new
        # registered configs; program cumulative 5853 -> 5913 (on the RUN).
        assert sweeps.r10_total_configs() == 60
        assert 5853 + sweeps.r10_total_configs() == 5913


class TestRound11:
    """Round-11 pre-declaration pins (docs/research-round-11-plan.md, ORDER
    021): the cross-asset regime-conditioning grid is committed BEFORE the sweep
    runs and these pins freeze it. Condition a base long on a RISK-LEG target by
    a CAUSAL cross-asset regime score (trading_lab.xasset_regime), CONTINUOUSLY
    via a causal rolling-percentile-rank -- NOT a binary gate (how R11 differs
    materially from the burned R4 crossasset_gate / regime_switch classes). Grid:
    3 signals x 3 windows x 3 targets = 27 configs; the mandatory unconditioned
    control arm is plain buy-and-hold of the same target."""

    def test_signals_are_the_three_causal_regime_scores(self):
        from trading_lab import xasset_regime
        assert sweeps._R11_SIGNALS == [
            "xasset_eq_bond_mom", "xasset_metals_riskoff", "xasset_breadth"]
        # identical to the module's registered signal names (the code the RUN uses)
        assert tuple(sweeps._R11_SIGNALS) == xasset_regime.REGIME_SIGNALS

    def test_windows_are_the_registered_trailing_windows(self):
        assert sweeps._R11_WINDOWS == [63, 126, 252]

    def test_targets_are_nyse_calendar_legs_btc_excluded(self):
        # All three targets share the NYSE calendar with the SPY/QQQ/GLD/TLT
        # regime inputs (no cross-calendar reindex). BTC-USD is EXCLUDED as a
        # target (its weekend calendar would force an as-of reindex).
        assert sweeps._R11_TARGETS == ["SPY", "QQQ", "NVDA"]
        assert "BTC-USD" not in sweeps._R11_TARGETS

    def test_percentile_window_is_fixed_252_not_swept(self):
        from trading_lab import xasset_regime
        assert sweeps._R11_PERCENTILE_WINDOW == 252
        # matches the module default -- the normalization window is not a
        # searched axis (only (signal, window, target) is).
        assert sweeps._R11_PERCENTILE_WINDOW == xasset_regime.PERCENTILE_WINDOW

    def test_configs_are_exactly_the_registered_product(self):
        configs = sweeps.r11_configs()
        expected = [{"signal": s, "window": w, "target": t}
                    for s in ["xasset_eq_bond_mom", "xasset_metals_riskoff",
                              "xasset_breadth"]
                    for w in [63, 126, 252]
                    for t in ["SPY", "QQQ", "NVDA"]]
        assert configs == expected
        assert len(configs) == 27

    def test_deterministic_order(self):
        assert sweeps.r11_configs() == sweeps.r11_configs()

    def test_round_total_configs_and_program_ledger(self):
        # Burden ledger: 3 signals x 3 windows x 3 targets = 27 new registered
        # configs; program cumulative 5913 -> 5940 (on the future RUN). Each
        # config names its own target, so targets do NOT multiply again.
        assert sweeps.r11_total_configs() == 27
        assert sweeps.R11_K == 27
        assert 5913 + sweeps.r11_total_configs() == 5940
