# 2026-07-19 — Round 9 run: execute the pre-registered signal-confluence vote

> **Status:** `complete` — Round 9 EXECUTED — cross-class ≥K-of-N
> signal-confluence vote: **11 KEEP-dev / 44 KILL / 5 KILL-SIG of 60 lanes,
> 0 promoted**, best informational t **1.04** (BTC-USD set3/k2) vs the K=4
> bar 2.24 and the program K=60 bar 3.14; gate 16 PASS / 44 FAIL (1 KEEP
> demoted, TLT set5/k2). Pre-registered correlation check: **0 of 15
> instruments trip the >0.5 disqualification** — members are near-INDEPENDENT
> (mean pairwise position-corr −0.19..+0.05), so the vote is NOT one signal
> counted twice; the honest mechanism is the co-agreement one. Trade-count:
> the strict all-agree corner (SET-3/K=3) genuinely COLLAPSES trades (median
> shrink 0.51 ⇒ SE-inflation ×1.40) and produces every KILL-SIG; looser votes
> INFLATE trades (whipsaw) yet still lose to B&H. 0 UNGRADEABLE, no degenerate
> zero-trade lane; runtime 26 s vs 900 s cap; program 5,793 → 5,853.
> Results: docs/research-round-9-results.md.

📊 Model: opus-4.8 · medium · research

## Why this session exists

