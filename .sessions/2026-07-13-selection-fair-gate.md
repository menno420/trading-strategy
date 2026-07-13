# 2026-07-13 — Selection-fair replay standing gate (round 6+ dev verdicts)

> **Status:** `in-progress` — building the R5-D selection-fair
> fixed-config replay into a STANDING GATE for round-6+ dev-lane KEEP
> verdicts: new module `src/trading_lab/selection_gate.py` (replay
> semantics lifted from `scripts/run_r5d_selection_fair.py`, PR #110),
> binding doc `docs/selection-fair-gate.md`, decision-ledger entry,
> tests. Historical results byte-untouched; no retroactive re-grading.

📊 Model: fable-5 · selection-fair-gate lane (worker session) · start 2026-07-13T15:20Z

⚑ Self-initiated: coordinator-sanctioned slice — executes the round-5
card's 💡 (make R5-D's selection-fair replay a standing gate) with the
coordinator's stricter semantic choices decided up front.

💡 **Session idea (placeholder — finalized before the flip):** track
gate-FAIL reasons as a first-class taxonomy in round rollups so
ungradeable-FAILs (infra rot) never masquerade as demotions (alpha
decay). To be sharpened and deduped against recent cards at close-out.

## Why this session exists

Round 5's R5-D slice (PR #110, `docs/research-round-5-results.md`
§ R5-D) replayed the program's five best KEEP-dev lanes selection-free
and found `selection_gap > 0` on only 3/5 — two lanes' searched
walk-forwards LOST to their own story-pinned fixed config (SLV −0.313,
META hourly −0.396). The round-5 card's 💡 asked for exactly this
follow-up: make the selection-fair fixed-config replay a standing gate
of future KEEP-dev grading, so a KEEP whose stitched edge exists only
under in-window re-selection is flagged the day it is minted instead of
rounds later. This session lands that gate — effective research round 6,
strictly forward-looking — plus its binding doc and tests.

## Work log

- 2026-07-13T15:20Z — branch `claude/selection-fair-gate` cut from
  origin/main HEAD `47d3cbc`. Collision check: `control/claims/` at HEAD
  contains only the READMEs — no overlap. Born-red FIRST commit: this
  card (`in-progress`) + claim `control/claims/selection-fair-gate.md`,
  per the claim-before-build convention.
- [[fill: work log continues as commits land]]

## Previous-session review

⟲ Most recent prior card (`.sessions/2026-07-13-round-5-research.md`,
Status `complete`, PR #110, merged as `47d3cbc` — the exact commit this
branch is cut from, so its claims were directly inspectable at branch
time). Its payload matches its promise: plan-before-outcome ordering is
visible in the branch history (`b6b8708` precedes every run commit), all
four registered slices landed with 1e-8 fidelity guards and 0 SKIPPED
lanes, and the results doc leads with the nulls and the one demotion
(META hourly `stochastic_reversion`, R5-B) rather than burying them. Its
💡 is the direct seed of this session, with concrete anchors
(`scripts/run_r5d_selection_fair.py`, the gap-sign test target) that
made this slice cheap to start. One honest gap it also named itself:
all four R5 runners re-copied the fidelity-guarded replay block instead
of sharing it — this session's module extraction is the first paydown of
that debt. No defect found in its work.

## Close-out

[[fill: close-out written at session end]]
