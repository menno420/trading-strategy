# 2026-07-17 — Strategy-family catalog

> **Status:** `in-progress`

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

[[fill: review the prior session card at flip time]]

## Close-out

[[fill: owner review of the catalog, then flip Status to `complete`]]
