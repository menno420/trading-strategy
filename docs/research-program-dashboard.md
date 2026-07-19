# Research Program Dashboard — Per-Round Scoreboard (P1 → Round 11)

> **Status:** `reference`
>
> One canonical, honest scoreboard for the whole research program, so the
> program-wide picture no longer has to be re-stitched from seven separate
> results docs. **Docs only:** this file changes no verdict, schedules
> nothing, reads no holdout data, and implies no promotion. Every number is
> carried from a cited committed source doc — where a round's doc does not
> state a number the cell reads `n/r` (not recorded), never an invented
> value. **POST-HOLDOUT, DEV-ONLY: the holdout is SPENT and promotion is
> CLOSED.** This is NOT investment advice.

## Headline

Across P1 baselines through Round 11 the program registered **5,940
registered configurations and promoted 0** — **no strategy ever cleared
the significance bar** (`trading_lab.promotion.min_tstat(K)` ≈ 2.638 at
K=12; the bar only ever rises). Promotion is **CLOSED**, the holdout is
**SPENT** (13 one-shot reads, ORDER 008), and the negative result *is* the
finding. The single PROMOTED-TO-FINDING ever minted — AAPL donchian, P2 era
— was demoted to RULE-PASS on 2026-07-10 under ORDER 007 (its holdout
confirmation was t = 0.02). Nothing in six-plus rounds came within ~1.0 t of
its bar; the best informational t anywhere is **1.66** (Round 5, an SLV
`williams_r_reversion` grid neighbor). This is a clean, honest **offline
research library, not a live trading system.**

## Per-round scoreboard

| Round | Configs added | Cumulative | KEEP-dev | KILL | KILL-SIG | Best t (vs 2.638) | Promoted | Source |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| P1 baselines | 590 | 590 | n/r¹ | n/r¹ | n/r¹ | n/r² | 0³ | `p1-*-results.md` (aggregated in `research-program-retrospective.md` §b) |
| Round 2 | 78 | 668 | 5 | 9 | —⁴ | n/r⁵ | 0 | `research-round-2-results.md` |
| interim · bollinger-mtf | 12 | 680 | 0 | n/r⁶ | —⁴ | n/r⁶ | 0 | `research/bollinger-mtf-dev-2026-07-12.md` |
| Round 3 | 3,468 | 4,148 | 58⁷ | 238⁷ | 4⁷ | 1.04 | 0 | `research-round-3-results.md`; `research-round-4-results.md` §R4-A |
| Round 4 | 197 | 4,345 | 5⁸ | 60⁸ | 30⁸ | 1.09⁹ | 0 | `research-round-4-results.md` |
| Round 5 | 14 | 4,359 | 4 | 1 | 0 | 1.66 | 0 | `research-round-5-results.md` |
| Round 6 | 696 | 5,055 | 3 | 47 | 8 | 0.60 | 0 | `research-round-6-results.md` |
| Round 7 | 360 | 5,415 | 5 | 25 | 0 | 1.20¹⁰ | 0 | `research-round-7-results.md` |
| Round 7C | 180 | 5,595 | 1 | 11 | 3 | 0.22 | 0 | `research-round-7c-results.md` |
| Round 7D | 6 | 5,601 | 0 | 6 | 0 | −0.74¹² | 0 | `research-round-7d-results.md` |
| Round 8 | 192 | 5,793 | 3 | 13 | 0 | 1.08 | 0 | `research-round-8-results.md` |
| Round 9 | 60 | 5,853 | 11 | 44 | 5 | 1.04¹³ | 0 | `research-round-9-results.md` |
| Round 10 | 60 | 5,913 | 11 | 40 | 9 | 1.04¹⁴ | 0 | `research-round-10-results.md` |
| Round 11 | 27 | 5,940 | 2 | 25 | 0 | 0.68¹⁵ | 0 | `research-round-11-results.md` |
| **Program total** | **5,940** | **5,940** | —¹¹ | —¹¹ | —¹¹ | **1.66** (R5-A) | **0** | rows above |

The cumulative column reconciles exactly: 590 + 78 + 12 + 3,468 + 197 + 14 +
696 + 360 + 180 + 6 + 192 + 60 + 60 + 27 = **5,940** (the `program_variants_tried` chain,
cross-checked against `src/trading_lab/sweeps.py` in
`research-program-retrospective.md` §b and
[cross-round-meta-analysis.md](cross-round-meta-analysis.md); each round's total
pinned by `tests/test_sweeps.py`). P2 (2 validation runs), P4 (99 transfer
backtests), and P5 (13 holdout reads) added *runs* but **no new registered
configs**, so they are not separate rows.

