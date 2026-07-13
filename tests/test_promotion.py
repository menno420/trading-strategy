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


class TestClassifyVerdict:
    """R4-A three-way sweep verdict (docs/research-round-4-plan.md § R4-A).

    Pre-registered rule: KILL-SIG iff the lane is not a KEEP and
    tstat <= -min_tstat at the lane's own recorded K -- the same
    Bonferroni bar, mirrored. Total: missing/NaN inputs degrade to KILL.
    """

    BAR_K12 = 2.638257273476751  # min_tstat(12), pinned

    def test_bar_constant_matches_min_tstat_k12(self):
        assert promotion.min_tstat(12) == pytest.approx(self.BAR_K12)

    def test_significantly_negative_is_kill_sig(self):
        assert promotion.classify_verdict(False, -3.01, self.BAR_K12) == \
            promotion.SWEEP_KILL_SIG

    def test_boundary_exactly_minus_bar_is_kill_sig(self):
        # The rule is <=, so t exactly at -bar crosses it.
        assert promotion.classify_verdict(
            False, -self.BAR_K12, self.BAR_K12) == promotion.SWEEP_KILL_SIG

    def test_just_inside_the_bar_stays_plain_kill(self):
        # SPY donchian's t = -2.417 misses the -2.638 bar: plain KILL.
        assert promotion.classify_verdict(False, -2.417, self.BAR_K12) == \
            promotion.SWEEP_KILL

    def test_keep_lane_with_negative_tstat_stays_keep(self):
        # KILL-SIG only ever applies to non-KEEP lanes.
        assert promotion.classify_verdict(True, -5.0, self.BAR_K12) == \
            promotion.SWEEP_KEEP

    def test_none_tstat_degrades_to_kill(self):
        assert promotion.classify_verdict(False, None, self.BAR_K12) == \
            promotion.SWEEP_KILL

    def test_none_bar_degrades_to_kill(self):
        assert promotion.classify_verdict(False, -9.9, None) == \
            promotion.SWEEP_KILL

    def test_nan_tstat_degrades_to_kill(self):
        assert promotion.classify_verdict(
            False, float("nan"), self.BAR_K12) == promotion.SWEEP_KILL

    def test_non_numeric_tstat_degrades_to_kill(self):
        assert promotion.classify_verdict(False, "oops", self.BAR_K12) == \
            promotion.SWEEP_KILL

    def test_noise_level_negative_is_kill(self):
        assert promotion.classify_verdict(False, -0.4, self.BAR_K12) == \
            promotion.SWEEP_KILL

    def test_positive_below_bar_non_keep_is_kill(self):
        assert promotion.classify_verdict(False, 1.04, self.BAR_K12) == \
            promotion.SWEEP_KILL

    def test_larger_k_raises_the_mirrored_bar_too(self):
        # t = -2.9 is KILL-SIG at K=12 (bar 2.638) but plain KILL at
        # K=75 (bar 3.21) -- the correction never weakens.
        bar75 = promotion.min_tstat(75)
        assert promotion.classify_verdict(False, -2.9, self.BAR_K12) == \
            promotion.SWEEP_KILL_SIG
        assert promotion.classify_verdict(False, -2.9, bar75) == \
            promotion.SWEEP_KILL


class TestR4KillsigRegradeScript:
    """Row-builder of scripts/run_r4_killsig_regrade.py on synthetic dicts."""

    @staticmethod
    def _script():
        import importlib.util
        from trading_lab import config
        path = config.REPO_ROOT / "scripts" / "run_r4_killsig_regrade.py"
        spec = importlib.util.spec_from_file_location(
            "run_r4_killsig_regrade", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def _lane(self, verdict="KILL", tstat=-1.0, min_tstat=2.638257273476751):
        return {
            "sweep": "r3-test", "instrument": "TEST", "family": "fam",
            "timeframe": "daily", "verdict": verdict,
            "promotion_grade": {"tstat": tstat, "min_tstat": min_tstat},
        }

    def test_kill_sig_row(self):
        mod = self._script()
        row = mod.regrade_lane(self._lane(tstat=-3.01))
        assert row["new_verdict"] == promotion.SWEEP_KILL_SIG
        assert row["original_verdict"] == "KILL"
        assert row["strategy"] == "fam"
        assert row["tstat"] == -3.01

    def test_keep_dev_verdict_string_maps_to_keep(self):
        mod = self._script()
        row = mod.regrade_lane(
            self._lane(verdict="KEEP (dev-candidate only)", tstat=-3.01))
        assert row["new_verdict"] == promotion.SWEEP_KEEP

    def test_missing_tstat_is_ungradeable_not_recomputed(self):
        mod = self._script()
        lane = self._lane()
        del lane["promotion_grade"]
        lane["verdict"] = None  # the XSEC bookkeeping-only shape
        row = mod.regrade_lane(lane)
        assert row["new_verdict"] == mod.UNGRADEABLE
        assert row["tstat"] is None

    def test_verdict_present_but_no_tstat_is_ungradeable(self):
        mod = self._script()
        lane = self._lane()
        lane["promotion_grade"] = {"min_tstat": 2.64}
        row = mod.regrade_lane(lane)
        assert row["new_verdict"] == mod.UNGRADEABLE

    def test_noise_kill_stays_kill(self):
        mod = self._script()
        row = mod.regrade_lane(self._lane(tstat=-0.4))
        assert row["new_verdict"] == promotion.SWEEP_KILL

    def test_committed_tsla_rsi_lane_regrades_kill_sig(self):
        # Integration pin against the byte-committed r3 summary that
        # motivated R4-A (PR #91 card: stitched OOS t = -3.01).
        import json
        from trading_lab import config
        mod = self._script()
        path = (config.EXPERIMENTS_DIR / "sweeps" / "r3-meanrev-new-tickers"
                / "rsi_mean_reversion__TSLA.json")
        row = mod.regrade_lane(json.loads(path.read_text()))
        assert row["new_verdict"] == promotion.SWEEP_KILL_SIG
        assert row["tstat"] == pytest.approx(-3.0110, abs=1e-4)
