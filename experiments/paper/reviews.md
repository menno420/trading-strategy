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

### review-2026-W29 — FLAT

- id: review-2026-W29
- review_week: 2026-W29 (ISO week of the grading pass)
- result: FLAT
- windows_graded_this_week: 0
- closed_windows_total: 0
- beat_total: 0
- miss_total: 0
- open_position: false
- watch_records: 1
- note: informational index only — not graded evidence; verdicts live solely in ledger.md (protocol §5-§7)
