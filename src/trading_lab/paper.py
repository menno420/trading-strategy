"""Paper-lane grading job (docs/paper-lane-protocol.md §5-§7, §9).

Parses ``experiments/paper/ledger.md``, finds trade windows whose exit has
filled, computes fills (t+1-open, 5+1 bps per side) and grades each closed
window net of costs against cycle-window buy-and-hold, appending the
verdict fields to the window's EXIT record. Market data comes EXCLUSIVELY
from ``trading_lab.data.load_paper_ohlcv`` — the paper-lane rail that
serves only bars >= ``config.PAPER_LANE_START`` and has no holdout escape
hatch of any kind. No other data access exists in this module.

Ledger record grammar (parser contract): records are ``### <heading>``
blocks; fields are ``- key: value`` bullets (wrapped continuations are
indented by two spaces; keys normalize to lowercase with underscores).
Trade rows carry ``action: ENTRY`` / ``action: EXIT`` plus ``signal_date``,
``intended_fill_bar`` and ``committed_at_utc``. Trade rows must strictly
alternate ENTRY, EXIT, ENTRY, ... (long/flat, max one open position); a
malformed sequence refuses to grade anything at all.

Write-back (§6: the weekly pass "appends the grades to the ledger"): ONLY
the EXIT record of a closed window is touched — its ``status:`` line flips
to ``GRADED`` (the prior value is preserved in ``pre_grade_status``) and
the verdict fields are appended as new bullets. Signal-side fields are
never edited; WATCH and ENTRY records are never mutated. Re-running is
idempotent: a record that already carries a ``verdict`` field is skipped
and the file is rewritten only when something new was graded.

Ambiguity resolves AGAINST the strategy (§9):

* ties are MISS (A5) — BEAT requires a strictly greater cycle return;
* a late or missing ``committed_at_utc`` on EITHER leg grades the window
  MISS regardless of P&L (A3; the protocol names the entry leg, so the
  exit leg resolves against the strategy too);
* "strictly before the fill bar's open" is bounded at 13:30 UTC on the
  fill date — 09:30 New York in daylight time, the EARLIER of the two
  possible UTC opens, so the stricter bound applies year-round.

Review index (informational, NOT graded evidence): each grading pass also
maintains ``experiments/paper/reviews.md`` — one record per ISO review
week, written idempotently (a same-week re-run with unchanged ledger state
is a byte-identical no-op) — so the protocol §7 aggregate denominator
(``m weeks reviewed, of which f FLAT``) is computable from the repo alone
instead of depending on a hand-appended FLAT note. Permission reading of
the binding protocol: §5 fixes the ledger's row grammar as trade-action
records and §6 only authorizes appending grades to the ledger — that is
NOT clear permission for machine-appended supplementary records inside the
protocol-governed ledger, so the index is a SEPARATE non-ledger artifact.
It decides nothing: the BEAT/MISS/FLAT grammar, the no-significance-claims
rule, and every ledger semantic stay defined solely by
``docs/paper-lane-protocol.md`` and are untouched. A malformed or
ungradeable pass (``LedgerFormatError``) records nothing — a failed pass
never counts as a reviewed week.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import config
from .data import load_paper_ohlcv

#: Cost per side, basis points (5 bps slippage + 1 bps commission — §2).
COST_BPS_PER_SIDE = config.DEFAULT_SLIPPAGE_BPS + config.DEFAULT_COMMISSION_BPS

#: Fixed notional per entry, protocol §4. No compounding, ever.
NOTIONAL_USD = 10_000.0

#: Strictest UTC bound for "before the fill bar's open" (09:30 New York
#: in daylight time; the earlier of the two possible UTC opens — §9 A3).
MARKET_OPEN_UTC = pd.Timedelta(hours=13, minutes=30)

DEFAULT_LEDGER = config.EXPERIMENTS_DIR / "paper" / "ledger.md"

#: Sibling review index maintained by each grading pass (informational,
#: not graded evidence — see module docstring). One record per ISO week.
REVIEWS_BASENAME = "reviews.md"

#: Review-record results: FLAT exactly per §7 (no position held and no
#: window graded in the review week); anything else is REVIEWED.
REVIEW_FLAT = "FLAT"
REVIEW_REVIEWED = "REVIEWED"

#: Header written when the review index does not exist yet. An existing
#: file's header is preserved verbatim — only record blocks are managed.
REVIEWS_HEADER = """\
# Paper-lane review index — informational, not graded evidence

