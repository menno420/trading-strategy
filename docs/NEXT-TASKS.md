# trading-lab — Next Tasks

> **Status:** `reference` — curated top next steps for a fresh owner-live seat.
> Distilled 2026-07-17 from the overnight planning menu
> ([planning/2026-07-17-overnight-menu.md](../planning/2026-07-17-overnight-menu.md),
> 25 veto-ready RESEARCH-ONLY proposals) plus the standing research plan.
> Source of truth stays: `CONSTITUTION.md` (rails) and
> [current-state.md](current-state.md) (what's true now).

**Standing rails on every task below** (non-negotiable — see `CONSTITUTION.md`):
RESEARCH-ONLY (no broker / exchange / live-API / real-money surface); holdout
**SPENT** (`HOLDOUT_START = 2025-01-09`, never reopened); promotion **CLOSED**
(every KEEP is dev-candidate only, `min_tstat` never lowered); plan-before-outcome
(grids pinned by tests, plan committed before any run); no self-armed routines.
Honest program headline: **5,055 configs registered, 0 promoted — nothing has
cleared significance.**

---

## Owner decisions needed (flagged — owner-only)

- **Install the parked weekly paper-grading executor?** ⚠️ owner go required.
  `.github/workflows/weekly-grading.yml` is fully designed (menu item 10) but
  **not installed**: host-owned cron `0 9 * * 5` + `workflow_dispatch`, runs
  `python3 scripts/grade_paper.py` (no args), needs `permissions: contents:write`
  + `pull-requests:write` (GITHUB_TOKEN scopes — **no new secret**). It was
  parked on the EAP order "do not re-arm routines until an owner per-seat go."
  **Unblock = one explicit owner go line.** Low urgency: grading is a no-op
  until ~early August 2026, and any live session can run `grade_paper.py`
  in-session meanwhile.
- **R5-C BTC-USD `bollinger_breakout` OOS** — owner-gated proposal
  ([proposals/r5c-btc-bollinger-breakout-oos-proposal.md](proposals/r5c-btc-bollinger-breakout-oos-proposal.md)).
  Not executable before ~2026-09-09 (needs ≥252 post-2026 daily bars). Queue as
  a dated owner decision; nothing to run yet.

## Top next steps (agent-actionable, RESEARCH-ONLY)

### 1. Run Round 7 — the next real research slice (M)

The plan is pre-registered, committed, and **unrun**
([research-round-7-plan.md](research-round-7-plan.md)): R7-A `drawdown_reversion`
+ R7-B `high_proximity`, 2 families × 15 daily tickers, **360 configs
(5,055 → 5,415)**, under the standing selection-fair gate + R5-D fixed-config
row. Promotion stays CLOSED, holdout untouched. This is the highest-signal
"do research" task on the board.

### 2. Ship the cheap S-sized quality / reproducibility guards (S each)

Contained, reversible, high-value for a fresh seat — all read-only over
committed caches, none touch a verdict. From the menu:

- **Paper-ledger linter** (item 12) — `scripts/lint_paper_ledger.py`: validate
  ENTRY/EXIT alternation, required §5 bullets, no backdated rows.
- **Cache-integrity manifest + CI check** (item 15) — `data/MANIFEST.md` with
  per-cache row-count / date-span / content-hash + a CI assertion (catches
  silent gaps or holdout bleed).
- **Config-grid registry linter** (item 22) — assert every `_R*_AXES` grid is
  pinned by a count/value test and matches the declared cumulative ledger.
- **Cache-coverage doc** (item 16) — `docs/data-coverage.md`: ticker × timeframe
  × date-span, so no one proposes a sweep against an absent cache.
- **§7 FLAT-week rollup emitter** (item 11) — derive the "m weeks reviewed, f
  FLAT" line from the ledger instead of hand-appending it.
- **Strategy-family catalog** (item 24) — `docs/strategy-catalog.md`: all 32
  families, one-line thesis, testing round, standing verdict class.

### 3. Pursue one new research direction (M)

Both reuse existing harnesses, both carry an explicit null prior:

- **Reusable causal regime module** `trading_lab.regime` (item 14) feeding a
  **vol-regime-gated trend family** (item 04) — first rolling-quantile regime
  family; the labeler is reused by several downstream proposals.
- **Cross-sectional drawdown ranking on XSEC-14** (item 02) — tests whether the
  program's only consistently-observed effect (drawdown) survives
  cross-sectionally where single-name lanes have nulled.

### 4. Fresh-seat onboarding + reproducibility docs (S)

- **Onboarding quickstart** (item 23) — `docs/onboarding-quickstart.md`, "first
  15 minutes": rails, read-order, module map, run-a-sweep-and-grade.
- **One-command replay smoke** (item 25) — `scripts/replay_smoke.py`: prove the
  whole load→grid→walk-forward→gate→verdict rail is wired without a full round.
- **Program results dashboard** (item 13) — one `docs/research-program-dashboard.md`
  aggregating rounds 1–7 (cumulative configs, KEEP/KILL tallies, best t vs the
  bar, promoted = 0).

## Housekeeping already done in the fresh-start cleanup (2026-07-17)

- Deleted the 3 stale `control/claims/*` files (README kept).
- Restamped `current-state.md` as the single living ledger; corrected the EAP
  timeline, autonomy wind-down, and re-creation facts.
- Stripped the merge/auto-merge/"silence = consent" doctrine from
  `CONSTITUTION.md`; retired the self-persistence doctrine in `docs/ROUTINES.md`;
  added deprecation banners to the EAP `control/` coordination scaffolding.

## The rest of the menu

The full 25-proposal menu (M/L research families 01, 03, 05–09, plus the
methodology hardening items 17–21: deflated Sharpe, purged/embargoed CV, block
bootstrap, Benjamini-Hochberg FDR, run-manifest layer) stays veto-ready in
[planning/2026-07-17-overnight-menu.md](../planning/2026-07-17-overnight-menu.md).
Anything M/L waits for an explicit owner pick; S-sized guards above may be built
on a claimed slice.
