# P5 holdout evaluation protocol — pre-registered, one shot

> **Status:** `binding` — the pre-registered protocol for the first and
> only evaluation against the locked holdout (roadmap P5 per
> [founding-plan.md](founding-plan.md); enforcement contract:
> [holdout-enforcement.md](holdout-enforcement.md)). Written 2026-07-10
> (lane `p5-prep`, QUEUE item 8 prep), BEFORE any unlock and before
> anyone has seen a single holdout number. **This document does NOT
> unlock anything** — see §7. Results land in
> [final-report.md](final-report.md) §Holdout.

## Why pre-registration

The founding plan's multiple-testing discipline exists because the more
you try, the less any single winner means — and the same logic applies
to *interpretation*: a verdict rule chosen after seeing the numbers is
just one more fitted parameter. Everything decision-shaped about the
holdout read — which strategies run, with which parameters, on which
window, and what counts as confirmed vs refuted — is therefore fixed in
this document while the holdout is still sealed. Nothing may be added,
removed, re-tuned, or re-judged afterward. Post-hoc cherry-picking is
prevented by construction: the subject list below is closed, and every
result is reported against its full variants-tried denominator.

## 1. Subjects — the closed list

**Inclusion rule (pre-registered):** every candidate that reached the P2
ledger ([p2-validation-results.md](p2-validation-results.md)) and was
not KILLED there — i.e. the 13 P4 subjects
([p4-transfer-results.md](p4-transfer-results.md)). This is the honest
rule from the founding plan: candidates were nominated by process
(walk-forward P1 sweeps → P2 verdicts), not by anyone's favorite; running
all of them with denominators attached prevents quietly testing only the
prettiest and prevents resurrecting killed ones.

- **PRIMARY subject (1):** `donchian × AAPL × daily` — the sole
  P2 PROMOTED-TO-FINDING (Sharpe 0.619 vs B&H 0.540 on 1980-12-12 →
  2009-12-31 pre-consumption data). The holdout read on the primary is
  the report's headline verdict.
- **SECONDARY subjects (12):** the 12 P2 UNVALIDATABLE-PRE-HOLDOUT
  candidates. For these, the holdout is the *only* unconsumed data that
  exists in their home instrument × timeframe (P1 consumed every
  pre-holdout bar — exact math in p2-validation-results.md), so this is
  their first and last out-of-selection test. All 12 run; all 12 are
  reported, each against its P1 lane's variants-tried burden.
- **EXCLUDED (1):** `pullback × GOOGL × daily` — KILLED at P2. Killed
  candidates stay dead; the holdout is not an appeals court.

Context carried into interpretation (pre-registered, so it cannot be
invented later): all 13 subjects TRANSFER-FAILED at P4 (13/99 pairs beat
B&H; the primary failed 1/8), which sharpens the prior *against* every
subject before the holdout is read.

## 2. Frozen parameters — verbatim, zero tuning

Each subject runs its `top_full_period_variant` parameters exactly as
recorded in its P1 sweep JSON — the same frozen vectors P2 and P4 used.
Copied verbatim below; source file cited per row (field:
`top_full_period_variant.params` in each JSON). Any mismatch between
this table and the sweep JSON at run time is a protocol violation: stop,
do not run.

