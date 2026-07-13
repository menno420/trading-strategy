"""R4-C survivor-committee tests: committee position math (mean of member
positions, disagreement -> fractional), group enumeration (>= 2 rule, no
cross-timeframe mixing, family dedup), the engine's fractional-position
support the committee relies on, and the pinned committee roster from the
committed KEEP surface."""

import json
from pathlib import Path

import pandas as pd
import pytest

from conftest import make_ohlcv
from trading_lab import sweeps
from trading_lab.engine import run_backtest
from trading_lab.ensemble import committee_positions, enumerate_committees

REPO_ROOT = Path(__file__).resolve().parents[1]
KEEP_UNIVERSE = REPO_ROOT / sweeps.R4_ENSEMBLE_KEEP_UNIVERSE


def _series(values, start="2024-01-01"):
    idx = pd.bdate_range(start, periods=len(values))
    return pd.Series([float(v) for v in values], index=idx)


def _lane(instrument, timeframe, strategy, sweep="r3-x"):
    return {"instrument": instrument, "timeframe": timeframe,
            "strategy": strategy, "sweep": sweep,
            "source_file": f"experiments/sweeps/{sweep}/"
                           f"{strategy}__{instrument}.json"}


class TestCommitteePositions:
    def test_mean_of_members(self):
        a = _series([1, 1, 0, 0, 1])
        b = _series([1, 0, 0, 1, 1])
        out = committee_positions([a, b])
        assert list(out) == [1.0, 0.5, 0.0, 0.5, 1.0]
        assert out.index.equals(a.index)

    def test_disagreement_yields_fractional(self):
        # Three members, one long: the committee is 1/3 long — the
        # fractional case the engine must support.
        members = [_series([1, 0, 0]), _series([0, 0, 0]), _series([0, 0, 1])]
        out = committee_positions(members)
        assert out.iloc[0] == pytest.approx(1 / 3)
        assert out.iloc[1] == 0.0
        assert out.iloc[2] == pytest.approx(1 / 3)

    def test_short_members_average_too(self):
        out = committee_positions([_series([-1, 1]), _series([1, 1])])
        assert list(out) == [0.0, 1.0]

    def test_result_stays_in_engine_range(self):
        out = committee_positions([_series([1, -1, 1]), _series([1, -1, 0]),
                                   _series([1, -1, -1])])
        assert (out.abs() <= 1).all()

    def test_unanimous_committee_equals_member(self):
        a = _series([0, 1, 1, 0])
        out = committee_positions([a, a.copy(), a.copy()])
        pd.testing.assert_series_equal(out, a.astype(float))

    def test_rejects_single_member(self):
        with pytest.raises(ValueError, match=">= 2 members"):
            committee_positions([_series([1, 0])])

    def test_rejects_misaligned_indices(self):
        a = _series([1, 0, 1])
        b = _series([1, 0, 1], start="2024-02-01")
        with pytest.raises(ValueError, match="misaligned"):
            committee_positions([a, b])

    def test_rejects_nan_and_out_of_range(self):
        a = _series([1, 0, 1])
        bad_nan = a.copy()
        bad_nan.iloc[1] = float("nan")
        with pytest.raises(ValueError, match="NaN"):
            committee_positions([a, bad_nan])
        with pytest.raises(ValueError, match=r"outside \[-1, 1\]"):
            committee_positions([a, a * 2])


class TestEngineFractionalPositions:
    """The committee relies on the engine's documented fractional support:
    positions in [-1, 1], costs charged on |change in held position|."""

    def test_half_position_pnl_and_costs(self):
        # Zero-cost check first: half position earns half the bar return.
        ohlcv = make_ohlcv([100.0, 110.0, 110.0])
        pos = pd.Series([0.5, 0.5, 0.0], index=ohlcv.index)
        res0 = run_backtest(ohlcv, pos, slippage_bps=0, commission_bps=0)
        # held = [0, 0.5, 0.5]; bar returns: open 100->110 (bar 1: 0%),
        # bar 2 closes at its close (0%). Bar 1: open 110/100 applies to
        # held[0]=0; bar 1 held 0.5 on 110->110 = 0.
        assert res0.returns.iloc[1] == pytest.approx(0.5 * (110 / 110 - 1))
        # With costs: entering 0.5 pays 0.5 * cost_per_side.
        res = run_backtest(ohlcv, pos, slippage_bps=5, commission_bps=1)
        cost_per_side = 6 / 1e4
        assert res.returns.iloc[1] == pytest.approx(-0.5 * cost_per_side)

    def test_fractional_rebalance_costs_only_the_delta(self):
        ohlcv = make_ohlcv([100.0] * 5)
        pos = pd.Series([0.5, 1.0, 1.0, 0.25, 0.25], index=ohlcv.index)
        res = run_backtest(ohlcv, pos, slippage_bps=5, commission_bps=1)
        cost = 6 / 1e4
        # held: [0, .5, 1, 1, .25]; |turnover|: [0, .5, .5, 0, .75]
        expected = [0.0, -0.5 * cost, -0.5 * cost, 0.0, -0.75 * cost]
        assert list(res.returns) == pytest.approx(expected)

    def test_committee_of_frozen_members_runs_end_to_end(self):
        ohlcv = make_ohlcv([100, 101, 103, 102, 104, 105, 103, 106])
        a = pd.Series([1, 1, 0, 0, 1, 1, 0, 0], index=ohlcv.index,
                      dtype=float)
        b = pd.Series([0, 1, 1, 0, 0, 1, 1, 0], index=ohlcv.index,
                      dtype=float)
        pos = committee_positions([a, b])
        res = run_backtest(ohlcv, pos)
        assert len(res.returns) == len(ohlcv)
        assert not res.returns.isna().any()


