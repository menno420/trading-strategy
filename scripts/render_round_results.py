#!/usr/bin/env python3
"""Render the mechanical results-table markdown block for a research slice.

READ-ONLY generator. Given a slice name (e.g. ``r8-hourly``) it loads the
committed ``experiments/sweeps/<slice>/summary.json`` plus the per-lane JSONs
and emits — to stdout — the standardized markdown block that every round
results doc has so far HAND-TRANSCRIBED from those same JSONs:

  (a) the slice-summary table row
      ``Slice | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Runtime vs cap``
  (b) the per-lane table
      ``Lane (family · instrument) | searched | bench | fixed | gap | t | gate | verdict``
  (c) the per-family Counts sub-tables
  (d) the reason_class rollup table + the MANDATORY UNGRADEABLE-share
      infrastructure-alarm line (standing rule 3)
  (e) the burden line (from the slice's registered/cumulative config counts)

Nothing here re-runs a sweep, touches the network, or grades anything: it only
RE-FORMATS numbers that already live in committed artifacts, so future round
results tables stop being typed by hand (the recurring transcription risk this
program has flagged). Numbers are formatted to match the existing docs
(3 decimals for Sharpe/t; null → ``—``).

Single-name slices only (one lane per ``family__ticker``). Portfolio slices
(one lane per config over a basket, e.g. ``r7d-xsec-drawdown``) have a
different lane shape and NO ``selection_gate`` block; they are detected and
skipped with a clear one-line message + non-zero exit (a documented limitation,
not a crash). Portfolio rendering is a future extension.

Usage::

    python3 scripts/render_round_results.py <slice-name>
    python3 scripts/render_round_results.py r8-hourly
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Self-bootstrap sys.path like the runners so the script is runnable from
# anywhere and importable by the test. (No trading_lab import is needed — this
# generator is pure read-only over committed JSON — but the repo root is used
# to resolve the sweeps directory.)
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT / "src"))

SWEEPS_DIR = _REPO_ROOT / "experiments" / "sweeps"

# Canonical display order for the reason_class rollup: PASS first, the FAIL_*
# classes next, and the UNGRADEABLE infra alarm ALWAYS last (it is called out
# specially, never mixed into the strategy story).
_REASON_ORDER = [
    "PASS",
    "FAIL_UNDERPERFORM",
    "FAIL_NONPOSITIVE",
    "UNGRADEABLE_NAN",
]

# Fixed notes for the known reason classes (mirrors the hand-written docs).
_REASON_NOTES = {
    "PASS": "searched arm reproduced + gradeable",
    "FAIL_UNDERPERFORM": "fixed replay does not beat B&H with positive Sharpe",
    "FAIL_NONPOSITIVE": "searched/fixed Sharpe non-positive",
}


class PortfolioSliceError(RuntimeError):
    """Raised when a slice is portfolio-shaped (single-name only supported)."""


# --------------------------------------------------------------------------- #
# Loading / detection
# --------------------------------------------------------------------------- #
def _slice_dir(slice_name: str) -> Path:
    return SWEEPS_DIR / slice_name


def load_lane_files(slice_dir: Path) -> dict[tuple[str, str], dict]:
    """Load every per-lane JSON (``<family>__<instrument>.json``) in a slice.

    Keyed by ``(family, instrument)``. ``summary.json`` is skipped.
    """
    lanes: dict[tuple[str, str], dict] = {}
    for path in sorted(slice_dir.glob("*__*.json")):
        if path.name == "summary.json":
            continue
        data = json.loads(path.read_text())
        lanes[(data.get("family"), data.get("instrument"))] = data
    return lanes


def is_portfolio_slice(lane_files: dict[tuple[str, str], dict]) -> bool:
    """A slice is portfolio-shaped when its lanes carry no ``selection_gate``.

    Single-name lanes always carry the per-lane ``selection_gate`` block (its
    result is the R5-D fixed-config row). Portfolio lanes (one config over a
    basket, e.g. ``xsec_drawdown``) instead carry a ``selection_walk_forward``
    block and a plural ``instruments`` list, and never a ``selection_gate``.
    """
    if not lane_files:
        return False
    return any("selection_gate" not in lane for lane in lane_files.values())


def load_slice(slice_name: str) -> tuple[dict, dict[tuple[str, str], dict]]:
    """Return ``(summary, lane_files)`` for a single-name slice.

    Raises ``FileNotFoundError`` if the slice or its ``summary.json`` is
    missing, and ``PortfolioSliceError`` if the slice is portfolio-shaped.
    """
    slice_dir = _slice_dir(slice_name)
    if not slice_dir.is_dir():
        raise FileNotFoundError(f"no such slice directory: {slice_dir}")

    lane_files = load_lane_files(slice_dir)
    if is_portfolio_slice(lane_files):
        raise PortfolioSliceError(slice_name)

    summary_path = slice_dir / "summary.json"
    if not summary_path.is_file():
        raise FileNotFoundError(f"missing summary.json: {summary_path}")
    summary = json.loads(summary_path.read_text())
    return summary, lane_files


# --------------------------------------------------------------------------- #
# Number formatting (match the hand-written docs)
# --------------------------------------------------------------------------- #
def fmt_sharpe(value) -> str:
    """3-decimal Sharpe/t; ``None``/NaN → em dash (matches the docs)."""
    if value is None:
        return "—"
    if isinstance(value, float) and value != value:  # NaN
        return "—"
    return f"{value:.3f}"


def fmt_runtime(seconds) -> str:
    """Seconds with unit: 1 decimal, trailing ``.0`` dropped so a whole-second
    cap renders ``900 s`` and a fractional runtime renders ``4.8 s`` — matching
    the docs."""
    s = f"{float(seconds):.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    return s + " s"


def fmt_share(count: int, total: int) -> str:
    """Percentage share the way the docs render it: 2 decimals, one trailing
    zero trimmed (50.00→50.0, 37.50→37.5, 6.25→6.25). Always ≥1 decimal."""
    if total == 0:
        return "0.0%"
    s = f"{100.0 * count / total:.2f}"
    if s.endswith("0"):
        s = s[:-1]
    return s + "%"


def fmt_int(value) -> str:
    """Thousands-separated integer, e.g. ``5,793`` (matches the burden line)."""
    return f"{int(value):,}"


# --------------------------------------------------------------------------- #
# Ordering helpers
# --------------------------------------------------------------------------- #
def ordered_families(lanes: list[dict]) -> list[str]:
    """Families in first-appearance order across the summary lanes."""
    seen: list[str] = []
    for lane in lanes:
        fam = lane["family"]
        if fam not in seen:
            seen.append(fam)
    return seen


def lanes_grouped_by_family(lanes: list[dict]) -> list[dict]:
    """Summary lanes regrouped family-by-family (the docs' per-lane table
    order), preserving each family's ticker order of first appearance."""
    out: list[dict] = []
    for fam in ordered_families(lanes):
        out.extend(lane for lane in lanes if lane["family"] == fam)
    return out


