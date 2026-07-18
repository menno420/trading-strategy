# 2026-07-18 — Cross-round meta-analysis of Rounds 1–8

> **Status:** `complete` — landed `docs/cross-round-meta-analysis.md`, an honest
> cross-round synthesis (P1 → Round 8, **5,793 registered configs / 0
> promoted** — the negative result IS the finding), plus a pytest-pinned
> read-only effect-size aggregator. RESEARCH-ONLY / in-sample: no sweep re-run,
> holdout SPENT and untouched, promotion CLOSED.

- **📊 Model:** Opus family · medium · research

## Why this session exists

The research program has run P1 baselines through Round 8: **5,793 registered
configurations, 0 promoted** — no strategy ever cleared the significance bar
(`trading_lab.promotion.min_tstat(K)` ≈ 2.638 at K=12). The negative result
*is* the finding. Two program-wide synthesis docs existed —
[research-program-retrospective.md](../docs/research-program-retrospective.md)
(narrative, Rounds 1–6) and
[research-program-dashboard.md](../docs/research-program-dashboard.md)
(scoreboard, P1 → Round 7) — but neither consolidated the four newest slices
(R7-A/B, R7-C, R7-D, R8) that carried the program from 5,415 to 5,793 configs,
and neither foregrounded the **effect-size distribution**: how far the strongest
dev arm each round sat *below* its bar, and why the best near-misses still fail
selection-fair correction.

This session added `docs/cross-round-meta-analysis.md`: an honest cross-round
synthesis of Rounds 1–8 that (a) extends the scoreboard to 5,793 / 0 promoted,
(b) foregrounds the effect-size distribution and the best near-misses, (c)
states what the negative result teaches, and (d) states what an owner-gated
future round would need. Every number traces to a committed round JSON or
results doc. RESEARCH-ONLY, in-sample: the holdout is SPENT and untouched,
promotion stays CLOSED, no sweep is re-run. A read-only helper
(`scripts/aggregate_effect_sizes.py`, pytest-pinned) mechanizes the R6–R8
effect-size table from the committed `summary.json` files so its numbers are
not hand-transcribed.

## Work log

- branch `claude/cross-round-meta-analysis` cut from origin/main HEAD `32cbb5f`
  (incl. #151 render_round_results.py). Born-red FIRST commit: this card +
  the claim.
- built `scripts/aggregate_effect_sizes.py` (read-only aggregator over
  committed `summary.json`) + `tests/test_aggregate_effect_sizes.py` (9 tests);
  authored `docs/cross-round-meta-analysis.md`; the doc's R6–R8 table is the
  aggregator's verbatim output (diff-checked); cross-linked the new doc from the
  dashboard + retrospective (read-path reachability).
- heartbeat: neutral in-flight record in `docs/current-state.md`.

💡 **Session idea:** the effect-size aggregator currently spans only the
machine-readable era (R6–R8 — slices with a uniform per-lane `tstat` in
`summary.json`). Two earlier committed artifacts already expose lane t-stats in
a nearly-compatible shape — `r4-killsig-regrade/summary.json` (302 re-graded
lanes, best t 1.378) and `r5-selection-fair/summary.json` (5 fixed-config
replay t's) — so a small per-schema adapter behind `_is_modern_run_slice` could
extend the mechanized effect-size view back toward Round 3 without hand-typing
those best-t figures into the meta-analysis. Anchor: `_is_modern_run_slice` /
`aggregate` in `scripts/aggregate_effect_sizes.py`; test target: assert the
extended selection includes `r4-killsig-regrade` and reproduces its best t
1.378 (labeled as a *re-grade* t, distinct from a searched-arm t, to avoid
conflating the two quantities). Keeps the honest caveat that P1/P2 have no
Bonferroni t by design, so they stay cited-not-computed.

## Previous-session review

⟲ PR #151 (`render-round-results`, merged) — landed
`scripts/render_round_results.py`, a read-only generator that emits a round's
results-table block from its committed slice JSONs, retiring the per-round
hand-transcription risk. My `aggregate_effect_sizes.py` is its sibling: same
read-only-over-`summary.json` posture, but aggregating the per-slice best-t
*across* rounds for the effect-size view rather than rendering one round's
table, and I reused its "reproduces the numbers, not a brittle byte-golden"
test stance. One inherited limitation confirmed: both tools skip the portfolio
lane shape (`r7d-xsec-drawdown` has no per-lane `tstat`/`selection_gate`
block), so R7-D's best-t is cited from its results doc, not mechanized — the
same documented TBD #151 flagged. No correctness defect found in #151.

## Close-out

**Done** (4 commits on `claude/cross-round-meta-analysis`):
- `64c1d22` — born-red FIRST commit: this session card (`in-progress` hold) +
  `control/claims/cross-round-meta-analysis.md`.
- `747e082` — `docs/cross-round-meta-analysis.md` (cross-round synthesis, P1 →
  Round 8) + `scripts/aggregate_effect_sizes.py` +
  `tests/test_aggregate_effect_sizes.py` (9 tests) + dashboard/retrospective
  cross-links (read-path reachability).
- `3f067e9` — heartbeat: neutral in-flight record in `docs/current-state.md`.
- (this commit) — close-out flip: badge `in-progress` → `complete`, Model line,
  💡 idea, previous-session review, all `[[fill:]]` resolved.

**Verify:**
- `python3 -m pytest -q` → **765 passed** (756 prior + 9 new aggregator tests).
- `python3 bootstrap.py check --strict` → EXIT 0 once this flip lands (the
  born-red in-progress HOLD was the only red; advisories only: seat-digest +
  pre-existing model-line payload nits on older cards).
- The doc's R6–R8 effect-size table is `aggregate_effect_sizes.py`'s verbatim
  stdout (diff-checked byte-for-byte); the aggregator's max searched t across
  R6–R8 is 1.195 (BTC-USD `high_proximity`, Round 7) and the program best t
  anywhere is 1.66 (R5), both far under the 2.638 bar.

**Integrity — RESEARCH-ONLY / in-sample:** the branch diff touches only the new
doc, the aggregator + its test, two docs cross-links, the current-state
heartbeat, the claim, and this card. NO strategy/backtest/verdict change, NO
sweep re-run, the holdout was never read, no fetch, `experiments/paper/**`
untouched, `control/status.md` (retired) untouched, no triggers, no broker code.
Promotion stays CLOSED, holdout stays SPENT. NO manual merge — the landing
workflow merges on green.

**Next:** the 💡 above — extend the effect-size aggregator back toward Round 3
via a per-schema adapter (`r4-killsig-regrade`, `r5-selection-fair`), labeling
re-grade t's distinct from searched-arm t's. Everything touching new data, the
holdout, or a promotion path stays OWNER-GATED (the FROZEN R5-C BTC-USD OOS
proposal is the single pre-registered option).
