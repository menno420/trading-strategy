# Research Program Retrospective — Rounds 1–6

> **Status:** `reference`
>
> Written 2026-07-14 (UTC). Synthesis of the research program from the
> founding plan through Round 6, against repo state origin/main
> `3b7a52e6c9cfaacd039ac2d25f5500f0ddf79e6a` (cited below as `@3b7a52e`).
> Docs only: this file changes no verdict, schedules nothing, reads no
> holdout data, and implies no promotion. Every number is quoted from a
> cited source; where the ledger lacks a number the text says
> "not measured". This is NOT investment advice.

---

## (a) Program timeline

Round 1 of the program is the P1 phase family (four sweep lanes plus the
P2/P4/P5 validation chain) — there was no "round" vocabulary yet. Round 3
has no plan document at all: "Unlike Round 2 there is no single
pre-registration document for this round; instead each slice committed its
grids to `trading_lab.sweeps` (with tests) *before* its sweep ran"
(docs/research-round-3-results.md@3b7a52e L15–19); its design lives in the
fifteen `.sessions/2026-07-13-r3-*.md` cards.

| Round | Date | Asked | Answered | Source |
|---|---|---|---|---|
| 1 / P1 trend daily | 2026-07-09 | 4 trend families × 8 tickers × daily, 177 configs, walk-forward 1008/252 | 7 of 32 lanes beat B&H OOS Sharpe; "weak evidence, not a discovery" | docs/p1-trend-following-results.md@3b7a52e L38, L69 |
| 1 / P1 mean-rev daily | 2026-07-10 | 3 MR families × 8 tickers, 144 configs | 3 of 24 lanes beat; Bollinger reversion 0-for-8 | docs/p1-mean-reversion-results.md@3b7a52e L40, L72, L80 |
| 1 / P1 trend hourly | 2026-07-10 | Same 4 trend families × 8 tickers × hourly, 177 configs | 5 of 32 beat, over a single ~8.5-month OOS regime | docs/p1-trend-hourly-results.md@3b7a52e L45, L78, L83–88 |
| 1 / P1 video BTC | 2026-07-10 | 3 interpretations of the DaviddTech video × BTC-USD daily, 92 configs | 3/3 beat B&H on BTC but "none is a finding"; 0/4 off-BTC spot checks beat | docs/p1-video-strategy-results.md@3b7a52e L74, L95, L99–126 |
| 1 / P2 validation | 2026-07-10 | Re-validate 14 P1 candidates outside the selection window, params frozen | 12/14 UNVALIDATABLE-PRE-HOLDOUT; 1 promoted (later demoted, see ORDER 007); 1 killed | docs/p2-validation-results.md@3b7a52e L47–48, L146–148 |
| 1 / P4 transfer | 2026-07-10 | 13 subjects × other cached instruments, frozen params, 99 backtests | **13/13 TRANSFER-FAILED**; only 13 of 99 pairs beat B&H (13%) | docs/p4-transfer-results.md@3b7a52e L101–104 |
| 1 / P5 holdout | 2026-07-10 | Pre-registered one-shot holdout read, 13 subjects | AAPL donchian confirmed 0.759 vs 0.740 — but t = 0.02, inside noise; holdout SPENT | docs/p5-holdout-protocol.md@3b7a52e §1, §5; docs/paper-lane-protocol.md@3b7a52e §8; docs/final-report.md@3b7a52e §Holdout |
| interim / bollinger-mtf | 2026-07-12 | Owner's MTF Bollinger idea, 12 pre-declared configs | Clean NULL — all 12 Δ Sharpe ≤ 0, 0 graded KEEP | docs/research/bollinger-mtf-dev-2026-07-12.md@3b7a52e L133–141 |
| 2 | 2026-07-10 | 3 new families, 78 registered configs, hard cap 100, first pre-registered round plan | **5 KEEP-dev / 9 KILL** of 14 lanes; promotion CLOSED (holdout spent) | docs/research-round-2.md@3b7a52e L3–16; docs/research-round-2-results.md@3b7a52e |
| 3 | 2026-07-13 | Surface expansion: 11 new families, 6 new tickers, hourly mean-reversion, XSEC-14; core 1,752 + extended slices = 3,468 configs | Core: **0 PROMOTED / 41 KEEP-dev / 125 KILL of 166**; best t 1.04 vs bar 2.64. Full committed surface (per R4-A re-grade): 58 KEEP / 238 KILL / 4 KILL-SIG / 2 UNGRADEABLE of 302 | docs/research-round-3-results.md@3b7a52e L10–13; docs/research-round-4-results.md@3b7a52e §R4-A |
| 4 | 2026-07-13 | Six pre-registered idea classes (KILL-SIG re-grade, cost stress, committees, regime/cross-asset conditioning, seasonality) | "Six slices, six honest answers, zero findings" | docs/research-round-4-plan.md@3b7a52e; docs/research-round-4-results.md@3b7a52e §closing tally |
| 5 | 2026-07-13 | Deepen the frozen top-5 KEEP-dev lanes: neighborhood, leave-one-split-out, bootstrap, selection-fair replay; no new searches | **4 KEEP-dev / 1 KILL**; 1 escalate-to-owner (verdict unchanged) | docs/research-round-5-plan.md@3b7a52e; docs/research-round-5-results.md@3b7a52e L14–23 |
| 6 | 2026-07-13 | First volume families and first gap family, under the standing selection-fair gate; 696 configs | **3 KEEP-dev / 47 KILL / 8 KILL-SIG of 58 lanes, 0 promoted**; best t 0.60 vs 2.638 | docs/research-round-6-plan.md@3b7a52e; docs/research-round-6-results.md@3b7a52e L17–33 |