# --------------------------------------------------------------------------- #
# Block builders
# --------------------------------------------------------------------------- #
def _round_prefix(slice_name: str) -> str:
    """``r8-hourly`` → ``R8``; ``r7c-conjunction`` → ``R7C``. Falls back to the
    upper-cased leading token."""
    head = slice_name.split("-", 1)[0]
    return head.upper()


def build_slice_summary(summary: dict) -> str:
    """(a) The one-row slice-summary table."""
    slice_name = summary["sweep"]
    lanes = summary["lanes"]
    families = ordered_families(lanes)
    instruments = sorted({lane["instrument"] for lane in lanes})
    n_instruments = len(instruments)
    # Timeframe is a lane-JSON field; the slice name usually carries it too.
    timeframe = slice_name.split("-", 1)[-1] if "-" in slice_name else ""

    label = (
        f"{_round_prefix(slice_name)} `{slice_name}` "
        f"({' + '.join(families)} × {n_instruments} {timeframe})".rstrip()
    )
    vc = summary["verdict_counts"]
    gc = summary["gate_counts"]
    row = (
        f"| {label} | {len(lanes)} | {vc['KEEP']} | {vc['KILL']} | "
        f"{vc['KILL-SIG']} | {gc['PASS']} / {gc['FAIL']} | "
        f"{fmt_runtime(summary['runtime_seconds'])} / "
        f"{fmt_runtime(summary['cap_seconds'])} |"
    )
    header = (
        "| Slice | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | "
        "Runtime vs cap |\n"
        "|---|---|---|---|---|---|---|"
    )
    return header + "\n" + row


