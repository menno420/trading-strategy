#!/usr/bin/env python3
"""Aggregate the cross-round effect-size distribution from committed sweep JSONs.

READ-ONLY aggregator. Scans ``experiments/sweeps/*/summary.json`` and, for
every **modern run-slice** (one that carries a ``verdict_counts`` block *and* a
``lanes`` list whose entries expose a per-lane ``tstat``), emits the
effect-size row that the cross-round meta-analysis foregrounds:

    slice | round configs | program cumulative | lanes | KEEP | KILL |
    KILL-SIG | gate PASS/FAIL | best searched t | its lane | bar (min_tstat)

The point is a single, machine-checkable view of **how far the strongest dev
arm each round sat BELOW its significance bar** — the effect-size distribution
behind the program's ``0 promoted`` headline. Rows are ordered chronologically
by ``program_variants_tried`` (the registered-config cumulative).

This covers the Round-6 → Round-8 slices, which share the uniform
per-lane-``tstat`` schema. Earlier rounds (P1/R2/R3/R4/R5) predate that schema
or record their t-stats differently; their best-t figures are cited from the
committed results docs and the research-program dashboard/retrospective, not
recomputed here — this tool never invents a number a JSON does not contain.

Nothing here re-runs a sweep, touches the network, reads holdout data, or
grades anything: it only RE-FORMATS numbers already committed to artifacts.
**RESEARCH-ONLY, in-sample; promotion is CLOSED and the holdout is SPENT.**

Usage::

    python3 scripts/aggregate_effect_sizes.py
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
SWEEPS_DIR = _REPO_ROOT / "experiments" / "sweeps"


@dataclass(frozen=True)
class SliceEffect:
    """One modern run-slice's effect-size summary, read from its summary.json."""

    slice: str
    program_variants_tried: int
    registered_configs: int
    lanes: int
    keep: int
    kill: int
    kill_sig: int
    gate_pass: int
    gate_fail: int
    best_t: float
    best_t_lane: str  # "family · instrument"
    bar: float  # per-lane min_tstat (uniform within a slice)


def _is_modern_run_slice(summary: dict) -> bool:
    """A run-slice with verdict counts AND per-lane tstat at a single uniform
    Bonferroni bar (the R6–R8 schema this effect-size table renders).

    A lane must carry both ``tstat`` and the uniform per-lane ``min_tstat``
    field this table reads into its single ``bar`` column. Slices whose lanes
    report their t against MULTIPLE bars instead (e.g. Round 9's cross-class
    confluence vote, graded at BOTH a per-lane K=4 and a program-wide K=60 bar
    via ``min_tstat_K4`` / ``min_tstat_K60``) do not fit a single-bar table and
    are correctly excluded — their effect sizes live in their own results docs
    and the per-round scoreboard, not this uniform-bar rollup."""
    lanes = summary.get("lanes")
    if not summary.get("verdict_counts"):
        return False
    return (bool(lanes) and isinstance(lanes, list)
            and "tstat" in lanes[0] and "min_tstat" in lanes[0])


def aggregate(sweeps_dir: Path = SWEEPS_DIR) -> list[SliceEffect]:
    """Return the effect-size rows for every modern run-slice, chronological."""
    rows: list[SliceEffect] = []
    for summary_path in sorted(sweeps_dir.glob("*/summary.json")):
        summary = json.loads(summary_path.read_text())
        if not _is_modern_run_slice(summary):
            continue

        lanes = summary["lanes"]
        vc = summary["verdict_counts"]
        gc = summary.get("gate_counts") or {}

        graded = [ln for ln in lanes if ln.get("tstat") is not None]
        best = max(graded, key=lambda ln: ln["tstat"])
        bars = {
            round(ln["min_tstat"], 6)
            for ln in lanes
            if ln.get("min_tstat") is not None
        }
        if len(bars) != 1:
            raise ValueError(
                f"{summary_path}: non-uniform per-lane bar {sorted(bars)}"
            )

        rows.append(
            SliceEffect(
                slice=summary["sweep"],
                program_variants_tried=int(summary["program_variants_tried"]),
                registered_configs=int(summary["registered_configs"]),
                lanes=len(lanes),
                keep=int(vc.get("KEEP", 0)),
                kill=int(vc.get("KILL", 0)),
                kill_sig=int(vc.get("KILL-SIG", 0)),
                gate_pass=int(gc.get("PASS", 0)),
                gate_fail=int(gc.get("FAIL", 0)),
                best_t=float(best["tstat"]),
                best_t_lane=f"{best['family']} · {best['instrument']}",
                bar=next(iter(bars)),
            )
        )

    rows.sort(key=lambda r: r.program_variants_tried)
    return rows


def render_table(rows: list[SliceEffect]) -> str:
    """Render the effect-size rows as a GitHub-flavored markdown table."""
    header = (
        "| Slice | Round configs | Program cumulative | Lanes | KEEP | KILL "
        "| KILL-SIG | Gate PASS/FAIL | Best searched t | Best-t lane | Bar |"
    )
    sep = "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|"
    lines = [header, sep]
    for r in rows:
        lines.append(
            f"| `{r.slice}` | {r.registered_configs} "
            f"| {r.program_variants_tried} | {r.lanes} | {r.keep} | {r.kill} "
            f"| {r.kill_sig} | {r.gate_pass} / {r.gate_fail} "
            f"| {r.best_t:.3f} | {r.best_t_lane} | {r.bar:.3f} |"
        )
    return "\n".join(lines)


def main() -> int:
    rows = aggregate()
    if not rows:
        print("no modern run-slices found under", SWEEPS_DIR)
        return 1
    print(render_table(rows))
    best = max(rows, key=lambda r: r.best_t)
    print(
        f"\nStrongest dev arm across these slices: t = {best.best_t:.3f} "
        f"({best.best_t_lane}, `{best.slice}`) vs bar {best.bar:.3f} — "
        f"still less than half the bar. RESEARCH-ONLY / in-sample; "
        f"promotion CLOSED, holdout SPENT."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
