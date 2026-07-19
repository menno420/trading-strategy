# 2026-07-19 — Round 10 run: execute the pre-registered inverse-confluence EXIT vote

> **Status:** `complete` — Round 10 EXECUTED — inverse-confluence EXIT vote
> (go-flat when ≥K distinct thesis-class members agree OUT), the De Morgan DUAL
> of R9's entry vote: **11 KEEP-dev / 40 KILL / 9 KILL-SIG of 60 lanes, 0
> promoted**, best informational t **1.04** (BTC-USD set3/k2 — the SAME lane and
> value as R9, as the dual demands) vs the K=4 bar 2.24 and program K=60 bar
> 3.14; gate 14 PASS / 46 FAIL (0 KEEP demoted). Pre-registered correlation
> check CONFIRMS the Pearson identity `corr(1-x,1-y)=corr(x,y)` to machine
> precision — exit-signal corr EQUALS R9 position corr on all 15 names (max diff
> 1.3e-15), **0 of 15 trip >0.5**. Exit-count: the strict SET-3/K3 exit steps
> aside a median 8.5% of bars (≈ buy-and-hold, adds nothing, near-zero t); the
> loose SET-5/K2 exit steps aside 85% of bars (sheds the drift) and holds 8 of
> the 9 KILL-SIG (NVDA −4.07, MSFT −3.34, JPM −2.89). 0 UNGRADEABLE, no
> degenerate ~0-exit lane; runtime 27 s vs 900 s cap; program 5,853 → 5,913.
> Results: docs/research-round-10-results.md.
>
> _(historical born-red hold, now cleared:)_ Round 10 EXECUTION: the RUN slice
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
- `scripts/run_r10_exit_confluence_sweep.py` — the 60-lane runner, mirroring
  `run_r9_confluence_sweep.py` verbatim; adapted only the compositor
  (`exit_confluence_positions`), the R10 grid constants, and the §6/§7 framing
  to exit-signals (exit-signal correlation + identity check; exit-count / flat
  fraction / SE-inflation). Asserts `r10_total_configs()` == 60 before running.
- `docs/research-round-10-results.md` (badge `reference`) + dashboard /
  meta-analysis / strategy-catalog / current-state R10 rows.

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
run honor the pre-registration?** Yes, end-to-end. The pinned grid resolved to
exactly `r10_total_configs()` = 60 (15 × 4), asserted by the runner before any
lane; instruments were the frozen `R10_INSTRUMENTS` tuple; members ran at their
fixed `DEFAULT_PARAMS` with NO per-member re-search; the compositor was
`exit_confluence_positions`; the `min_tstat` bar was counted at K=4 per lane and
K=60 program-wide, never lowered; the holdout was never read. The registered
**null** held: 40 KILL / 9 KILL-SIG / 11 weak KEEP-dev, best t 1.04 far under
both bars, 0 promoted. **Both pre-registered predictions confirmed exactly:**
(1) the Pearson identity `corr(1-x,1-y)=corr(x,y)` holds to 1.3e-15 — the
exit-signal correlation EQUALS R9's position correlation number-for-number,
proving R10 is the De Morgan dual over one identical panel; (2) the two exit
corners null from opposite sides — strict SET-3/K3 ≈ buy-and-hold (median flat
8.5%, near-zero t), loose SET-5/K2 sheds drift (median flat 85%, 8 of 9
KILL-SIG). **One honest sharpening of the prior (not a defect):** the plan
framed the harm as landing "either corner"; the run localizes it — the KILL-SIG
concentrate specifically in the LOOSE SET-5/K2 exit (the mirror of R9, whose
KILL-SIG were all the STRICT corner), because on the 5-member panel a 2-of-5
flat threshold fires almost constantly. Same null, mechanised precisely as the
inverse of R9.

## Close-out

**Done** (3 commits):
- `97ef9ed` — born-red FIRST commit: this session card (`in-progress` hold).
- `ffc20fd` — the runner `scripts/run_r10_exit_confluence_sweep.py`, the 60-lane
  sweep + artifacts under `experiments/sweeps/r10-exit-confluence/` + 15 ledger
  runs + `index.jsonl`, `docs/research-round-10-results.md`, the R10 rows in
  dashboard / meta-analysis / strategy-catalog / current-state, and the
  `.substrate/guard-fires.jsonl` telemetry delta.
- (this commit) — close-out flip: badge `in-progress` → `complete`, close-out
  slots resolved.

**Verify:**
- `python3 -m pytest -q` → 809 passed.
- `python3 bootstrap.py check --strict` → EXIT 0 (the born-red in-progress hold
  clears when the badge flips to `complete`).
- Integrity: the branch diff touches only
  `scripts/run_r10_exit_confluence_sweep.py`
  + `experiments/sweeps/r10-exit-confluence/**` + `experiments/runs`
  + `index.jsonl` + `docs/research-round-10-results.md`
  + `docs/research-program-dashboard.md` + `docs/cross-round-meta-analysis.md`
  + `docs/strategy-catalog.md` + `docs/current-state.md` + this session card
  + `.substrate/guard-fires.jsonl`. The holdout was never read, `unlock_holdout`
  never passed, no fetch, `experiments/paper/**` untouched, no triggers, no
  broker/exchange code, the `min_tstat` bar unchanged, promotion CLOSED / 0
  promoted. R10's dual K=4/K=60 schema is correctly excluded from the
  uniform-2.638-bar `aggregate_effect_sizes.py` rollup (same as R9 — the lanes
  carry `min_tstat_K4`/`min_tstat_K60`, not a bare `min_tstat`), so that
  generated table is unchanged.

**Next (guard recipe):** R10 makes the FOURTH runner (R7C, R8, R9, R10) pasting
the identical grade-one-lane pipeline (`grade = promotion.grade_promotion(...);
verdict_pre_gate = promotion.classify_verdict(...); gate =
selection_gate.run_selection_gate(...); verdict = selection_gate.apply_gate(...)`)
around a swapped position source. The R9 card's proposed
`grade_lane(ohlcv, positions_or_fn, *, variants_tried, per_split, top_variant,
recorded_searched_sharpe, costs, timeframe) -> lane_dict` helper in `trading_lab`
(golden-tested against a committed lane JSON byte-for-byte) is now overdue — it
would have made R10 a ~40-line diff. The confluence/exit-confluence family
(R9 + R10) is now fully characterized as a proven De Morgan pair: do NOT re-run
either with more members or K values (the mechanism is understood, both null,
the bar is untouched). Any further confluence work needs new OWNER-GATED data,
not more dev-surface votes.
