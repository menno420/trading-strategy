# 2026-07-14 — Night research-infra improvements (reason_class + review index)

> **Status:** `complete` — both 💡-seeded improvements landed on PR #121:
> (1) every selection-gate result now carries an additive machine-readable
> `reason_class` (8 classes, one per existing code path; `UNGRADEABLE_*`
> subset = infrastructure alarm for round-7+ rollups; zero decision or
> reason-string changes), and (2) the paper-lane grading job maintains an
> idempotent per-ISO-week review index `experiments/paper/reviews.md`
> making the protocol §7 `m weeks reviewed, of which f FLAT` denominator
> machine-readable — as a SEPARATE non-ledger artifact because the binding
> protocol does not clearly permit supplementary machine-appended ledger
> records (reading recorded below). 646 → 668 tests, twice-run dry-run
> byte-identical. Claim deleted in this same commit.

📊 Model: fable-5 · night-research-infra lane (night worker session) · start 2026-07-14T01:35Z

⚑ Self-initiated: coordinator-sanctioned night slice — executes the two most
recent cards' 💡 seeds as one PR of two small, tested, backward-compatible
infrastructure improvements:

1. **Machine-readable `reason_class` on selection-gate results**
   (`src/trading_lab/selection_gate.py`) — the 💡 of
   `.sessions/2026-07-13-selection-fair-gate.md`: additive taxonomy derived
   from the gate's existing failure paths so round-7 rollups can count
   ungradeable subtypes as infrastructure alarms rather than strategy
   evidence. No pass/fail decision logic changes.
2. **Idempotent per-pass review record for the paper-lane grader**
   (`scripts/grade_paper.py` / `src/trading_lab/paper.py`) — the 💡 of
   `.sessions/2026-07-13-night-grading-preverify.md`: make the protocol §7
   `m weeks reviewed, of which f FLAT` denominator machine-readable.
   BEAT/MISS/FLAT grammar, the t-stat ban and ledger semantics stay
   untouched (docs/paper-lane-protocol.md §7 is binding pre-registration).

