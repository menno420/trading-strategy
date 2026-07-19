# 2026-07-19 — Round 10 run: execute the pre-registered inverse-confluence EXIT vote

> **Status:** `in-progress` — Round 10 EXECUTION (born-red hold): the RUN slice
> of the pre-registered inverse-confluence EXIT vote (go-flat when ≥K distinct
> thesis-class members agree OUT), the De Morgan DUAL of R9's entry vote. Builds
> `scripts/run_r10_exit_confluence_sweep.py`, runs the pinned 60-config grid
> (`sweeps.r10_total_configs()` = 60) on the committed 15-ticker daily dev
> surface, grades honestly under the standing corrections (Round-2 KEEP/KILL,
> ORDER 007 informational t, `classify_verdict` KILL-SIG, the selection-fair
> gate on every lane), computes the two mandatory pre-registered first-class
> sections (the §6 exit-signal correlation/overlap check confirming the Pearson
> `corr(1-x,1-y)=corr(x,y)` identity vs R9, and the §7 exit-count / power-impact
> analysis flagging any degenerate ~0-exit lane), and writes
> `docs/research-round-10-results.md`. POST-HOLDOUT, DEV-ONLY: the holdout is
> SPENT and promotion is CLOSED — every KEEP is a dev-candidate only, never a
> finding. The `min_tstat` bar is UNCHANGED (K=4 per-lane ≈ 2.24, K=60
> program ≈ 3.14). Program cumulative 5,853 → 5,913 on this RUN.

📊 Model: opus-4.8 · medium · research

## Why this session exists

The Round-10 pre-registration (`docs/research-round-10-plan.md`, badge
`binding`, merged as PR #155) landed PLAN + CODE INFRASTRUCTURE only — the
`ensemble.exit_confluence_positions` risk-OFF exit-vote gate (long by default,
go flat when ≥k members are flat) + the pinned 60-config grid
(`sweeps._R10_*`, `r10_total_configs()` = 60) with tests, ZERO results. This
session is the separately-claimed RUN slice (plan-before-outcome, the ORDER
014 round-6 precedent, exactly as R9 split #153 plan / #154 run). It builds
`scripts/run_r10_exit_confluence_sweep.py`, mirroring `run_r9_confluence_sweep.py`
verbatim and adapting only the compositor (`exit_confluence_positions` instead
of `confluence_positions`) and the R10 grid constants, runs the 60-lane sweep
on the committed 15-ticker daily dev surface, grades it honestly, computes the
§6 and §7 sections, and writes `docs/research-round-10-results.md`.

The owner's idea, verbatim (2026-07-19): *"isn't it a good idea to find
multiple strategies and wait untill at least 2 or 3 give the same signals?"*
Round 9 answered the ENTRY framing (require ≥K agreement to enter). Round 10
answers the INVERTED complement the coordinator authorized on the same live
owner turn: *does using strategy-agreement to decide when to STEP ASIDE beat
just holding?*

## Work log

- branch `claude/r10-exit-confluence-run` cut from origin/main HEAD `025d9c9`
  (#155, the R10 pre-registration; program cumulative 5,853 registered
  configs / 0 promoted). Born-red FIRST commit: this card.
- (pending) `scripts/run_r10_exit_confluence_sweep.py` — the 60-lane runner.
- (pending) `docs/research-round-10-results.md` + dashboard / meta-analysis /
  strategy-catalog / current-state R10 rows.

💡 **Session idea:** R10 recycles the identical grade-one-lane pipeline the R9
run flagged (full-period backtest → Round-2 rule → `grade_promotion` →
`classify_verdict` → `run_selection_gate` → `apply_gate` → lane JSON), differing
ONLY in the position source (`exit_confluence_positions` vs `confluence_positions`)
and the reused member panels. This is now the FOURTH runner (R7C, R8, R9, R10)
pasting that block verbatim — the R9 card's proposed `grade_lane(...)` helper in
`trading_lab` (golden-tested against a committed lane JSON byte-for-byte) would
have made R10 a ~40-line diff. Anchor: the identical `grade =
promotion.grade_promotion(...); verdict_pre_gate = promotion.classify_verdict(...);
gate = selection_gate.run_selection_gate(...); verdict =
selection_gate.apply_gate(...)` block; test target: golden lane-JSON reproduction.

## Previous-session review

⟲ PR #155 (`r10-inverse-confluence-prereg`, merged as main `025d9c9`) — landed
`docs/research-round-10-plan.md` (badge `binding`): the inverse-confluence
exit-vote pre-registration this run executes — the `exit_confluence_positions`
gate (implemented as `1 - confluence_positions([1-m for m in members], k)`, the
De Morgan dual), the reused R9 member panels (SET-3, SET-5), the 4 exit-vote
configs (K∈{2,3}), the 15-ticker surface, the 60-config burden, the registered
null, the mandatory §6 exit-signal correlation check (with the `corr(1-x,1-y)=
corr(x,y)` identity prediction), and the §7 exit-count/power section. **Did the
run honor the pre-registration?** [[fill: yes/divergences after execution]]

## Close-out

[[fill: commits, verify tails, integrity, next]]
