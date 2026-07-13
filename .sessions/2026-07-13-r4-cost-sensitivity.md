# 2026-07-13 — R4-B: execution-cost sensitivity re-grade of round-3 KEEPs

> **Status:** `in-progress`

📊 Model: fable-5 · trading-research (worker session) · start 2026-07-13T09:48:37Z

💡 **Session idea:** (placeholder — filled at close-out with a genuine
observation from the work, not a pre-written one.)

## Why this session exists

Round 4 slice R4-B (`docs/research-round-4-plan.md` @ main, pre-registered
and merged before this session started): the 58 round-3 KEEP-dev lanes
(the KEEP universe re-graded by R4-A, PR #100,
`experiments/sweeps/r4-killsig-regrade/summary.json`) were graded only at
baseline costs (5 bps slippage + 1 bp commission per side). KEEPs cluster
on weak benchmarks with small margins — exactly what realistic execution
costs erase. R4-B re-grades every KEEP-dev lane at two stressed cost tiers,
**2×** baseline (10 bps + 2 bp) and **4×** baseline (20 bps + 4 bp), on the
same rail, same walk-forward windows, same chosen variants (NO re-search:
stressing costs must not become a second selection pass — pre-registered).
Kill criterion per lane per tier: KILL iff stitched OOS Sharpe ≤ same-window
same-cost B&H Sharpe or ≤ 0. A lane keeps dev-candidate status only if it
survives the 2× tier; 4× is a robustness gradient. Pre-registered
hypothesis: most or all KEEPs flip to KILL. Owner mandate: ORDER 012
generative rung; bar unchanged; holdout SPENT; promotion CLOSED.

## Work log

- 2026-07-13T09:48Z — branch `claude/r4-cost-sensitivity` cut from
  origin/main HEAD (`08ddbd4`, the merged R4-A slice). Born-red FIRST
  commit: this card `in-progress` + claim
  `control/claims/2026-07-13-r4-cost-sensitivity.md`, pushed before any
  implementation; PR opened READY immediately after.

## Previous-session review

(to be filled at close-out — review of `.sessions/2026-07-13-r4-killsig.md`)

## Close-out

(to be filled: Done / Verify / Next when the slice lands)
