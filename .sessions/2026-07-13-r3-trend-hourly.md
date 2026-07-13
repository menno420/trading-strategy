# 2026-07-13 — R3 slice 14: Round-3 trend/momentum families × hourly bars (dev-only)

> **Status:** `complete` — the TIMEFRAME axis extended to the Round-3
> TREND side with zero new strategy code: the four Round-3 trend/momentum
> families (roc_momentum, adx_filtered_sma, aroon_trend, trix_momentum)
> re-swept on HOURLY bars over the frozen 8-ticker universe on the
> p1-trend-hourly dev rail, mirroring slice 5 (r3-meanrev-hourly, PR #85)
> exactly — grids reused VERBATIM by delegation (bar-denominated), NO new
> strategy code, NO new parameter territory, nothing fetched. Honest
> outcome **0 PROMOTED / 2 KEEP (dev-candidate only) / 30 KILL /
> 0 INSUFFICIENT-DATA** of 32 lanes — the LOWEST KEEP rate of any Round-3
> lane and the mirror image of slice 5's 13/32 on the identical rail and
> window; max t = 0.13 vs the 2.64 bar, both KEEPs razor-thin, no lane
> crosses the negative bar. This slice lands AFTER the Round-3 synthesis
> (PR #89, slices 1-8) and extends the round; the synthesis doc is NOT
> rewritten — its delta is recorded here. This card was born red
> (`in-progress`) and flipped `complete` as the deliberate last content
> change before push; the claim file is deleted in this same commit.

📊 Model: fable-5 · r3-trend-hourly lane (worker session) · start 2026-07-13T04:05Z

💡 **Session idea:** the walk-forward already knows which lanes are
selector-churn and never says so — record it. Every sweep JSON carries a
`per_split` table with the params each train window chose, but no field
summarizes it, so the single most diagnostic fact about this lane is
invisible unless you count by hand: across its 32 lanes only TWO chose
the SAME variant in all 5 splits — and those two are EXACTLY the two
KEEPs (aroon_trend GLD, trix_momentum MSFT; every one of the 30 KILLs
re-selected params mid-stream, mean 3.1 distinct param sets per 5
splits; slice 5's meanrev lanes churn identically at 3.2). A
`param_stability` block per sweep record — {`n_distinct_param_sets`,
`modal_params`, `modal_share`} — is pure arithmetic on the `per_split`
rows already in every existing JSON (backfillable by a one-off script,
zero new search burden, ~5 lines in the sweep scripts or free with the
long-owed runner extraction). Payoff: (a) separates "stable rule that
honestly loses" from "the selector never converged" — two KILLs the
Friday grading should read very differently; (b) gives KEEP triage a
free robustness screen (a KEEP with 5 distinct param sets is
selection-luck on its face; both of this lane's KEEPs pass, which is
worth knowing even though their t-stats say noise); (c) machine-checkable
against history: recompute from `per_split` in any merged sweep JSON and
compare. Not covered by the standing idea stack (cost-drag, verdict
index, control_arm_delta, KILL-SIG, oos_coverage, round manifest): those
grade the OUTPUT numbers; this one grades the SELECTOR's behavior, a
column the lab currently throws away.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slice 5 (PR #85) expanded the timeframe axis for the four
mean-reversion families; the four Round-3 TREND-side single-instrument
families (roc_momentum, adx_filtered_sma from slice 2; aroon_trend from
slice 4; trix_momentum from slice 8) had never run on hourly bars. This
slice completes that mirror: NO new strategy code, grids reused VERBATIM
(bar-denominated per the p1-trend-hourly convention), committed hourly
caches only, walk-forward 1008/252 BARS, hourly annualization 1638.
Promotion is CLOSED post-holdout: mostly-KILL was the expected outcome
and is recorded as a first-class result.

## Work log

- 2026-07-13T04:05Z — clone hard-synced to origin/main HEAD `5bc063d`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface"
  lane (slice 14, trend-side timeframe expansion). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-trend-hourly`; this card + the claim
  `control/claims/2026-07-13-r3-trend-hourly.md` are the born-red FIRST
  commit (`d5de0e1`), pushed before any build work.
- 2026-07-13T04:07Z — commit `8e5b1d6`: Round-3 slice-14 grids declared
  in `trading_lab.sweeps` BEFORE the sweep ran (`R3_TREND_HOURLY_*`):
  each family's declared Round-3 daily 12-variant grid reused VERBATIM by
  **delegating** to the source lane's generator
  (`_R3_TREND_HOURLY_SOURCES` → r3-roc-adx, r3-aroon-cci,
  r3-trix-ichimoku) — the slice-13 convention, so the slice-5
  subset-of-the-published-daily-axes relation degenerates to equality and
  BOTH forms are pinned in
  `tests/test_sweeps.py::TestR3TrendHourlyGrid` (9 tests: registry match,
  no-new-strategies, counts 12 × 4 × 8 = 384, verbatim-equality pin,
  slice-5-form daily-subset check, constraints/frozen-params/control-arms
  check, runnability, unknown-family, determinism). Bar-denominated per
  p1-trend-hourly: the same numbers mean hours-to-days (roc lookback 252
  bars ≈ 38.8 hourly sessions ≈ 2 months; adx slow 200 ≈ 31 sessions;
  trix period 15 ≈ 2.3 sessions). ADX period 14 stays frozen; the
  committed control arms (aroon entry==exit==0, trix signal_period==0)
  are inherited unchanged. Registry constant `R3_TREND_HOURLY_FAMILY`
  (no strategy code). `config.UNIVERSE` untouched.
- 2026-07-13T04:09Z — sweep run (`scripts/run_r3_trend_hourly_sweep.py`,
  modeled on `scripts/run_r3_meanrev_hourly_sweep.py`: committed hourly
  caches only, zero network fetches, `load_ohlcv` default rail with
  `data_end < HOLDOUT_START` additionally asserted per ticker — every
  lane 2023-08-10 → **2025-01-08 20:30**, 2475-2476 bars; costs 5 bps +
  1 bp per side; hourly annualization 1638; walk-forward 1008/252 BAR
  convention kept decide-and-flag as in p1-trend-hourly/slice 5 → 5
  splits, stitched OOS 2024-03-07 → 2024-11-22 = 1260 bars ≈ 8.5 months,
  one regime, the SAME window as slice 5; 384 registered configs, program
  cumulative 3764 = 3380 prior + 384; first-class `INSUFFICIENT-DATA`
  verdict path present — 0 occurrences; `negative_bar_crossed` recorded
  per lane per the slice-11/13 convention). Honest verdicts (Round-2
  KEEP/KILL rule; ORDER 007 t-stat at Bonferroni K=12 → min t 2.64,
  informational only, promotion CLOSED):
  - roc_momentum: **8/8 KILL** (best NVDA 1.115 vs 1.387, t=−0.24; GLD
    1.809 vs 2.056, t=−0.22).
  - adx_filtered_sma: **8/8 KILL** (best GLD 1.933 vs 2.056, t=−0.11;
    META 0.460 vs 0.494, t=−0.03 — a hair short).
  - aroon_trend: **7/8 KILL**; KEEP (dev-candidate only) GLD 2.068 vs
    2.056, t=0.01 — razor-thin over the strongest benchmark on the board.
  - trix_momentum: **7/8 KILL**; KEEP MSFT 0.298 vs 0.148, t=0.13 — the
    familiar weak-benchmark repeat offender.
  - Honest pattern: 2/32 (~6%) is the LOWEST KEEP rate of any Round-3
    lane, the mirror image of slice 5's 13/32 on the identical rail and
    OOS window — intraday, these reversion grids looked less bad and
    these trend grids look worse; consistent in kind with p1-trend-hourly
    (5/32) and the same families' daily lanes (roc/adx 2/16, aroon 1/12,
    trix 4/12). No lane crosses t ≤ −2.64 (closest AAPL trix −2.08). The
    bar-denominated convention's cost is starkest for roc_momentum:
    lookback 252 bars is ~2 months on hourly bars, so "annual momentum"
    was never what ran here — the lane measures the convention, honestly,
    and the convention loses. 32 sweep summaries in
    `experiments/sweeps/r3-trend-hourly/` (all `timeframe: "hourly"`,
    `variants_tried=12`), 32 top-variant ledger rows, index rebuilt via
    `trading_lab.ledger.rebuild_index()`. Commit `81c8b37`.
- 2026-07-13T04:11Z — verify: `python3 -m pytest -q` → **427 passed**
  (418 on main + 9 new grid tests); pre-flip `bootstrap.py check --strict
  --require-session-log` red ONLY on the designed born-red gate. PR **#94**
  opened READY (non-draft) with the full honest results table, the
  bar-denomination note and the explicit synthesis-scope note; no merge
  action by this session (auto-merge-enabler is the landing path).
- Round-3 delta recorded here, NOT in the synthesis doc (it is scoped to
  slices 1-8 / PRs #81-#88 with pinned totals): after this slice the
  extended round stands at **3,084 registered configs, 280 graded lanes,
  0 PROMOTED / 60 KEEP-dev / 220 KILL**, program cumulative **3,764**.
- 2026-07-13T04:14Z — flip + claim-delete folded into this final commit.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-btc-coverage.md`,
Status `complete`) landed PR #93 clean and is, with slice 5's card, the
direct template of this session: born-red first commit, grids reused
VERBATIM by delegation with the equality pin in tests, dev rail asserted
in-script, synthesis doc left untouched with the extended-round delta in
the card, flip+claim-delete in one final commit. Its verify block
reproduces at this session's start: 418 passed on main matches its
claimed count, and its "program cumulative 3,380" is what this session's
`PROGRAM_PRIOR_CONFIGS = 3380` anchors to. Three observations from
building on it: (1) its 💡 (`oos_coverage` — the walk-forward silently
discards the newest dev bars) is precisely quantifiable on this lane and
still unimplemented: (2476 − 1008) mod 252 = 208 hourly bars, so every
lane here is blind to ~2024-11-22 → 2025-01-08, exactly as it predicted;
this card's own 💡 is deliberately its sibling (both are one-field
summaries of per_split/window facts the JSONs already contain but never
surface). (2) Its family-split observation (trend/momentum beat
oscillators on decade-trending BTC daily) does NOT carry to this rail:
the same four trend families that went 5/7 KEEP there go 2/32 here while
slice 5's reversion went 13/32 — regime and timeframe dominate family
identity, one more reason none of these dev-KEEPs deserve belief before
a real OOS protocol. (3) Its note that `adx_filtered_sma` inherits a
gate with no committed neutral arm applies verbatim here too (verbatim
reuse faithfully inherits the slice-2 decision) — this lane likewise
cannot say whether the ADX gate helps on hourly bars, only that the
gated composite goes 0/8; inherited and noted, not patched, same honest
choice. No defect found in its work.

## Close-out

**Done:** on branch `claude/r3-trend-hourly` (PR #94) —

1. Pre-declared Round-3 slice-14 grids (`src/trading_lab/sweeps.py`,
   `R3_TREND_HOURLY_*`: four trend/momentum families × 12 variants, each
   the source lane's Round-3 daily grid VERBATIM via delegation,
   bar-denominated on hourly bars; breakout/ichimoku out of scope with
   the reason stated in the section comment) + registry constant only,
   no strategy code (`src/trading_lab/strategies/__init__.py`) + 9 grid
   tests (`tests/test_sweeps.py::TestR3TrendHourlyGrid`).
2. Sweep script `scripts/run_r3_trend_hourly_sweep.py` (p1-trend-hourly /
   slice-5 conventions; first-class `INSUFFICIENT-DATA` verdict path,
   0 occurrences; `negative_bar_crossed` flag per the slice-11/13
   convention, 0 crossings) + 32 lane summaries under
   `experiments/sweeps/r3-trend-hourly/` + 32 top-variant ledger rows
   (`variants_tried` = 12) + rebuilt `experiments/index.jsonl`.
3. NO new strategy code, NO new data fetches, NO synthesis-doc rewrite
   (delta recorded in this card's work log).
4. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 427 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-trend-hourly.md`
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
the `param_stability` block (this card's 💡 — on this lane
selector-stability separates KEEP from KILL 2/2 vs 0/30, backfillable
from every merged sweep JSON), then the standing stack (`oos_coverage`
(slice 13's 💡 — 208 tail bars unscored per lane here), the per-lane
cost-drag/breakeven-bps line (slice 5's 💡 — the 6 bps/side default binds
hardest on exactly these hourly lanes), sweep-runner extraction — this
script is a TWELFTH hand-copy — `control_arm_delta`, KILL-SIG, the
round-scope manifest, graded-unit schema normalization). The 2 KEEPs are
dev-candidates only; any OOS test of them is OWNER-GATED behind a new
pre-registered protocol on post-2026 data, per
docs/research-round-2-results.md and docs/research-round-3-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
