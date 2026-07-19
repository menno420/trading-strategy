# 2026-07-19 — Round 11 pre-registration (cross-asset regime conditioning, continuous + causal)

> **Status:** `complete` — Round 11 pre-registration (PLAN + CODE
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

**Done** (6 commits on `claude/r11-xasset-regime-prereg`, cut from origin/main
HEAD `06371bb`):
- `64c72d5` — born-red FIRST commit: this session card (`in-progress` hold).
- `b2e1032` — `control/inbox.md` ORDER 021 (Round 11 cross-asset regime
  conditioning) under a decide-and-flag provenance note (the ORDER 019/020
  precedent; `control/` RETIRED at HEAD).
- `fd7cf9b` — `src/trading_lab/xasset_regime.py`: the 3 causal regime signals +
  `regime_conditioned_positions` (continuous causal rolling-percentile-rank,
  trailing 252) + `tests/test_xasset_regime.py` (33 tests incl. the headline
  no-lookahead truncation test).
- `6e74b06` — the R11 grid pinned in `sweeps.py` (`_R11_SIGNALS`, `_R11_WINDOWS`,
  `_R11_TARGETS`, `_R11_PERCENTILE_WINDOW`, `r11_configs()`,
  `r11_total_configs()` = 3 × 3 × 3 = 27, `R11_K = 27`) + 7 pins in
  `tests/test_sweeps.py::TestRound11`.
- `6527035` — the BINDING plan `docs/research-round-11-plan.md` (badge `binding`)
  + a PLAN-ONLY reachability bullet in `docs/current-state.md`'s rounds list
  (NOT a CLOSED flip; the 5,913/0 tally + holdout/promotion rails untouched) +
  the guard-fires telemetry delta.
- (this commit) — close-out flip: badge `in-progress` → `complete`, close-out
  written. The pre-registration is a complete, landable deliverable on its own.

**Verify:**
- `python3 -m pytest -q` → **849 passed** (809 prior + 33 `test_xasset_regime` +
  7 `TestRound11` sweeps pins). The CAUSALITY / no-lookahead truncation test
  (`tests/test_xasset_regime.py::TestNoLookahead`) PASSES — the score and the
  conditioned position at bar t are identical on the full series vs
  `series.iloc[:t+1]` across all 3 signals × 3 windows, so the design does NOT
  leak.
- `python3 bootstrap.py check --strict` → the only red pre-flip was the born-red
  in-progress HOLD on this card (by design); it clears when the badge flips to
  `complete`. Advisories only: seat-digest + pre-existing model-line payload nits
  on OLDER cards (never exit-affecting); this card's Model line carries the
  taught three-field form (`opus-4.8 · medium · idea/planning`).
- `r11_total_configs()` == **27**; no member/target substitutions were required —
  the regime legs (SPY/QQQ/GLD/TLT) and targets (SPY/QQQ/NVDA) are all committed
  NYSE-calendar daily caches; BTC-USD is excluded by design (weekend calendar).

**Integrity — PLAN + INFRASTRUCTURE, ZERO results:** the branch diff touches
only the plan doc, the `xasset_regime` module + its tests, the pinned R11 grid +
its tests, the ORDER 021 inbox append, the current-state reachability bullet, the
guard-fires telemetry delta, and this card. NO sweep run, NO backtest, NO runner,
NO verdict; the holdout was never read, no fetch, `requirements.txt` unchanged,
`experiments/paper/**` untouched, no triggers, no broker code. Promotion stays
CLOSED / 0 promoted, holdout stays SPENT, the `min_tstat` bar is unchanged. NO
manual merge — the landing workflow merges on green.

**Next (the R11 RUN slice, a future separately-claimed session + card):** clone a
gate-carrying daily runner into `scripts/run_r11_xasset_regime_sweep.py` (load
the aligned target + regime-leg closes via `load_ohlcv`, compose each (signal ×
window × target) via `xasset_regime.regime_conditioned_positions`, benchmark vs
buy-and-hold, grade under the Round-2 rule + selection-fair gate on every lane),
re-assert the truncation / prefix-invariance property on the REAL cached panels
before grading, report the base buy-and-hold Sharpe next to each conditioned
lane, and land `docs/research-round-11-results.md` (5,913 → 5,940), flipping the
round to CLOSED in `docs/current-state.md`.