def build_lane_table(summary: dict) -> str:
    """(b) The per-lane table (family-grouped, docs order)."""
    header = (
        "| Lane (family · instrument) | searched | bench | fixed | gap | "
        "t (K=12) | gate | verdict |\n"
        "|---|---|---|---|---|---|---|---|"
    )
    rows = []
    for lane in lanes_grouped_by_family(summary["lanes"]):
        rows.append(
            f"| {lane['family']} · {lane['instrument']} | "
            f"{fmt_sharpe(lane['oos_sharpe'])} | "
            f"{fmt_sharpe(lane['bench_sharpe'])} | "
            f"{fmt_sharpe(lane['fixed_sharpe'])} | "
            f"{fmt_sharpe(lane['selection_gap'])} | "
            f"{fmt_sharpe(lane['tstat'])} | "
            f"{lane['gate']} | **{lane['verdict']}** |"
        )
    return header + "\n" + "\n".join(rows)


def _counts(lanes: list[dict]) -> dict:
    keep = sum(1 for l in lanes if l["verdict"] == "KEEP")
    kill = sum(1 for l in lanes if l["verdict"] == "KILL")
    killsig = sum(1 for l in lanes if l["verdict"] == "KILL-SIG")
    gate_pass = sum(1 for l in lanes if l["gate"] == "PASS")
    gate_fail = sum(1 for l in lanes if l["gate"] == "FAIL")
    return {
        "lanes": len(lanes),
        "KEEP": keep,
        "KILL": kill,
        "KILL-SIG": killsig,
        "PASS": gate_pass,
        "FAIL": gate_fail,
    }


def build_counts(summary: dict) -> str:
    """(c) Overall + per-family Counts sub-tables."""
    lanes = summary["lanes"]
    parts: list[str] = []

    overall = _counts(lanes)
    parts.append("### Counts — overall\n")
    parts.append(
        "| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | "
        "KEEPs demoted by gate |\n"
        "|---|---|---|---|---|---|---|\n"
        f"| {overall['lanes']} | {overall['KEEP']} | {overall['KILL']} | "
        f"{overall['KILL-SIG']} | {overall['PASS']} | {overall['FAIL']} | "
        f"{summary['keeps_demoted_by_gate']} |"
    )

    for fam in ordered_families(lanes):
        fam_lanes = [l for l in lanes if l["family"] == fam]
        c = _counts(fam_lanes)
        parts.append(f"\n### Counts — `{fam}` ({c['lanes']} lanes)\n")
        parts.append(
            "| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL |\n"
            "|---|---|---|---|---|---|\n"
            f"| {c['lanes']} | {c['KEEP']} | {c['KILL']} | {c['KILL-SIG']} | "
            f"{c['PASS']} | {c['FAIL']} |"
        )
    return "\n".join(parts)


