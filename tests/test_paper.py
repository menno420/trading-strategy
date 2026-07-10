"""Paper-lane grading-job tests (docs/paper-lane-protocol.md §5-§7, §9).

Offline: synthetic ledgers + a synthetic cache written with save_cache and
read back only through the paper-lane rail. No network, ever.
"""

import inspect
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import trading_lab.paper as paper_mod
from trading_lab import config
from trading_lab.data import save_cache
from trading_lab.paper import (LedgerFormatError, grade_ledger,
                               parse_records)

COST = (config.DEFAULT_SLIPPAGE_BPS + config.DEFAULT_COMMISSION_BPS) / 1e4

HEADER = "# Paper-lane ledger (test)\n\n## Records\n\n"

WATCH_RECORD = (
    "### paper-0001 — WATCH (lane opening)\n"
    "- id: paper-0001\n"
    "- committed_at_utc: 2026-07-10T21:44:51Z\n"
    "- strategy_id: donchian_AAPL_daily_e15x5\n"
    "- instrument: AAPL, daily bars\n"
    "- status: **WATCH** — strategy flat, warm-up pending,\n"
    "  first evaluable entry signal after 15 lane bars.\n\n"
)


def _d(ts) -> str:
    return str(pd.Timestamp(ts).date())


def _on_time(fill_date) -> str:
    """A commit timestamp comfortably before the fill bar's open."""
    return f"{_d(pd.Timestamp(fill_date) - pd.Timedelta(days=1))}T21:00:00Z"


def trade_record(rid, action, fill_date, committed, status="OPEN") -> str:
    signal = pd.Timestamp(fill_date) - pd.Timedelta(days=1)
    return (
        f"### {rid} — {action}\n"
        f"- id: {rid}\n"
        f"- committed_at_utc: {committed}\n"
        "- strategy_id: donchian_AAPL_daily_e15x5\n"
        "- instrument: AAPL, daily bars\n"
        f"- action: {action}\n"
        f"- signal_date: {_d(signal)}\n"
        f"- intended_fill_bar: {_d(fill_date)}\n"
        f"- status: {status}\n\n"
    )


@pytest.fixture
def cache(tmp_path):
    """Synthetic cache spanning poison pre-lane bars + lane bars.

    Pre-lane bars (< PAPER_LANE_START) are priced 500.0 as poison: if the
    grader ever consumed one, every graded number would be visibly wrong.
    Lane bars are 100.0 except lane[3] and lane[15] at 90.0.
    Returns (data_dir, lane_dates).
    """
    idx = pd.bdate_range("2026-06-01", periods=60)
    lane_mask = idx >= pd.Timestamp(config.PAPER_LANE_START)
    lane = idx[lane_mask]
    assert len(lane) >= 21 and lane_mask.sum() < len(idx)
    opens = pd.Series(np.where(lane_mask, 100.0, 500.0), index=idx)
    opens[lane[3]] = 90.0   # entry-1 fill (dip)
    opens[lane[15]] = 90.0  # exit-2 fill
    df = pd.DataFrame({"open": opens, "high": opens, "low": opens,
                       "close": opens, "volume": 1_000_000.0})
    df.index.name = "timestamp"
    save_cache(df, "AAPL", "daily", data_dir=tmp_path)
    return tmp_path, lane


def write_ledger(tmp_path, body: str) -> Path:
    path = tmp_path / "ledger.md"
    path.write_text(HEADER + body)
    return path


