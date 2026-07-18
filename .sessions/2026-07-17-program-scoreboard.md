# 2026-07-17 — Program research scoreboard

> **Status:** `in-progress`

📊 Model: opus-4.8 · program-scoreboard lane (overnight worker, owner order 2026-07-17T22:39Z / menu proposal 13) · start 2026-07-17T23:59Z

💡 **Session idea:** building the per-round table needed two hand-aggregations
that a script should own: Round 4's row is the *sum* of the R4-C/D/E/F
new-search slices (5 KEEP / 60 KILL / 30 KILL-SIG, excluding the A/B
re-grades of Round 3), and Round 3's row uses the full committed surface
(3,468 configs / 302 summaries / 58-238-4) rather than the doc's own core
headline (1,752 / 41 / 125). Both were transcribed by hand from the results
docs + retrospective — a drift surface that grows each round. Promote a
deterministic `scripts/render_program_dashboard.py` that regenerates this
scoreboard's numeric cells directly from each slice's committed
`experiments/sweeps/<SLICE>/summary.json` + the cumulative chain in
`sweeps.py`, with a golden test that it reproduces the committed table
cells — so the canonical scoreboard becomes generated-and-diffable instead
of hand-built (distinct from the round-7 card's per-lane-table generator:
that dedupes one results doc; this dedupes the cross-round rollup).

## Why this session exists

Menu proposal #13 (from the overnight menu): stand up **one canonical,
honest program scoreboard** instead of stitching the picture together from
seven separate results docs every time someone asks "what did the whole
program find?". The answer is uncomfortable and worth stating once, cleanly:
across P1 baselines through Round 7 the program registered **5,415 configs
and promoted 0** — no strategy ever cleared the significance bar. This
session builds `docs/research-program-dashboard.md`: a per-round table
(configs added + cumulative, KEEP-dev / KILL / KILL-SIG, best informational
t vs the 2.638 K=12 bar, promoted) with every number carried from a cited
committed results/retrospective doc — no fabricated numbers. Docs-only
research lane: no code, no strategy/backtest changes, no verdict changed,
holdout untouched (SPENT), promotion CLOSED. Owner-live handoff at
wind-down: this is a build-then-review slice — implement, open the PR READY,
and leave the card `in-progress` for the owner's numbers review before flip.

## Work log

- branch `claude/program-scoreboard` cut from origin/main HEAD `82ef4cc`
  (Round 7 run / PR #141 — program cumulative 5,415). Born-red FIRST
  commit: this card.

## Previous-session review

`[[fill: at close-out]]`

## Close-out

`[[fill: at close-out]]`
