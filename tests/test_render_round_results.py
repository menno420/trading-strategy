"""Tests for scripts/render_round_results.py — the results-doc table generator.

What must hold: run the generator's ``render`` on the COMMITTED ``r8-hourly``
slice and assert it REPRODUCES THE KEY NUMBERS that were hand-transcribed into
``docs/research-round-8-results.md`` — the lane count, the verdict counts, the
gate PASS/FAIL split, the reason_class rollup (including the single
``UNGRADEABLE_NAN`` infra-alarm lane), and the burden tally — plus that it
always emits the mandatory UNGRADEABLE-share infrastructure-alarm line
(standing rule 3). This is a "reproduces the numbers + emits the alarm" test,
NOT a brittle byte-for-byte golden, so honest results-doc prose edits do not
break it. Portfolio-shaped slices must be detected and rejected, not crashed.
"""

import importlib.util

from trading_lab import config


def _script():
    path = config.REPO_ROOT / "scripts" / "render_round_results.py"
    spec = importlib.util.spec_from_file_location("render_round_results", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


MOD = _script()


def _render_r8():
    summary, lane_files = MOD.load_slice("r8-hourly")
    return MOD.render(summary, lane_files), summary, lane_files


# --------------------------------------------------------------------------- #
# Loading / shape
# --------------------------------------------------------------------------- #
def test_r8_is_single_name_slice():
    summary, lane_files = MOD.load_slice("r8-hourly")
    assert not MOD.is_portfolio_slice(lane_files)
    # 16 lanes both in summary and as per-lane JSONs.
    assert len(summary["lanes"]) == 16
    assert len(lane_files) == 16


def test_portfolio_slice_is_rejected_not_crashed():
    # r7d-xsec-drawdown is portfolio-shaped (no per-lane selection_gate block).
    import pytest

    with pytest.raises(MOD.PortfolioSliceError):
        MOD.load_slice("r7d-xsec-drawdown")
    # And the CLI exits non-zero with a clear message (documented limitation).
    assert MOD.main(["r7d-xsec-drawdown"]) == 2


# --------------------------------------------------------------------------- #
# Key numbers reproduced from docs/research-round-8-results.md
# --------------------------------------------------------------------------- #
def test_slice_summary_row_numbers():
    block = MOD.build_slice_summary(_render_r8()[1])
    # Header + exactly one data row.
    row = [ln for ln in block.splitlines() if ln.startswith("| R8")][0]
    cells = [c.strip() for c in row.strip("|").split("|")]
    # label | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Runtime vs cap
    assert cells[1] == "16"
    assert cells[2] == "3"   # KEEP
    assert cells[3] == "13"  # KILL
    assert cells[4] == "0"   # KILL-SIG
    assert cells[5] == "8 / 8"
    assert cells[6] == "4.8 s / 900 s"


def test_verdict_and_gate_counts():
    _, summary, _ = _render_r8()
    counts = MOD._counts(summary["lanes"])
    assert counts["lanes"] == 16
    assert counts["KEEP"] == 3
    assert counts["KILL"] == 13
    assert counts["KILL-SIG"] == 0
    assert counts["PASS"] == 8   # gate PASS
    assert counts["FAIL"] == 8   # gate FAIL
    assert summary["keeps_demoted_by_gate"] == 0


def test_per_family_counts():
    _, summary, _ = _render_r8()
    by_fam = {}
    for lane in summary["lanes"]:
        by_fam.setdefault(lane["family"], []).append(lane)
    dd = MOD._counts(by_fam["drawdown_reversion"])
    hp = MOD._counts(by_fam["high_proximity"])
    assert (dd["lanes"], dd["KEEP"], dd["KILL"], dd["PASS"], dd["FAIL"]) == (8, 3, 5, 6, 2)
    assert (hp["lanes"], hp["KEEP"], hp["KILL"], hp["PASS"], hp["FAIL"]) == (8, 0, 8, 2, 6)


def test_reason_class_rollup_counts():
    _, _, lane_files = _render_r8()
    counts = MOD.reason_class_counts(lane_files)
    assert counts == {
        "PASS": 8,
        "FAIL_UNDERPERFORM": 6,
        "FAIL_NONPOSITIVE": 1,
        "UNGRADEABLE_NAN": 1,
    }
    # The one ungradeable lane is GLD drawdown_reversion.
    assert MOD._ungradeable_lanes(lane_files) == ["GLD drawdown_reversion"]


def test_burden_line():
    _, summary, _ = _render_r8()
    line = MOD.build_burden(summary)
    assert "192 new registered configs" in line
    assert "5,601 → 5,793" in line


# --------------------------------------------------------------------------- #
# Mandatory infrastructure-alarm line (standing rule 3)
# --------------------------------------------------------------------------- #
def test_infra_alarm_line_emitted_when_nonzero():
    block, _, lane_files = _render_r8()
    rollup = MOD.build_reason_rollup(*_render_r8()[1:])
    # Nonzero UNGRADEABLE share → alarm raised, share stated, never strategy.
    assert "UNGRADEABLE share 1/16 = 6.25% (nonzero)" in rollup
    assert "infrastructure alarm raised per standing rule 3" in rollup
    assert "NEVER treated as strategy evidence" in rollup
    # The UNGRADEABLE_NAN rollup row is present and flagged INFRASTRUCTURE ALARM.
    assert "UNGRADEABLE_NAN" in rollup
    assert "INFRASTRUCTURE ALARM" in rollup
    # And it surfaces in the full assembled block too.
    assert "infrastructure alarm raised" in block


def test_infra_alarm_line_says_no_alarm_when_zero(tmp_path):
    # Synthesize a zero-ungradeable slice from the r8 lanes minus the NaN lane.
    _, summary, lane_files = _render_r8()
    clean = {k: v for k, v in lane_files.items()
             if v.get("selection_gate", {}).get("reason_class") != "UNGRADEABLE_NAN"}
    rollup = MOD.build_reason_rollup(summary, clean)
    assert "no infrastructure alarm" in rollup
    assert "0.0%" in rollup


# --------------------------------------------------------------------------- #
# Formatting helpers
# --------------------------------------------------------------------------- #
def test_number_formatting():
    assert MOD.fmt_sharpe(1.012000316949979) == "1.012"
    assert MOD.fmt_sharpe(None) == "—"
    assert MOD.fmt_sharpe(float("nan")) == "—"
    assert MOD.fmt_runtime(4.825) == "4.8 s"
    assert MOD.fmt_runtime(900) == "900 s"
    assert MOD.fmt_share(8, 16) == "50.0%"
    assert MOD.fmt_share(6, 16) == "37.5%"
    assert MOD.fmt_share(1, 16) == "6.25%"
    assert MOD.fmt_int(5793) == "5,793"


def test_nan_lane_renders_em_dash_in_table():
    _, summary, _ = _render_r8()
    table = MOD.build_lane_table(summary)
    gld = [ln for ln in table.splitlines()
           if "drawdown_reversion · GLD" in ln][0]
    # searched / fixed / gap / t are all NaN → em dash; bench (2.056) is shown.
    assert gld.count("—") == 4
    assert "2.056" in gld