class TestGrading:
    def _two_window_ledger(self, tmp_path, lane) -> Path:
        body = (
            WATCH_RECORD
            + trade_record("paper-0002", "ENTRY", lane[3], _on_time(lane[3]))
            + trade_record("paper-0003", "EXIT", lane[10], _on_time(lane[10]))
            + trade_record("paper-0004", "ENTRY", lane[12], _on_time(lane[12]))
            + trade_record("paper-0005", "EXIT", lane[15], _on_time(lane[15]))
        )
        return write_ledger(tmp_path, body)

    def test_grades_closed_windows_beat_then_tie_miss(self, cache, tmp_path):
        data_dir, lane = cache
        path = self._two_window_ledger(tmp_path, lane)
        report = grade_ledger(path, data_dir=data_dir,
                              now="2026-08-20T00:00:00Z")
        assert [g.verdict for g in report.graded] == ["BEAT", "MISS"]
        assert report.changed and not report.already_graded

        g1, g2 = report.graded
        # window 1: buy the dip at 90, exit at 100 — beats holding
        assert g1.entry_fill_open == 90.0 and g1.exit_fill_open == 100.0
        assert g1.cycle_start_date == _d(lane[0])   # first LANE bar,
        assert g1.cycle_start_open == 100.0          # never a poison 500 bar
        trade1 = (100.0 * (1 - COST)) / (90.0 * (1 + COST)) - 1
        bh1 = (100.0 * (1 - COST)) / (100.0 * (1 + COST)) - 1
        assert g1.strategy_cycle_return_net == pytest.approx(trade1)
        assert g1.bh_cycle_return_net == pytest.approx(bh1)
        assert g1.strategy_cycle_return_net > g1.bh_cycle_return_net
        assert g1.shares == pytest.approx(10_000.0 / 90.0)
        assert not g1.late_commit

        # window 2: cycle starts at window 1's exit fill (§7); entry open
        # equals cycle-start open, so strategy and B&H tie EXACTLY -> MISS
        # (§9 A5: ties resolve against the strategy).
        assert g2.cycle_start_date == _d(lane[10])
        assert g2.strategy_cycle_return_net == g2.bh_cycle_return_net
        assert g2.verdict == "MISS" and not g2.late_commit

        text = path.read_text()
        assert text.count("- verdict: BEAT") == 1
        assert text.count("- verdict: MISS") == 1
        assert text.count("- status: GRADED") == 2
        assert "- pre_grade_status: OPEN" in text
        # WATCH record byte-for-byte untouched
        assert WATCH_RECORD in text
        assert "500" not in text  # no poison pre-lane price leaked anywhere

    def test_idempotent_rerun_never_double_grades(self, cache, tmp_path):
        data_dir, lane = cache
        path = self._two_window_ledger(tmp_path, lane)
        grade_ledger(path, data_dir=data_dir, now="2026-08-20T00:00:00Z")
        before = path.read_bytes()
        # different `now`: an already-graded row must not even re-stamp
        report = grade_ledger(path, data_dir=data_dir,
                              now="2026-09-01T00:00:00Z")
        assert not report.changed and report.graded == []
        assert report.already_graded == ["paper-0003", "paper-0005"]
        assert path.read_bytes() == before

    def test_late_commit_is_miss_regardless_of_pnl(self, cache, tmp_path):
        data_dir, lane = cache
        # same winning window as above, but the ENTRY commit lands exactly
        # AT the fill bar's open bound (not strictly before) -> late -> MISS
        late = f"{_d(lane[3])}T13:30:00Z"
        body = (WATCH_RECORD
                + trade_record("paper-0002", "ENTRY", lane[3], late)
                + trade_record("paper-0003", "EXIT", lane[10],
                               _on_time(lane[10])))
        path = write_ledger(tmp_path, body)
        report = grade_ledger(path, data_dir=data_dir)
        (g,) = report.graded
        assert g.late_commit and g.verdict == "MISS"
        assert g.strategy_cycle_return_net > g.bh_cycle_return_net  # won on P&L
        assert "- late_commit: true — graded MISS regardless of P&L" \
            in path.read_text()

    def test_missing_commit_timestamp_is_miss(self, cache, tmp_path):
        data_dir, lane = cache
        body = (trade_record("paper-0002", "ENTRY", lane[3], "")
                + trade_record("paper-0003", "EXIT", lane[10],
                               _on_time(lane[10])))
        path = write_ledger(tmp_path, body)
        report = grade_ledger(path, data_dir=data_dir)
        assert report.graded[0].late_commit
        assert report.graded[0].verdict == "MISS"


