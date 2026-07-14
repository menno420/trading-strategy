# 2026-07-14 — Research-program retrospective: rounds 1–6 synthesis

> **Status:** `complete` — docs-only synthesis delivered:
> `docs/research-program-retrospective.md` (badge `reference`, 451 lines
> after fixes), the honest single-document story of the 6-round /
> 5,055-registered-config program — timeline, funnel, family autopsies,
> survivors, methodology evolution, honest assessment, round-7+ options —
> every number cited to its ledger source at pinned SHA `3b7a52e`. The
> draft was then adversarially spot-checked against the tree: 43
> claim-groups (> 60 individual numbers) re-derived from the cited
> docs/artifacts, 41/43 verified verbatim (t-stats recomputed from
> `NormalDist().inv_cdf`, artifact JSONs re-parsed, `*_total_configs()`
> executed), the 2 misses were citation-anchor imprecision with ZERO
> numeric errors, and both anchors were fixed in a follow-up commit. NO
> sweep, NO fetch, NO holdout read, NO verdict change, NO code change.
> Claim deleted in this close-out commit.

📊 Model: fable-5 · rounds-retrospective lane (coordinator-dispatched, owner's 2026-07-14 night directive) · start 2026-07-14T01:32Z

💡 **Session idea (deduped against recent cards — distinct from the
round-6-plan card's machine-readable BURDEN ledger (`experiments/burden.json`
+ test pin, which drift-proofs the cumulative registered-config count),
the round-6-run card's shared lane-pipeline entry point, the
selection-fair-gate card's `reason_class` taxonomy, and the round-5
card's standing-gate idea):** the adversarial re-check found the
program's per-round OUTCOME tallies drift between docs even where the
burden number is right — `bollinger-mtf-dev-2026-07-12.md` still says
"602 (590+12)" where the reconciled P1 prior makes it 668/680, and
`research-round-5-plan.md` repeats the pre-re-grade "312 / 64" that
round 4 corrected to 302/58. The burden ledger cannot catch this class:
verdict/lane tallies live in `experiments/sweeps/*/summary.json`
(`verdict_counts`) and `experiments/index.jsonl`, not in `sweeps.py`
totals. Fix the class, not the instances: one machine-generated funnel
table (script reads every summary.json `verdict_counts` +
`*_total_configs()` and emits a per-round rows/verdicts/cumulative
table into a single committed doc) that all other docs LINK instead of
hand-copying — hand-copied tallies then become diff-able against one
generated source and the drift class dies. Anchors: `verdict_counts` in
`experiments/sweeps/r6-*/summary.json`; `r6_total_configs` in
`src/trading_lab/sweeps.py`; test target: a reconciliation check that
the generated table's totals equal the artifacts' sums.

## Why this session exists

Coordinator dispatch on the owner's 2026-07-14 night directive: no single
document tells the story of the 6-round, 5,055-registered-config research
program honestly. This session synthesizes rounds 1–6 into
`docs/research-program-retrospective.md` — timeline, funnel, family
autopsies, survivors, methodology evolution, honest assessment, and
round-7+ options, every number cited to the round plan/results docs and
experiments summaries. Docs-only: NO sweeps, NO data fetches, NO holdout
reads, NO verdict changes, NO code modifications. This card is born red
and flips `complete` as the deliberate last step.

## Work log

- 2026-07-14T01:32Z — branch `claude/rounds-retrospective` cut from
  origin/main HEAD `3b7a52e`. Collision check: `control/claims/` at HEAD
  contains only the README — no live claims; no open ORDER in
  `control/inbox.md` covers a retrospective/docs-synthesis scope. Born-red
  FIRST commit: this card + claim
  `control/claims/2026-07-14-rounds-retrospective.md`.
- 2026-07-14T01:49Z — retrospective commit `a8b4e3b`:
  `docs/research-program-retrospective.md` (450 lines, badge `reference`
  within the first 12 lines) + reachability link in
  `docs/current-state.md`. Every claim cited to a pinned-SHA source;
  "NOT investment advice / NO promotion implied" stated in the header
  and in the assessment section; every KEEP qualified dev-only.
- adversarial verify pass (read-only): 43 claim-groups re-derived from
  the cited sources — artifact JSONs parsed, t_min values recomputed,
  `sweeps.py` totalers executed, quotes matched verbatim. Result: 41
  VERIFIED, 2 citation-anchor mismatches (the "208 hourly" figure cited
  to the btc-coverage card that only covers the 239-daily figure; the
  quoted phrase "only ever rises" anchored to r5-results L266–267 when
  the verbatim phrase lives at L10), 0 numeric errors, 0 unverifiable.
  Also confirmed: all 39 cited paths exist, no holdout artifact cited,
  badge + reachability satisfied.
- citation-fix commit `53b190f`: both anchors corrected — added
  `.sessions/2026-07-13-r3-trend-hourly.md@3b7a52e L153` for the 208,
  and re-anchored the quote to "L10, L266–267" (L10 verified to contain
  the verbatim phrase before editing).
- heartbeat commit `2d2b23b`: one `night-2026-07-14:` key:value line
  appended to `control/status.md`; `control/inbox.md`/`outbox.md`
  byte-untouched.
- close-out: this commit (card flips `complete`, claim deleted).

## Previous-session review

⟲ PR #118 (round-6 run, squash `0d12515`, card
`.sessions/2026-07-13-round-6-run.md`) — the most recent completed
session, and the retrospective's single largest evidence supplier, so
its claims were re-verified at source rather than trusted: its headline
(3 KEEP-dev / 47 KILL / 8 KILL-SIG of 58, 0 promoted) matches the
`verdict_counts` in all three `experiments/sweeps/r6-*/summary.json`
artifacts exactly; its per-lane detail held to the digit under
re-parsing (all 7 gap-family KILL-SIG t-stats verbatim, MSFT
`mfi_reversion` −2.892 as the sole R6-A KILL-SIG, KEEP t-stats
0.601/0.180/0.287, control-arm 0.471 vs 0.479, the exact
`2.638257273476751` bar string present per-lane); its burden accounting
(696 consumed, 4359 → 5055) reconciles with `r6_total_configs()`
executed at HEAD and with `program_variants_tried: 5055` in the
r6-volume-hourly artifact; and its card's gate/runtime/claims-lifecycle
statements match the tree (gate block present in lane JSONs, claim file
gone at HEAD). No defect found in its work — an unusually strong
property for a 58-lane, 696-config results drop is that a hostile
line-by-line re-derivation found nothing to correct.