> **Status:** `informational`
>
> Machine-readable per-pass review index, written idempotently by the
> protocol §6 grading job (`trading_lab.paper.grade_ledger`, invoked via
> `scripts/grade_paper.py`): one record per ISO review week, updated in
> place when the same week's ledger state changes, never duplicated. It
> exists so the protocol §7 aggregate denominator (`m weeks reviewed, of
> which f FLAT`) is computable from the repo alone. This file is NOT part
> of the protocol-governed ledger (`experiments/paper/ledger.md`), is NOT
> graded evidence, and decides nothing: verdicts, the BEAT/MISS/FLAT
> grammar, the no-significance-claims rule and all ledger semantics are
> defined solely by [docs/paper-lane-protocol.md](../../docs/paper-lane-protocol.md)
> and live solely in the ledger. A week with no grading pass leaves no
> record here — this index enumerates passes that ran, it cannot invent
> weeks that were missed (§6: a missed pass delays grading, nothing else).

## Review records (one per ISO week, newest last)
"""

_FIELD_RE = re.compile(r"^- ([^:]+):\s*(.*)$")


class LedgerFormatError(ValueError):
    """Raised when the ledger is malformed; nothing is graded (§9)."""


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

@dataclass
class Record:
    """One ``### ...`` ledger record: fields plus its line span."""
    heading: str
    start: int            # line index of the heading
    end: int              # one past the record's last line
    bullet_end: int       # one past the last field-bullet line
    fields: dict[str, str] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return self.fields.get("id", self.heading.lstrip("# ").strip())

    @property
    def action(self) -> str:
        return self.fields.get("action", "").strip().upper()

    @property
    def status_token(self) -> str:
        raw = self.fields.get("status", "").replace("*", "").strip()
        m = re.match(r"[A-Za-z-]+", raw)
        return m.group(0).upper() if m else ""

    @property
    def graded(self) -> bool:
        return "verdict" in self.fields


def parse_records(lines: list[str]) -> list[Record]:
    """Parse ``### `` record blocks and their ``- key: value`` bullets."""
    heads = [i for i, ln in enumerate(lines) if ln.startswith("### ")]
    records: list[Record] = []
    for k, s in enumerate(heads):
        e = heads[k + 1] if k + 1 < len(heads) else len(lines)
        rec = Record(heading=lines[s], start=s, end=e, bullet_end=s + 1)
        last_key: str | None = None
        for j in range(s + 1, e):
            m = _FIELD_RE.match(lines[j])
            if m:
                key = m.group(1).strip().lower().replace(" ", "_")
                rec.fields[key] = m.group(2).strip()
                last_key = key
                rec.bullet_end = j + 1
            elif lines[j].startswith("  ") and last_key is not None:
                rec.fields[last_key] += " " + lines[j].strip()
                rec.bullet_end = j + 1
            else:
                last_key = None
        records.append(rec)
    return records