class TestEnumerateCommittees:
    def test_min_members_rule(self):
        lanes = [_lane("AAA", "daily", "s1"), _lane("AAA", "daily", "s2"),
                 _lane("BBB", "daily", "s1")]  # BBB is a single survivor
        out = enumerate_committees(lanes, min_members=2)
        assert [c["instrument"] for c in out] == ["AAA"]
        assert len(out[0]["members"]) == 2

    def test_no_cross_timeframe_mixing(self):
        # Same instrument, two timeframes with one KEEP each: NO committee
        # may form — daily and hourly members never mix.
        lanes = [_lane("AAA", "daily", "s1"), _lane("AAA", "hourly", "s2")]
        assert enumerate_committees(lanes, min_members=2) == []
        # ... and with 2 per timeframe, two SEPARATE committees form.
        lanes += [_lane("AAA", "daily", "s3"), _lane("AAA", "hourly", "s4")]
        out = enumerate_committees(lanes, min_members=2)
        assert [(c["instrument"], c["timeframe"]) for c in out] == \
            [("AAA", "daily"), ("AAA", "hourly")]

    def test_family_dedup_is_deterministic_and_performance_blind(self):
        # Duplicate family from two sweeps: the lexicographically-first
        # (sweep, source_file) wins; the loser is reported, not dropped.
        lanes = [_lane("AAA", "daily", "dup", sweep="r3-zz-later"),
                 _lane("AAA", "daily", "dup", sweep="r3-aa-earlier"),
                 _lane("AAA", "daily", "other")]
        out = enumerate_committees(lanes, min_members=2)
        assert len(out) == 1
        members = out[0]["members"]
        assert len(members) == 2
        dup = next(m for m in members if m["strategy"] == "dup")
        assert dup["sweep"] == "r3-aa-earlier"
        assert [m["sweep"] for m in out[0]["deduped_out"]] == ["r3-zz-later"]
        assert len(out[0]["group_lanes"]) == 3

    def test_dedup_can_drop_group_below_min(self):
        # Two lanes of the SAME family are one family: no committee.
        lanes = [_lane("AAA", "daily", "dup", sweep="r3-a"),
                 _lane("AAA", "daily", "dup", sweep="r3-b")]
        assert enumerate_committees(lanes, min_members=2) == []

    def test_deterministic_ordering(self):
        lanes = [_lane("ZZZ", "daily", "s1"), _lane("ZZZ", "daily", "s2"),
                 _lane("AAA", "hourly", "s1"), _lane("AAA", "hourly", "s2")]
        out1 = enumerate_committees(list(lanes), min_members=2)
        out2 = enumerate_committees(list(reversed(lanes)), min_members=2)
        assert out1 == out2
        assert [(c["instrument"], c["timeframe"]) for c in out1] == \
            [("AAA", "hourly"), ("ZZZ", "daily")]


@pytest.fixture(scope="module")
def committees():
    report = json.loads(KEEP_UNIVERSE.read_text())
    keeps = [r for r in report["lanes"] if r["new_verdict"] == "KEEP"]
    assert len(keeps) == sweeps.R4_ENSEMBLE_EXPECTED_KEEPS == 58
    return enumerate_committees(
        keeps, min_members=sweeps.R4_ENSEMBLE_MIN_MEMBERS)


class TestCommittedRosterPinned:
    """The committee roster is fully determined, BEFORE the sweep runs, by
    the committed KEEP surface (R4-A, PR #100) plus the registered rules —
    pinned here so the run cannot silently drift."""

    def test_twelve_committees_with_expected_member_counts(self, committees):
        got = {(c["instrument"], c["timeframe"]): len(c["members"])
               for c in committees}
        assert got == {
            ("AAPL", "daily"): 3, ("AAPL", "hourly"): 2,
            ("AMZN", "hourly"): 3, ("BTC-USD", "daily"): 5,
            ("GOOGL", "hourly"): 3, ("JPM", "daily"): 2,
            ("META", "daily"): 6, ("META", "hourly"): 6,
            ("MSFT", "hourly"): 3, ("SLV", "daily"): 3,
            ("TLT", "daily"): 9, ("XOM", "daily"): 6,
        }

    def test_only_duplicates_are_the_two_donchian_lanes(self, committees):
        deduped = [(c["instrument"], m["strategy"], m["sweep"])
                   for c in committees for m in c["deduped_out"]]
        assert sorted(deduped) == [
            ("TLT", "donchian", "r3-trend-new-tickers"),
            ("XOM", "donchian", "r3-trend-new-tickers"),
        ]

    def test_single_survivor_lanes_excluded(self, committees):
        # 58 KEEPs = 51 members + 2 deduped-out + 5 single-survivor lanes
        # (GLD daily, GLD hourly, QQQ daily, SLV hourly, TSLA daily).
        n_members = sum(len(c["members"]) for c in committees)
        n_deduped = sum(len(c["deduped_out"]) for c in committees)
        assert n_members == 51 and n_deduped == 2
        grouped = {(c["instrument"], c["timeframe"]) for c in committees}
        assert ("GLD", "daily") not in grouped
        assert ("GLD", "hourly") not in grouped
        assert ("QQQ", "daily") not in grouped
        assert ("SLV", "hourly") not in grouped
        assert ("TSLA", "daily") not in grouped

    def test_no_family_repeats_inside_a_committee(self, committees):
        for c in committees:
            fams = [m["strategy"] for m in c["members"]]
            assert len(fams) == len(set(fams))
