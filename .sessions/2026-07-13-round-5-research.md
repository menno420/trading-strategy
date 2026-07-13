# 2026-07-13 — Round 5 research: deepen top KEEP-dev candidates

> **Status:** `in-progress`

📊 Model: fable-5 · trading-research (worker session, phase 1 of 3) · start 2026-07-13T14:05Z

💡 **Session idea:** the R4-B frozen-replay machinery (per-split params
replayed on identical positional test windows, 1e-8 fidelity guard)
generalizes beyond cost tiers: the same replay harness can serve
subsampling/bootstrap and split-stability slices at near-zero marginal
code — extract the replay core (`replay_lane(source_file, mutate_fn)`)
once instead of re-copying it into every R5 runner.

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
This session (phase 1) writes and lands the pre-registration only; NO
experiment runs here.

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

## Previous-session review

⟲ Most recent prior card (`.sessions/2026-07-13-r4-regime.md`, Status
`complete`, PR #104) landed the R4-D regime-conditional null clean; its
control-arm-discipline observation ("searched arm vs near-fixed control
mixes conditioning-hurts with bigger-grids-overfit") is the direct seed
of this round's R5-D selection-fair slice, and the round-4 closing
tally's "What round 5 should look at" items 1 (selection-fair controls /
story-pinned configs) and 2 (replay pin) are pre-registered here as R5-D
and inside R5-A/C's replay-fidelity guards. No defect found in its work.

## Close-out

(to be written at session close; this card is born red by design and
flips `complete` only when the phase-1 deliverable — the merged
pre-registration — is done.)
