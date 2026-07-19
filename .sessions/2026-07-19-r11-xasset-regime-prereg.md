# 2026-07-19 — Round 11 pre-registration (cross-asset regime conditioning, continuous + causal)

> **Status:** `in-progress` — Round 11 pre-registration (PLAN + CODE
> INFRASTRUCTURE, ZERO results): `docs/research-round-11-plan.md` (binding)
> conditions a base long position on a RISK-LEG target (SPY/QQQ/NVDA) by a
> CAUSAL cross-asset regime score — the self-serve first step from
> `docs/research-direction-new-data-sources.md` §2.1, built entirely from the
> EXISTING daily cache (no new data, no new dependency). This PR lands the plan
> + the `trading_lab.xasset_regime` module (3 causal regime signals + the
> continuous rolling-percentile conditioning) + its tests (headline: a
> no-lookahead truncation test) + the pinned 27-config R11 grid
> (`sweeps._R11_*`, `r11_total_configs()` = 27) with test pins. It runs NOTHING
> and grades NOTHING — the sweep RUNNER + graded results are a separate future
> RUN PR with its own card. POST-HOLDOUT, DEV-ONLY: holdout SPENT, promotion
> CLOSED, `min_tstat` bar never lowered. This pre-registration is a complete,
> landable deliverable on its own — the card flips `complete` as the final
> commit, after tests + bootstrap are green.

📊 Model: opus-4.8 · medium · idea/planning

## Why this session exists

After 10 rounds / 5,913 registered configs / 0 promoted, the price/volume dev
surface is mined out. The new-data-source scoping memo
(`docs/research-direction-new-data-sources.md`, PR #157) named **cross-asset /
macro-regime** as the LOWEST-cost, SELF-SERVE first step — testable entirely on
the committed 15-ticker daily cache (TLT/GLD/SPY/QQQ legs), with NO new
ingestion, NO new ticker, NO new dependency. Coordinator-authorized on the
owner's standing 2026-07-19 turn, Round 11 executes that first step under the
identical plan-before-outcome protocol every round has used.

The memo's HONEST caveat is the design constraint: cross-asset conditioning is
NOT virgin territory — the Round-4 `crossasset_gate` (0 KEEP / 2 KILL, §R4-E)
and `regime_switch` (0 KEEP / 6 KILL, §R4-D) are BURNED classes where the
unconditioned control beat the gate. R11 MUST differ materially: it conditions
CONTINUOUSLY (a causal rolling-percentile-rank of a real-valued regime score,
sizing exposure smoothly) rather than with a binary on/off gate, and it carries
a MANDATORY unconditioned control arm (plain buy-and-hold of the same target).

Per the header protocol, this pre-registration PR lands PLAN + CODE
INFRASTRUCTURE only (the causal regime module + its tests + the pinned grid),
ZERO results/outcomes; the sweep runner + graded
`docs/research-round-11-results.md` are a separate future RUN PR. Held
BORN-RED: the card stays `in-progress` until tests + bootstrap are green.

## Work log

- branch `claude/r11-xasset-regime-prereg` cut from origin/main HEAD `06371bb`
  (#157, the new-data direction doc; program 5,913 registered configs / 0
  promoted). Born-red FIRST commit: this card.
- ORDER 021 appended to `control/inbox.md` (decide-and-flag provenance note,
  mirroring the ORDER 019/020 precedent — `control/` is RETIRED at HEAD but the
  coordinator-authorized owner turn is landed here under that flag).
- `src/trading_lab/xasset_regime.py` — the 3 causal cross-asset regime signals
  (`xasset_eq_bond_mom`, `xasset_metals_riskoff`, `xasset_breadth`) built from a
  dict of aligned daily closes given window W, plus
  `regime_conditioned_positions(...)` returning the target's continuous position
  ∈ [0,1] = the CAUSAL rolling-percentile-rank (trailing 252) of the chosen
  score. Every score at bar t uses ONLY data with timestamp ≤ t (trailing
  windows only; rolling, never full-sample, normalization).
- `tests/test_xasset_regime.py` — headline no-lookahead TRUNCATION test (score
  and conditioned position at bar t identical on the full series vs the series
  truncated at bar t), plus shape/range tests and a hand-constructed example per
  signal.
- the R11 grid pinned in `sweeps.py` (`_R11_SIGNALS`, `_R11_WINDOWS`,
  `_R11_TARGETS`, `_R11_PERCENTILE_WINDOW`, `r11_total_configs()` = 3 × 3 × 3 =
  27) + pins in `tests/test_sweeps.py`.
- `docs/research-round-11-plan.md` (badge `binding`) + a PLAN-ONLY reachability
  bullet in `docs/current-state.md`'s rounds list (NOT a CLOSED flip, NOT a
  tally/holdout/promotion change — that is the RUN PR's job at flip time).

💡 **Session idea:** the whole R11 design rides on ONE load-bearing correctness
property — regime-detection lookahead is the #1 failure mode for this class, and
the CAUSAL rolling-percentile-rank (trailing 252, never full-sample) is the
mechanism that forecloses it. The truncation unit test in
`tests/test_xasset_regime.py` (score AND position at bar t identical on the full
series vs `series.iloc[:t+1]`) is the guarantee — if it ever fails, the design
leaks. Guard recipe: `xasset_regime.regime_conditioned_positions` /
`src/trading_lab/xasset_regime.py`; test target
`tests/test_xasset_regime.py::TestNoLookahead` — the RUN session must clone a
gate-carrying runner and assert the same truncation property on the REAL cached
panels before grading, not only on synthetic series.

## Previous-session review

⟲ PR #157 (`r11-new-data-direction`, merged) — landed
`docs/research-direction-new-data-sources.md`, a PLAN-ONLY scoping memo that
split candidate NEW data types by access cost. It named **cross-asset /
macro-regime (§2.1)** as the recommended SELF-SERVE first step — the only
candidate needing zero new data access, computable from the existing cache — and
recorded the burned-class caveat verbatim: any cross-asset round must differ
materially from R4 `crossasset_gate` / `regime_switch` (continuous conditioning
and/or a genuinely new relationship) with a mandatory unconditioned control arm.
R11 is exactly that first step, pre-registered under the identical protocol. No
sweep re-run, holdout untouched — confirmed clean at HEAD (`06371bb`).

## Close-out

(to be written at flip)
