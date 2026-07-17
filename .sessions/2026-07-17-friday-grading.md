# 2026-07-17 — Friday in-session paper-lane grading pass (executor of record)

> **Status:** `complete`

Born-red HOLD: this card ships `in-progress` on purpose so the substrate-gate
holds this PR red until the grading pass is fully recorded. It flips to
`complete` in the LAST commit of this session, which releases the gate.

- **📊 Model:** opus-4.8 · medium · review/verify

⚑ Scope (claimed, `control/claims/friday-grading.md`, branch
`claude/friday-grading`): run this week's Friday paper-lane grading pass
in-session. The scheduled grading trigger
(`trig_01BsYsMABu2vfH4d2MzuSLs6`, cron `0 9 * * 5`) is bound to an ARCHIVED
session and will NOT fire; the replacement host-owned `weekly-grading.yml`
workflow is DESIGNED but PARKED (owner per-seat go pending — do NOT install
it). The documented fallback (`control/status.md` → `grading_friday`): any
live session runs `scripts/grade_paper.py` in-session (idempotent, no
persistence). This session is the executor of record for the
2026-07-17 09:00–09:08Z window. Rails: RESEARCH-ONLY, paper data only, no
broker / exchange / live-API surface touched, holdout untouched, no trigger
create/delete/fire, `control/inbox.md` byte-untouched.

## Six-field summary

- **WHAT:** run the Friday 2026-07-17 paper-lane grading pass in-session and
  record it, since the bound scheduled executor is archived and the
  replacement workflow is parked.
- **WHERE:** `control/status.md` (heartbeat + grading-pass record, this seat's
  one writer), `control/claims/friday-grading.md` (claim), and this card. NO
  paper-lane data file is committed — see the "no-op" note below.
- **HOW:** `python3 scripts/grade_paper.py` (no args — the contract), run
  in-session against a hard-synced `origin/main` (`a7017ca`). Idempotent:
  a second run added no further diff.
- **WHY:** the Friday grading window has no live scheduled executor this week;
  the fallback keeps the paper lane's per-week review index honest and
  computable from the repo alone (§7 aggregate denominator).
- **UNBLOCKS:** the 2026-07-17 (ISO week 2026-W29) grading pass is now on
  record; nothing further is owed until the first evaluable window (~early
  August 2026, the 16th paper-lane bar).
- **VERIFY:** `scripts/grade_paper.py` exit 0; `experiments/paper/ledger.md`
  graded evidence UNTOUCHED (paper-0001 WATCH left intact, no verdict
  appended); `experiments/paper/reviews.md` stays byte-identical to its
  header-only template (`git diff origin/main` empty); full `pytest` green
  (668 passed), including `test_committed_index_matches_generated_header`.

## Run facts

- Grading executor path: **in-session `scripts/grade_paper.py`** (the
  documented fallback), NOT the archived cron trigger and NOT the parked
  `weekly-grading.yml` workflow (confirmed ABSENT on `origin/main`).
