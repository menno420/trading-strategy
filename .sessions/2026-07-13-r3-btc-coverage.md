# 2026-07-13 — R3 slice 13: Round-3 families × BTC-USD coverage (dev-only)

> **Status:** `complete` — the ten single-instrument families Round 3
> added (stochastic_reversion, williams_r_reversion, roc_momentum,
> adx_filtered_sma, aroon_trend, cci_reversion, bollinger_breakout,
> atr_trailing, trix_momentum, ichimoku_trend) swept on BTC-USD daily
> with their declared Round-3 12-variant grids reused VERBATIM (by
> delegation — the grids cannot drift); NO new strategy code, NO new
> parameter territory, nothing fetched. None of these families had ever
> run on BTC-USD. Honest outcome **0 PROMOTED / 5 KEEP (dev-candidate
> only) / 5 KILL** of 10 lanes — a clean family split: all three
> oscillator mean-reversion families KILL hard on the decade-trending
> asset, the trend/momentum/breakout families edge past a STRONG B&H
> benchmark (0.821), max t = 1.38 vs the 2.64 bar — deep inside noise.
> This slice lands AFTER the Round-3 synthesis (PR #89, slices 1-8) and
> extends the round; the synthesis doc is NOT rewritten — its delta is
> recorded here. This card was born red (`in-progress`) and flipped
> `complete` as the deliberate last content change before push; the
> claim file is deleted in this same commit.

📊 Model: fable-5 · r3-btc-coverage lane (worker session) · start 2026-07-13T03:51Z

💡 **Session idea:** the walk-forward silently discards the freshest dev
bars, and nobody is told. `walk_forward` builds contiguous 252-bar test
windows after the 1008-bar warmup and drops the tail remainder — on this
slice that is (3767 − 1008) mod 252 = **239 bars**: every lane's stitched
OOS ends 2024-05-14 while the dev rail runs to 2025-01-08, so the entire
2024-H2 BTC run — the freshest, most regime-relevant dev data — was never
scored by ANY reported number, and the sweep JSON nowhere says so (a
reader must diff `walk_forward.oos_end` against `data_end` and know the
modulo rule). The same discard happens on every daily lane (for the all-8
universe it is (n−1008) mod 252 per ticker) and it is always the NEWEST
bars — the systematically-worst bars to be blind on. Add an
`oos_coverage` block to every sweep record, computed at sweep time:
{`discarded_tail_bars`, `discarded_tail_start/end`, `dev_bars_scored_pct`}
— pure arithmetic on values already in the record, zero new search
burden — and optionally a declared-in-advance final SHORT split (test =
the remainder, flagged as sub-standard-width) so the tail at least
appears in the per-split table. Payoff: (a) "how much of the dev rail
does this OOS number actually cover?" becomes a machine-readable field
instead of modulo archaeology; (b) stale-tail blindness stops compounding
as caches grow (every re-fetch moves the discard window); (c) any future
regime-shift claim can be checked against whether the shift's bars were
even scored. Machine-checkable: recompute `discarded_tail_bars` from
`n_bars`, `train_size`, `test_size` in any existing sweep JSON and
compare `oos_end` + tail = `data_end`.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." The committed BTC-USD daily cache (P1 video lane; dev rail
2014-09-17 → 2025-01-08, 3767 bars) had only ever been swept by the
video-lane families (supertrend_flip, macd_supertrend, the dual-EMA
control), the R2 §3b keltner_breakout arm and the P4 transfer spot
checks — the TEN single-instrument families Round 3 added had NEVER run
on it. This slice completes that coverage, the BTC-USD counterpart of
slices 10-12's new-tickers coverage. The eleventh Round-3 family,
xsec_momentum, is deliberately OUT of scope: a cross-sectional basket
strategy whose expanded lane (slice 9) explicitly excludes BTC-USD over
the calendar-mixing problem (crypto trades 7 days/week). Backtests run on
the default `load_ohlcv` dev rail (holdout ≥ 2025-01-09 excluded; the
holdout is SPENT). Promotion is CLOSED post-holdout: mostly-KILL is an
acceptable outcome and is recorded as a first-class result.

## Work log