## Close-out

**Done:** on branch `claude/rounds-retrospective`, five commits:
`979738a` (born-red card + claim) → `a8b4e3b` (retrospective doc +
current-state reachability link) → `53b190f` (two citation-anchor
fixes found by the adversarial pass) → `2d2b23b` (status heartbeat) →
this close-out (card flipped `complete`, claim
`control/claims/2026-07-14-rounds-retrospective.md` deleted).

**Verify:** adversarial spot-check as logged above (41/43 claim-groups
verbatim-verified, 2 anchor fixes applied, 0 numeric errors);
`python3 bootstrap.py check --strict` green with this card complete
(pre-flip it held exactly one red: the designed born-red hold).
Integrity at close: diff vs main touches ONLY
`docs/research-program-retrospective.md` (new), one link line in
`docs/current-state.md`, one heartbeat line in `control/status.md`,
this card, and the claim deletion. Every `experiments/**` and `data/**`
file byte-untouched; `data/p5holdout/` never read; no fetches; no
`src/` or `scripts/` or `tests/` change; no verdict touched; promotion
CLOSED and untouched; `control/inbox.md`/`outbox.md` byte-untouched;
no triggers created or modified; NO merge action by this session on its
own PR (#120) — the auto-merge enabler is the landing path.

**Next (guard recipe):** the retrospective records two ledger-vs-ledger
inconsistencies it did NOT edit (BTC-USD R3 baseline OOS 1.258 in the
btc-coverage card vs 1.238 in the R4-B table
`docs/research-round-4-results.md` L142; the stale tallies named in
this card's 💡) — a future docs session fixing either should cite this
card's verify pass rather than re-deriving, and the funnel-table idea
above is the class-level fix.

Session end: badge flipped `complete` in this final content commit
before push.