def _pair_windows(trades: list[Record]) -> tuple[list[tuple[Record, Record]],
                                                 Record | None]:
    """Pair strictly-alternating ENTRY/EXIT rows into windows.

    Returns (closed pairs in ledger order, the unpaired open ENTRY or None).
    Any other sequence is malformed: refuse to grade anything (§9 —
    ambiguity resolves against the strategy).
    """
    pairs: list[tuple[Record, Record]] = []
    open_entry: Record | None = None
    for rec in trades:
        if rec.action == "ENTRY":
            if open_entry is not None:
                raise LedgerFormatError(
                    f"malformed ledger: ENTRY {rec.id!r} while ENTRY "
                    f"{open_entry.id!r} is still open; grading nothing")
            open_entry = rec
        else:  # EXIT
            if open_entry is None:
                raise LedgerFormatError(
                    f"malformed ledger: EXIT {rec.id!r} without a prior "
                    "open ENTRY; grading nothing")
            pairs.append((open_entry, rec))
            open_entry = None
    return pairs, open_entry


# ---------------------------------------------------------------------------
# Grading
# ---------------------------------------------------------------------------

@dataclass
class WindowGrade:
    entry_id: str
    exit_id: str
    verdict: str                    # BEAT | MISS
    late_commit: bool
    entry_fill_date: str
    entry_fill_open: float
    exit_fill_date: str
    exit_fill_open: float
    shares: float
    trade_return_net: float
    cycle_start_date: str
    cycle_start_open: float
    strategy_cycle_return_net: float
    bh_cycle_return_net: float


@dataclass
class GradeReport:
    graded: list[WindowGrade] = field(default_factory=list)
    already_graded: list[str] = field(default_factory=list)   # exit ids
    pending_fill: list[str] = field(default_factory=list)     # exit ids
    open_entries: list[str] = field(default_factory=list)     # entry ids
    watch: list[str] = field(default_factory=list)            # record ids
    flat_review: bool = False
    changed: bool = False
    # Review-index fields (additive; informational, not graded evidence).
    review_week: str = ""                 # ISO week key, e.g. 2026-W29
    review_result: str = ""               # REVIEW_FLAT | REVIEW_REVIEWED
    review_path: Path | None = None
    review_changed: bool = False           # index file written this pass
    weeks_reviewed: int = 0                # m in the §7 aggregate line
    flat_weeks: int = 0                    # f in the §7 aggregate line
    beat_total: int = 0                    # k (all-time, from the ledger)
    miss_total: int = 0


def _fill(bars: pd.DataFrame, intended: str) -> tuple[pd.Timestamp, float] | None:
    """First bar at/after the intended fill date, or None if not printed yet."""
    sel = bars.index[bars.index >= pd.Timestamp(intended)]
    if len(sel) == 0:
        return None
    ts = sel[0]
    return ts, float(bars.loc[ts, "open"])


def _committed_late(committed: str, fill_date: pd.Timestamp) -> bool:
    """True unless committed strictly before the fill bar's open (§9 A3).

    A missing or unparseable timestamp is late — against the strategy.
    """
    if not committed:
        return True
    try:
        ts = pd.Timestamp(committed)
    except (ValueError, TypeError):
        return True
    ts = ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")
    open_utc = fill_date.tz_localize("UTC") + MARKET_OPEN_UTC
    return not (ts < open_utc)


def _grade_window(entry: Record, exit_: Record,
                  cycle_start: tuple[pd.Timestamp, float],
                  entry_fill: tuple[pd.Timestamp, float],
                  exit_fill: tuple[pd.Timestamp, float]) -> WindowGrade:
    c = COST_BPS_PER_SIDE / 1e4
    (entry_date, entry_open) = entry_fill
    (exit_date, exit_open) = exit_fill
    (cycle_date, cycle_open) = cycle_start

    entry_eff = entry_open * (1 + c)
    exit_eff = exit_open * (1 - c)
    trade_ret = exit_eff / entry_eff - 1.0
    # Strategy over the cycle: flat (0%) outside the window, the trade
    # inside it — so the cycle return IS the trade return (§7).
    strat_cycle = trade_ret
    bh_cycle = exit_eff / (cycle_open * (1 + c)) - 1.0

    late = (_committed_late(entry.fields.get("committed_at_utc", ""), entry_date)
            or _committed_late(exit_.fields.get("committed_at_utc", ""), exit_date))
    verdict = "BEAT" if (not late and strat_cycle > bh_cycle) else "MISS"

    return WindowGrade(
        entry_id=entry.id, exit_id=exit_.id, verdict=verdict,
        late_commit=late,
        entry_fill_date=str(entry_date.date()), entry_fill_open=entry_open,
        exit_fill_date=str(exit_date.date()), exit_fill_open=exit_open,
        shares=NOTIONAL_USD / entry_open, trade_return_net=trade_ret,
        cycle_start_date=str(cycle_date.date()), cycle_start_open=cycle_open,
        strategy_cycle_return_net=strat_cycle, bh_cycle_return_net=bh_cycle,
    )


