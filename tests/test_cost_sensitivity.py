"""R4-B cost-sensitivity re-grade tests (scripts/run_r4_cost_sensitivity.py).

What must hold: (a) the stressed tiers are exactly 2x/4x the committed
baseline and the engine actually RECEIVES those numbers; (b) on the same
trades, higher per-side costs can never increase the net Sharpe (the whole
premise of the slice); (c) the pre-registered per-tier kill rule (KILL iff
stitched OOS Sharpe <= same-cost B&H Sharpe or <= 0, ties KILL); (d) an
irreproducible lane is SKIPPED, never approximated.
"""

import importlib.util
import json
import math

import numpy as np
import pandas as pd
import pytest

from trading_lab import config, metrics
from trading_lab.engine import run_backtest


def _script():
    path = config.REPO_ROOT / "scripts" / "run_r4_cost_sensitivity.py"
    spec = importlib.util.spec_from_file_location("run_r4_cost_sensitivity",
                                                  path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _script()


def synthetic_ohlcv(n=400, seed=7):
    rng = np.random.default_rng(seed)
    close = 100.0 * np.cumprod(1.0 + rng.normal(0.0003, 0.01, n))
    idx = pd.bdate_range("2015-01-01", periods=n)
    return pd.DataFrame({
        "open": close * (1 + rng.normal(0, 0.001, n)),
        "high": close * 1.01, "low": close * 0.99,
        "close": close, "volume": np.full(n, 1e6),
    }, index=idx)


def oscillating_positions(index, period=5):
    """Deterministic long/flat square wave — plenty of turnover."""
    return pd.Series([(i // period) % 2 for i in range(len(index))],
                     index=index, dtype=float)


class TestCostTiers:
    def test_tiers_are_exact_multiples_of_committed_baseline(self):
        assert MOD.COST_TIERS["2x"] == {
            "slippage_bps": 2 * config.DEFAULT_SLIPPAGE_BPS,
            "commission_bps": 2 * config.DEFAULT_COMMISSION_BPS}
        assert MOD.COST_TIERS["4x"] == {
            "slippage_bps": 4 * config.DEFAULT_SLIPPAGE_BPS,
            "commission_bps": 4 * config.DEFAULT_COMMISSION_BPS}

    def test_tiers_match_preregistered_bps(self):
        # docs/research-round-4-plan.md § R4-B, verbatim numbers.
        assert MOD.COST_TIERS["2x"] == {"slippage_bps": 10.0,
                                        "commission_bps": 2.0}
        assert MOD.COST_TIERS["4x"] == {"slippage_bps": 20.0,
                                        "commission_bps": 4.0}


class TestEngineReceivesStressedCosts:
    @pytest.mark.parametrize("tier,slip,comm", [("2x", 10.0, 2.0),
                                                ("4x", 20.0, 4.0)])
    def test_replay_passes_tier_costs_to_engine(self, monkeypatch, tier,
                                                slip, comm):
        ohlcv = synthetic_ohlcv()
        frozen = [{"test": [0, 200], "params": {},
                   "positions": oscillating_positions(ohlcv.index[:200])},
                  {"test": [200, 400], "params": {},
                   "positions": oscillating_positions(ohlcv.index[200:400])}]
        seen = []
        real = MOD.run_backtest

        def spy(ohlcv_, pos, **kw):
            seen.append((kw["slippage_bps"], kw["commission_bps"]))
            return real(ohlcv_, pos, **kw)

        monkeypatch.setattr(MOD, "run_backtest", spy)
        out = MOD.replay_at_costs(ohlcv, frozen, "daily",
                                  **MOD.COST_TIERS[tier])
        assert seen == [(slip, comm)] * 2  # every split, exact stressed bps
        assert len(out["returns"]) == 400

    def test_engine_meta_records_stressed_costs(self):
        ohlcv = synthetic_ohlcv()
        pos = oscillating_positions(ohlcv.index)
        res = run_backtest(ohlcv, pos, **MOD.COST_TIERS["2x"],
                           timeframe="daily")
        assert res.meta["slippage_bps"] == 10.0
        assert res.meta["commission_bps"] == 2.0
        assert res.cost_bps_per_side == 12.0


class TestCostMonotonicity:
    def test_higher_costs_never_increase_sharpe_on_same_trades(self):
        ohlcv = synthetic_ohlcv()
        pos = oscillating_positions(ohlcv.index)
        sharpes = []
        for mult in (0, 1, 2, 4, 8):
            res = run_backtest(
                ohlcv, pos,
                slippage_bps=mult * config.DEFAULT_SLIPPAGE_BPS,
                commission_bps=mult * config.DEFAULT_COMMISSION_BPS,
                timeframe="daily")
            sharpes.append(metrics.sharpe(res.returns, "daily"))
        assert all(a >= b for a, b in zip(sharpes, sharpes[1:])), sharpes
        # with real turnover the drop must be strict, not accidental ties
        assert sharpes[0] > sharpes[-1]

    def test_replay_stitched_sharpe_monotone_across_tiers(self):
        ohlcv = synthetic_ohlcv(seed=11)
        frozen = [{"test": [0, 200], "params": {},
                   "positions": oscillating_positions(ohlcv.index[:200])},
                  {"test": [200, 400], "params": {},
                   "positions": oscillating_positions(ohlcv.index[200:400])}]
        base = MOD.replay_at_costs(ohlcv, frozen, "daily",
                                   **MOD.BASELINE_COSTS)
        two = MOD.replay_at_costs(ohlcv, frozen, "daily",
                                  **MOD.COST_TIERS["2x"])
        four = MOD.replay_at_costs(ohlcv, frozen, "daily",
                                   **MOD.COST_TIERS["4x"])
        s = [metrics.sharpe(r["returns"], "daily") for r in (base, two, four)]
        assert s[0] > s[1] > s[2], s

    def test_positions_identical_across_tiers(self):
        # frozen_positions never sees costs — the trades are the same trades
        ohlcv = synthetic_ohlcv(seed=3)
        per_split = [{"test": [100, 250],
                      "params": {"fast": 10, "slow": 50}}]
        from trading_lab.strategies import STRATEGIES
        a = MOD.frozen_positions(ohlcv, STRATEGIES["sma_crossover"],
                                 per_split)
        b = MOD.frozen_positions(ohlcv, STRATEGIES["sma_crossover"],
                                 per_split)
        pd.testing.assert_series_equal(a[0]["positions"], b[0]["positions"])
        assert a[0]["test"] == [100, 250]
        assert len(a[0]["positions"]) == 150


class TestGradeTier:
    def test_keep_requires_beating_bench_and_zero(self):
        assert MOD.grade_tier(0.5, 0.4) is True
        assert MOD.grade_tier(0.5, 0.5) is False   # tie -> KILL
        assert MOD.grade_tier(0.4, 0.5) is False
        assert MOD.grade_tier(0.0, -0.5) is False  # <= 0 -> KILL
        assert MOD.grade_tier(-0.1, -0.5) is False
        assert MOD.grade_tier(0.1, -0.5) is True

    def test_missing_or_nan_kills(self):
        assert MOD.grade_tier(None, 0.1) is False
        assert MOD.grade_tier(0.5, None) is False
        assert MOD.grade_tier(float("nan"), 0.1) is False
        assert MOD.grade_tier(0.5, float("nan")) is False


class TestLaneSkip:
    def test_unknown_strategy_skips_before_any_data_load(self):
        source = {"family": "no_such_family", "instrument": "AAPL",
                  "timeframe": "daily"}
        with pytest.raises(MOD.LaneSkip, match="no_such_family"):
            MOD.prepare_lane(source, "synthetic-lane.json")


class TestCommittedArtifactPin:
    """The committed 2x detail file for aroon_trend x AAPL reproduces from
    the committed r3 lane: frozen params, same windows, stressed costs."""

    def test_aroon_aapl_2x_reproduces(self):
        r3 = json.loads((config.REPO_ROOT / "experiments" / "sweeps"
                         / "r3-aroon-cci" / "aroon_trend__AAPL.json"
                         ).read_text())
        r4 = json.loads((config.REPO_ROOT / "experiments" / "sweeps"
                         / "r4-cost-sensitivity"
                         / "r3-aroon-cci__aroon_trend__AAPL__2x.json"
                         ).read_text())
        assert r4["costs"] == {"slippage_bps": 10.0, "commission_bps": 2.0}
        assert r4["cost_tier"] == "2x"
        from trading_lab.data import load_ohlcv
        from trading_lab.strategies import STRATEGIES
        ohlcv = load_ohlcv("AAPL", "daily")
        frozen = MOD.frozen_positions(ohlcv, STRATEGIES["aroon_trend"],
                                      r3["walk_forward"]["per_split"])
        got = MOD.replay_at_costs(ohlcv, frozen, "daily",
                                  slippage_bps=10.0, commission_bps=2.0)
        assert metrics.sharpe(got["returns"], "daily") == pytest.approx(
            r4["walk_forward"]["oos_metrics"]["sharpe"], abs=1e-9)
        # stressed-cost stitched OOS must sit below the committed baseline
        assert (r4["walk_forward"]["oos_metrics"]["sharpe"]
                < r3["walk_forward"]["oos_metrics"]["sharpe"])

    def test_rollup_counts_match_lane_rows(self):
        rollup = json.loads((config.REPO_ROOT / "experiments" / "sweeps"
                             / "r4-cost-sensitivity" / "summary.json"
                             ).read_text())
        graded = [r for r in rollup["lanes"] if r["status"] == "GRADED"]
        c = rollup["counts"]
        assert c["keep_universe"] == 58
        assert c["graded"] + c["skipped"] == len(rollup["lanes"]) == 58
        assert c["survive_2x"] == sum(
            1 for r in graded if r["tiers"]["2x"]["verdict"].startswith("KEEP"))
        assert c["survive_4x"] == sum(
            1 for r in graded if r["tiers"]["4x"]["verdict"].startswith("KEEP"))
        # the robustness gradient can only shrink: surviving 4x implies
        # nothing, but the counts must be ordered
        assert c["survive_4x"] <= c["survive_2x"] <= c["graded"]
        for r in graded:
            assert r["r4b_dev_candidate"] == (
                r["tiers"]["2x"]["verdict"].startswith("KEEP"))
