# 2026-07-19 — Round 11 run: execute the pre-registered cross-asset regime conditioning sweep

> **Status:** `complete` — Round 11 EXECUTED — cross-asset regime conditioning
> (condition a RISK-LEG target's exposure CONTINUOUSLY on a CAUSAL cross-asset
> regime score, graded against the unconditioned buy-and-hold control): **2
> KEEP-dev / 25 KILL / 0 KILL-SIG of 27 lanes, 0 promoted**, best informational t
> **0.68** (NVDA `xasset_breadth`/W252) vs the per-lane K=9 bar 2.54 and program
> K=27 bar 2.90; gate 4 PASS / 23 FAIL (0 KEEP demoted). The mandatory
> unconditioned control arm is decisive: **only 2 of 27 conditioned lanes beat
> their own base buy-and-hold** (both NVDA `xasset_breadth`, +0.106 / +0.175
> Sharpe), median lane −0.257 Sharpe, because a rank-normalized exposure averages
> ~0.5 and structurally sheds the drift. The **headline no-lookahead truncation
> control PASSES on the REAL cached panels** (45 probes, score + position
> bit-for-bit identical full vs truncated, max |diff| = 0.0) — the null is causal,
> not a hindsight artifact. 0 UNGRADEABLE, no degenerate ~constant lane (position
> std 0.30–0.35); runtime 36 s vs 900 s cap; program 5,913 → 5,940. Reproduces the
> burned R4 `crossasset_gate` (0/2) / `regime_switch` (0/6) null in continuous
> form. Results: docs/research-round-11-results.md.
>
> _(historical born-red hold, now cleared:)_ Round 11 EXECUTION: the RUN slice of the
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
ledger pin. **Did the pre-registration hold?** Yes, end-to-end. The pinned grid
resolved to exactly `r11_total_configs()` = 27 (3 signals × 3 windows × 3
targets), asserted by the runner before any lane; the signals, windows, targets
(BTC excluded), and the fixed 252-bar percentile window were the frozen
`sweeps._R11_*` constants; the `min_tstat` bar was counted at K=9 per lane and
K=27 program-wide, never lowered; the holdout was never read (`unlock_holdout`
never passed). The mandatory §4 causality control was re-asserted on the REAL
cached panels BEFORE grading (45 prefix-invariance probes across all 3 signals ×
3 windows, max |diff| = 0.0) — the load-bearing guarantee held bit-for-bit on the
real data, not only the synthetic test series, so the reported edge is causal.
The registered **null** held: 25 KILL / 2 weak KEEP-dev, best t 0.68 far under
both bars, 0 promoted, and the mandatory control arm confirmed only 2 of 27 lanes
beat their base hold (median −0.257 Sharpe). The honest mechanism the plan's §1
prior named — conditioning loses to its control — is localized precisely: a
rank-normalized exposure averages ~0.5 and sheds the drift rather than timing the
drawdowns, and the continuous form reproduces the burned R4 binary-gate null
rather than escaping it (the 2 nominal KEEPs are survivorship of higher average
exposure on the single highest-drift name, NVDA, not a regime edge).

## Close-out

**Done** (3 commits):
- `f5fd096` — born-red FIRST commit: this session card (`in-progress` hold).
- `155d4b7` — the runner `scripts/run_r11_xasset_regime_sweep.py`, the 27-lane
  sweep + artifacts under `experiments/sweeps/r11-xasset-regime/` (27 per-lane
  JSON + `summary.json` + `base_hold_comparison.json` + `results.csv`) + 3 ledger
  runs + `index.jsonl`, `docs/research-round-11-results.md`, the R11 rows in
  dashboard / meta-analysis / strategy-catalog / current-state (tally 5,913 →
  5,940, R11 PLAN-ONLY bullet flipped to graded CLOSED), and the
  `.substrate/guard-fires.jsonl` telemetry delta.
- (this commit) — close-out flip: badge `in-progress` → `complete`, close-out
  slots resolved.

**Verify:**
- `python3 -m pytest -q` → 849 passed (the no-lookahead `TestNoLookahead` and all
  `tests/test_sweeps.py` R11 pins green).
- `python3 bootstrap.py check --strict` → EXIT 0 after the badge flips to
  `complete` (the born-red in-progress hold clears on the flip; the pre-flip
  EXIT 1 was the designed hold, not a defect).
- Integrity: the branch diff touches only
  `scripts/run_r11_xasset_regime_sweep.py`
  + `experiments/sweeps/r11-xasset-regime/**` + `experiments/runs`
  + `index.jsonl` + `docs/research-round-11-results.md`
  + `docs/research-program-dashboard.md` + `docs/cross-round-meta-analysis.md`
  + `docs/strategy-catalog.md` + `docs/current-state.md` + this session card
  + `.substrate/guard-fires.jsonl`. The holdout was never read, `unlock_holdout`
  never passed, no fetch, `experiments/paper/**` untouched, no triggers, no
  broker/exchange code, the `min_tstat` bar unchanged, promotion CLOSED / 0
  promoted. R11's dual K=9/K=27 schema (lanes carry `min_tstat_K9`/`min_tstat_K27`,
  not a bare `min_tstat`, like R9/R10) is correctly excluded from the
  uniform-2.638-bar `aggregate_effect_sizes.py` rollup, so that generated table
  is unchanged.

**Next (guard recipe):** R11 is the FIFTH runner (R7C, R8, R9, R10, R11) pasting
the identical grade-one-lane pipeline (`grade = promotion.grade_promotion(...);
verdict_pre_gate = promotion.classify_verdict(...); gate =
selection_gate.run_selection_gate(...); verdict = selection_gate.apply_gate(...)`)
around a swapped position source. The proposed `grade_lane(...)` helper in
`trading_lab` (golden-tested against a committed lane JSON byte-for-byte) is now
five rounds overdue. R11 adds one genuinely new anchor worth a helper: a
multi-ticker position factory whose gate-replay closure reindexes the aligned
regime panel to the (possibly truncated) target frame (`make_regime_strategy` in
`scripts/run_r11_xasset_regime_sweep.py`) — the causal-panel-slice pattern any
future cross-asset round will need; test target: prefix-invariance of the
closure's positions on a truncated panel, mirroring
`tests/test_xasset_regime.py::TestNoLookahead`. The cross-asset conditioning
class is now characterized in BOTH forms — binary (R4, burned) and continuous
(R11, null) — with the unconditioned control reported alongside: do NOT re-run it
on the existing cache with more signals/windows/targets (same rank-normalized
half-invested drag). Any further cross-asset work needs new OWNER-GATED data
(fundamentals / flows, the memo's higher-potential candidates), not more
dev-surface regime shapes.