### Footnotes (every figure is cited)

1. P1 predates the KEEP/KILL vocabulary (introduced in Round 2 §6; KILL-SIG
   only from R4-A). P1 graded beats-vs-B&H: 7/32 trend daily, 3/24
   mean-reversion, 5/32 trend hourly, 3/3 on BTC but "none is a finding"
   (video) — "weak evidence, not a discovery"
   (`research-program-retrospective.md` §a; the four `p1-*-results.md`).
   590 = 177 + 144 + 177 + 92.
2. No Bonferroni t was computed in P1 by design. The only significance ever
   attached to a P1/P2 lane came from the later ORDER 007 re-grade of AAPL
   donchian: t = 0.42 at K=1 (3.448 at honest K=177), demoted
   (`p2-regrade-aapl-donchian.md`; `research-program-retrospective.md` §b/§f).
3. 0 net/standing. The single PROMOTED-TO-FINDING (AAPL donchian) was
   demoted to RULE-PASS on 2026-07-10; its one-shot holdout confirmation was
   t = 0.02 (`research-program-retrospective.md` §d/§f).
4. The KILL-SIG verdict class (t ≤ −`min_tstat`, the mirrored bar) did not
   exist until R4-A, so it is undefined (`—`) for Round 2 and the interim
   slice.
5. Round 2 computed no t-stats anywhere, by design
   (`research-round-2-results.md`).
6. bollinger-mtf: a clean NULL — all 12 pre-declared Δ Sharpe ≤ 0, 0 graded
   KEEP; no t reported (`research/bollinger-mtf-dev-2026-07-12.md`;
   `research-program-retrospective.md` §b). Listed as its own row so the
   cumulative reconciles (668 + 12 = 680).
7. Round 3's own **core** headline is 1,752 configs / 41 KEEP-dev / 125 KILL
   of 166 core lanes, best t 1.04 (`research-round-3-results.md`). This row
   instead uses the **full committed surface** — 3,468 configs across 13
   core + extended sweeps → 302 per-lane summaries, re-graded **58 KEEP /
   238 KILL / 4 KILL-SIG** (+2 UNGRADEABLE) by R4-A
   (`research-round-4-results.md` §R4-A; funnel in
   `research-program-retrospective.md` §b) — so the config count matches the
   4,148 cumulative. The 4 KILL-SIG arose from the R4-A re-grade, not from
   Round 3 as-run.
8. Round 4 **new-search** slices only: R4-C committees 5 KEEP / 7 KILL, R4-D
   regime 0/6, R4-E cross-asset 0/2, R4-F day-of-week 0/45 + 30 KILL-SIG (at
   the honest K=75 bar, 3.209) — sum **5 KEEP / 60 KILL / 30 KILL-SIG** of
   95 new-search lanes (`research-round-4-results.md` §closing tally). R4-A
   (302-lane re-grade of Round 3) and R4-B (2×/4× cost re-grade of the 58
   KEEPs, killing 16 at 2×) are re-grades of prior-round lanes and are
   excluded here to avoid double-counting Round-3 lanes.
9. Best t among Round-4 **new** configs: 1.09 (R4-C committees,
   `research-round-4-results.md` §R4-C). R4-B's cost re-grade of a Round-3
   survivor (BTC-USD `bollinger_breakout` at 2× costs) reached 1.315 — the
   highest number attributed to Round 4 — but it is a re-grade of a Round-3
   lane, not a new Round-4 config.
10. 1.20 in the round headline; 1.195 in the per-lane t column (BTC-USD
    daily `high_proximity`, `research-round-7-results.md`).
11. KEEP-dev / KILL / KILL-SIG are **not additive** across rounds: later
    rounds re-grade and demote earlier lanes (R4-A/B re-grade Round 3; R5-B
    demoted a Round-3 KEEP), and no document states a merged post-Round-6
    standing KEEP list — the combined surviving surface is explicitly "not
    measured" (`research-program-retrospective.md` §b/§f). The program's best
    informational t anywhere is **1.66** (R5-A, SLV `williams_r_reversion`
    ±1-grid-step neighbor), still far under any bar.
12. R7-D is a PORTFOLIO lane graded at the xsec K=6 convention (bar ≈2.39),
    not K=12; its best t is negative — every lane underperforms the basket B&H
    (`research-round-7d-results.md`).