The Round-9 pre-registration (`docs/research-round-9-plan.md`, badge
`binding`, merged as PR #153) landed PLAN + CODE INFRASTRUCTURE only — the
`ensemble.confluence_positions` vote gate + the pinned 60-config grid
(`sweeps._R9_*`, `r9_total_configs()` = 60) with tests, ZERO results. This
session is the separately-claimed RUN slice (plan-before-outcome, the ORDER
014 round-6 precedent). It builds `scripts/run_r9_confluence_sweep.py`, runs
the 60-lane sweep on the committed 15-ticker daily dev surface, grades it
honestly under the standing corrections (Round-2 KEEP/KILL rule, ORDER 007
informational t, `classify_verdict` KILL-SIG, the selection-fair gate on every
lane), computes the two mandatory pre-registered first-class sections (the §6
correlation/overlap check and the §7 trade-count / power-impact analysis), and
writes `docs/research-round-9-results.md`. POST-HOLDOUT, DEV-ONLY: the holdout
is SPENT and promotion is CLOSED — every KEEP is a dev-candidate only, never a
finding. The `min_tstat` bar is UNCHANGED (K=4 per-lane ≈ 2.24, K=60
program ≈ 3.14).

The owner's question, verbatim: *"isn't it a good idea to find multiple
strategies and wait untill at least 2 or 3 give the same signals?"* Round 9
answers it directly and honestly on dev data.

## Work log

- branch `claude/r9-confluence-run` cut from origin/main HEAD `6f1a4e9`
  (#153, the R9 pre-registration; program cumulative 5,793 registered
  configs / 0 promoted). Born-red FIRST commit: this card.
- `scripts/run_r9_confluence_sweep.py` — the 60-lane runner: members at fixed
  `DEFAULT_PARAMS`, `confluence_positions(members, k)`, full-dev-period
  `run_backtest`, Lo-2002 Sharpe-delta t via `promotion.grade_promotion`
  (K=4), `classify_verdict`, the selection-fair gate on every lane (searched
  arm = instrument best-of-4, fidelity-guarded), the §6 correlation block and
  §7 trade-count block, artifacts under `experiments/sweeps/r9-confluence/`.
- `docs/research-round-9-results.md` (badge `reference`) + dashboard /
  meta-analysis / strategy-catalog / current-state R9 rows.

💡 **Session idea:** the R9 lane grader re-implements the R7C lane loop
(full/OOS backtest → Round-2 rule → `grade_promotion` → `classify_verdict` →
`run_selection_gate` → `apply_gate` → lane JSON) around a different position
source (a confluence compositor instead of a registry family). That grade-one-
lane pipeline is now pasted verbatim in `run_r7c_conjunction_sweep.py`,
`run_r9_confluence_sweep.py`, and the R8 runner. Promote a single
`grade_lane(ohlcv, positions_or_fn, *, variants_tried, per_split, top_variant,
recorded_searched_sharpe, costs, timeframe) -> lane_dict` helper in
`trading_lab` (or a `scripts/_lane.py`) that every round runner calls, so a new
round writes only its position source + grid assertion. Anchor: the identical
`grade = promotion.grade_promotion(...); verdict_pre_gate =
promotion.classify_verdict(...); gate = selection_gate.run_selection_gate(...);
verdict = selection_gate.apply_gate(...)` block; test target: a golden test
that the helper reproduces a committed lane JSON byte-for-byte.

## Previous-session review

⟲ PR #153 (`r9-confluence-prereg`, merged) — landed
`docs/research-round-9-plan.md` (badge `binding`): the cross-class ≥K-of-N
confluence-vote pre-registration this run executes — the member panels
(SET-3, SET-5), the 4 vote configs (K∈{2,3}), the 15-ticker surface, the 60
-config burden, the registered null, the mandatory §6 correlation check and §7
trade-count/power section, and the exact runner + results a run must add.
**Did the run honor the pre-registration?** Yes, end-to-end. The pinned grid
resolved to exactly `r9_total_configs()` = 60 (15 × 4), asserted by the runner
before any lane; instruments were the frozen `R9_INSTRUMENTS` tuple; members
ran at their fixed `DEFAULT_PARAMS` with NO per-member re-search; the
`min_tstat` bar was counted at K=4 per lane and K=60 program-wide, never
lowered; the holdout was never read. The registered **null** ("most lanes
KILL — confluence carries no benchmark-beating edge; a negative result is the
expected, publishable outcome") **held**: 44 KILL / 5 KILL-SIG / 11 weak
KEEP-dev, best t 1.04 far under both bars, 0 promoted. **One honest divergence
from the registered prior (a sharper, more honest finding, not a defect):**
the plan's mechanism was "distinct-class signals anti-correlate, so the vote
collapses trade count and power." The run confirms the anti-correlation (mean
pairwise position-corr is NEGATIVE on all 15 names, 0 trip >0.5 — so the vote
is genuinely NOT one signal counted twice), but the trade-count effect is
regime-split: the strict all-agree corner (SET-3/K=3) DOES collapse trades
(median shrink 0.51) and is exactly where all 5 KILL-SIG lanes land, while the
looser majority votes INFLATE trades (median shrink up to ~2.0 — whipsaw
churn), losing to B&H by paying more costs for a choppier, less-in-market
exposure. Same null, more precisely mechanised than the plan's baseline.

## Close-out

**Done** (3 commits):
- `34af557` — born-red FIRST commit: this session card (`in-progress` hold).
- `4ea9383` — the runner `scripts/run_r9_confluence_sweep.py`, the 60-lane
  sweep + artifacts under `experiments/sweeps/r9-confluence/` + 15 ledger runs
  + `index.jsonl`, `docs/research-round-9-results.md`, the R9 rows in
  dashboard / meta-analysis / strategy-catalog / current-state, and the
  `aggregate_effect_sizes.py` selector tightening (R9's dual K=4/K=60 bar
  schema excluded from the uniform-2.638-bar rollup).
- (this commit) — close-out flip: badge `in-progress` → `complete`, close-out
  slots resolved.

**Verify:**
- `python3 -m pytest -q` → 786 passed.
- `python3 bootstrap.py check --strict` → EXIT 0 at flip (the born-red
  in-progress hold clears when the badge flips to `complete`).
- Integrity: the branch diff touches only `scripts/run_r9_confluence_sweep.py`
  + `experiments/sweeps/r9-confluence/**` + `experiments/runs` + `index.jsonl`
  + `docs/research-round-9-results.md` + `docs/research-program-dashboard.md`
  + `docs/cross-round-meta-analysis.md` + `docs/strategy-catalog.md`
  + `docs/current-state.md` + this session card + `.substrate/guard-fires.jsonl`.
  The holdout was never read, `unlock_holdout` never passed, no fetch,
  `experiments/paper/**` untouched, no triggers, no broker/exchange code, the
  `min_tstat` bar unchanged, promotion CLOSED / 0 promoted.

**Next (guard recipe):** the 5 KILL-SIG lanes are all the strict-vote corner
(SET-3/K=3 on AAPL/BTC/JPM/NVDA + SET-5/K=3 on MSFT, NVDA t −5.09 the
strongest) — insisting ALL distinct classes agree is significantly
value-destroying on high-drift names, the R7-C conjunction-harm pattern
recurring one abstraction up (a cross-class AND vote, not a within-class AND).
A future round should NOT re-run confluence with more members or more K values
(the mechanism is understood and the bar is untouched); if anything, register
the INVERSE (a ≥K-of-N vote to EXIT / go flat, testing whether agreement times
risk-off better than risk-on). The 11 weak KEEP-devs cluster on the same
low-vol / high-drift survivorship names prior rounds returned (BTC, TLT, XOM,
GLD) — feed them to the stability battery before anyone cites them.