def _grade_bullets(g: WindowGrade, pre_grade_status: str, now: str) -> list[str]:
    lines = [
        f"- pre_grade_status: {pre_grade_status}",
        f"- verdict: {g.verdict}",
        f"- graded_at_utc: {now}",
    ]
    if g.late_commit:
        lines.append("- late_commit: true — graded MISS regardless of P&L "
                     "(protocol §5, §9 A3)")
    else:
        lines.append("- late_commit: false")
    lines += [
        f"- entry_fill_date: {g.entry_fill_date}",
        f"- entry_fill_open: {g.entry_fill_open:.6f}",
        f"- exit_fill_date: {g.exit_fill_date}",
        f"- exit_fill_open: {g.exit_fill_open:.6f}",
        f"- shares: {g.shares:.6f} ($10,000 / entry fill open, protocol §4)",
        f"- trade_return_net: {g.trade_return_net:.6f}",
        f"- cycle_start_date: {g.cycle_start_date}",
        f"- cycle_start_open: {g.cycle_start_open:.6f}",
        f"- strategy_cycle_return_net: {g.strategy_cycle_return_net:.6f}",
        f"- bh_cycle_return_net: {g.bh_cycle_return_net:.6f}",
        "- verdict_rule: BEAT iff strategy_cycle_return_net > "
        "bh_cycle_return_net strictly; ties and late commits are MISS "
        "(protocol §7, §9 A3/A5)",
    ]
    return lines


# ---------------------------------------------------------------------------
# Review index (informational, not graded evidence — module docstring)
# ---------------------------------------------------------------------------

def _iso_week(stamp: str) -> str | None:
    """``2026-07-17T09:05:00Z`` → ``2026-W29``; unparseable → None."""
    try:
        iso = pd.Timestamp(stamp).isocalendar()
    except (ValueError, TypeError):
        return None
    return f"{int(iso[0])}-W{int(iso[1]):02d}"


def _review_block(week: str, result: str, *, graded_this_week: int,
                  beat_total: int, miss_total: int, closed_total: int,
                  open_position: bool, watch: int) -> list[str]:
    """Render one review record. Deterministic in the ledger state and the
    week key — re-rendering an unchanged week yields identical lines, which
    is what makes the index write idempotent."""
    return [
        f"### review-{week} — {result}",
        "",
        f"- id: review-{week}",
        f"- review_week: {week} (ISO week of the grading pass)",
        f"- result: {result}",
        f"- windows_graded_this_week: {graded_this_week}",
        f"- closed_windows_total: {closed_total}",
        f"- beat_total: {beat_total}",
        f"- miss_total: {miss_total}",
        f"- open_position: {'true' if open_position else 'false'}",
        f"- watch_records: {watch}",
        "- note: informational index only — not graded evidence; verdicts "
        "live solely in ledger.md (protocol §5-§7)",
    ]


def _trim(block: list[str]) -> list[str]:
    block = list(block)
    while block and block[-1] == "":
        block.pop()
    return block


