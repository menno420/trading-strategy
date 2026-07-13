# 2026-07-13 — R3 slice 15: hourly-matrix completion — remaining four Round-3 families × hourly bars (dev-only)

> **Status:** `complete` — the Round-3 hourly TIMEFRAME matrix COMPLETED
> with zero new strategy code: the four Round-3 families the hourly axis
> still lacked (cci_reversion, bollinger_breakout, atr_trailing,
> ichimoku_trend) re-swept on HOURLY bars over the frozen 8-ticker
> universe on the p1-trend-hourly dev rail, mirroring slice 5
> (r3-meanrev-hourly, PR #85) and slice 14 (r3-trend-hourly, PR #94)
> exactly — grids reused VERBATIM by delegation (bar-denominated), NO new
> strategy code, NO new parameter territory, nothing fetched. Every
> Round-3 single-instrument family now has both a daily and an hourly
> lane. Honest outcome **0 PROMOTED / 4 KEEP (dev-candidate only) /
> 28 KILL / 0 INSUFFICIENT-DATA** of 32 lanes — between slice 14's 2/32
> and slice 5's 13/32 on the identical rail and window; max t = 0.90 vs
> the 2.64 bar, three of four KEEPs on the weak META benchmark, no lane
> crosses the negative bar. This slice lands AFTER the Round-3 synthesis
> (PR #89, slices 1-8) and extends the round; the synthesis doc is NOT
> rewritten — its delta is recorded here. This card was born red
> (`in-progress`) and flipped `complete` as the deliberate last content
> change before push; the claim file is deleted in this same commit.

📊 Model: fable-5 · r3-hourly-completion lane (worker session) · start 2026-07-13T04:20Z

💡 **Session idea:** the KEEP rule grades against a benchmark but never
says how hard the grader was — record it. With the hourly matrix now
complete, all 96 lanes of slices 5/14/15 share one byte-identical OOS
window, and the pattern is systematic: the weakest benchmark-Sharpe
tercile yields 12/32 KEEPs, the strongest 3/30; KEEP-lane benchmarks
average OOS Sharpe 0.77 vs 1.13 for KILLs; 3 of this lane's 4 KEEPs sit
on META (B&H 0.494, the second-weakest equity benchmark on the board),
and slice 14's MSFT trix KEEP sat on the weakest (0.148). A
`bench_difficulty` field per sweep record — {`bench_oos_sharpe_rank`
within the lane's slice, `weak_benchmark_keep` flag when a KEEP's
benchmark is in the bottom tercile} — is pure arithmetic on the
`benchmark_oos_metrics` already in every JSON (backfillable by a one-off
script over all merged sweeps, zero new search burden). Payoff: (a) the
Friday grading can separate "beat a strong benchmark" from "cleared a
low bar" — two KEEPs it should read very differently; (b) it makes the
easy-grader bias of any benchmark-relative rule measurable per round
instead of anecdotal ("the familiar weak-benchmark repeat offender" has
appeared in card prose four times now without ever becoming a field);
(c) machine-checkable against history. Not covered by the standing
stack (param_stability, oos_coverage, cost-drag, verdict index,
control_arm_delta, KILL-SIG, round manifest): those grade the
strategy's numbers or the selector's behavior; this one grades the
BENCHMARK's difficulty — the denominator of every verdict, currently
recorded but never ranked.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slice 5 (PR #85) put the four mean-reversion families on hourly
bars; slice 14 (PR #94) mirrored it for the four classic trend/momentum
families. Four Round-3 single-instrument families remained untested
intraday: cci_reversion (slice 4), bollinger_breakout + atr_trailing
(slice 6), ichimoku_trend (slice 8). This slice completes the Round-3
hourly matrix: NO new strategy code, grids reused VERBATIM by delegation
(bar-denominated per the p1-trend-hourly convention), committed hourly
caches only, walk-forward 1008/252 BARS, hourly annualization 1638.
Promotion is CLOSED post-holdout: mostly-KILL is an acceptable outcome
and is recorded as a first-class result.

## Work log

- 2026-07-13T04:20Z — clone hard-synced to origin/main HEAD `882a314`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface"
  lane (slice 15, hourly-matrix completion). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-hourly-completion`; this card + the claim
  `control/claims/2026-07-13-r3-hourly-completion.md` are the born-red
  FIRST commit (`3757e27`), pushed before any build work.
- 2026-07-13T04:22Z — commit `9991941`: Round-3 slice-15 grids declared
  in `trading_lab.sweeps` BEFORE the sweep ran (`R3_HOURLY_COMPLETION_*`):
  each family's declared Round-3 daily 12-variant grid reused VERBATIM by
  **delegating** to the source lane's generator
  (`_R3_HOURLY_COMPLETION_SOURCES` → r3-aroon-cci, r3-breakout,
  r3-trix-ichimoku) — the slice-13/14 convention, so the slice-5
  subset-of-the-published-daily-axes relation degenerates to equality and
  BOTH forms are pinned in
  `tests/test_sweeps.py::TestR3HourlyCompletionGrid` (10 tests: registry
  match, no-new-strategies, matrix-completion pin — slices 5/14/15
  disjoint and jointly covering every Round-3 single-instrument family —
  counts 12 × 4 × 8 = 384, verbatim-equality pin, slice-5-form
  daily-subset check, constraints/frozen-params check, runnability,
  unknown-family, determinism). Bar-denominated per p1-trend-hourly: the
  same numbers mean hours-to-days (cci period 20 ≈ 3 hourly sessions;
  atr_trailing turtle channel 55 ≈ 8.5 sessions; Hosoda 9/26/52 ≈
  1.4/4/8 sessions). The ichimoku senkou displacement stays frozen at 26
  BARS; the slice-6 pure-threshold note carries over (no control arm
  applicable for bollinger_breakout/atr_trailing); cci/ichimoku inherit
  their slice-4/8 committed-grid decisions unchanged. Registry constant
  `R3_HOURLY_COMPLETION_FAMILY` (no strategy code). `config.UNIVERSE`
  untouched.
- 2026-07-13T04:23Z — sweep run
  (`scripts/run_r3_hourly_completion_sweep.py`, modeled on
  `scripts/run_r3_trend_hourly_sweep.py`: committed hourly caches only,
  zero network fetches, `load_ohlcv` default rail with
  `data_end < HOLDOUT_START` additionally asserted per ticker — every
  lane 2023-08-10 → **2025-01-08 20:30**, 2476 bars; costs 5 bps + 1 bp
  per side; hourly annualization 1638; walk-forward 1008/252 BAR
  convention kept decide-and-flag as in the three prior hourly lanes → 5
  splits, stitched OOS 2024-03-07 → 2024-11-22 = 1260 bars ≈ 8.5 months,
  one regime, the SAME window as slices 5/14; 384 registered configs,
  program cumulative 4148 = 3764 prior + 384; first-class
  `INSUFFICIENT-DATA` verdict path present — 0 occurrences: ichimoku's
  78-bar warmup (senkou_b 52 + displacement 26) fits the 1008-bar train
  windows, VERIFIED by every ichimoku lane producing 5 full splits
  rather than assumed; `negative_bar_crossed` recorded per lane per the
  slice-11/13 convention). Honest verdicts (Round-2 KEEP/KILL rule;
  ORDER 007 t-stat at Bonferroni K=12 → min t 2.64, informational only,
  promotion CLOSED):
  - cci_reversion: **7/8 KILL**; KEEP (dev-candidate only) META 1.523 vs
    0.494, t=0.90 — the lane's best t-stat, still nowhere near 2.64.
  - bollinger_breakout: **7/8 KILL**; KEEP META 0.754 vs 0.494, t=0.23.
    Worst family by level: 5 of 8 lanes NEGATIVE OOS Sharpe (long-only
    band breakouts whipsaw at hourly costs).
  - atr_trailing: **8/8 KILL** (best NVDA 1.312 vs 1.387, t=−0.07 — a
    hair short; GLD 0.007 vs 2.056, t=−1.80).
  - ichimoku_trend: **6/8 KILL**; KEEP GOOGL 1.320 vs 1.010, t=0.27 and
    KEEP META 0.583 vs 0.494, t=0.08.
  - Honest pattern: 4/32 (~13%) sits between slice 14's 2/32 (trend) and
    slice 5's 13/32 (reversion) on the identical rail and OOS window,
    consistent in kind with these families' daily lanes (cci 1/12 PR
    #84; bollinger_breakout 2/12 + atr_trailing 1/12 PR #86; ichimoku
    2/12 PR #88) — completing the matrix changed no conclusion. The
    KEEPs do NOT replicate across timeframes: atr_trailing's daily KEEP
    (META) goes KILL here on the same ticker; cci's daily KEEP (SLV)
    goes KILL hourly while its hourly KEEP (META) was a daily KILL. No
    lane crosses t ≤ −2.64 (closest AAPL bollinger_breakout −2.02).
    32 sweep summaries in `experiments/sweeps/r3-hourly-completion/`
    (all `timeframe: "hourly"`, `variants_tried=12`), 32 top-variant
    ledger rows, index rebuilt via `trading_lab.ledger.rebuild_index()`.
    Commit `80eafab`.
- 2026-07-13T04:26Z — verify: `python3 -m pytest -q` → **437 passed**
  (427 on main + 10 new grid tests); pre-flip `bootstrap.py check
  --strict --require-session-log` red ONLY on the designed born-red
  gate. PR **#95** opened READY (non-draft) with the full honest results
  table, the bar-denomination note and the explicit synthesis-scope
  note; one factual error in the first PR body (atr_trailing's daily
  KEEP misremembered as TSLA — it was META) caught against the merged
  r3-breakout JSONs and corrected in place before any review; no merge
  action by this session (auto-merge-enabler is the landing path).
- Round-3 delta recorded here, NOT in the synthesis doc (it is scoped to
  slices 1-8 / PRs #81-#88 with pinned totals): after this slice the
  extended round stands at **3,468 registered configs, 312 graded lanes,
  0 PROMOTED / 64 KEEP-dev / 248 KILL**, program cumulative **4,148**.
- 2026-07-13T04:30Z — flip + claim-delete folded into this final commit.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-trend-hourly.md`,
Status `complete`) landed PR #94 clean and is the direct template of
this session: born-red first commit, grids reused VERBATIM by delegation
with the equality pin in tests, dev rail asserted in-script, synthesis
doc left untouched with the extended-round delta in the card,
flip+claim-delete in one final commit. Its verify block reproduces at
this session's start: 427 passed on main matches its claimed count, and
its "program cumulative 3,764" is what this session's
`PROGRAM_PRIOR_CONFIGS = 3764` anchors to. Three observations from
building on it: (1) its scope note held its promise — the slice-14
sweeps.py comment explicitly declared "a breakout/ichimoku hourly lane
would be its own declared slice", and this session IS that slice; the
matrix-completion test added here (disjointness + joint coverage of all
Round-3 single-instrument families across slices 5/14/15) turns that
prose contract into a pinned invariant. (2) Its 💡 (`param_stability` —
selector churn separates KEEP from KILL) gets fresh corroborating
evidence here in weakened form: NONE of this lane's four KEEPs is a
stable single-param selector (distinct param sets across the 5 splits:
GOOGL ichimoku 2, META bollinger_breakout 3, META ichimoku 3, META cci
4 — computed from the committed `per_split` rows), so its 2/2-vs-0/30
separation on slice 14 does not generalize unmodified — worth knowing before anyone builds the field and trusts it
as a screen; this card's own 💡 (`bench_difficulty`) is deliberately its
complement, grading the benchmark rather than the selector. (3) Its
"regime and timeframe dominate family identity" observation is confirmed
from a new angle: this lane's KEEPs fail to replicate across timeframes
on the SAME tickers (atr_trailing META daily-KEEP → hourly-KILL; cci SLV
daily-KEEP → hourly-KILL). Its work-log SHA prose (`5bc063d` as "HEAD")
was correct at its start time and superseded the same hour by its own
merge — no defect, just a reminder that card SHAs are start-of-session
facts. No defect found in its work.

## Close-out

**Done:** on branch `claude/r3-hourly-completion` (PR #95) —

1. Pre-declared Round-3 slice-15 grids (`src/trading_lab/sweeps.py`,
   `R3_HOURLY_COMPLETION_*`: four remaining families × 12 variants, each
   the source lane's Round-3 daily grid VERBATIM via delegation,
   bar-denominated on hourly bars) + registry constant only, no strategy
   code (`src/trading_lab/strategies/__init__.py`) + 10 grid tests
   (`tests/test_sweeps.py::TestR3HourlyCompletionGrid`, incl. the
   matrix-completion pin).
2. Sweep script `scripts/run_r3_hourly_completion_sweep.py`
   (p1-trend-hourly / slice-5/14 conventions; first-class
   `INSUFFICIENT-DATA` verdict path, 0 occurrences — ichimoku's 78-bar
   warmup verified to fit, not assumed; `negative_bar_crossed` flag per
   the slice-11/13 convention, 0 crossings) + 32 lane summaries under
   `experiments/sweeps/r3-hourly-completion/` + 32 top-variant ledger
   rows (`variants_tried` = 12) + rebuilt `experiments/index.jsonl`.
3. NO new strategy code, NO new data fetches, NO synthesis-doc rewrite
   (delta recorded in this card's work log).
4. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 437 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-hourly-completion.md`
→ exit 0 after this flip (pre-flip the only red was the designed born-red
gate). Integrity at close: dev rail only (every lane
`data_end = 2025-01-08`, asserted per ticker in-script), holdout (SPENT)
untouched, `unlock_holdout` never passed, `data/p5holdout/` untouched,
paper-lane files byte-untouched, `control/inbox.md` + `control/status.md`
+ `control/outbox.md` byte-untouched, no triggers created or modified,
`config.UNIVERSE` untouched, committed caches only (zero network
fetches), no broker/order/exchange code, no promotion/finding language
beyond the recorded KILL/KEEP-dev verdicts, NO merge action taken by
this session.

**Next (guard recipe):** none owed for correctness. Follow-up candidates:
the `bench_difficulty` field (this card's 💡 — with the hourly matrix
complete, 12/32 KEEPs in the weakest benchmark tercile vs 3/30 in the
strongest is now a measurable bias, backfillable from every merged sweep
JSON), then the standing stack (`param_stability` (slice 14's 💡 — with
the caveat recorded above: GOOGL ichimoku KEEPs while churning),
`oos_coverage`, the per-lane cost-drag/breakeven-bps line, sweep-runner
extraction — this script is a THIRTEENTH hand-copy — `control_arm_delta`,
KILL-SIG, the round-scope manifest, graded-unit schema normalization).
The 4 KEEPs are dev-candidates only; any OOS test of them is OWNER-GATED
behind a new pre-registered protocol on post-2026 data, per
docs/research-round-2-results.md and docs/research-round-3-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
