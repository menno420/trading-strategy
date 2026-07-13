"""Equal-weight survivor committees — Round-4 slice R4-C.

POST-HOLDOUT, DEV-ONLY (ORDER 012). Pre-registered in
``docs/research-round-4-plan.md`` § "R4-C — Ensemble / committee of
survivors", merged to main BEFORE this module existed: per instrument with
>= 2 KEEP-dev families, form an equal-weight signal committee —
**position = mean of member positions** — and grade it vs (a) the best
single member and (b) buy-and-hold, on the same rail, costs, and
walk-forward windows as the members. Members are FROZEN as the lanes'
already-committed choices (no re-search inside the committee).

Two adopted conventions the plan is silent on (recorded here, in the
runner, and in the results doc; both decided BEFORE any committee ran):

* **Grouping is instrument x timeframe.** Mixing daily and hourly member
  positions is not meaningful (different bar clocks, different
  walk-forward windows), so a "qualifying instrument" is an
  (instrument, timeframe) pair with >= 2 KEEP-dev lanes.
* **One member per family per committee** (the plan says "families").
  Where the same family holds two KEEP lanes on one instrument x
  timeframe (duplicate round-3 coverage), the committee takes ONE —
  chosen by a performance-blind, deterministic tiebreak: lexicographically
  smallest ``(sweep, source_file)``, which for the two duplicated families
  on the committed KEEP surface (TLT and XOM ``donchian``) coincides with
  first-committed chronology. Deduped-out lanes are still reported, and
  the runner's best-member comparison uses ALL KEEP lanes of the group
  (the superset), which can only RAISE the bar the committee must clear.

The committee is the only new object; averaging long/flat members yields
fractional positions, which :func:`trading_lab.engine.run_backtest`
supports natively (positions in [-1, 1]; costs are charged on
``|change in held position|``, fractional included).

Research only: this module composes simulated positions; it never touches
brokers or orders.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Mapping, Sequence

import pandas as pd


def committee_positions(members: Sequence[pd.Series]) -> pd.Series:
    """Equal-weight committee position: the MEAN of member positions.

    ``members`` are the frozen per-bar position series of the committee
    members over the SAME bars (identical indices). Disagreement yields
    fractional positions by design — e.g. two members at 1 and 0 give 0.5.
    The mean of values in [-1, 1] stays in [-1, 1], so the result is
    always a valid engine position series.
    """
    if len(members) < 2:
        raise ValueError(f"a committee needs >= 2 members, got {len(members)}")
    first = members[0]
    for i, pos in enumerate(members):
        if not pos.index.equals(first.index):
            raise ValueError(f"member {i} index misaligned with member 0 — "
                             "committee members must share the same bars")
        if pos.isna().any():
            raise ValueError(f"member {i} positions contain NaN")
        if (pos.astype(float).abs() > 1).any():
            raise ValueError(f"member {i} positions outside [-1, 1]")
    return sum(m.astype(float) for m in members) / float(len(members))


def enumerate_committees(lanes: Sequence[Mapping], *,
                         min_members: int = 2) -> list[dict]:
    """Enumerate committee groups from KEEP-lane rows.

    ``lanes`` are mappings with at least ``instrument``, ``timeframe``,
    ``strategy``, ``sweep`` and ``source_file`` keys (the shape of the
    R4-A re-grade report rows). Groups by (instrument, timeframe) —
    NEVER across timeframes — dedupes to one lane per strategy family
    (performance-blind lexicographic ``(sweep, source_file)`` tiebreak),
    and returns only groups with >= ``min_members`` members, sorted by
    (instrument, timeframe). Each returned dict has:

    * ``instrument``, ``timeframe``
    * ``members`` — the deduped lanes, sorted by (strategy, sweep)
    * ``deduped_out`` — duplicate-family lanes excluded from the
      committee (still part of the group's best-member superset)
    * ``group_lanes`` — ALL the group's KEEP lanes (members + deduped_out)
    """
    groups: dict[tuple[str, str], list[Mapping]] = defaultdict(list)
    for lane in lanes:
        groups[(lane["instrument"], lane["timeframe"])].append(lane)

    committees = []
    for (instrument, timeframe), rows in sorted(groups.items()):
        by_family: dict[str, Mapping] = {}
        deduped_out = []
        for lane in sorted(rows, key=lambda r: (r["strategy"], r["sweep"],
                                                r["source_file"])):
            fam = lane["strategy"]
            if fam in by_family:  # first (sweep, source_file) wins
                deduped_out.append(lane)
            else:
                by_family[fam] = lane
        members = sorted(by_family.values(),
                         key=lambda r: (r["strategy"], r["sweep"]))
        if len(members) < min_members:
            continue
        committees.append({
            "instrument": instrument,
            "timeframe": timeframe,
            "members": list(members),
            "deduped_out": deduped_out,
            "group_lanes": sorted(rows, key=lambda r: (r["strategy"],
                                                       r["sweep"],
                                                       r["source_file"])),
        })
    return committees
