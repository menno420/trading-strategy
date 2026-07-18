"""Tests for scripts/aggregate_effect_sizes.py — the cross-round effect-size
aggregator used by docs/cross-round-meta-analysis.md.

What must hold: the aggregator reads the COMMITTED modern run-slice
``summary.json`` files (R6–R8, the slices carrying a per-lane ``tstat``) and
reproduces the KEY effect-size numbers that the meta-analysis foregrounds — the
selected slice set, each slice's verdict/gate counts, the best searched t and
the lane it belongs to, the uniform per-lane bar, and the chronological order.
These are the same numbers committed to the round results docs; the test pins
that the tool re-derives them from the JSONs rather than inventing any. It is a
"reproduces the numbers" test, not a brittle golden string.
"""

import importlib.util
import sys

from trading_lab import config


def _script():
    path = config.REPO_ROOT / "scripts" / "aggregate_effect_sizes.py"
    spec = importlib.util.spec_from_file_location("aggregate_effect_sizes", path)
    mod = importlib.util.module_from_spec(spec)
    # Register before exec so the module's frozen dataclass can resolve its own
    # module namespace (dataclasses inspects sys.modules[cls.__module__]).
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


MOD = _script()
ROWS = MOD.aggregate()
BY_SLICE = {r.slice: r for r in ROWS}


# --------------------------------------------------------------------------- #
# Selection + ordering
# --------------------------------------------------------------------------- #
def test_selects_exactly_the_modern_run_slices():
    # R6–R8 slices share the per-lane-tstat schema; nothing else qualifies.
    assert set(BY_SLICE) == {
        "r6-volume",
        "r6-gap",
        "r6-volume-hourly",
        "r7-drawdown-reversion",
        "r7-high-proximity",
        "r7c-conjunction",
        "r8-hourly",
    }


def test_rows_are_chronological_by_cumulative():
    cumulative = [r.program_variants_tried for r in ROWS]
    assert cumulative == sorted(cumulative)
    # Newest slice is Round 8 at the program cumulative headline 5,793.
    assert ROWS[-1].slice == "r8-hourly"
    assert ROWS[-1].program_variants_tried == 5793


def test_bar_is_uniform_2638_everywhere():
    # The K=12 Bonferroni bar, never lowered.
    assert all(round(r.bar, 3) == 2.638 for r in ROWS)


# --------------------------------------------------------------------------- #
# Per-slice numbers (traced to the committed round results docs)
# --------------------------------------------------------------------------- #
def test_r8_hourly_numbers():
    r = BY_SLICE["r8-hourly"]
    assert (r.keep, r.kill, r.kill_sig) == (3, 13, 0)
    assert (r.gate_pass, r.gate_fail) == (8, 8)
    assert round(r.best_t, 3) == 1.079
    assert r.best_t_lane == "drawdown_reversion · MSFT"
    assert r.lanes == 16
    assert r.registered_configs == 192


def test_r7_high_proximity_holds_the_program_best_t_among_modern_slices():
    r = BY_SLICE["r7-high-proximity"]
    assert round(r.best_t, 3) == 1.195
    assert r.best_t_lane == "high_proximity · BTC-USD"
    # And it is the strongest dev arm across the modern (R6–R8) set.
    strongest = max(ROWS, key=lambda x: x.best_t)
    assert strongest.slice == "r7-high-proximity"
    # Still less than half the 2.638 bar — nothing clears it.
    assert strongest.best_t < strongest.bar / 2


def test_r7c_conjunction_is_the_only_modern_slice_with_kill_sig():
    r = BY_SLICE["r7c-conjunction"]
    assert (r.keep, r.kill, r.kill_sig) == (1, 11, 3)
    sig_slices = {x.slice for x in ROWS if x.kill_sig > 0}
    assert sig_slices == {"r6-volume", "r6-gap", "r7c-conjunction"}


def test_r6_gap_is_the_sharpest_null():
    r = BY_SLICE["r6-gap"]
    assert (r.keep, r.kill, r.kill_sig) == (0, 5, 7)
    assert r.best_t < 0  # even its strongest arm is negative


def test_no_slice_reports_a_promotion():
    # verdict vocabulary is KEEP/KILL/KILL-SIG only — no PROMOTE anywhere.
    import json

    for slug in BY_SLICE:
        summary = json.loads(
            (MOD.SWEEPS_DIR / slug / "summary.json").read_text()
        )
        assert "PROMOTE" not in summary["verdict_counts"]


# --------------------------------------------------------------------------- #
# Rendering
# --------------------------------------------------------------------------- #
def test_render_table_has_a_row_per_slice_and_a_header():
    table = MOD.render_table(ROWS)
    assert table.count("\n") == len(ROWS) + 1  # header + separator + N rows − 1
    assert "Best searched t" in table
    for slug in BY_SLICE:
        assert f"`{slug}`" in table
