# 2026-07-13 — Round 5 research: deepen top KEEP-dev candidates

> **Status:** `complete` — Round 5 landed end-to-end on one branch
> (PR #110): pre-registration first (`docs/research-round-5-plan.md`,
> badge `binding`, merged-before-outcomes discipline via the plan commit
> `b6b8708` preceding every run commit), then all four registered slices
> against the FROZEN top-5 KEEP-dev lanes, then this close-out. Honest
> round headline: **4 KEEP-dev / 1 KILL / 0 KILL-SIG / 0 promoted / 1
> owner-gated escalate proposal.** R5-A (`bdd723b`): no knife edges —
> all 14 pre-declared ±1-step neighbors beat B&H, 5/5 KEEP. R5-B
> (`74af0ce`): the round's one demotion — META hourly
> `stochastic_reversion` KILLed as single-window luck (worst-case
> leave-one-out delta −0.164; the whole edge lived in split 0). R5-C
> (`7b75e40`): bootstrap agrees with the point estimates, 5/5 KEEP, and
> BTC-USD `bollinger_breakout` trips the registered escalate branch at
> `P(delta ≤ 0) = 0.042` → owner-gated proposal
> `docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md` (verdict
> unchanged, nothing scheduled or run). R5-D (`3d96440`): every top
> variant beats B&H selection-free, but `selection_gap > 0` on only 3/5.
> Rollup + results doc in `f612083`; burden 4345 → 4359 (14 R5-A
> neighbors, the round's only new configs); promotion CLOSED, holdout
> SPENT, nothing here is a finding. This card was born red and flips
> `complete` in this final commit; the claim file is deleted in this
> same commit.

📊 Model: fable-5 · trading-research (worker session, phases 1–3 of 3) · start 2026-07-13T14:05Z

💡 **Session idea (deduped against .sessions/*.md — distinct from the
r4-regime card's cardinality-matched CONTROL-ARM idea, which is about
conditioning-slice fairness):** R5-D measured `selection_gap` on the
program's five BEST lanes and got a negative sign on two of them (SLV
−0.313, META hourly −0.396 — the searched walk-forward LOST to its own
story-pinned fixed config) with only BTC-USD visibly gaining (+0.185).
Make the selection-fair fixed-config replay a STANDING GATE of future
KEEP-dev grading, not a once-per-round slice: every sweep runner that
walk-forward-searches a grid also replays its top full-period variant
selection-free on the identical test windows (the 1e-8 fidelity-guarded
replay core already exists in all four R5 runners — anchor:
`scripts/run_r5d_selection_fair.py`) and writes `selection_gap` into the
lane JSON at grade time, so a KEEP whose stitched edge exists only under
re-selection is flagged the day it is minted instead of rounds later.
Test target: a gap-sign fixture in `tests/test_sweeps.py` (searched arm
degraded on a synthetic series → gap must come out negative).

## Why this session exists

Round 4 closed (PRs #100–#105, closing tally in
docs/research-round-4-results.md) with 0 promoted; the cumulative program
surface stands at ~4,345 registered configs / 312 graded lanes,
0 PROMOTED / 64 KEEP-dev / 248 KILL, best t anywhere 1.38 (BTC-USD
`bollinger_breakout`) against the 2.638 bar at K=12. The R4-B cost stress
pruned the machine-readable KEEP surface to 42 dev-candidates surviving
the 2x tier. Round 5 changes direction again: instead of new idea classes,
it DEEPENS the evaluation of the strongest surviving dev-candidates —
robustness, stability, and selection-fairness of the top KEEP-dev lanes —
pre-registered in docs/research-round-5-plan.md BEFORE any run, dev rail
only via `trading_lab.data.load_ohlcv`, holdout SPENT, promotion CLOSED.
Phase 1 of this session wrote and landed the pre-registration only; the
later phases of the same session (same branch, same PR #110) ran the
four registered slices against it and wrote this close-out — the
plan-commit-precedes-run-commits ordering is visible in the branch
history (`b6b8708` < `e662d76` < `bdd723b`).

## Work log

- 2026-07-13T14:05Z — branch `claude/round-5-research` cut from
  origin/main HEAD `3c628e4`. Collision check: `control/claims/` at HEAD
  contains only the two READMEs — no overlap with this scope. Born-red
  FIRST commit: this card (`in-progress`) + claim
  `control/claims/2026-07-13-round-5-research.md`, per the
  claim-before-build convention.
- 2026-07-13T14:10Z — second commit: `docs/research-round-5-plan.md`
  (badge `binding` within the first 12 lines, R4 precedent) +
  reachability link in `docs/current-state.md` under the Round-4 mention,
  same linking convention as prior round plans. Plan pre-registers four
  experiments (R5-A parameter-neighborhood stability, R5-B
  time-split/regime stability, R5-C moving-block bootstrap of the t-stat,
  R5-D selection-fair fixed-config replay) deepening the top KEEP-dev
  candidates. All facts cited in the plan were re-derived from committed
  artifacts this session (r4-cost-sensitivity summary.json, r3 per-lane
  JSONs), not recalled.
- 2026-07-13T14:19Z — `9fcc396`: one-line `control/status.md` fix
  (`pointer_venture_retro` path `docs/retros/` → `docs/retro/`),
  coordinator-dictated verbatim — the finding PR #109 recorded but
  correctly declined to guess at from repo layout alone.
- 2026-07-13T14:25Z — R5-A pre-declaration commit `e662d76`
  (grids-before-run rail): `R5A_TARGET_LANES` / `r5a_neighbors` in
  `trading_lab.sweeps` — 14 clipped ±1-grid-step neighbors of the five
  frozen top variants, every one a point of the source lane's committed
  Round-3 grid (pinned by tests; no new parameter territory) — plus the
  four runner scripts, all logic before any outcome existed.
- 2026-07-13T14:31Z — runs, one commit per slice, in plan order:
  - `bdd723b` R5-A: **5 KEEP / 0 KILL / 0 KILL-SIG** — all 14 neighbors
    beat same-window B&H (100% vs the ≥50% rule); no knife edges; best
    neighbor t 1.66 vs the unchanged 2.638 bar. LEDGERED (R4-C
    genuinely-new-run precedent): 14 probe rows, `variants_tried=1`,
    index rebuilt. Fidelity guard: all 5 baselines within 1e-8.
  - `74af0ce` R5-B: **4 KEEP / 1 KILL** — META hourly
    `stochastic_reversion` demoted; its per-split deltas (+4.05, +0.34,
    −0.49, −0.97, +1.55) put the whole stitched edge in split 0, and
    the worst-case leave-one-out delta is −0.164. Survivors' worst-case
    LOO deltas +0.091 to +0.326. Report-only (R4-B precedent).
  - `7b75e40` R5-C: **5 KEEP / 0 KILL**, seed 20260713, 1,000 paired
    moving-block resamples/lane; `P(delta ≤ 0)` 0.042–0.247, all far
    below the 0.60 KILL bar; BTC-USD (0.042 ≤ 0.10) trips the
    registered ESCALATE branch → owner-gated proposal doc committed,
    verdict unchanged, nothing scheduled or run.
  - `3d96440` R5-D: **5 KEEP / 0 KILL** — every committed top variant
    beats B&H selection-free, but `selection_gap > 0` on only 3/5
    (SLV −0.313, META hourly −0.396): re-selection is closer to noise
    than signal on this surface.
- 2026-07-13T14:37Z — `f612083`: pre-registered ALL-FOUR aggregation
  applied (`scripts/run_r5_rollup.py` →
  `experiments/sweeps/r5-rollup/summary.json`) + full honest write-up
  `docs/research-round-5-results.md` + reachability link. Round verdict:
  **4 KEEP-dev / 1 KILL of the top 5, 0 promoted**. Two mechanized
  plan ambiguities recorded as interpretation-not-method deviations in
  the results doc (R5-A worst-neighbor KILL-SIG t; R5-B best split =
  argmin LOO delta); neither was load-bearing.
- 2026-07-13T14:44Z — close-out phase: this card filled in, badge
  flipped `complete`, claim file deleted — one final commit. Verify
  reran green (pytest 583; `bootstrap.py check --strict` red only on
  the designed born-red hold pre-flip). No merge action by this
  session; the already-armed auto-merge enabler is the landing path.

## Previous-session review

⟲ Most recent prior card (`.sessions/2026-07-13-r4-regime.md`, Status
`complete`, PR #104) landed the R4-D regime-conditional null clean; its
control-arm-discipline observation ("searched arm vs near-fixed control
mixes conditioning-hurts with bigger-grids-overfit") is the direct seed
of this round's R5-D selection-fair slice, and the round-4 closing
tally's "What round 5 should look at" items 1 (selection-fair controls /
story-pinned configs) and 2 (replay pin) are pre-registered here as R5-D
and inside R5-A/C's replay-fidelity guards. No defect found in its work.

⟲ Close-out addendum — PR #109 (the R4-A KILL-SIG ratification review,
card `.sessions/2026-07-13-kill-sig-review.md`), checked against GitHub
at close: **merged** 2026-07-13T14:03:52Z by `github-actions[bot]` (the
auto-merge-enabler path, as designed), squash commit `3c628e4` — which
is exactly the commit this session's branch was cut from, so its claims
were directly inspectable at branch time. Its payload matches its
promise: 1 file changed (+285, the session card alone), zero code/doc
changes, verdict ACCEPT ratifying the ALREADY-merged R4-A adoption of
`classify_verdict` rather than re-implementing anything — the right
disposition for a proposal that had quietly shipped. Two things it did
well that this round leaned on: (1) it re-verified the R4-A regrade
counts at HEAD instead of trusting card prose (the 4-KILL-SIG tail this
round's slices then never fired — 0 KILL-SIG across all 20 R5 grades is
consistent with that ~1.3% base rate on 5 strong lanes); (2) its
bundled `pointer_venture_retro` finding explicitly DECLINED to guess a
fix from this repo's layout — the coordinator then dictated the exact
path, landed here as `9fcc396`, which is how an out-of-scope finding
should travel. No defect found in its work.

## Close-out

**Done:** on branch `claude/round-5-research` (PR #110), nine commits
`a4a0488` → this one —

1. `docs/research-round-5-plan.md` (badge `binding`, commit `b6b8708`
   BEFORE any outcome): frozen top-5 target set, four registered
   slices with kill/escalate criteria, caps, and the ALL-FOUR
   aggregation rule; linked from `docs/current-state.md`.
2. `control/status.md` one-line coordinator-dictated pointer fix
   (`9fcc396`).
3. Pre-declared R5-A neighbor grids + tests (`e662d76`), then the four
   slices in plan order, one commit each (`bdd723b`, `74af0ce`,
   `7b75e40`, `3d96440`) — 20 lane grades total, every replaying slice
   fidelity-guarded at 1e-8 with 0 SKIPPED lanes.
4. Round verdict (`f612083`, rollup + results doc): **4 KEEP-dev /
   1 KILL (META hourly `stochastic_reversion`, demoted by R5-B) /
   0 KILL-SIG / 0 promoted**; 1 owner-gated escalate proposal
   (`docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md`,
   BTC-USD `P(delta ≤ 0) = 0.042`) that changes no verdict, schedules
   nothing, and the owner may freely ignore.
5. Burden: 14 new registered configs (R5-A neighbors only), program
   cumulative 4345 → 4359; no K counted down, no bar lowered
   (informational t graded at each lane's committed K=12 throughout);
   runtime caps never hit (0.3–1.4 s vs 300–600 s).
6. Artifacts: `experiments/sweeps/r5-{neighborhood,split-stability,
   bootstrap,selection-fair,rollup}/` (21 JSONs), 14 ledger rows +
   rebuilt `experiments/index.jsonl` (R5-A only; R5-B/C/D report-only
   per the R4-B precedent), `docs/research-round-5-results.md` with
   nulls and the demotion first-class.
7. This card (born-red first commit `a4a0488` → flipped `complete`
   last) — claim file `control/claims/2026-07-13-round-5-research.md`
   deleted in this same commit.

**Verify:** `python3 -m pytest -q` → 583 passed (this branch adds 11
tests, all R5-A pre-declaration pins in `tests/test_sweeps.py`; no
existing test touched). `python3 bootstrap.py check --strict` → green
with this card complete (pre-flip its only red was the designed
born-red hold). Integrity at close: diff
vs main touches only the plan/results/proposal docs,
`docs/current-state.md` links, `src/trading_lab/sweeps.py` +
`tests/test_sweeps.py` (R5-A pre-declaration), the four
`scripts/run_r5*.py` runners + `scripts/run_r5_rollup.py`,
`experiments/sweeps/r5-*/`, 14 ledger rows + rebuilt index, the
one-line `control/status.md` fix, `.substrate/guard-fires.jsonl`,
`.sessions/`, and the claim deletion. Every `experiments/sweeps/r3-*/`
and `r4-*/` file byte-untouched; holdout (SPENT) untouched,
`data/p5holdout/` never read, `unlock_holdout` never passed;
`experiments/paper/**` byte-untouched; `control/inbox.md` and
`control/outbox.md` byte-untouched; no triggers created or modified; no
broker/order/exchange code; NO merge action taken by this session (the
auto-merge-enabler armed squash auto-merge on PR #110 — left alone).

**Next (guard recipe):** none owed for correctness. Follow-ups
unblocked, in rough order of value: (1) this card's 💡 —
`selection_gap` as a standing per-lane grade column (anchors and test
target named above); (2) the R5-C escalate proposal sits OWNER-GATED —
no repo session should schedule or run it; (3) the demoted META hourly
lane should be excluded from any future top-K freeze (the rollup JSON
is the machine-readable source); (4) the standing replay-core
extraction remains open — all four R5 runners re-copied the
fidelity-guarded replay block, the eighth-plus copy of that pattern.
Nothing reopens promotion; any OOS claim stays OWNER-GATED on
post-2026 data.

Session end: badge flipped `complete` in this final content commit
before push.