def reason_class_counts(lane_files: dict[tuple[str, str], dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for lane in lane_files.values():
        rc = lane.get("selection_gate", {}).get("reason_class", "UNKNOWN")
        counts[rc] = counts.get(rc, 0) + 1
    return counts


def _sorted_reason_classes(counts: dict[str, int]) -> list[str]:
    def key(rc: str) -> tuple[int, str]:
        idx = _REASON_ORDER.index(rc) if rc in _REASON_ORDER else len(_REASON_ORDER)
        return (idx, rc)

    return sorted(counts, key=key)


def _ungradeable_lanes(lane_files: dict[tuple[str, str], dict]) -> list[str]:
    out = []
    for (family, instrument), lane in lane_files.items():
        if lane.get("selection_gate", {}).get("reason_class") == "UNGRADEABLE_NAN":
            out.append(f"{instrument} {family}")
    return sorted(out)


def build_reason_rollup(
    summary: dict, lane_files: dict[tuple[str, str], dict]
) -> str:
    """(d) reason_class rollup table + the mandatory UNGRADEABLE infra-alarm
    line (standing rule 3)."""
    counts = reason_class_counts(lane_files)
    total = len(lane_files)
    ungradeable_lanes = _ungradeable_lanes(lane_files)
    ungradeable_n = counts.get("UNGRADEABLE_NAN", 0)

    lines = ["### reason_class rollup (standing rule 3)\n"]
    lines.append("| reason_class | count | share | note |")
    lines.append("|---|---|---|---|")
    for rc in _sorted_reason_classes(counts):
        n = counts[rc]
        share = fmt_share(n, total)
        if rc == "UNGRADEABLE_NAN":
            lane_str = ", ".join(ungradeable_lanes) if ungradeable_lanes else "—"
            note = (
                f"INFRASTRUCTURE ALARM — degenerate/NaN stitched OOS "
                f"({lane_str}); NOT strategy evidence"
            )
            # Bold the whole alarm row (matches the hand-written docs).
            lines.append(f"| **{rc}** | **{n}** | **{share}** | **{note}** |")
        else:
            note = _REASON_NOTES.get(rc, "")
            lines.append(f"| {rc} | {n} | {share} | {note} |")

    lines.append("")
    if ungradeable_n == 0:
        lines.append(
            f"**UNGRADEABLE share 0/{total} = {fmt_share(0, total)} → "
            f"no infrastructure alarm.**"
        )
    else:
        lane_str = ", ".join(ungradeable_lanes)
        lines.append(
            f"**UNGRADEABLE share {ungradeable_n}/{total} = "
            f"{fmt_share(ungradeable_n, total)} (nonzero) → infrastructure "
            f"alarm raised per standing rule 3.** The ungradeable "
            f"lane(s) ({lane_str}) produced degenerate/NaN stitched OOS "
            f"returns; reported as an infra fact and NEVER treated as "
            f"strategy evidence (counted KILL by the Round-2 tie-to-KILL "
            f"rule, not by a measured underperformance)."
        )
    return "\n".join(lines)


def build_burden(summary: dict) -> str:
    """(e) The burden line from the slice's config counts."""
    registered = summary["registered_configs"]
    cumulative_after = summary["program_variants_tried"]
    cumulative_before = cumulative_after - registered
    return (
        f"**Burden:** {fmt_int(registered)} new registered configs; program "
        f"cumulative {fmt_int(cumulative_before)} → {fmt_int(cumulative_after)}."
    )


def render(summary: dict, lane_files: dict[tuple[str, str], dict]) -> str:
    """Assemble the full standardized results-table block."""
    blocks = [
        build_slice_summary(summary),
        build_lane_table(summary),
        build_counts(summary),
        build_reason_rollup(summary, lane_files),
        build_burden(summary),
    ]
    return "\n\n".join(blocks) + "\n"


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Render the mechanical results-table markdown block for a "
            "single-name research slice from its committed sweep JSONs."
        )
    )
    parser.add_argument(
        "slice",
        help="slice name, e.g. r8-hourly (a directory under experiments/sweeps/)",
    )
    args = parser.parse_args(argv)

    try:
        summary, lane_files = load_slice(args.slice)
    except PortfolioSliceError:
        print(
            f"portfolio slice '{args.slice}' — not yet supported by this "
            f"generator (single-name only); see docs/research-round-8-results.md "
            f"(portfolio rendering is a documented future extension).",
            file=sys.stderr,
        )
        return 2
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    sys.stdout.write(render(summary, lane_files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