def _update_reviews(reviews_path: Path, week: str,
                    block: list[str]) -> tuple[bool, int, int]:
    """Insert or update this week's record in the review index.

    Returns ``(changed, weeks_reviewed, flat_weeks)``. Idempotent: an
    unchanged week rewrites nothing; a changed same-week state updates the
    week's record IN PLACE (never a duplicate); other weeks' records are
    preserved verbatim, as is an existing header.
    """
    if reviews_path.exists():
        old_text = reviews_path.read_text()
    else:
        old_text = REVIEWS_HEADER
    lines = old_text.split("\n")
    records = parse_records(lines)
    header = _trim(lines[:records[0].start] if records else lines)

    blocks = [_trim(lines[r.start:r.end]) for r in records]
    ids = [r.id for r in records]
    target = f"review-{week}"
    if target in ids:
        blocks[ids.index(target)] = _trim(block)
    else:
        blocks.append(_trim(block))

    new_text = "\n\n".join(["\n".join(header)]
                           + ["\n".join(b) for b in blocks]) + "\n"
    changed = new_text != old_text
    if changed:
        reviews_path.write_text(new_text)
    flats = sum(1 for b in blocks if f"- result: {REVIEW_FLAT}" in b)
    return changed, len(blocks), flats


def grade_ledger(ledger_path: Path | str | None = None, *,
                 data_dir: Path | None = None,
                 now: str | None = None,
                 reviews_path: Path | str | None = None) -> GradeReport:
    """Grade every closed, ungraded window in the paper ledger.

    Idempotent: already-graded records (any record carrying a ``verdict``
    field) are never touched; WATCH and ENTRY records are never mutated;
    the file is rewritten only when a new grade landed. Market data is
    read only via ``load_paper_ohlcv`` (bars >= PAPER_LANE_START only),
    and only when there is at least one window that needs grading.

    Each successful pass also maintains the sibling review index
    (``reviews_path``, default ``<ledger dir>/reviews.md``) — one record
    per ISO review week so the §7 ``m weeks reviewed, of which f FLAT``
    denominator is machine-readable. The index write is idempotent too:
    a same-week re-run with unchanged ledger state is a byte-identical
    no-op, and a changed same-week state updates the week's record in
    place, never duplicating it. Informational only, not graded evidence
    (module docstring); ``report.changed`` still refers to the LEDGER
    alone.
    """
    path = Path(ledger_path) if ledger_path is not None else DEFAULT_LEDGER
    text = path.read_text()
    lines = text.split("\n")
    records = parse_records(lines)
    now = now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    report = GradeReport()
    report.watch = [r.id for r in records if r.status_token == "WATCH"]

    trades = [r for r in records if r.action in ("ENTRY", "EXIT")]
    pairs, open_entry = _pair_windows(trades)
    if open_entry is not None:
        report.open_entries.append(open_entry.id)

    todo = [(e, x) for (e, x) in pairs if not x.graded]
    report.already_graded = [x.id for (_, x) in pairs if x.graded]

    edits: list[tuple[Record, list[str]]] = []  # (exit record, new bullets)
    if todo:
        ticker = todo[0][0].fields.get("instrument", "AAPL").split(",")[0]
        bars = load_paper_ohlcv(ticker.strip().upper(), "daily",
                                data_dir=data_dir)
        if bars.empty:
            raise LedgerFormatError(
                "no paper-lane bars available yet; nothing can be graded")
        prev_exit_fill = (bars.index[0], float(bars["open"].iloc[0]))
        for entry, exit_ in pairs:  # in order: cycles chain exit-to-exit (§7)
            cycle_start = prev_exit_fill
            entry_fill = _fill(bars, entry.fields.get("intended_fill_bar", ""))
            exit_fill = _fill(bars, exit_.fields.get("intended_fill_bar", ""))
            if entry_fill is None or exit_fill is None:
                # window not closed yet: exit (or even entry) hasn't printed
                if not exit_.graded:
                    report.pending_fill.append(exit_.id)
                break  # later windows depend on this cycle boundary
            if not exit_.graded:
                g = _grade_window(entry, exit_, cycle_start,
                                  entry_fill, exit_fill)
                report.graded.append(g)
                pre = exit_.fields.get("status", "")
                edits.append((exit_, _grade_bullets(g, pre, now)))
            prev_exit_fill = exit_fill

    # A pending-fill EXIT means the position is still open until it prints.
    has_open_position = bool(report.open_entries or report.pending_fill)
    report.flat_review = not has_open_position and not report.graded

    if edits:
        for exit_, bullets in sorted(edits, key=lambda t: t[0].start,
                                     reverse=True):
            for j in range(exit_.start, exit_.bullet_end):
                if lines[j].startswith("- status:"):
                    lines[j] = "- status: GRADED"
                    break
            lines[exit_.bullet_end:exit_.bullet_end] = bullets
        path.write_text("\n".join(lines))
        report.changed = True

    # Review index (informational, not graded evidence): one record per
    # ISO week, deterministic in the ledger's post-pass state, so a
    # same-week re-run is a byte-identical no-op (never a duplicate).
    week = _iso_week(now)
    prev_graded = [x for (_, x) in pairs if x.graded]  # graded before now
    prev_verdicts = [x.fields.get("verdict", "").strip()
                     for x in prev_graded]
    report.beat_total = (len([g for g in report.graded
                              if g.verdict == "BEAT"])
                         + prev_verdicts.count("BEAT"))
    report.miss_total = (len([g for g in report.graded
                              if g.verdict == "MISS"])
                         + prev_verdicts.count("MISS"))
    graded_this_week = (len(report.graded)
                        + sum(1 for x in prev_graded
                              if _iso_week(x.fields.get("graded_at_utc",
                                                        "")) == week))
    report.review_result = (REVIEW_FLAT
                            if not has_open_position and not graded_this_week
                            else REVIEW_REVIEWED)
    report.review_week = week
    block = _review_block(
        week, report.review_result, graded_this_week=graded_this_week,
        beat_total=report.beat_total, miss_total=report.miss_total,
        closed_total=len(report.graded) + len(report.already_graded),
        open_position=has_open_position, watch=len(report.watch))
    report.review_path = (Path(reviews_path) if reviews_path is not None
                          else path.parent / REVIEWS_BASENAME)
    (report.review_changed, report.weeks_reviewed,
     report.flat_weeks) = _update_reviews(report.review_path, week, block)
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    """Run one grading pass on the repo ledger and print the §7 summary."""
    report = grade_ledger()
    for g in report.graded:
        print(f"{g.exit_id}: {g.verdict}  strategy_cycle="
              f"{g.strategy_cycle_return_net:+.4%} vs "
              f"bh_cycle={g.bh_cycle_return_net:+.4%}"
              + ("  [LATE COMMIT]" if g.late_commit else ""))
    for rid in report.pending_fill:
        print(f"{rid}: OPEN — exit not filled yet, ungraded (§6)")
    for rid in report.open_entries:
        print(f"{rid}: OPEN — position open, ungraded (§6)")
    for rid in report.watch:
        print(f"{rid}: WATCH — not gradeable, left untouched")
    if report.flat_review:
        print("FLAT — no window closed and no position open this pass (§7)")
    beats = len([g for g in report.graded if g.verdict == "BEAT"])
    n_closed = len(report.graded) + len(report.already_graded)
    print(f"this pass: {beats} BEAT of {len(report.graded)} newly graded "
          f"windows; {n_closed} closed windows total in ledger "
          f"({len(report.watch)} WATCH, "
          f"{len(report.open_entries) + len(report.pending_fill)} open)")
    print(f"review index: {report.review_week} {report.review_result} — "
          f"{report.review_path} "
          f"({'updated' if report.review_changed else 'unchanged'}; "
          f"informational, not graded evidence)")
    print(f"aggregate (§7): {report.beat_total} BEAT of {n_closed} closed "
          f"windows ({report.weeks_reviewed} weeks reviewed, of which "
          f"{report.flat_weeks} FLAT)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
