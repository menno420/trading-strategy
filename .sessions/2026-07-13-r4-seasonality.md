# 2026-07-13 — R4-F: day-of-week seasonality sweep

> **Status:** `in-progress`

📊 Model: fable-5 · trading-research (worker session) · start 2026-07-13T10:04:04Z

💡 **Session idea:** (placeholder — filled at close-out with a genuine
observation from the work, not a pre-written one.)

## Why this session exists

Round 4 slice R4-F (`docs/research-round-4-plan.md` @ main, pre-registered
and merged before this session started): Round 3 varied families,
parameters, tickers, and timeframes but never *calendar* structure.
Day-of-week is the cheapest calendar hypothesis and a classic
multiple-testing trap — which makes it the right stress test of the
round's correction discipline. This slice sweeps a long-on-one-weekday
rule across the **15 committed daily tickers**; K counts ALL day×ticker
combos tested: 5 weekdays × 15 tickers = **K = 75**, so the bar RISES to
`min_tstat(75)` ≈ **3.21** (vs 2.64 at K=12) — the bar is never lowered,
K is never counted down. Pre-registered hypothesis: **null after
correction** — no day×ticker combo clears the K=75 bar. Pre-registered
rule: KEEP (dev-candidate only) iff a combo clears BOTH the Round-2
benchmark rule and t ≥ 3.21 at K=75; everything else KILL (or KILL-SIG at
t ≤ −3.21, R4-A having landed in PR #100). Owner mandate: ORDER 012
generative rung; holdout SPENT; promotion CLOSED.

## Work log

- 2026-07-13T10:04Z — branch `claude/r4-seasonality` cut from origin/main
  HEAD (`01a75a3`, the merged R4-B slice). Collision check:
  `control/claims/` at HEAD holds morning-tally + night-report +
  order-night-run — no overlap. Born-red FIRST commit: this card
  `in-progress` + claim `control/claims/2026-07-13-r4-seasonality.md`,
  pushed before any implementation; PR opened READY immediately after.

## Previous-session review

(to be filled at close-out — review of
`.sessions/2026-07-13-r4-cost-sensitivity.md`)

## Close-out

(to be filled: Done / Verify / Next when the slice lands)