- Base: `origin/main` HEAD `a7017ca` (hard-sync clean; PR #137 in history).
- Command: `python3 scripts/grade_paper.py` (no args) · run 2026-07-17T09:14:21Z ·
  **exit 0**.
- stdout digest:
  - `paper-0001: WATCH — not gradeable, left untouched`
  - `FLAT — no window closed and no position open this pass (§7)`
  - `this pass: 0 BEAT of 0 newly graded windows; 0 closed windows total in ledger (1 WATCH, 0 open)`
  - `review index: 2026-W29 FLAT — experiments/paper/reviews.md (updated; informational, not graded evidence)`
  - `aggregate (§7): 0 BEAT of 0 closed windows (1 weeks reviewed, of which 1 FLAT)`
- Result: **true NO-OP — nothing paper-lane committed.** `ledger.md` is
  untouched (WATCH intact, no verdict). The script regenerates a W29 FLAT
  record into `experiments/paper/reviews.md` at run time, but that file is
  a **regenerable runtime artifact deliberately kept header-only in git** —
  the invariant `test_committed_index_matches_generated_header`
  (`tests/test_paper.py`) asserts the committed index is byte-identical to
  `paper_mod.REVIEWS_HEADER` ("the committed header-only index is
  byte-identical to what the grader would generate, so the first real pass
  only appends"). So the run's reviews.md append is left UNCOMMITTED and the
  file is restored to its header-only template; committing it would (and
  initially did, at `e6fb4a9`) turn CI's required `pytest` red. The only
  committed changes this session are `control/**` + this card + the
  `.substrate/guard-fires.jsonl` check telemetry.

## Files touched (committed)

- `control/status.md` — heartbeat overwrite + grading-pass record (this seat
  is its one writer)
- `control/claims/friday-grading.md` — claim (this session)
- `.substrate/guard-fires.jsonl` — substrate-check telemetry delta (committed
  per the checker's instruction; do not revert)
- this card

NOT committed by design: `experiments/paper/reviews.md` — the grader appends
a W29 FLAT record to it at run time, but the file is a regenerable runtime
artifact kept header-only in git (see the Run-facts no-op note; enforced by
`test_committed_index_matches_generated_header`). It was restored to its
header-only template after the run. `experiments/paper/ledger.md` — untouched.

## Evidence SHAs

- Base: `a7017ca` (= `origin/main` at boot, hard-sync clean; `git ls-remote
  origin main` = `git rev-parse HEAD`)
- Claim commit: `0ae11a0` (`control/claims/friday-grading.md`)

## Close-out

**Previous-session review:** the most recent complete cards are the
2026-07-16 overnight autonomous cycle (overnight planning menu PR #136, and
the honest overnight heartbeat restamp + ORDER 017 append, PR #137, HEAD
`a7017ca`) and the main-cron-verify CI card (PR #134). PR #137's status
restamp is exactly what flagged this Friday window as executor-less
(`grading_friday`: "no live executor secured this session → fallback: any
live session runs scripts/grade_paper.py in-session") — this session
executes that documented fallback. It adds no strategy code, runs no lane,
spends no holdout, and touches no trigger; it only runs the grading job and
records the pass, so it inherits the standing rails (promotion CLOSED,
holdout SPENT, RESEARCH-ONLY) verbatim.

💡 **Session idea (deduped against prior cards):** the paper lane has a subtle
trap a fresh in-session executor can fall into (this session did, then
corrected): `scripts/grade_paper.py` WRITES a per-week record into
`experiments/paper/reviews.md`, but that file is intentionally kept
header-only in git and the record is a regenerable artifact — committing the
run output turns CI's required `pytest` red via
`test_committed_index_matches_generated_header`. The contract lives only in
that test's docstring, not in the script's own help text or in
`docs/paper-lane-protocol.md` §6. A durable guard recipe: make
`scripts/grade_paper.py` print an explicit "reviews.md is regenerated per
pass — do NOT commit it" line on exit (anchor: `trading_lab.paper.main`
final print), and/or add a `.gitattributes`/pre-commit note; the test target
that pins the invariant is
`tests/test_paper.py::TestReviewIndex::test_committed_index_matches_generated_header`.
Converging the parked `weekly-grading.yml` (once owner-approved) on this same
no-arg job would also keep the human fallback and the workflow on ONE code
path. (Anchors: `trading_lab.paper.main` / `scripts/grade_paper.py`; parked
`weekly-grading.yml`; `control/status.md` → `grading_executor` /
`grading_friday`.)

## Landing discipline

Born-red HOLD by design: the FIRST commit ships this card `in-progress` so
the gate stays red and the PR cannot merge prematurely. The card flips to
`complete` in the LAST commit alongside the final `control/status.md`
heartbeat overwrite — that release is the only thing that lets the auto-merge
enabler carry the PR in. This session does NOT merge its own PR.