class TestNotGradeable:
    def test_watch_only_ledger_untouched_no_data_needed(self, tmp_path):
        """Today's honest state: WATCH only — no cache exists, no data is
        loaded, nothing mutates, and the pass reports FLAT."""
        path = write_ledger(tmp_path, WATCH_RECORD)
        before = path.read_bytes()
        report = grade_ledger(path, data_dir=tmp_path / "no-cache-here")
        assert report.watch == ["paper-0001"]
        assert report.flat_review and not report.changed
        assert report.graded == [] and report.pending_fill == []
        assert path.read_bytes() == before

    def test_repo_ledger_parses_and_is_left_alone(self, tmp_path):
        """The real committed ledger (paper-0001 WATCH) round-trips."""
        real = config.EXPERIMENTS_DIR / "paper" / "ledger.md"
        copy = tmp_path / "ledger.md"
        shutil.copy(real, copy)
        records = parse_records(copy.read_text().split("\n"))
        assert [r.id for r in records] == ["paper-0001"]
        assert records[0].status_token == "WATCH"
        report = grade_ledger(copy, data_dir=tmp_path / "no-cache-here")
        assert report.watch == ["paper-0001"] and not report.changed
        assert copy.read_bytes() == real.read_bytes()

    def test_open_entry_reported_not_graded(self, cache, tmp_path):
        data_dir, lane = cache
        rec = trade_record("paper-0002", "ENTRY", lane[3], _on_time(lane[3]))
        path = write_ledger(tmp_path, WATCH_RECORD + rec)
        before = path.read_bytes()
        report = grade_ledger(path, data_dir=data_dir)
        assert report.open_entries == ["paper-0002"]
        assert report.graded == [] and not report.changed
        assert not report.flat_review  # a position is open
        assert path.read_bytes() == before

    def test_exit_not_filled_yet_is_pending(self, cache, tmp_path):
        data_dir, lane = cache
        beyond = lane[-1] + pd.Timedelta(days=30)
        body = (trade_record("paper-0002", "ENTRY", lane[3], _on_time(lane[3]))
                + trade_record("paper-0003", "EXIT", beyond, _on_time(beyond)))
        path = write_ledger(tmp_path, body)
        before = path.read_bytes()
        report = grade_ledger(path, data_dir=data_dir)
        assert report.pending_fill == ["paper-0003"]
        assert report.graded == [] and not report.changed
        assert not report.flat_review  # still open until the exit prints
        assert path.read_bytes() == before

    def test_malformed_alternation_refuses_to_grade(self, cache, tmp_path):
        data_dir, lane = cache
        body = trade_record("paper-0002", "EXIT", lane[10], _on_time(lane[10]))
        path = write_ledger(tmp_path, body)
        before = path.read_bytes()
        with pytest.raises(LedgerFormatError, match="grading nothing"):
            grade_ledger(path, data_dir=data_dir)
        assert path.read_bytes() == before


class TestHoldoutDiscipline:
    def test_grader_source_never_touches_holdout(self):
        """The grader must have zero holdout surface: no unlock token of
        any kind, and no call path to the standard loader — only the
        paper-lane rail (protocol §3, §9 A2)."""
        src = inspect.getsource(paper_mod)
        assert "unlock" not in src.lower()
        assert "load_ohlcv" not in src.replace("load_paper_ohlcv", "")

    def test_grade_script_source_never_touches_holdout(self):
        script = (config.REPO_ROOT / "scripts" / "grade_paper.py").read_text()
        assert "unlock" not in script.lower()
        assert "load_ohlcv" not in script.replace("load_paper_ohlcv", "")
