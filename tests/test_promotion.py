"""Promotion-significance-bar tests (ORDER 007) with hand-computed values.

The rule under test: promotion to FINDING requires beating buy-and-hold net
of costs AND clearing a minimum t-stat on the Sharpe delta (Lo 2002 SE,
Bonferroni-adjusted for variants tried). Below the bar = RULE-PASS
(candidate), never PROMOTED-TO-FINDING.
"""

import math

import pytest

from trading_lab import promotion

# The ledgered P2 numbers for donchian x AAPL (entry=15, exit=5), verbatim
# from experiments/runs/20260710T033624806389Z-1943c6697c7c.json.
AAPL_STRAT_SHARPE = 0.618958789483348
AAPL_BH_SHARPE = 0.5401802040286563
AAPL_N_BARS = 7331


class TestSharpeSE:
    def test_matches_lo_2002_hand_computation(self):
        # SR_annual=0.6, daily: SR_per = 0.6/sqrt(252);
        # SE = sqrt((1 + SR_per^2/2)/N) * sqrt(252)
        sr, n = 0.6, 2520
        sr_per = sr / math.sqrt(252.0)
        expected = math.sqrt((1 + sr_per ** 2 / 2) / n) * math.sqrt(252.0)
        assert promotion.sharpe_se(sr, n, "daily") == pytest.approx(expected)

    def test_shrinks_with_sample_size(self):
        assert promotion.sharpe_se(0.6, 10000, "daily") < \
            promotion.sharpe_se(0.6, 1000, "daily")

    def test_rejects_nonpositive_n(self):
        with pytest.raises(ValueError):
            promotion.sharpe_se(0.6, 0, "daily")

    def test_unknown_timeframe_raises(self):
        with pytest.raises(ValueError):
            promotion.sharpe_se(0.6, 100, "weekly")


class TestMinTstat:
    def test_single_variant_is_one_sided_5pct(self):
        # Phi^-1(0.95) = 1.6449
        assert promotion.min_tstat(1) == pytest.approx(1.6449, abs=1e-4)

    def test_threshold_rises_with_variants_tried(self):
        t1 = promotion.min_tstat(1)
        t41 = promotion.min_tstat(41)
        t177 = promotion.min_tstat(177)
        assert t1 < t41 < t177
        # Bonferroni at K=177: Phi^-1(1 - 0.05/177) = 3.4479
        assert t177 == pytest.approx(3.4479, abs=1e-4)

    def test_nonpositive_variants_treated_as_one(self):
        assert promotion.min_tstat(0) == promotion.min_tstat(1)


class TestGradePromotion:
    def test_killed_when_delta_nonpositive(self):
        grade = promotion.grade_promotion(
            strategy_sharpe=0.5, benchmark_sharpe=0.6,
            n_periods=2520, timeframe="daily")
        assert grade["verdict"] == promotion.VERDICT_KILLED

    def test_rule_pass_when_positive_but_insignificant(self):
        # +0.05 Sharpe over ~4 years of daily bars: t << 1.645.
        grade = promotion.grade_promotion(
            strategy_sharpe=0.65, benchmark_sharpe=0.60,
            n_periods=1008, timeframe="daily")
        assert grade["verdict"] == promotion.VERDICT_RULE_PASS
        assert 0 < grade["tstat"] < grade["min_tstat"]

    def test_promoted_when_edge_clears_the_bar(self):
        # +1.0 Sharpe over 7331 daily bars: t ~ 5.2 > 1.645.
        grade = promotion.grade_promotion(
            strategy_sharpe=1.54, benchmark_sharpe=0.54,
            n_periods=7331, timeframe="daily")
        assert grade["verdict"] == promotion.VERDICT_PROMOTED
        assert grade["tstat"] >= grade["min_tstat"]

    def test_variants_tried_can_demote_a_marginal_winner(self):
        kwargs = dict(strategy_sharpe=1.0, benchmark_sharpe=0.6,
                      n_periods=7331, timeframe="daily")
        assert promotion.grade_promotion(
            **kwargs, variants_tried=1)["verdict"] == \
            promotion.VERDICT_PROMOTED  # t ~ 2.1 > 1.645
        assert promotion.grade_promotion(
            **kwargs, variants_tried=177)["verdict"] == \
            promotion.VERDICT_RULE_PASS  # bar rises to 3.4479

    def test_rejects_nan_sharpe(self):
        with pytest.raises(ValueError):
            promotion.grade_promotion(
                strategy_sharpe=float("nan"), benchmark_sharpe=0.5,
                n_periods=100, timeframe="daily")


class TestAAPLDonchianRegrade:
    """The ORDER 007 re-grade, pinned: this is the ledgered computation."""

    def test_regrade_arithmetic_and_verdict(self):
        grade = promotion.grade_promotion(
            strategy_sharpe=AAPL_STRAT_SHARPE,
            benchmark_sharpe=AAPL_BH_SHARPE,
            n_periods=AAPL_N_BARS, timeframe="daily", variants_tried=1)
        # Edge +0.0788, SE 0.1855, t = 0.425 -- deep inside noise.
        assert grade["sharpe_delta"] == pytest.approx(0.0788, abs=1e-4)
        assert grade["sharpe_se"] == pytest.approx(0.1855, abs=1e-4)
        assert grade["tstat"] == pytest.approx(0.4247, abs=1e-4)
        assert grade["min_tstat"] == pytest.approx(1.6449, abs=1e-4)
        # Beats B&H but is NOT significant even at the most lenient
        # denominator (K=1): candidate, not a finding.
        assert grade["verdict"] == promotion.VERDICT_RULE_PASS

    def test_demotion_is_robust_to_any_larger_denominator(self):
        # The P1 lane behind the candidate tried 41 donchian variants inside
        # a 177-config lane; any K >= 1 only raises the bar.
        for k in (1, 41, 177):
            grade = promotion.grade_promotion(
                strategy_sharpe=AAPL_STRAT_SHARPE,
                benchmark_sharpe=AAPL_BH_SHARPE,
                n_periods=AAPL_N_BARS, timeframe="daily", variants_tried=k)
            assert grade["verdict"] == promotion.VERDICT_RULE_PASS