### Per-round verdicts by family

P1 predates the KEEP/KILL vocabulary (introduced by Round 2 §6,
docs/research-round-2.md@3b7a52e L138–139); its tallies are beats-vs-B&H.
KILL-SIG exists only from R4-A onward.

| Round | Family / slice | KEEP-dev | KILL | KILL-SIG | Source |
|---|---|---|---|---|---|
| 2 | vol_filtered_trend (4 lanes) | 0 | 4 | — | docs/research-round-2-results.md@3b7a52e L33–34 |
| 2 | keltner_breakout (4 lanes) | 2 | 2 | — | docs/research-round-2-results.md@3b7a52e L105–109 |
| 2 | xsec_momentum (6 configs, portfolio) | 3 | 3 | — | docs/research-round-2-results.md@3b7a52e L199–204 |
| 3 core | r3-stoch-willr (16) | 2 | 14 | — | docs/research-round-3-results.md@3b7a52e §Scoreboard |
| 3 core | r3-roc-adx (16) | 2 | 14 | — | ibid. |
| 3 core | r3-new-tickers (18) | 5 | 13 | — | ibid. |
| 3 core | r3-aroon-cci (24) | 4 | 20 | — | ibid. |
| 3 core | r3-meanrev-hourly (32) | 13 | 19 | — | ibid. |
| 3 core | r3-breakout (24) | 3 | 21 | — | ibid. |
| 3 core | r3-xsec-expanded (12) | 6 | 6 | — | ibid. |
| 3 core | r3-trix-ichimoku (24) | 6 | 18 | — | ibid. |
| 3 ext | r3-trend-new-tickers (24) | 5 | 19 | — | .sessions/2026-07-13-r3-trend-new-tickers.md@3b7a52e L93–109 |
| 3 ext | r3-meanrev-new-tickers (30) | 3 | 27 | — | .sessions/2026-07-13-r3-meanrev-new-tickers.md@3b7a52e |
| 3 ext | r3-gated-new-tickers (18) | 4 | 14 | — | .sessions/2026-07-13-r3-gated-new-tickers.md@3b7a52e |
| 3 ext | r3-btc-coverage (10) | 5 | 5 | — | .sessions/2026-07-13-r3-btc-coverage.md@3b7a52e |
| 3 ext | r3-trend-hourly (32) | 2 | 30 | — | .sessions/2026-07-13-r3-trend-hourly.md@3b7a52e |
| 3 ext | r3-hourly-completion (32) | 4 | 28 | — | .sessions/2026-07-13-r3-hourly-completion.md@3b7a52e |
| 3 (committed surface, per R4-A) | all 302 summaries | 58 | 238 | 4 (+2 UNGRADEABLE) | docs/research-round-4-results.md@3b7a52e §R4-A |
| 4 | R4-B cost stress of 58 KEEPs | 42 survive 2× / 25 survive 4× | 16 die at 2× | 0 | docs/research-round-4-results.md@3b7a52e §R4-B |
| 4 | R4-C committees (12) | 5 | 7 | 0 | ibid. §R4-C |
| 4 | R4-D regime-conditional (6) | 0 | 6 | 0 | ibid. §R4-D |
| 4 | R4-E cross-asset gate (2) | 0 | 2 | 0 | ibid. §R4-E |
| 4 | R4-F day-of-week (75 combos) | 0 | 45 | 30 | ibid. §R4-F |
| 5 | top-5 deepening (rollup) | 4 | 1 | 0 (1 escalate) | docs/research-round-5-results.md@3b7a52e L14–31; experiments/sweeps/r5-rollup/summary.json |
| 6 | R6-A volume daily (30 lanes) | 2 | 27 | 1 | docs/research-round-6-results.md@3b7a52e L35–40; experiments/sweeps/r6-volume/summary.json |
| 6 | R6-B overnight_gap (12 lanes) | 0 | 5 | 7 | ibid.; experiments/sweeps/r6-gap/summary.json |
| 6 | R6-C volume hourly (16 lanes) | 1 | 15 | 0 | ibid.; experiments/sweeps/r6-volume-hourly/summary.json |