| # | Subject (family × ticker × tf) | Frozen params (verbatim) | Source (experiments/sweeps/…) |
|---|---|---|---|
| P | donchian × AAPL × daily | `{"entry": 15, "exit": 5}` | p1-trend-following-daily/donchian__AAPL.json |
| S1 | sma_crossover × META × daily | `{"fast": 15, "slow": 75}` | p1-trend-following-daily/sma_crossover__META.json |
| S2 | ema_crossover × META × daily | `{"fast": 25, "slow": 50}` | p1-trend-following-daily/ema_crossover__META.json |
| S3 | donchian × META × daily | `{"entry": 55, "exit": 55}` | p1-trend-following-daily/donchian__META.json |
| S4 | supertrend_flip × BTC-USD × daily | `{"ema_len": 200, "macd_fast": 12, "macd_signal": 9, "macd_slow": 26, "st_mult": 2.0, "st_period": 14}` | p1-video-strategy-daily/supertrend_flip__BTC-USD.json |
| S5 | macd_supertrend × BTC-USD × daily | `{"ema_len": 100, "macd_fast": 12, "macd_signal": 9, "macd_slow": 26, "st_mult": 2.0, "st_period": 14}` | p1-video-strategy-daily/macd_supertrend__BTC-USD.json |
| S6 | rsi_mean_reversion × META × daily | `{"overbought": 50, "oversold": 10, "period": 2}` | p1-mean-reversion-daily/rsi_mean_reversion__META.json |
| S7 | pullback × META × daily | `{"entry_lookback": 7, "exit_len": 7, "trend_len": 100}` | p1-mean-reversion-daily/pullback__META.json |
| S8 | sma_crossover × GOOGL × hourly | `{"fast": 10, "slow": 75}` | p1-trend-hourly/sma_crossover__GOOGL.json |
| S9 | ema_crossover × GOOGL × hourly | `{"fast": 20, "slow": 50}` | p1-trend-hourly/ema_crossover__GOOGL.json |
| S10 | donchian × GOOGL × hourly | `{"entry": 40, "exit": 40}` | p1-trend-hourly/donchian__GOOGL.json |
| S11 | donchian × AMZN × hourly | `{"entry": 40, "exit": 40}` | p1-trend-hourly/donchian__AMZN.json |
| S12 | macd × META × hourly | `{"fast": 5, "signal": 5, "slow": 26}` | p1-trend-hourly/macd__META.json |

Notes carried forward verbatim from the earlier phases: S10 and S11
share a frozen vector, so they are not independent evidence; S12 was
P1-flagged the least trustworthy candidate (fastest grid corner,
unstable per-split Sharpes).

## 3. Engine settings (identical to every prior phase)

- **Fills:** t+1-open — a signal computed on bar *t* executes at the
  next bar's open (engine default; no-lookahead rule).
- **Costs:** 5 bps slippage + 1 bps commission per side (engine
  defaults). Net-of-cost metrics only.
- **Position model:** long/flat, as in P1/P2/P4; no leverage, no shorts.
- **Benchmark:** buy-and-hold of the same instrument over the *exact
  same* holdout window as each subject, same costs, computed per
  subject.
- **Metrics:** the standard ledger set (Sharpe, Sortino, max drawdown,
  CAGR, win rate, turnover, n_trades), annualization per the lane
  conventions already ledgered (252 for daily, 252 × 6.5 for hourly;
  BTC-USD daily keeps the 252 convention with the same understatement
  caveat recorded in p1-video-strategy-results.md — it cancels in the
  vs-B&H comparison).
- **Evaluation shape:** single full-window frozen-parameter run per
  subject (the P2/P4 precedent: walk-forward is degenerate for a
  single-variant grid — there is no selection left to do). One backtest
  per subject + one B&H benchmark per subject: 13 subject runs, 0 new
  variants (`variants_tried = 1` per ledger row, with the P1 lane
  burden reported alongside — §6).

## 4. The holdout window — exact

- **Start: 2025-01-09** (= `HOLDOUT_START` in `src/trading_lab/config.py`,
  pinned by `tests/test_data.py::test_holdout_constant_unchanged`).
- **End: the last bar available at evaluation time** for each subject's
  instrument × timeframe, fetched through the repo's standard path
  (`trading_lab.data.fetch_ohlcv` then `load_ohlcv(...,
  unlock_holdout=True)` — the ONLY load path permitted, per the
  residual-bypass rule in holdout-enforcement.md; no ad-hoc reads of
  `data/**`).
- **Hourly contingency (pre-registered):** Yahoo's hourly history has a
  moving ~35-month floor (NEXT-BOOT known wall). If, at evaluation time,
  hourly bars are no longer obtainable back to 2025-01-09, the hourly
  subjects (S8–S12) run on the obtainable window `max(2025-01-09,
  earliest obtainable bar) → data end`, and the report must state the
  actual window per subject. A shortened window is reported as-is —
  never padded, never substituted with a different timeframe. If an
  hourly subject's obtainable window contains fewer than 250 bars
  (< ~2 trading weeks of hourly data), its verdict is recorded as
  **NOT-EVALUABLE** rather than pretending a read.
- Indicator warm-up may use pre-holdout bars (they are dev data, already
  consumed); *scored* returns begin at the first holdout-window fill.

## 5. Pre-registered verdict rules — written before any holdout number exists

Judged exactly the way P2 promotion was judged (net-of-cost Sharpe vs
B&H over the same window), so the standard cannot drift:

- **PRIMARY (AAPL-donchian): CONFIRMED** iff strategy Sharpe > B&H
  Sharpe on the holdout window, net of costs. **REFUTED** otherwise
  (including ties and including "positive absolute return but below
  B&H" — the benchmark is holding, per the founding plan). No secondary
  metric can rescue or overturn this verdict; Sortino/MDD/CAGR are
  reported as color, not as criteria.
- **Each SECONDARY: HOLDOUT-BEAT** iff strategy Sharpe > B&H Sharpe on
  its holdout window, net of costs; **HOLDOUT-MISS** otherwise;
  **NOT-EVALUABLE** only via the §4 hourly-contingency rule. Secondary
  verdicts are *descriptive*, not promotions: with 12 secondaries drawn
  from lanes that tried 92–177 configurations each, some HOLDOUT-BEATs
  are expected by chance, and no secondary becomes a "finding" from a
  single holdout beat. The aggregate line to report is
  `k of 12 secondaries beat B&H` next to the full selection burden
  (§6), plus the pre-registered null: under the pre-holdout base rates
  (7/32, 3/24, 5/32 lanes beating B&H; 13/99 at P4), several beats out
  of 12 are unremarkable.
- **Interpretation guard:** verdicts are computed mechanically from the
  ledgered numbers by the rules above. If a rule turns out to be
  ambiguous in some edge case, the resolution must be the one *less
  favorable* to the strategy, and the ambiguity must be documented in
  the report.

## 6. Reporting rules

- Every reported result carries its **variants-tried denominator**: the
  subject's `variants_tried = 1` for the holdout run itself PLUS the P1
  lane burden behind the candidate (177 trend-daily, 92 video, 144
  mean-reversion-daily, 177 trend-hourly configurations, plus per-split
  re-selection as documented in each P1 doc), and the program-wide
  total of 13 subjects read on the holdout.
- All 13 verdicts are published in [final-report.md](final-report.md)
  §Holdout — beats and misses alike, no omissions, ledger rows cited.
- **One shot, then final.** After the holdout numbers are read: no
  further tuning, no re-runs, no parameter changes, no new variants, no
  strategy modifications, no "let's just check one more window" —
  ever. The holdout is spent the moment it is read; any subsequent
  optimization against it would be in-sample by definition. The report
  is then final. Follow-on research would require genuinely new data
  (post-2026 bars accruing beyond the evaluated window) and a new
  pre-registered protocol — an owner decision, out of scope here.

## 7. Mechanical unlock steps — owner-gated

Semantics per [holdout-enforcement.md](holdout-enforcement.md). This
protocol document does **not** unlock anything; writing it, merging it,
and reading it leave the holdout exactly as sealed as before. The
unlock is an explicit OWNER action (⚑, click-level), flagged in
`control/status.md`:

1. **Owner gate (the click):** the owner authorizes the one-shot
   evaluation explicitly — a new ORDER in `control/inbox.md` (the
   manager/owner is that file's sole writer) naming this protocol doc
   as the binding procedure. No session may infer authorization from
   anything less: not from this doc existing, not from QUEUE item 8,
   not from a status flag.
2. **The evaluating session** (a later, dedicated session — not the
   session that wrote this doc) re-reads this protocol at HEAD,
   verifies the frozen-param table against the sweep JSONs (§2), then
   and only then:
   - fetches fresh bars through `trading_lab.data.fetch_ohlcv` (the raw
     cache is allowed to contain holdout bars; the rail is at load
     time);
   - loads them with `load_ohlcv(..., unlock_holdout=True)` — the
     P5-only kwarg, which emits `HoldoutViolationWarning` (expected and
     correct here, and ONLY here);
   - writes every holdout ledger row with `holdout_unlocked=True`,
     which stamps a visible `"holdout_unlocked": true` marker into each
     run file; `rebuild_index` propagates it into
     `experiments/index.jsonl`. **Every ledger row for a holdout run
     MUST carry this marker** — rows self-declare forever that the
     holdout was used, and the CI audit
     (`tests/test_ledger.py::TestCommittedLedgerAudit`) fails any
     post-boundary row without it.
3. **Scope of the unlock:** exactly the 13 runs (+ 13 B&H benchmarks)
   of §1–§3, once each. The unlock kwargs appear nowhere else; any
   `HoldoutViolationWarning` or `holdout_unlocked` marker outside that
   session is a violation per the enforcement contract.
4. **Afterward:** results into final-report.md §Holdout, verdicts by
   §5, denominators by §6, report final. The evaluating session's card
   and status record that the holdout was consumed.