💡 **Session idea (deduped against recent cards — distinct from the
selection-fair-gate card's `reason_class` taxonomy and the
night-grading-preverify card's review record, both of which THIS session
executed; from the kill-sig-review card's verdict-grammar unification; and
from the r4-regime card's cardinality-matched control arm):** the new
review index can enumerate only passes that RAN — a silently missed Friday
fire (dead trigger, archived seat) still leaves no trace anywhere until a
human notices, and protocol §6 says a missed pass "delays grading" with
nobody paged. Add a grading-pass **liveness watchdog**: a tiny read-only
check that compares today's ISO week against the newest `### review-*`
record in `experiments/paper/reviews.md` and, once the lane's first record
exists, flags a gap of ≥ 2 weeks as an infrastructure alarm on the
heartbeat (never a verdict — the index is informational by design).
Anchors: `_iso_week` + `parse_records` in `src/trading_lab/paper.py`
(both reusable as-is); wire-in candidate: an advisory checker line in the
kit gate or a `scripts/check_paper_liveness.py` the Friday prompt runs
first; test target: a stale-index fixture in `tests/test_paper.py`.

## Why this session exists

Both improvements were seeded as deduped 💡 ideas on completed cards and are
pure research-infrastructure: they change no verdict, no grading semantics,
and no protocol rule. Landing them before round 7 / the 2026-07-17 grading
fire makes the next rollup and the first weekly pass more auditable.

## Work log

- 2026-07-14T01:35Z — hard-synced to origin/main `3b7a52e`; read at HEAD:
  control/inbox.md, control/status.md, docs/current-state.md,
  CONSTITUTION.md, docs/CAPABILITIES.md, docs/selection-fair-gate.md,
  docs/paper-lane-protocol.md (§7 closely), both originating 💡 cards,
  src/trading_lab/selection_gate.py, src/trading_lab/paper.py,
  scripts/grade_paper.py, tests/test_selection_gate.py, tests/test_paper.py.
  Claim collision check: `control/claims/` at HEAD holds only its README —
  no overlap. Baseline verify: `python3 -m pytest -q` → 646 passed;
  `python3 bootstrap.py check --strict` → all checks passed. This born-red
  card + claim are the FIRST commit; PR opens READY immediately after.
- 2026-07-14T01:36Z — first commit `807823d` pushed; PR #121 opened READY
  (never draft, never self-merged; the auto-merge enabler is the landing
  path).
- 2026-07-14T01:41Z — improvement 1 commit `18feaa7`: `reason_class` on
  every gate result. Taxonomy derived strictly from the existing outcome
  paths in `run_selection_gate` — `PASS`, `FAIL_UNDERPERFORM` (fixed > 0
  but ≤ bench, ties included), `FAIL_NONPOSITIVE` (fixed ≤ 0; takes
  precedence when both conjuncts fail), `UNGRADEABLE_MISSING_WINDOWS`,
  `UNGRADEABLE_DRIFT` (window does not fit loaded data — the code path
  whose verbatim reason already says "missing data / cache drift"),
  `UNGRADEABLE_NONCONTIGUOUS`, `UNGRADEABLE_FIDELITY`, `UNGRADEABLE_NAN` —
  no class without a code path, no code path without a class. Additive
  only: `gate`, `reason` strings, all fields, `gate_decision`, `apply_gate`
  byte-equivalent in behavior. Doc section + call-sketch note added to
  `docs/selection-fair-gate.md` (Status badge untouched at line 3, inside
  the docs-gate's first-12-lines window). 12 new tests (`TestReasonClass`)
  cover every class, the precedence rule, taxonomy closure, gate↔class
  consistency, and legacy-schema superset.
- 2026-07-14T01:44Z — improvement 2 commit `c3b8be6`: per-pass review
  index. **§7 permission reading (the decision this slice turned on):**
  protocol §5 fixes the ledger's row grammar as trade-action records
  ("one row per action (ENTRY or EXIT)"), §6 authorizes only "appends the
  grades to the ledger", and §7's FLAT "is recorded" names no home — that
  is NOT clear permission for machine-appended supplementary records
  inside the protocol-governed ledger, so per the assignment rule the
  record lives in a SEPARATE non-ledger artifact:
  `experiments/paper/reviews.md` (badge `informational`), documented
  in-file as informational, not graded evidence. `grade_ledger` renders
  one deterministic record per ISO review week (FLAT exactly per §7: no
  position held and no window graded that week — decided from the
  ledger's own `graded_at_utc` stamps, so a same-week second pass after a
  grading pass stays REVIEWED) and updates the week's record in place,
  never duplicating; unchanged state = byte-identical no-op. `main()`
  additionally prints the §7 aggregate line with explicit denominators.
  A malformed/ungradeable pass (`LedgerFormatError`) records nothing — a
  failed pass never counts as a reviewed week. `ledger.md` byte-untouched;
  BEAT/MISS/FLAT grammar and t-stat ban untouched; the holdout-discipline
  source scans still pass (no `unlock`, only the paper rail). 10 new tests
  (`TestReviewIndex`) including same-week idempotency, the 09:00Z/09:05Z
  duplicate-fire shape, in-place same-week update, malformed-pass
  no-record, and committed-header parity.
- 2026-07-14T01:45Z — dry-run per the PR #115 FLAT pattern: throwaway
  `cp -r` tree copy under the session scratchpad,
  `python3 scripts/grade_paper.py` run TWICE — pass 1 exit 0, §7 FLAT
  shape preserved, `review-2026-W29 — FLAT` record created; pass 2 exit 0,
  reviews.md sha256 byte-identical, "unchanged" reported. Throwaway
  removed; real tree clean. Full suite: **668 passed** (646 baseline + 22
  new, zero failures); `bootstrap.py check --strict` red only on this
  card's designed born-red hold pre-flip. Close-out commit: heartbeat
  line appended, card flipped `complete`, claim deleted.

## Previous-session review

⟲ Most recent landing before this branch cut: **PR #119** (`3b7a52e`,
"Night close 2026-07-14: ORDER 014 close-out heartbeat + outbox report" —
the exact commit this branch is cut from). Control-only fast-lane traffic,
correctly shipped without a session card. Verified against the tree: its
re-stamped `control/status.md` claims match git history field-for-field —
#116 plan `c0e6459`, #118 run `0d12515`, #115 items 4+5 `d6e3cf9`, all
present on main exactly as stated; its claim
file (`night-close-2026-07-14`) was added and deleted within the same PR,
leaving `control/claims/` clean at HEAD — the whiteboard discipline
working as designed. The two most recent CARDS
(`2026-07-13-selection-fair-gate.md`, `2026-07-13-night-grading-preverify.md`,
both `complete`) each carried exactly one concrete, anchored 💡 — those
anchors (`_fail()` call sites; the never-persisted `flat_review` flag)
were accurate and made this session cheap to start, which is the card
system paying rent. One honest gap inherited and closed here: the
preverify card proved the FLAT pass writes nothing, but nothing in-repo
said WHERE a review denominator should live — this session's §7
permission reading records that decision durably. No defect found in
either session's work.

## Close-out

**Done:** on branch `claude/night-research-infra` (PR #121), commits
`807823d` (born-red card + claim) → `18feaa7` (reason_class) → `c3b8be6`
(review index) → this close-out —

1. `src/trading_lab/selection_gate.py`: additive `reason_class` on every
   gate result (constants + `REASON_CLASSES` / `UNGRADEABLE_CLASSES`
   frozensets for rollups); `docs/selection-fair-gate.md` § reason_class
   table; 12 tests.
2. `src/trading_lab/paper.py` + `experiments/paper/reviews.md`: the
   idempotent per-ISO-week review index (separate informational artifact,
   §7 reading above); `main()` §7 aggregate line; 10 tests.
3. Heartbeat: one `night_2026-07-14_research_infra:` line appended to
   `control/status.md`; inbox/outbox untouched.

**Verify:** `python3 -m pytest -q` → **668 passed** (baseline 646 + 22
new, zero failures). `python3 bootstrap.py check --strict` → green with
this card complete (pre-flip its only red was the designed born-red
hold). Integrity at close: diff vs main touches ONLY the two source
modules, their two test files, `docs/selection-fair-gate.md`, the new
`experiments/paper/reviews.md` (header-only — no pass has officially
run), one appended status line, this card, and the claim lifecycle.
`experiments/paper/ledger.md` and every other `experiments/**` file
byte-untouched; holdout never read (it is SPENT), `unlock_holdout` never
typed into lane code; no broker/order/exchange-write code; no triggers
created/modified; no gate decision or protocol semantic changed; NO merge
action by this session — the auto-merge enabler is PR #121's landing path.

**Next (guard recipe):** this card's 💡 — the grading-pass liveness
watchdog (anchors: `_iso_week` + `parse_records` in
`src/trading_lab/paper.py`; stale-index fixture in `tests/test_paper.py`).
For round 7: rollup code should consume
`selection_gate.UNGRADEABLE_CLASSES` and page on any nonzero share
(docs/selection-fair-gate.md § reason_class states the rule).

Session end: badge flipped `complete` in this final content commit
before push.