Roadmap note: the founding plan ordered P2→P3→P4→P5
(docs/founding-plan.md@3b7a52e L59–70); the executed sequence was
P2→P4→P5 and no P3-named results doc exists — the round-2/3 family
expansions functionally occupy that slot. No document explains the skip.

## (b) The cumulative funnel

**5,055 registered configurations → 0 promoted.** The chain, verified two
independent ways (the doc chain of "program cumulative" lines, and
`src/trading_lab/sweeps.py@3b7a52e` total_configs functions plus the
committed artifact `experiments/sweeps/r6-volume-hourly/summary.json`
field `"program_variants_tried": 5055`):

| Stage | Configs | Cumulative | Source |
|---|---|---|---|
| P1 (four lanes: 177+144+177+92) | 590 | 590 | docs/research-round-2.md@3b7a52e §2 L52–61 |
| Round 2 (48+24+6) | 78 | 668 | docs/research-round-2-results.md@3b7a52e L19–23; sweeps.py r2_* = 78 |
| bollinger-mtf dev slice | 12 | 680 | docs/research/bollinger-mtf-dev-2026-07-12.md@3b7a52e L164; docs/research-round-3-results.md@3b7a52e L63 ("680 before tonight") |
| Round 3 (13 sweeps, core + extended) | 3,468 | 4,148 | .sessions/2026-07-13-r3-hourly-completion.md@3b7a52e L110, L149–152; sweeps.py r3_* sum = 3,468 |
| Round 4 (75 R4-F + 12 R4-C + 84 R4-D + 26 R4-E; A/B are re-grades, zero) | 197 | 4,345 | docs/research-round-4-results.md@3b7a52e L517–518 |
| Round 5 (R5-A neighbors) | 14 | 4,359 | docs/research-round-5-results.md@3b7a52e L21–23 |
| Round 6 (360+144+192) | 696 | 5,055 | docs/research-round-6-plan.md@3b7a52e L98; experiments/sweeps/r6-volume-hourly/summary.json |

P2 (2 runs), P4 (99 backtests, 0 new variants) and P5 (13 holdout reads)
added runs but no registered configs (docs/p2-validation-results.md@3b7a52e
L157; docs/p4-transfer-results.md@3b7a52e L65–68; docs/research-round-2.md@3b7a52e L62).

**What 5,055 is not:** `experiments/index.jsonl@3b7a52e` is the run-level
ledger — 658 rows whose `variants_tried` sum to 8,678, because it includes
B&H benchmark runs, P2/P4 replays, and probe rows. The registered-config
burden is the pre-declared chain above, not a recount of the index; the
5,055 cannot be reproduced from index.jsonl.

**Bookkeeping drift, stated honestly rather than reconciled silently:**

- The 12-config bollinger-mtf slice is double-booked inconsistently:
  its own doc states "program cumulative 602 (590 + 12)"
  (docs/research/bollinger-mtf-dev-2026-07-12.md@3b7a52e L164), ignoring
  Round 2's 78 configs already registered at 668
  (docs/research-round-2-results.md@3b7a52e L19–23). The round-3 anchor
  "680 before tonight" (docs/research-round-3-results.md@3b7a52e L63) is
  only consistent as 668 + 12; the mtf doc's 602 is internally stale.
  Downstream totals (4,148 → 5,055) are unaffected.
- The round-3 KEEP tally drifts between prose and committed artifacts:
  "~312 lanes / 64 KEEP" (docs/research-round-4-plan.md@3b7a52e L21–23,
  echoing .sessions/2026-07-13-r3-hourly-completion.md@3b7a52e L149–152)
  vs the committed machine-readable surface of 302 summaries / 58 KEEP
  (docs/research-round-4-results.md@3b7a52e L35–37, which reconciles the
  two explicitly). docs/research-round-5-plan.md@3b7a52e L20–22 repeats
  the stale 312/64 prose tally without the reconciliation note.

### KEEP-dev surface over time

- Post-round-3 peak: **58** KEEP-dev lanes among the 302 committed
  summaries (docs/research-round-4-results.md@3b7a52e §R4-A).
- After R4-B 2× cost stress: **42** of 58 keep status; 25 survive 4×
  (gradient only) (ibid. §R4-B).
- Round 5 froze the **top 5** by baseline t among the 42
  (docs/research-round-5-plan.md@3b7a52e §target set) and killed one:
  **4** KEEP-dev after R5-B (docs/research-round-5-results.md@3b7a52e L14–23).