13. R9 is the cross-class ≥K-of-N signal-confluence vote graded at its honest
    multiplicities — per-lane K=4 (bar 2.24) and program-wide K=60 (bar 3.14);
    best t 1.04 (BTC-USD SET-3/K=2) is under half the nearer bar. The 5
    KILL-SIG lanes are all the strict all-agree corner (significantly
    value-destroying on high-drift names: NVDA −5.09, MSFT −2.88, JPM −2.64;
    `research-round-9-results.md`).
14. R10 is the inverse-confluence EXIT vote (the De Morgan dual of R9: hold by
    default, go flat when ≥K distinct classes agree OUT), graded at the same
    honest multiplicities — per-lane K=4 (bar 2.24) and program-wide K=60 (bar
    3.14). Best t 1.04 is the SAME BTC-USD SET-3/K=2 lane and value as R9 (the
    dual gives the same best), under half the nearer bar. The 9 KILL-SIG lanes
    are 8 the loose SET-5/K=2 exit + MSFT SET-5/K=3 (significantly
    value-destroying on high-drift names: NVDA −4.07, MSFT −3.34, JPM −2.89,
    GOOGL −2.67). The pre-registered exit-signal correlation EQUALS R9's
    position correlation to 1e-15 (`corr(1-x,1-y)=corr(x,y)` confirmed), 0/15
    trip >0.5; `research-round-10-results.md`.
15. R11 is the cross-asset regime conditioning round (condition a risk-leg
    target's exposure CONTINUOUSLY on a CAUSAL cross-asset regime score via a
    causal rolling-percentile-rank), graded at its honest multiplicities —
    per-lane K=9 (bar 2.54) and program-wide K=27 (bar 2.90). Best t 0.68 (NVDA
    `xasset_breadth`/W252) is barely a quarter of the nearer bar; 0 KILL-SIG.
    Only 2 of 27 conditioned lanes beat their own base buy-and-hold (both NVDA
    `xasset_breadth`); the median lane loses −0.257 Sharpe to its hold because a
    rank-normalized exposure averages ~0.5 and structurally sheds the drift. The
    headline no-lookahead truncation control PASSES on the real panels (45
    probes, 0 diff), so the null is causal, not a hindsight artifact; reproduces
    the burned R4 `crossasset_gate` (0/2) / `regime_switch` (0/6) null with the
    continuous form + unconditioned control (`research-round-11-results.md`).

## How to read this

- **KEEP-dev = dev-candidate only, never a finding.** Every KEEP above is a
  dev-data artifact scored on the same window it was selected in — not an
  out-of-sample claim. Genuine OOS validation of any survivor requires a
  new, owner-gated, pre-registered protocol on post-2026 data.
- **The bar is never lowered.** `min_tstat(K) = Φ⁻¹(1 − 0.05/max(1,K))` is a
  one-sided Bonferroni correction over K = variants tried; it **only ever
  rises** (1.645 at K=1, ≈2.33 at K=5, 2.638 at K=12, up to 3.448 at
  K=177). K rises only as more variants are tried; no K was ever counted
  down.
- **Best-t is informational.** Promotion is CLOSED and the holdout is SPENT,
  so the "Best t" column measures nothing that could promote — it exists to
  show how far the strongest dev arm each round sat *below* its bar. None
  came within ~1.0 t.
- **KILL-SIG = significantly harmful** (t ≤ −`min_tstat`), a mirror of the
  bar in the negative. A KILL-SIG is *explicitly NOT a signal to invert* the
  strategy — it flags a lane whose measured harm is beyond noise (often an
  exposure artifact, e.g. Round 4's 30 day-of-week KILL-SIGs).
- **Nulls and KILLs are first-class results.** The program's product is its
  ledgered negative evidence, not a strategy.

---

*Provenance: generated 2026-07-17 (UTC) from the cited committed results and
retrospective docs at origin/main HEAD `82ef4cc` (Round 7 / PR #141), and
extended 2026-07-19 with the R7-C / R7-D / R8 / R9 rows (carried from
[cross-round-meta-analysis.md](cross-round-meta-analysis.md) and
`research-round-9-results.md`). This is a docs-only synthesis — source code
and merged results always win over this page. Extended 2026-07-19 with the R10
row (inverse-confluence exit vote, 60 configs / 0 promoted; carried from
`research-round-10-results.md`) and the R11 row (cross-asset regime
conditioning, 27 configs / 0 promoted; carried from
`research-round-11-results.md`). See [research-program-retrospective.md](research-program-retrospective.md)
for the narrative synthesis (Rounds 1–6),
[cross-round-meta-analysis.md](cross-round-meta-analysis.md) for the
effect-size synthesis extended through Round 8 (5,793 configs / 0 promoted),
and each linked `research-round-N-results.md` for the per-round detail.*
