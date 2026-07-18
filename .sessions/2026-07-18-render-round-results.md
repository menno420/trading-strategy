# 2026-07-18 — render_round_results.py: mechanize results-doc tables

> **Status:** `in-progress`

📊 Model: opus-4.8 · render-round-results lane (overnight worker, owner GO
2026-07-18T13:47Z / R7-run-card 💡 + menu #13-adjacent) · start
2026-07-18T16:25:32Z

## Why this session exists

Every run slice this session (R7-A/B, R7-C, R7-D, R8) hand-transcribed a
per-lane results table from the committed lane JSONs into
`docs/research-round-<N>-results.md` — the searched/bench/fixed/gap/t row, the
counts sub-tables, the reason_class rollup, the UNGRADEABLE infra-alarm line,
and the burden tally. Hand-transcription is a copy risk that GROWS every round
(more lanes, more families, more numbers to fat-finger), and this program has
repeatedly flagged transcription-risk as its recurring failure mode. This
session adds `scripts/render_round_results.py`: a pure read-only generator that
emits the standardized results-table markdown block for a single-name research
slice directly from its committed `experiments/sweeps/<slice>/` JSONs, so
future round results tables are mechanical + diffable instead of typed by hand.
NO strategy/backtest/verdict changes, NO sweep re-run — it only re-formats
numbers that already exist in committed artifacts.

## Work log

- branch `claude/render-round-results` cut from origin/main HEAD (incl. the R8
  run, #150). Born-red FIRST commit: this card.

💡 **Session idea:** the slice-summary row's human label —
`R8 \`r8-hourly\` (drawdown_reversion + high_proximity × 8 hourly)` — is the
one field the generator still has to SYNTHESIZE (round prefix parsed from the
slice name, families joined, ticker-count × timeframe) rather than read
verbatim from a JSON. A tiny `"slice_label"` string committed into each
`summary.json` at run time (the runner already knows all four facts) would let
the generator read the label instead of reconstructing it, removing the last
non-mechanical guess from the results block. Anchor: the label-synthesis helper
in `render_round_results.py`; test target: assert the rendered slice row equals
`summary["slice_label"]` once the runner emits it. (Distinct from the
round-8-run card's shared-hourly-runner idea — that dedupes the `run_*` runner
body; this adds one authored string to the summary schema.)

## Previous-session review

[[fill:]]

## Close-out

[[fill:]]