- Round 6's own 58 new lanes closed at **3** KEEP-dev
  (docs/research-round-6-results.md@3b7a52e L17–19). No document merges
  the 4 round-5 survivors with the 3 round-6 KEEPs into one standing
  list — the combined post-r6 surface is **not measured**.
- Promotions: **0**, in every round. The only PROMOTED-TO-FINDING ever
  minted (AAPL donchian, P2 era) was demoted to RULE-PASS on 2026-07-10
  under ORDER 007 (docs/p2-regrade-aapl-donchian.md@3b7a52e).

### The multiple-testing bar

`t = (SR_strategy − SR_benchmark) / SE(SR_strategy)` with the Lo (2002)
iid SE, and **`t_min(K) = Φ⁻¹(1 − 0.05/max(1,K))`** — a one-sided
Bonferroni correction over K = variants tried
(src/trading_lab/promotion.py@3b7a52e L28–45, L64, L108; prose twin
docs/p2-regrade-aapl-donchian.md@3b7a52e L27–39). Values in use:
t_min(1)=1.645, t_min(5)≈2.33, t_min(12)=2.638 (exact
2.638257273476751 per-lane in the r6 summary.json files), t_min(13)=2.665,
t_min(14)=2.690, t_min(75)=3.209, t_min(177)=3.448. The bar "only ever
rises"; no K was ever counted down
(docs/research-round-5-results.md@3b7a52e L266–267).

Its role in the zero: the one pre-bar promotion, AAPL donchian, showed
t = 0.42 vs 1.645 at K=1 (3.448 at honest K=177) and was demoted
(docs/p2-regrade-aapl-donchian.md@3b7a52e L71–74); its holdout
confirmation was t = 0.02 (docs/paper-lane-protocol.md@3b7a52e §8). Best
t per round afterward: round 3 **1.04** vs 2.64
(docs/research-round-3-results.md@3b7a52e L12); round 4 best stressed t
**1.315** (BTC-USD bollinger_breakout at 2× costs,
docs/research-round-4-results.md@3b7a52e §R4-B); round 5 best neighbor t
**1.66** (SLV williams_r period=21/sell_above=−20,
docs/research-round-5-results.md@3b7a52e L46–48); round 6 best t **0.60**
(BTC-USD obv_trend, docs/research-round-6-results.md@3b7a52e L18–19).
Against bars of 2.33–3.45, nothing in six rounds came within ~1 of its bar.

## (c) What died and why

- **Overnight gap: 0/12 with 7 KILL-SIG** — "the sharpest null in six
  rounds, stronger than the registered hypothesis … post-gap next-day
  drift/reversion is not merely unexploitable net of costs, it is
  SIGNIFICANTLY harmful on 7 of 12 tickers (informational t down to −4.01
  on AAPL)" (docs/research-round-6-results.md@3b7a52e §R6-B). The 7
  KILL-SIG lanes: AAPL −4.014, MSFT −3.018, NVDA −3.773, GOOGL −3.971,
  AMZN −2.778, GLD −2.650, QQQ −3.699 (ibid. L191–204; artifact
  experiments/sweeps/r6-gap/summary.json verdict_counts
  {KEEP:0, KILL:5, KILL-SIG:7}). Every fixed-config replay also lost to
  B&H — "the family itself has no edge here" (ibid. L179–182). Caveat the
  doc itself carries: fills are t+1 open, so only post-gap drift was
  tested; the classic same-day gap-capture claim "was NOT testable and is
  NOT graded by these KILLs" (ibid. L176–181).
- **Volume adds nothing** — the pre-registered control result: confirmed
  (`price_confirm=True`) arms' full-period mean Sharpe **0.471 vs 0.479**
  for pure OBV (docs/research-round-6-results.md@3b7a52e §R6-A);
  mfi_reversion went 0/15 daily with one KILL-SIG (MSFT t = **−2.892**,
  experiments/sweeps/r6-volume/summary.json). Closing tally: "the volume
  column — the last untouched data channel in the committed caches — does
  not carry exploitable information on this surface … 46 volume lanes
  yielding 3 weak KEEPs" (ibid. L317–321). obv_trend hourly went 0/8;
  hourly overall was "a KILL amplifier at baseline costs (15/16)"
  (ibid. L221, L323–324).
- **Transfer failure (P4)** — **13/13 TRANSFER-FAILED**; frozen params
  beat B&H on only 13 of 99 instrument pairs (13%); no subject reached
  even TRANSFER-WEAK (docs/p4-transfer-results.md@3b7a52e L101–104).
  Nothing found on one instrument ever worked on another.
