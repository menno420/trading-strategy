# 2026-07-17 — Program research scoreboard

> **Status:** `complete` — Canonical program research scoreboard landed —
> docs/research-program-dashboard.md aggregates P1→Round 7 (5,415 registered
> configs, 0 promoted, program-max informational t 1.66 (R5-A) vs the
> unchanged 2.638 bar); docs-only, no verdict changed; reachable from
> current-state.md.

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

⟲ PR #141 (`round-7-run`, merged) — executed the two pre-registered Round-7
slices (R7-A `drawdown_reversion` + R7-B `high_proximity`) top-down under
the selection-fair gate: 30 lanes / 360 configs graded as **5 KEEP-dev /
25 KILL / 0 KILL-SIG, 0 promoted**, best informational t **1.195** (BTC-USD
`high_proximity`, shown 1.20 in the round headline) vs the unchanged 2.638
K=12 bar, program cumulative 5,055 → 5,415. Those recorded numbers match
what I aggregated into the scoreboard from `docs/research-round-7-results.md`
to the cell: the Round 7 row is **360 configs added / cumulative 5,415 /
5 KEEP-dev / 25 KILL / 0 KILL-SIG / best t 1.20 (footnote 10: 1.195 in the
per-lane t column) / 0 promoted** — no drift between the card's headline,
the results doc, and the scoreboard row. Its docs-plus-code claim also held
against the tree: R7 touched `src/trading_lab/strategies` + `sweeps.py` +
tests + the sweep/run artifacts but never the holdout or promotion path, and
the 0-promoted verdict I carried forward is the one it recorded. One honest
nit: the R7 card presents best t as **1.195** in its Status headline but the
scoreboard shows **1.20** in the same "Best t" column (with the 1.195
per-lane value pushed to footnote 10) — the two are the same measurement
rounded differently, and the footnote reconciles them, but a reader diffing
headline-to-cell sees a cosmetic 1.195-vs-1.20 mismatch rather than a single
canonical rendering. Otherwise no defect found — the aggregation is faithful.

## Close-out

**Done** (3 commits):
- `fbb8195` — born-red FIRST commit: this session card.
- `12f8320` — `docs/research-program-dashboard.md` (canonical per-round
  scoreboard, P1 → Round 7) + `docs/current-state.md` pointer so the
  dashboard is reachable from the living ledger.
- (this commit) — close-out flip: badge `in-progress` → `complete`,
  previous-session-review + close-out slots resolved.

**Verify:**
- `python3 -m pytest -q` → 694 passed.
- `python3 bootstrap.py check --strict` → EXIT 0 at flip (the born-red
  in-progress hold clears when the badge flips to `complete`).
- Integrity: the branch diff touches only
  `docs/research-program-dashboard.md` + the `docs/current-state.md` pointer
  + this session card — docs-only. No `src/` / code change, no verdict
  changed, holdout never read (SPENT), `experiments/paper/**` untouched,
  `control/status.md` untouched, no triggers, `min_tstat` bar unchanged,
  promotion CLOSED / 0 promoted. NO manual merge — the auto-merge enabler
  lands PR #142 on green.

**Next:** menu #24 (strategy-family catalog) is the natural companion to
this scoreboard — the dashboard rolls up *what each round found*, the
catalog would roll up *what each strategy family is*. Maintenance note for
whoever updates this page: the KEEP-dev / KILL / KILL-SIG cells are
**per-round-as-graded** and are footnoted for re-grade non-additivity
(Round 3/4's re-grade slices are deliberately excluded from later rows to
avoid double-counting) — a future maintainer editing the table must
preserve those footnotes, or the cumulative story silently drifts. Plus
this card's 💡 `scripts/render_program_dashboard.py` (regenerate the numeric
cells from each slice's committed `summary.json` + the `sweeps.py`
cumulative chain, with a golden test) to end hand-aggregation of the
cross-round rollup.