- 2026-07-13T03:51Z — clone hard-synced to origin/main HEAD `2a1fa22`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface"
  lane (slice 13, Round-3 families × BTC-USD coverage). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-btc-coverage`; this card + the claim
  `control/claims/2026-07-13-r3-btc-coverage.md` are the born-red FIRST
  commit (`b10f8e2`), pushed before any build work.
- 2026-07-13T03:53Z — grids declared in `trading_lab.sweeps` BEFORE the
  sweep ran (`R3_BTC_COVERAGE_*`): each of the ten families' Round-3
  12-variant grids reused VERBATIM by **delegating** to the source lane's
  generator (`_R3_BTC_COVERAGE_SOURCES` → r3-stoch-willr, r3-roc-adx,
  r3-aroon-cci, r3-breakout, r3-trix-ichimoku) — byte-identical grids by
  construction, equality per family pinned in
  `tests/test_sweeps.py::TestR3BtcCoverageGrid` (7 tests) along with the
  pinned 10-family set, counts (12 × 10 × 1 = 120), instrument
  lane-locality and runnability. `config.UNIVERSE` untouched. Commit
  `bbc7610`.
- 2026-07-13T03:55Z — sweep run (`scripts/run_r3_btc_coverage.py`,
  modeled on `scripts/run_r3_trend_new_tickers.py`: `load_ohlcv` default
  rail with `data_end ≤ 2025-01-08` ASSERTED — actual 2025-01-08 exactly;
  costs 5 bps + 1 bp per side; walk-forward 1008/252 contiguous stitched
  OOS vs same-window same-cost B&H; 120 registered configs, program
  cumulative 3380 = 3260 prior + 120). **Calendar/annualization** follows
  the existing BTC-USD lanes' (P1 video sweep) convention VERBATIM,
  recorded in every sweep JSON as `annualization_note`: BTC trades ~365
  days/year but metrics use the lab-wide `PERIODS_PER_YEAR["daily"] =
  252`, so annualized Sharpe/CAGR are UNDERSTATED by a constant factor
  for strategy and benchmark alike — same-window comparisons unaffected;
  flagged, not patched. The 1008/252-BAR windows span ~2.8/~0.7 calendar
  years on BTC (7-day weeks) rather than ~4/~1. **One new B&H ledger
  row** (variants_tried=1): BTC-USD had NO buy-and-hold baseline on the
  ledger — the P1 video lane predates the slice-3 baseline convention —
  recorded once here (a benchmark, not a searched config).
  Honest verdicts (Round-2 KEEP/KILL rule; ORDER 007 t-stat at Bonferroni
  K = 12 → min t 2.64, informational only, promotion CLOSED; all lanes
  share the stitched OOS window 2017-06-21 → 2024-05-14, 10 splits, 2520
  bars, B&H OOS Sharpe 0.821):
  - Oscillator mean-reversion: **3/3 KILL** — stochastic_reversion 0.022
    (t=−2.53), cci_reversion 0.151 (t=−2.12), williams_r_reversion 0.247
    (t=−1.81). Fading a decade-trending asset loses badly.
  - Trend/momentum/breakout: **5/7 KEEP (dev-candidate only)** —
    bollinger_breakout 1.258 (t=1.38, the slice's best), trix_momentum
    1.024 (t=0.64), ichimoku_trend 1.020 (t=0.63), roc_momentum 0.913
    (t=0.29), atr_trailing 0.901 (t=0.25); adx_filtered_sma 0.771
    (t=−0.16) and aroon_trend 0.773 (t=−0.15) KILL by a hair.
  - Honest pattern: this slice BREAKS the weak-benchmark clustering of
    slices 10-12 (whose KEEPs sat exclusively on XOM 0.294 / TLT 0.196) —
    here 5 KEEPs beat a STRONG 0.821 benchmark. Max t = 1.38 vs 2.64:
    deep inside noise; NOT findings, nothing promoted. Per the slice-11
    convention the script records a `negative_bar_crossed` flag per lane:
    **no lane crosses t ≤ −2.64** — stochastic_reversion at −2.53 is the
    closest non-crossing in slices 10-13 (slice 11's TSLA rsi −3.01
    remains the only crossing).
  - 10 sweep summaries in `experiments/sweeps/r3-btc-coverage/`, 10
    top-variant ledger rows (`variants_tried` = 12) + 1 B&H baseline row,
    index rebuilt via `trading_lab.ledger.rebuild_index()`. Commit
    `0438bcb`.
- 2026-07-13T03:57Z — verify: `python3 -m pytest -q` → **418 passed**
  (411 on main + 7 new grid tests); pre-flip `bootstrap.py check --strict
  --require-session-log` red ONLY on the designed born-red gate. PR **#93**
  opened READY (non-draft) with the full honest results table, the
  calendar/annualization convention note, the xsec scope note and the
  explicit synthesis-scope note; no merge action by this session
  (auto-merge-enabler is the landing path).
- Round-3 delta recorded here, NOT in the synthesis doc (it is scoped to
  slices 1-8 / PRs #81-#88 with pinned totals): after this slice the
  extended round stands at **2,700 registered configs, 248 graded lanes,
  0 PROMOTED / 58 KEEP-dev / 190 KILL**, program cumulative **3,380**.
- 2026-07-13T04:00Z — flip + claim-delete folded into this final commit.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-gated-new-tickers.md`,
Status `complete`) landed PR #92 clean and is the direct template of this
session: born-red first commit, grids pre-declared with relations pinned
by tests, dev rail asserted, synthesis doc left untouched with the
extended-round delta in the card, flip+claim-delete in one final commit.
Its verify block reproduces at this session's start: 411 passed on main
matches its claimed count, and its "program cumulative 3,260" is what
this session's `PROGRAM_PRIOR_CONFIGS = 3260` is anchored to. Three
observations from building on it: (1) its close-out lists the
sweep-runner extraction as hand-copied "a TENTH time" — this session
partially answered the adjacent drift risk on the GRID side by
delegating to the source generators instead of hand-copying axes dicts
(equality is now structural, the test pin is belt-and-braces), but the
~250-line runner script is still a hand-copy, an ELEVENTH time; the
extraction remains the top structural follow-up. (2) Its 💡
(`control_arm_delta` for gated grids) is unimplemented and this slice
shows the convention gap it sits on: `adx_filtered_sma` is a gated family
whose slice-2 grid committed NO gate-off neutral arm (unlike
vol_filtered_trend's slice-12 grid), and verbatim reuse faithfully
inherits that — this lane cannot say whether the ADX gate helps or hurts
on BTC-USD, only that the gated composite KILLs by a hair; adding an arm
would have broken verbatim reuse, so the honest choice was to inherit
and note it. (3) Its KILL-SIG lineage note (slice 11's 💡) gets another
clean boundary case here: stochastic_reversion at t=−2.53 would still
grade plain KILL under KILL-SIG (bar −2.64) — the class keeps
discriminating exactly where intended. No defect found in its work; its
weak-benchmark-clustering framing was a genuinely useful prior that this
slice then HONESTLY broke (5 KEEPs on a strong 0.821 benchmark) — a
reminder that the pattern was an observation, not a law.

## Close-out

**Done:** on branch `claude/r3-btc-coverage` (PR #93) —

1. Pre-declared Round-3 slice-13 grids (`src/trading_lab/sweeps.py`,
   `R3_BTC_COVERAGE_*`: ten families × 12 variants, each the source
   lane's Round-3 grid VERBATIM via delegation; xsec_momentum out of
   scope with the reason stated) + tests
   (`tests/test_sweeps.py::TestR3BtcCoverageGrid`, 7 tests).
2. Sweep script `scripts/run_r3_btc_coverage.py` (dev rail asserted;
   video-lane annualization convention recorded per JSON;
   `negative_bar_crossed` flag per the slice-11 convention) + 10 lane
   summaries under `experiments/sweeps/r3-btc-coverage/` + 10
   top-variant ledger rows (`variants_tried` = 12) + the single BTC-USD
   B&H baseline row (previously absent from the ledger) + rebuilt
   `experiments/index.jsonl`.
3. NO new strategy code, NO new data fetches, NO synthesis-doc rewrite
   (delta recorded in this card's work log).
4. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 418 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-btc-coverage.md`
→ exit 0 after this flip (pre-flip the only red was the designed born-red
gate). Integrity at close: dev rail only (`data_end = 2025-01-08`,
asserted in-script), holdout (SPENT) untouched, `unlock_holdout` never
passed, `data/p5holdout/` untouched, paper-lane files byte-untouched,
`control/inbox.md` + `control/status.md` + `control/outbox.md`
byte-untouched, no triggers created or modified, no market data fetched,
no broker/order/exchange code, no promotion/finding language beyond the
recorded KILL/KEEP-dev verdicts, NO merge action taken by this session.

**Next (guard recipe):** none owed for correctness. Follow-up candidates:
the `oos_coverage` block (this card's 💡 — pure arithmetic on fields
already in every sweep JSON; 239 of BTC-USD's freshest dev bars were
never scored by any walk-forward window), then the standing stack
(sweep-runner extraction — now an eleventh hand-copy —
`control_arm_delta` (slice 12's 💡), KILL-SIG (slice 11's 💡), the
round-scope manifest (slice 10's 💡), graded-unit schema normalization,
walk-forward warm-history fix, provenance sidecar). The 5 KEEPs are
dev-candidates only; any OOS test of them is OWNER-GATED behind a new
pre-registered protocol on post-2026 data, per
docs/research-round-2-results.md and docs/research-round-3-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