- **Conditioning lost to its own controls, on every axis tested** —
  "conditioning of every kind tested — volatility (PR #92), trend
  strength (R4-D), cross-asset momentum (R4-E) — subtracted value against
  its own unconditioned control"
  (docs/research-round-4-results.md@3b7a52e §closing item 4). Detail: the
  volatility gate's `vol_filter=False` arm beat the gated arm on all six
  instruments (e.g. SPY 0.859 vs 0.519)
  (.sessions/2026-07-13-r3-gated-new-tickers.md@3b7a52e L123–129); R4-D
  0/6 KEEP, mean control_arm_delta −0.067, with TLT beating B&H (0.219 vs
  0.196) yet losing to its own control (0.293) (ibid. §R4-D); R4-E gated
  lost to ungated on both lanes (SPY −0.302, QQQ −0.635) (ibid. §R4-E).
- **Day-of-week seasonality: 0/75** at the honest K=75 bar of 3.209; best
  t 0.317 (TSLA Friday); 30 KILL-SIG driven by the exposure artifact
  ("one-day-a-week exposure loses to being invested"); worst combo GOOGL
  Thursday −5.840 (docs/research-round-4-results.md@3b7a52e §R4-F).
- **Retroactively significant harm in round 3 (R4-A)** — adx_filtered_sma
  GOOGL −3.100, rsi_mean_reversion TSLA −3.011, cci_reversion NVDA
  −2.930, cci_reversion AAPL −2.838, all vs the 2.638 bar; a KILL-SIG "is
  explicitly NOT a signal to invert"
  (docs/research-round-4-results.md@3b7a52e §R4-A, L68–73).
- **Mean-reversion vs trend patterns across tickers/timeframes** — MACD
  was the worst trend family on 5 of 8 tickers on both timeframes, its
  churn cost-eaten (docs/p1-trend-following-results.md@3b7a52e L82–84;
  docs/p1-trend-hourly-results.md@3b7a52e L95–97), then 6/6 KILL on the
  new tickers (.sessions/2026-07-13-r3-trend-new-tickers.md@3b7a52e L98).
  Bollinger reversion went 0-for-8
  (docs/p1-mean-reversion-results.md@3b7a52e L80); pullback was negative
  outright on both metals (ibid. L85–87). Daily trend "mostly lags
  buy-and-hold after realistic costs" (0/20 on MSFT/NVDA/GOOGL/AMZN/GLD,
  docs/p1-trend-following-results.md@3b7a52e L74–75); hourly trend lost
  27 of 32 lanes (docs/p1-trend-hourly-results.md@3b7a52e L90–91). What
  both families earned when they "won" was a drawdown-reduction profile
  concentrated on META's 2022 crash, not return enhancement
  (docs/p1-trend-following-results.md@3b7a52e L80–81;
  docs/p1-mean-reversion-results.md@3b7a52e L88–92). Hourly KEEPs did
  not replicate on the same tickers at daily, and KEEP rates tracked
  benchmark weakness: "weakest benchmark-Sharpe tercile yields 12/32
  KEEPs, the strongest 3/30"
  (.sessions/2026-07-13-r3-hourly-completion.md@3b7a52e L130–139).
  xsec_reversal died 6/6 with "ranking DIRECTION swings stitched OOS
  Sharpe by ~0.9 while parameters move it ≤ 0.2"
  (docs/research-round-3-results.md@3b7a52e §patterns item 5).

## (d) What survived and how fragile it is

Four lanes survived round 3 → R4-B → all four round-5 slices; a fifth
died in R5-B. Round 6 added three weak new KEEP-devs (BTC-USD obv_trend
t 0.60; META obv_trend t 0.18; AMZN mfi_reversion hourly t 0.29 —
docs/research-round-6-results.md@3b7a52e; experiments/sweeps/r6-volume/summary.json,
r6-volume-hourly/summary.json). No survivor is a finding; every t below
is against a bar it never approached.

1. **BTC-USD daily bollinger_breakout** (period=10, num_std=1.0) — the
   strongest survivor. R3: OOS 1.258 vs B&H 0.821, t = 1.38 vs bar 2.64
   (.sessions/2026-07-13-r3-btc-coverage.md@3b7a52e L114–117). R4-B: 2×
   costs t = 1.315, 4× t = 1.190 — best stressed t in the program
   (docs/research-round-4-results.md@3b7a52e §R4-B). R5: both neighbors
   beat B&H (1.024/1.088); worst leave-one-out delta +0.326; bootstrap
   **P(delta≤0) = 0.042** — the only lane at/below the 0.10 escalate bar,
   producing the owner-gated R5-C proposal (verdict unchanged);
   selection_gap +0.185 (docs/research-round-5-results.md@3b7a52e L66–67,
   L131–135, L152–160, L216–219). Fragility: "a 1.4-t dev edge on a
   heavily-mined surface usually regresses"
   (docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md@3b7a52e §6);
   the walk-forward tail discard means 239 of the freshest BTC daily dev
   bars (the entire 2024-H2 run) were never scored by any reported number
   (.sessions/2026-07-13-r3-btc-coverage.md@3b7a52e L23–46).
