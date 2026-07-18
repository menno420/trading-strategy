# 2026-07-17 — Strategy-family catalog

> **Status:** `complete` — Strategy-family catalog landed —
> docs/strategy-catalog.md tables all 32 families (class · thesis · round
> tested · standing dev-only verdict · per-row source); reachable from
> repo-navigation-map.md; docs-only, no verdict changed; promotion CLOSED /
> 0 promoted.

Born-red HOLD: this card ships `in-progress` on purpose so the substrate-gate
holds this PR red until the catalog is reviewed and the close-out is written.
It is deliberately NOT flipped by the worker — the owner reviews the catalog
first, then the flip to `complete` (the LAST step) releases the gate.

- **📊 Model:** opus-4.8 · strategy-catalog lane (overnight worker, owner order 2026-07-17T22:39Z / menu #24) · start 2026-07-18T00:11:38Z

💡 **Session idea:** one committed table so future proposals can cite
family adjacency accurately (class, thesis, round, standing verdict) instead
of re-deriving it from seven separate results docs.

## Why this session exists

Menu #24 (owner order 2026-07-17T22:39Z): the research program now carries 32
strategy families across `src/trading_lab/strategies/`, and every new round
plan re-derives "nearest burned neighbour" adjacency by hand from seven
results docs (`p1-*-results.md`, `research-round-{2,3,4,5,6,7}-results.md`, the
retrospective). This session builds ONE reference table —
`docs/strategy-catalog.md` — that states each family's class, one-line thesis,
round tested, and standing dev-only verdict with a per-row source, so
adjacency is cited, not re-derived. Docs-only, owner-live handoff: no strategy
code, no sweep, no verdict change, no holdout read, promotion stays CLOSED.

## Work log

- Enumerated the full registry from `src/trading_lab/strategies/__init__.py`
  (`STRATEGIES` = 30 single-name families + `PORTFOLIO_STRATEGIES` = 2 = 32).
- Read each `strategies/<name>.py` module docstring for the one-line thesis.
- Cross-referenced standing verdicts against the committed results docs
  (`p1-trend-following`, `p1-mean-reversion`, `p1-video-strategy`,
  `research-round-{2,3,4,5,6,7}-results.md`, `research-program-retrospective.md`)
  — every row carries the source it was read from.
- Wrote `docs/strategy-catalog.md` (`reference` badge) and linked it from
  `docs/repo-navigation-map.md` for reachability.

## Previous-session review

⟲ PR #142 (`program-scoreboard`, merged) — stood up the canonical program
scoreboard `docs/research-program-dashboard.md`: one per-round table (configs
added + cumulative, KEEP-dev / KILL / KILL-SIG, best informational t vs the
unchanged 2.638 K=12 bar, promoted) rolling up P1 → Round 7 to **5,415
registered configs / 0 promoted**, program-max informational t **1.66 (R5-A)**,
reachable from `current-state.md`. Docs-only, no verdict changed, holdout
untouched (SPENT), promotion CLOSED. **Consistency with this catalog:** the
scoreboard's per-round KEEP/KILL/KILL-SIG tallies and this catalog's
per-family standing verdicts are two projections of the *same* committed
round results docs (`research-round-{2..7}-results.md`, the P1 docs, the
retrospective), so they reconcile at the round where the mapping is clean —
Round 7's scoreboard row (**5 KEEP-dev / 25 KILL / 0 KILL-SIG**) is exactly
the sum of this catalog's two R7 family rows, `drawdown_reversion` §R7-A
(3 KEEP-dev / 12 KILL) + `high_proximity` §R7-B (2 KEEP-dev / 13 KILL); the
0-promoted headline is identical on both pages. **One honest nit (not a
defect):** the two pages are *not* row-to-row additive at every round because
they aggregate at different granularities — the scoreboard cells are
**per-round-as-graded** (with the R3/R4 re-grade slices deliberately excluded
and footnoted for non-additivity), whereas this catalog carries each family's
**standing** verdict, which folds in *later* re-grades (e.g. `stochastic_reversion`
is KEEP-dev standing but its META-hourly lane was demoted to KILL in R5, and
`mfi_reversion` holds KEEP-dev standing while carrying an R6 MSFT-daily
KILL-SIG). So a reader must not expect an arbitrary scoreboard round row to
equal a slice of family standing verdicts; both numbers are correct at their
own altitude and trace to the same docs. No numeric drift found between the
two where the granularities do line up.

## Close-out

**Done** (3 commits):
- `3a26482` — born-red FIRST commit: this session card (`in-progress` hold).
- `74bee9c` — `docs/strategy-catalog.md` (all 32 families: class · thesis ·
  round · standing dev-only verdict · per-row source) + the
  `docs/repo-navigation-map.md` link so the catalog is reachable.
- (this commit) — close-out flip: badge `in-progress` → `complete`,
  previous-session-review + close-out slots resolved.

**Verify:**
- `python3 -m pytest -q` → 694 passed.
- `python3 bootstrap.py check --strict` → EXIT 0 at flip (the born-red
  in-progress hold clears when the badge flips to `complete`).
- Integrity: the branch diff touches only `docs/strategy-catalog.md` +
  the `docs/repo-navigation-map.md` link + this session card — docs-only. No
  `src/` / code change, no verdict changed, holdout never read (SPENT),
  `experiments/paper/**` untouched, `control/status.md` untouched, no
  triggers, `min_tstat` bar unchanged, promotion CLOSED / 0 promoted. NO
  manual merge — the auto-merge enabler lands PR #143 on green.

**Next:** this catalog is the adjacency reference future proposals should
cite (a family's class · thesis · round · standing verdict) instead of
re-deriving "nearest burned neighbour" from seven results docs by hand. Keep
it updated when a new family lands — the two Round-7 families
(`drawdown_reversion`, `high_proximity`) are its newest rows, so the next
round's families are what a maintainer adds next.
