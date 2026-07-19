# 2026-07-19 — Round 11 run: execute the pre-registered cross-asset regime conditioning sweep

> **Status:** `in-progress` — Round 11 EXECUTION: the RUN slice of the
> pre-registered cross-asset regime conditioning round (condition a RISK-LEG
> target's exposure CONTINUOUSLY on a CAUSAL cross-asset regime score, graded
> against the unconditioned buy-and-hold control). Builds
> `scripts/run_r11_xasset_regime_sweep.py`, runs the pinned 27-config grid
> (`sweeps.r11_total_configs()` = 27; 3 signals × 3 windows × 3 targets
> SPY/QQQ/NVDA) on the committed daily dev surface, grades honestly under the
> standing corrections (Round-2 KEEP/KILL, ORDER 007 informational t,
> `classify_verdict` KILL-SIG, the selection-fair gate on every lane), reports
> the mandatory unconditioned control arm (base buy-and-hold Sharpe next to every
> lane + how many lanes beat their own hold), re-asserts the headline
> no-lookahead truncation/prefix-invariance property on the REAL cached panels,
> and writes `docs/research-round-11-results.md`. POST-HOLDOUT, DEV-ONLY: the
> holdout is SPENT and promotion is CLOSED — every KEEP is a dev-candidate only,
> never a finding. The `min_tstat` bar is UNCHANGED (K=9 per-lane ≈ 2.54, K=27
> program ≈ 2.90). Program cumulative 5,913 → 5,940 on this RUN. **0-promoted is
> the expected, publishable outcome.**

📊 Model: opus-4.8 · medium · research

## Why this session exists

The Round-11 pre-registration (`docs/research-round-11-plan.md`, badge
`binding`, merged as PR #158) landed PLAN + CODE INFRASTRUCTURE only — the
`trading_lab.xasset_regime` module (3 causal cross-asset regime scores +
`regime_conditioned_positions`, continuous causal rolling-percentile
conditioning) + the pinned 27-config grid (`sweeps._R11_*`,
`r11_total_configs()` = 27) with tests (headline no-lookahead truncation test),
ZERO results. This session is the separately-claimed RUN slice
(plan-before-outcome, the ORDER 014 round-6 precedent, exactly as R9 split #153
plan / #154 run and R10 split #155 plan / #156 run). It builds
`scripts/run_r11_xasset_regime_sweep.py`, mirroring
`run_r10_exit_confluence_sweep.py`, runs the 27-lane sweep on the committed daily
dev surface, grades it honestly with the mandatory unconditioned control arm,
re-asserts the causality guarantee on the real panels, and writes
`docs/research-round-11-results.md`.

The direction, verbatim (scoping memo §2.1, PR #157): cross-asset / macro-regime
is the LOWEST-cost, SELF-SERVE first step from the new-data-source frontier —
the only candidate testable with data the lab ALREADY holds. R11 answers: *does
conditioning a risk-leg's exposure on a CONTINUOUS, CAUSAL cross-asset regime
score beat just holding that leg?* — the CONTINUOUS form the burned binary R4
`crossasset_gate` (0/2) / `regime_switch` (0/6) never tried.

## Work log

- branch `claude/r11-xasset-regime-run` cut from origin/main HEAD `bc710c7`
  (#158, the R11 pre-registration; program cumulative 5,913 registered
  configs / 0 promoted). Born-red FIRST commit: this card.
- `scripts/run_r11_xasset_regime_sweep.py` — the 27-lane runner, mirroring
  `run_r10_exit_confluence_sweep.py`; adapts the position source to
  `xasset_regime.regime_conditioned_positions` (continuous causal
  rolling-percentile conditioning of a cross-asset regime score), the grade
  dimension to (signal, window) per target (per-lane K=9, program K=27), and
  adds the mandatory unconditioned control arm + a RUN-side re-assertion of the
  truncation / prefix-invariance property on the REAL cached panels. Asserts
  `r11_total_configs()` == 27 before running.
- `docs/research-round-11-results.md` (badge `reference`) + dashboard /
  meta-analysis / strategy-catalog / current-state R11 rows.

💡 **Session idea:** R11 is now the FIFTH runner (R7C, R8, R9, R10, R11) pasting
the identical grade-one-lane pipeline (full-period backtest → Round-2 rule →
`grade_promotion` → `classify_verdict` → `run_selection_gate` → `apply_gate` →
lane JSON), differing ONLY in the position source and the search dimension. The
R9/R10 cards' proposed `grade_lane(...)` helper in `trading_lab` (golden-tested
against a committed lane JSON byte-for-byte) is now FIVE rounds overdue — it
would have made R11 a ~40-line diff over the position factory. Anchor: the
identical `grade = promotion.grade_promotion(...); verdict_pre_gate =
promotion.classify_verdict(...); gate = selection_gate.run_selection_gate(...);
verdict = selection_gate.apply_gate(...)` block; test target: golden lane-JSON
reproduction. The one genuinely new R11 wrinkle worth a helper: a multi-ticker
position factory whose gate-replay closure reindexes the aligned regime panel to
the (possibly truncated) target frame — the causal-panel-slice pattern the next
cross-asset round will also need.

## Previous-session review

⟲ PR #158 (`r11-xasset-regime-prereg`, merged as main `bc710c7`) — landed
`docs/research-round-11-plan.md` (badge `binding`): the cross-asset regime
conditioning pre-registration this run executes, the `trading_lab.xasset_regime`
module (3 causal scores `xasset_eq_bond_mom` / `xasset_metals_riskoff` /
`xasset_breadth` + `regime_conditioned_positions`, continuous causal
rolling-percentile conditioning), the pinned 27-config grid (`sweeps._R11_*`,
`r11_total_configs()` = 27), `tests/test_xasset_regime.py` (headline no-lookahead
truncation test + shape/range/hand-constructed examples), and the 5,913 → 5,940
ledger pin. **Did the pre-registration hold?** [[fill: resolved at close-out —
whether the pinned grid ran as written, the causality control re-asserted on the
real panels, and the registered null held.]]

## Close-out

[[fill: resolved as the deliberate LAST commit once everything is green and
current-state is updated.]]