2. **SLV daily williams_r_reversion** — R3 t = 1.04 (round-3 best); R4-B
   2× t = 0.936, 4× t = 0.722; R5-A produced the program's best t
   anywhere, 1.66, in a neighbor — still under 2.638; R5-C P(delta≤0) =
   0.133; R5-D selection_gap **−0.313**: the searched walk-forward LOST
   to its own fixed config (docs/research-round-3-results.md@3b7a52e L94;
   docs/research-round-4-results.md@3b7a52e §R4-B;
   docs/research-round-5-results.md@3b7a52e L46–48, L170, L203–207).
   Fragility: it sits on the second-weakest benchmark on the board
   (0.170) — "low bar cleared, not an edge"
   (docs/research-round-3-results.md@3b7a52e §patterns item 1).
3. **META daily ichimoku_trend** — R3 t = 0.96; R4-B 2× t = 0.894, 4×
   t = 0.761; R5 all slices pass (LOO worst +0.152; P(delta≤0) = 0.116;
   selection_gap +0.010) (docs/research-round-3-results.md@3b7a52e L132;
   docs/research-round-4-results.md@3b7a52e §R4-B;
   docs/research-round-5-results.md@3b7a52e L131–135, L170, L217–218).
   Fragility: "META flatters most families … 9 KEEP / 5 KILL,
   family-agnostically … This says more about META's dev-window path than
   about any strategy" (docs/research-round-3-results.md@3b7a52e
   §patterns item 2).
4. **TLT daily ema_crossover** — R3 t = 0.90; R4-B 2× t = 0.845, 4×
   t = 0.724; R5-B worst LOO margin **+0.091**, the smallest of any
   survivor; R5-C P(delta≤0) = 0.107, just above the escalate bar
   (.sessions/2026-07-13-r3-trend-new-tickers.md@3b7a52e L95–97;
   docs/research-round-4-results.md@3b7a52e §R4-B;
   docs/research-round-5-results.md@3b7a52e L131–135, L170). Fragility:
   TLT's 0.196 is the weakest daily benchmark on the board
   (docs/research-round-3-results.md@3b7a52e §patterns item 1).
5. **META hourly stochastic_reversion — killed by R5-B.** Per-split
   deltas "+4.05, +0.34, −0.49, −0.97, +1.55 — the entire stitched edge
   lives in split 0"; full delta **+1.035 → −0.164** with the best split
   removed. "With only 5 splits (the hourly cache is short), one hot
   window carried a 1.5-Sharpe stitched lane"
   (docs/research-round-5-results.md@3b7a52e L100–130). The bootstrap
   independently flagged the same lane as shakiest (delta std 1.13 vs
   0.24–0.30 for the daily lanes) (ibid. L170–176).

**Selection itself is close to noise.** R5-D's fixed-config replays showed
selection_gap > 0 on just 3 of 5 top lanes (SLV −0.313, META hourly
−0.396): "in-window grid re-picking is closer to noise than to signal"
(docs/research-round-5-results.md@3b7a52e L198–219). At round-6 scale,
selection_gap > 0 on only **2 of 58** lanes
(docs/research-round-6-results.md@3b7a52e L17–33).

## (e) Methodology evolution

Present from the founding plan (binding on all of P1): walk-forward only,
locked 18-month holdout, realistic costs (5 bps slippage + 1 bp
commission per side, t+1-open fills), variants-tried counting, B&H
benchmark with negative results ledgered
(docs/founding-plan.md@3b7a52e §Methodology L13–35). Added after, each
with a documented catch:

| Addition (when) | What it is | Documented example of what it caught |
|---|---|---|
| ORDER 007 Bonferroni bar (2026-07-10) | Promotion needs t ≥ t_min(K); before it, "a +0.001 Sharpe edge on a short window would have promoted" (docs/p2-regrade-aapl-donchian.md@3b7a52e L11–20) | Demoted the program's only promotion: AAPL donchian t = 0.42 vs 1.645 (ibid. L71–74) |
| Pre-registration (P4 docstring → P5 protocol doc → full round plans from R2) | Verdict rules fixed before any run; "a verdict rule chosen after seeing the numbers is just one more fitted parameter" (docs/p5-holdout-protocol.md@3b7a52e L14–17) | R2's binding cap (78/100, contingency untouched) and adversarial tie rule "resolve AGAINST the strategy" (docs/research-round-2.md@3b7a52e §4, §6 L140–141); R4-D/E/F null hypotheses were all pre-committed and all confirmed |
| KILL-SIG verdict class (R4-A) | Mirror of the bar in the negative: t ≤ −t_min(K) (src/trading_lab/promotion.py@3b7a52e L151–176) | 4 significantly-harmful r3 lanes (GOOGL adx −3.100 …); then 30+1 in R4-F and 8 in round 6 (docs/research-round-4-results.md@3b7a52e §R4-A, §R4-F; docs/research-round-6-results.md@3b7a52e) |
| 2× / 4× cost stress (R4-B) | Re-grade all KEEPs at doubled and quadrupled costs, no re-search | Killed 16/58 KEEPs at 2×; "hourly lanes die at twice the daily rate" (docs/research-round-4-results.md@3b7a52e §R4-B) |
| Mandatory control arms + `control_arm_delta` (R4-D/E) | Every conditioning lane carries its unconditioned twin | TLT regime lane beat B&H but lost to its own control — "without it, TLT would have looked like a weak KEEP" (docs/research-round-4-results.md@3b7a52e §R4-D) |
| Honest K accounting (K=13/14/75) | Bar rises with every control and combo counted | Three positive-t Fridays that "would have been 'dev-candidates' at the lane-local bar" miss K=75's 3.209 "by an order of magnitude" (docs/research-round-4-results.md@3b7a52e §R4-F L202–208) |
| Leave-one-split-out stability (R5-B) | KEEP only if the delta survives removal of the best split | The META hourly single-window-luck lane that every other slice passed (docs/research-round-5-results.md@3b7a52e L287–289) |
| Moving-block bootstrap (R5-C) | P(delta≤0) from 1,000 block resamples, seeded | Independently flagged the same fragile lane (delta std 1.13) and tripped the escalate branch exactly once (BTC-USD, 0.042) (docs/research-round-5-results.md@3b7a52e L170–176; experiments/sweeps/r5-bootstrap/summary.json) |
| Fixed-config rows (R5-D, standing from round 6) | Selection-free replay of the committed top variant on every searched lane | Searched arms losing to their own fixed configs (SLV −0.313, META hourly −0.396); at r6 scale, 14 PASS-but-KILL lanes, e.g. NVDA obv_trend fixed 1.427 beats bench 1.295 while the searched arm loses by 0.002 (docs/research-round-5-results.md@3b7a52e L198–219; docs/research-round-6-results.md@3b7a52e) |
| Selection-fair standing gate (round 6+) | A dev KEEP additionally requires the fixed-config replay to beat same-window B&H; UNGRADEABLE = FAIL; forward-only, round ≤5 verdicts stand — rule doc [selection-fair-gate.md](selection-fair-gate.md) | Ran on all 58 round-6 lanes: 17 PASS / 41 FAIL, demoted 0 KEEPs (every Round-2-rule KEEP independently passed) (docs/research-round-6-results.md@3b7a52e L26–28, L294–303) |

Two guards are notable for never firing, which is itself the documented
result: the 1e-8 replay fidelity guard (0 SKIPPED across R4-B/C, all of
R5, and 58/58 r6 lanes) and the round-6 runtime caps (25.6/12.0/7.9 s
against 900–1200 s caps, no CAP-HIT)
(docs/research-round-6-results.md@3b7a52e L304–311).

## (f) Honest program assessment

**This is NOT investment advice, and NO promotion is implied by anything
in this document.** Promotion is CLOSED; the holdout is SPENT (13 reads,
one shot each, ORDER 008 — docs/paper-lane-protocol.md@3b7a52e §8). Every
KEEP-dev above is a dev-data artifact, not an out-of-sample claim.

What the evidence supports: the dev surface is mined out. Three
consecutive round closings state it in nearly identical words — round 4:
"Anything further on this surface needs either new data (OWNER-GATED) or
a genuinely different idea class, not more variants"
(docs/research-round-4-results.md@3b7a52e L573–575); round 5
(docs/research-round-5-results.md@3b7a52e L297–300) and round 6
(docs/research-round-6-results.md@3b7a52e L331–332) repeat the sentence.
Round 6 tested the last untouched data channel (volume) and the first
open-column family (gaps) and produced the program's weakest best-t
(0.60) and sharpest null.

The single pre-registered out-of-sample option is the R5-C BTC-USD
bollinger_breakout proposal
(docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md@3b7a52e):
**FROZEN, OWNER-GATED, NOT SCHEDULED, NOT RUN** — "No agent may execute
it autonomously, fetch data for it, or act on it without an explicit
owner ORDER"; it changes no verdict, and "Doing nothing is a perfectly
acceptable owner choice."

