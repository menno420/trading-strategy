# 2026-07-14 — Night research-infra improvements (reason_class + review index)

> **Status:** `in-progress`

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
