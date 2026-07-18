# 2026-07-18 — Cross-round meta-analysis of Rounds 1–8

> **Status:** `in-progress`

📊 Model: [[fill:model-line — flip form `- **📊 Model:** <family> · <effort> · <task-class>`]]

## Why this session exists

The research program has run P1 baselines through Round 8: **5,793 registered
configurations, 0 promoted** — no strategy ever cleared the significance bar
(`trading_lab.promotion.min_tstat(K)` ≈ 2.638 at K=12). The negative result
*is* the finding. Two program-wide synthesis docs exist —
[research-program-retrospective.md](../docs/research-program-retrospective.md)
(narrative, Rounds 1–6, at `@3b7a52e`) and
[research-program-dashboard.md](../docs/research-program-dashboard.md)
(scoreboard, P1 → Round 7) — but neither consolidates the four newest slices
(R7-A/B, R7-C, R7-D, R8) that carried the program from 5,415 to 5,793 configs,
and neither foregrounds the **effect-size distribution** across rounds: how far
the strongest dev arm each round sat *below* its bar, and why the best
near-misses still fail selection-fair correction.

This session adds `docs/cross-round-meta-analysis.md`: an honest cross-round
synthesis of Rounds 1–8 that (a) extends the scoreboard to 5,793 / 0 promoted,
(b) foregrounds the effect-size distribution and the handful of best near-misses,
(c) states what the negative result teaches, and (d) states what an owner-gated
future round would need. Every number traces to a committed round JSON or
results doc. RESEARCH-ONLY, in-sample: the holdout is SPENT and untouched,
promotion stays CLOSED, no sweep is re-run — only already-committed data is
aggregated. A small read-only helper (`scripts/aggregate_effect_sizes.py`,
pytest-pinned) mechanizes the R6–R8 effect-size table from the committed
`summary.json` files so its numbers are not hand-transcribed.

## Work log

- branch `claude/cross-round-meta-analysis` cut from origin/main HEAD `32cbb5f`
  (incl. #151 render_round_results.py). Born-red FIRST commit: this card +
  the claim.

💡 **Session idea:** [[fill:idea — resolve at flip]]

## Previous-session review

[[fill:previous-session review — resolve at flip]]

## Close-out

[[fill:close-out — commit list, verify lines, integrity statement, next — resolve at flip]]