**Known not-measured items** (each per the ledger's own words):

- Deflated Sharpe ratio — preferred by the founding plan, never
  computable: cross-trial variance and return skew/kurtosis were never
  persisted; the Bonferroni t bar was substituted as the declared
  equivalent (docs/p2-regrade-aapl-donchian.md@3b7a52e L46–51).
- Per-lane OOS trade counts / exposure through round 3 — "a KEEP on few
  trades is indistinguishable from a KEEP on many"
  (docs/research-round-3-results.md@3b7a52e L188–191); R4-F's 30
  KILL-SIGs are read as exposure artifacts but no exposure-matched
  benchmark was ever run.
- Cost-drag / breakeven-bps — gross-vs-net never recorded; "edge killed
  by 6 bps" vs "no edge" indistinguishable on hourly lanes
  (.sessions/2026-07-13-r3-meanrev-hourly.md@3b7a52e L13–31).
- Same-day overnight gap capture — "NOT testable in this engine and is
  NOT claimed" (docs/research-round-6-plan.md@3b7a52e §R6-B L165–168).
- 239 unscored BTC-USD daily OOS bars (and 208 hourly) — the
  walk-forward tail discard means the freshest dev data was never scored
  (.sessions/2026-07-13-r3-btc-coverage.md@3b7a52e L23–46).
- No merged post-r6 KEEP-dev list — no document states the combined
  surviving surface (4 round-5 survivors + 3 round-6 KEEPs).
- Round 2 significance — no t-stats were computed anywhere in round 2 by
  design; its 5 KEEPs never faced the ORDER 007 bar
  (docs/research-round-2-results.md@3b7a52e L14–15).
- Drawdown reduction — the only consistently observed effect, never a
  decision metric ("drawdown is not the pre-registered decision metric
  and buys no KEEP", docs/research-round-2-results.md@3b7a52e L82–84).

## (g) Options for round 7+

A neutral menu. No option is recommended here; per
control/status.md@3b7a52e L22, "round 7 awaits manager/owner direction."

1. **New data classes (owner-gated).** New tickers or extended history
   require a fetch decision the agents cannot take
   (docs/research-round-6-plan.md@3b7a52e L38–46 — "the honest 'new
   tickers' answer for Round 6 is *none available without a fetch*").
   Cost: an explicit owner ORDER plus fetch/caching work; compute
   comparable to a round-3-style sweep. Could establish: whether the
   surviving families behave the same on unmined instruments/periods —
   genuine dev-fresh evidence. Could NOT establish: any out-of-sample
   claim about the existing survivors (new dev data mined the same way
   inherits the same K burden), nor a promotion (holdout spent; a new
   promotion path needs its own pre-registered owner-gated protocol,
   docs/paper-lane-protocol.md@3b7a52e §8).
2. **Genuinely new idea families on existing data.** Cost: lowest — no
   owner action, committed caches only, compute in the round-6 range
   (r6 ran 696 configs in under 26 s/slice,
   docs/research-round-6-results.md@3b7a52e L304–311); complexity is in
   inventing families that are not variants of the 20+ already burned.
   Could establish: another honest null, or a new weak KEEP-dev cohort.
   Could NOT establish: anything about the existing survivors, or any
   OOS claim — and three round closings already predict the null; the
   volume round showed what "the last untouched channel" bought (3 weak
   KEEPs of 46 lanes).
3. **Execute the pre-registered R5-C OOS check (owner-gated).** Cost:
   one owner ORDER fixing a post-2026 window of ≥252 BTC-USD daily bars
   before any bar is inspected, one fetch, one selection-free replay —
   minimal compute. Could establish: a first genuinely out-of-sample
   read on the program's strongest survivor at the pre-registered bar
   (min_tstat(5) ≈ 2.33, "and the owner may reasonably demand the full
   program K",
   docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md@3b7a52e §4).
   Could NOT establish: a promotion by itself (the proposal changes no
   verdict), and a single lane's pass/fail generalizes to nothing else;
   the proposal's own prior is that "a 1.4-t dev edge on a heavily-mined
   surface usually regresses" (ibid. §6).
4. **Stopping / steady-state.** Cost: zero compute, zero owner action —
   the paper lane already runs on cron (first weekly grading pass
   2026-07-17, control/status.md@3b7a52e L15–21) and its protocol is
   explicit that no BEAT streak promotes
   (docs/paper-lane-protocol.md@3b7a52e §8). Could establish: slow
   forward evidence on the one RULE-PASS candidate at zero mining cost;
   preserves the program's negative results, which are its main product.
   Could NOT establish: anything new about the KEEP-dev surface, and
   forward paper evidence accrues at ~1 grading window/week — years to
   significance at any honest bar (not measured: no power calculation
   exists in the ledger).

---

*Sources: all citations at origin/main `3b7a52e`. Round 1 = the P1/P2/P4/P5
phase documents; round 3's design lives in `.sessions/2026-07-13-r3-*.md`
cards rather than a plan doc. See also
[research-round-6-results.md](research-round-6-results.md) for the most
recent round close and [selection-fair-gate.md](selection-fair-gate.md)
for the standing gate.*
