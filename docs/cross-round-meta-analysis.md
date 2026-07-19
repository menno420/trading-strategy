# Cross-Round Meta-Analysis — Rounds 1–10

> **Status:** `reference`
>
> Written 2026-07-18 (UTC); scoreboard extended 2026-07-19 with Rounds 9 and 10.
> An honest synthesis across the whole research program — P1 baselines through
> Round 10 — consolidating what the existing
> program-wide docs cover separately: the narrative
> [research-program-retrospective.md](research-program-retrospective.md)
> (Rounds 1–6) and the scoreboard
> [research-program-dashboard.md](research-program-dashboard.md) (P1 → Round 7).
> This doc extends both through the five newest slices (R7-A/B, R7-C, R7-D, R8,
> R9) and foregrounds the **effect-size distribution** — how far the strongest dev
> arm each round sat *below* its significance bar.
>
> **RESEARCH-ONLY, IN-SAMPLE.** Every number below traces to a committed round
> JSON or results doc; where a figure was never recorded the text says so. This
> file reads **no holdout data** — the holdout is **SPENT** and untouched
> (13 one-shot reads, ORDER 008) — schedules nothing, changes no verdict, and
> implies **no promotion**: promotion is **CLOSED**. Source code and merged
> results always win over this page. **This is NOT investment advice.**

---

## Headline — the negative result IS the finding

Across P1 baselines through Round 10 the program registered **5,913 registered
configurations and promoted 0.** **No strategy ever cleared the significance
bar** (`trading_lab.promotion.min_tstat(K)` ≈ 2.638 at K=12; the bar only ever
rises). The negative result *is* the finding — a clean, honest **offline
research library, not a live trading system.**

The single PROMOTED-TO-FINDING ever minted — AAPL donchian, P2 era — was
demoted to RULE-PASS on 2026-07-10 under ORDER 007; its one-shot holdout
confirmation was t = 0.02 (`p2-regrade-aapl-donchian.md`;
`research-program-retrospective.md` §d/§f). Nothing in eight rounds came within
~1.0 t of its bar. The program's best informational t **anywhere** is **1.66**
(Round 5, an SLV `williams_r_reversion` grid neighbor,
`research-round-5-results.md` L46–48) — still far under any bar in use.

## Per-round scoreboard (P1 → Round 10)

Extends the [dashboard](research-program-dashboard.md) (P1 → Round 7) with the
five post-Round-7 slices (R7-C, R7-D, R8, R9, R10). Every cell is carried from a cited
committed source; `n/r` = not recorded in the round's doc (never an invented
value). KEEP/KILL/KILL-SIG are **not additive** across rounds — later rounds
re-grade and demote earlier lanes (see the dashboard's footnote 11) — so the
**Program total** row totals only the two additive columns (configs and
promotions).

| Round | Configs added | Cumulative | KEEP-dev | KILL | KILL-SIG | Best t (vs bar) | Promoted | Source |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| P1 baselines | 590 | 590 | n/r¹ | n/r¹ | n/r¹ | n/r¹ | 0 | `p1-*-results.md` |
| Round 2 | 78 | 668 | 5 | 9 | —² | n/r² | 0 | `research-round-2-results.md` |
| interim · bollinger-mtf | 12 | 680 | 0 | n/r | —² | n/r | 0 | `research/bollinger-mtf-dev-2026-07-12.md` |
| Round 3 | 3,468 | 4,148 | 58³ | 238³ | 4³ | 1.04 (vs 2.64) | 0 | `research-round-3-results.md`; `research-round-4-results.md` §R4-A |
| Round 4 | 197 | 4,345 | 5⁴ | 60⁴ | 30⁴ | 1.09 (vs 2.64) | 0 | `research-round-4-results.md` |
| Round 5 | 14 | 4,359 | 4 | 1 | 0 | **1.66** (vs 2.64) | 0 | `research-round-5-results.md` |
| Round 6 | 696 | 5,055 | 3 | 47 | 8 | 0.60 (vs 2.64) | 0 | `research-round-6-results.md` |
| Round 7 (A+B) | 360 | 5,415 | 5 | 25 | 0 | 1.20 (vs 2.64) | 0 | `research-round-7-results.md` |
| Round 7C | 180 | 5,595 | 1 | 11 | 3 | 0.22 (vs 2.64) | 0 | `research-round-7c-results.md` |
| Round 7D | 6 | 5,601 | 0 | 6 | 0 | −0.74 (vs 2.39)⁵ | 0 | `research-round-7d-results.md` |
| Round 8 | 192 | 5,793 | 3 | 13 | 0 | 1.08 (vs 2.64) | 0 | `research-round-8-results.md` |
| Round 9 | 60 | 5,853 | 11 | 44 | 5 | 1.04 (vs 2.24 / 3.14)⁷ | 0 | `research-round-9-results.md` |
| Round 10 | 60 | 5,913 | 11 | 40 | 9 | 1.04 (vs 2.24 / 3.14)⁸ | 0 | `research-round-10-results.md` |
| **Program total** | **5,913** | **5,913** | —⁶ | —⁶ | —⁶ | **1.66** (R5) | **0** | rows above |

The cumulative column reconciles exactly: the dashboard's chain to 5,415
(P1 → Round 7) plus **180 (R7-C) + 6 (R7-D) + 192 (R8) + 60 (R9) + 60 (R10) =
5,913** (`sweeps.r7c_total_configs()` / `r7d_total_configs()` /
`r9_total_configs()` / `r10_total_configs()` and the R8 grid identity, each
pinned by `tests/test_sweeps.py`; the R10 `summary.json` `program_variants_tried`
field reads `5913`). P2/P4/P5 added *runs* but no new registered configs, so they
are not separate rows.

**Footnotes.** ¹ P1 predates the KEEP/KILL vocabulary (Round 2 §6) and computed
no Bonferroni t by design; it graded beats-vs-B&H (7/32 trend daily, 3/24
mean-rev, 5/32 trend hourly) — "weak evidence, not a discovery"
(`research-program-retrospective.md` §a). ² The KILL-SIG class did not exist
until R4-A, and Round 2 computed no t-stats anywhere by design. ³ Round 3's own
core headline is 1,752 configs / 41 KEEP / 125 KILL of 166 lanes (best t 1.04);
this row uses the **full committed surface** (3,468 configs → 302 summaries)
re-graded 58 KEEP / 238 KILL / 4 KILL-SIG by R4-A. ⁴ Round 4 **new-search**
slices only (R4-C/D/E/F); R4-A/B are re-grades of prior-round lanes, excluded to
avoid double-counting. ⁵ R7-D is a PORTFOLIO lane graded at the xsec K=6
convention (bar ≈2.39), not K=12; its best t is negative (every lane
underperforms the basket B&H). ⁶ KEEP/KILL/KILL-SIG are non-additive across
rounds (dashboard fn 11); the combined post-Round-9 standing KEEP surface is
explicitly **not measured** in any committed doc. ⁷ R9 is the cross-class
≥K-of-N signal-confluence vote graded at the round's honest multiplicities —
per-lane K=4 (bar 2.24) and program-wide K=60 (bar 3.14); its best t 1.04
(BTC-USD SET-3/K=2) is under half the nearer bar. The 5 KILL-SIG lanes are all
the strict all-agree corner (SET-3/K=3 + one SET-5/K=3), significantly
value-destroying on high-drift names (NVDA −5.09, MSFT −2.88, JPM −2.64).
⁸ R10 is the inverse-confluence EXIT vote — the De Morgan dual of R9 (hold by
default, go flat when ≥K distinct classes agree OUT) — graded at the same
honest multiplicities (per-lane K=4 bar 2.24, program K=60 bar 3.14). Its best t
1.04 is the SAME BTC-USD SET-3/K=2 lane and value as R9 (the dual gives the same
best). The 9 KILL-SIG lanes are 8 the loose SET-5/K=2 exit + MSFT SET-5/K=3
(value-destroying on high-drift names: NVDA −4.07, MSFT −3.34, JPM −2.89, GOOGL
−2.67). The pre-registered exit-signal correlation EQUALS R9's position
correlation to 1e-15 (`corr(1-x,1-y)=corr(x,y)` confirmed numerically), 0/15
trip >0.5 — R10 is a proven De Morgan pair with R9 over one identical panel.

## Effect-size distribution — how far below the bar

The zero is not a story of near-misses that "just missed." It is a distribution
whose *strongest* arm each round sat a factor of two or more below its bar. For
the machine-readable era (Rounds 6–8 — the slices carrying a uniform per-lane
`tstat` in their `summary.json`), the table below is **generated, not
hand-typed**, by `python3 scripts/aggregate_effect_sizes.py` (read-only
aggregator over the committed `experiments/sweeps/*/summary.json`, pinned by
`tests/test_aggregate_effect_sizes.py`):

<!-- generated by scripts/aggregate_effect_sizes.py from committed summary.json -->
| Slice | Round configs | Program cumulative | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Best searched t | Best-t lane | Bar |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|
| `r6-volume` | 360 | 4719 | 30 | 2 | 27 | 1 | 9 / 21 | 0.601 | obv_trend · BTC-USD | 2.638 |
| `r6-gap` | 144 | 4863 | 12 | 0 | 5 | 7 | 0 / 12 | -0.585 | overnight_gap · SLV | 2.638 |
| `r6-volume-hourly` | 192 | 5055 | 16 | 1 | 15 | 0 | 8 / 8 | 0.287 | mfi_reversion · AMZN | 2.638 |
| `r7-drawdown-reversion` | 180 | 5235 | 15 | 3 | 12 | 0 | 7 / 8 | 0.302 | drawdown_reversion · XOM | 2.638 |
| `r7-high-proximity` | 180 | 5415 | 15 | 2 | 13 | 0 | 7 / 8 | 1.195 | high_proximity · BTC-USD | 2.638 |
| `r7c-conjunction` | 180 | 5595 | 15 | 1 | 11 | 3 | 2 / 13 | 0.217 | washout_recovery · TLT | 2.638 |
| `r8-hourly` | 192 | 5793 | 16 | 3 | 13 | 0 | 8 / 8 | 1.079 | drawdown_reversion · MSFT | 2.638 |

Read across the whole program, the best informational t per round is:
P1/P2 — no Bonferroni t by design (the only one ever attached, AAPL donchian's
ORDER-007 re-grade, was t = 0.42 at K=1, demoted); Round 3 **1.04**; Round 4
best *new-config* t **1.09** (best stressed re-grade t 1.315, a Round-3 lane);
Round 5 **1.66** (the program maximum, an SLV `williams_r` neighbor); Round 6
**0.60**; Round 7 **1.20**; Round 7C **0.22**; Round 7D **−0.74** (K=6 bar);
Round 8 **1.08** (`research-program-dashboard.md`; the round results docs).
Against bars of 2.33–3.45, **nothing in eight rounds came within ~1.0 t of its
bar**, and the two most-mined instruments produce the two largest numbers
(BTC-USD, SLV) — the signature of selection on a heavily-searched surface, not
of edge.

## The best near-misses — and why they still fail

Four lanes are the program's strongest, and each fails a *different* honest
correction. None is a finding; every t below is against a bar it never
approached.

1. **BTC-USD daily `bollinger_breakout`** (period=10, num_std=1.0) — the
   strongest survivor. R3 t = 1.38; the best *stressed* t in the program at 2×
   costs (t = 1.315); the only lane to trip the R5-C bootstrap escalate branch
   (P(delta≤0) = 0.042), producing the FROZEN owner-gated R5-C OOS proposal
   (`research-round-4-results.md` §R4-B; `research-round-5-results.md` L152–160;
   `proposals/r5c-btc-bollinger-breakout-oos-proposal.md`). **Why it still
   fails:** even its own proposal's prior is "a 1.4-t dev edge on a
   heavily-mined surface usually regresses" (§6), and the walk-forward tail
   discard means the freshest 239 BTC daily dev bars were never scored
   (`.sessions/2026-07-13-r3-btc-coverage.md` L23–46). It sits at ~half the
   K=12 bar, and BTC is the single most-searched instrument on the board.
2. **SLV daily `williams_r_reversion`** — R5-A produced the program's best t
   *anywhere*, **1.66**, in a grid neighbor. **Why it still fails:** R5-D's
   selection-free fixed-config replay showed the searched arm **lost to its own
   fixed config** (selection_gap **−0.313**) — the "edge" is in-window
   re-selection, not signal — and it sits on the second-weakest benchmark on
   the board (0.170): "low bar cleared, not an edge"
   (`research-round-5-results.md` L46–48, L203–207; `research-round-3-results.md`
   §patterns item 1).
3. **BTC-USD daily `high_proximity`** (Round 7, t = 1.195, gate PASS) — the
   strongest arm of the machine-readable era. **Why it still fails:** BTC-USD
   already holds a price-only trend-family KEEP-dev, so "close within *p* of the
   trailing *N*-bar high" re-expresses a trend filter rather than adding a
   channel; `selection_gap < 0` on all 15 `high_proximity` lanes
   (`research-round-7-results.md` §R7-B).
4. **MSFT hourly `drawdown_reversion`** (Round 8, t = 1.079, gate PASS) — the
   best hourly arm. **Why it still fails:** the entire hourly stitched OOS is a
   **single ~8.5-month 2024 regime** (5 splits) — the thinnest
   evidence-per-config in the program and the exact R5-B single-window-luck
   exposure that demoted a prior hourly KEEP; "hourly did not manufacture a real
   edge here; it manufactured a handful of regime-fragile dev-candidates on the
   thinnest possible evidence" (`research-round-8-results.md`).

The common thread is **selection-fairness**: R5-D and the standing
selection-fair gate (round 6+) replay each lane's committed top variant with no
in-window re-selection and require it to beat same-window B&H. Across Round 7's
30 lanes `selection_gap > 0` on **only 1**; across Round 7C's 15 lanes on only 1
(and that one, GLD, was *demoted* to KILL by the gate — the first R7-family gate
demotion). "In-window grid re-picking is closer to noise than to signal"
(`research-round-5-results.md` L198–219) is the load-bearing reason the
near-misses are not real.

## Why nothing cleared the bar

Five convergent findings, each ledgered across multiple rounds:

- **The dev surface is mined out.** Three consecutive round closings (4, 5, 6)
  state it in nearly identical words: "anything further on this surface needs
  either new data (OWNER-GATED) or a genuinely different idea class, not more
  variants" (`research-round-4-results.md` L573–575, echoed in 5 and 6). Rounds
  7, 7C, 7D and 8 tested exactly the two permitted moves — new idea *families*
  and a new *bar frequency* on committed caches — and each confirmed the null.
- **Selection ≈ noise.** At Round-6 scale `selection_gap > 0` on only 2 of 58
  lanes; at Round-7 scale 1 of 30; Round 7C 1 of 15. Walk-forward re-selection
  subtracted value almost everywhere it was measured.
- **Conditioning loses to its own controls, on every axis tested** —
  volatility, trend strength, cross-asset momentum all subtracted value against
  their unconditioned controls (`research-round-4-results.md` §closing item 4);
  the mandatory control-arm guard is why "TLT would have looked like a weak KEEP"
  without it.
- **Drawdown reduces drawdown, not return.** The only consistently observed
  effect across the program is drawdown *reduction*, never a decision metric and
  never a benchmark-beating return edge. Round 7's `drawdown_reversion` (3 weak
  KEEP-devs, all low-vol, none near the bar), Round 7D's cross-sectional
  `xsec_drawdown` (0/6, every lane below the basket B&H), and Round 8's hourly
  re-sweep all confirm the drawdown channel carries no exploitable OOS
  information (`research-round-7-results.md`; `research-round-7d-results.md`;
  `research-round-8-results.md`).
- **Nothing transfers.** P4 was 13/13 TRANSFER-FAILED — frozen params beat B&H
  on only 13 of 99 instrument pairs (`p4-transfer-results.md` L101–104); nothing
  found on one instrument ever worked on another.

Notably, the sharpest *information* the program produced is on the KILL side:
overnight gap 0/12 with 7 KILL-SIG (t to −4.01, `research-round-6-results.md`
§R6-B) and the Round-7C conjunction significantly value-destroying on three
high-drift names (AMZN −3.00, MSFT −3.72, QQQ −3.11). A KILL-SIG is explicitly
**NOT a signal to invert** — it flags measured harm beyond noise, usually an
exposure artifact.

## What the negative result teaches

- **The methodology worked exactly as designed.** Each guard added over the
  program caught a documented false positive: the ORDER-007 Bonferroni bar
  demoted the program's only promotion; leave-one-split-out (R5-B) caught the
  META-hourly single-window-luck lane every other slice passed; the bootstrap
  (R5-C) independently flagged the same fragile lane; the selection-fair gate
  (round 6+) demoted a Round-7C KEEP. The zero is a *measured* zero, not an
  absence of looking (`research-program-retrospective.md` §e).
- **A rising, never-lowered bar is what makes the zero honest.**
  `t_min(K) = Φ⁻¹(1 − 0.05/max(1,K))` rises monotonically with variants tried
  (1.645 at K=1 → 2.638 at K=12 → 3.448 at K=177) and was never counted down.
  Under a lane-local bar, several Round-4 Fridays and various weak KEEPs "would
  have been dev-candidates"; at the honest K they miss "by an order of
  magnitude."
- **Nulls and KILLs are the product.** The program's deliverable is its
  ledgered negative evidence — 5,793 configs, every verdict traceable to a
  committed JSON — not a strategy. Honest nulls are first-class.

## What an owner-gated future round would need

Nothing here is recommended; this is a neutral menu, and "doing nothing is a
perfectly acceptable owner choice" (`research-program-retrospective.md` §f–g;
the R5-C proposal). Each option below states what it *could* and *could not*
establish:

1. **New data classes (owner-gated).** New tickers or extended history require a
   fetch decision agents cannot take. Could establish whether surviving families
   behave the same on unmined instruments — genuine dev-fresh evidence. Could
   **not** establish any OOS claim about existing survivors (new dev data mined
   the same way inherits the same K burden) or a promotion (holdout spent).
2. **Genuinely new idea families on existing data.** Lowest cost — committed
   caches only. But three round closings already predict the null, and Rounds
   6–8 spent the last untouched channels (volume, gaps, bar frequency,
   drawdown-anatomy, interaction conjunctions) confirming it.
3. **Execute the pre-registered R5-C BTC-USD OOS check (owner-gated).** One
   owner ORDER fixing a post-2026 window before any bar is inspected, one fetch,
   one selection-free replay. Could establish a first genuinely out-of-sample
   read on the strongest survivor at the pre-registered bar (`min_tstat(5)` ≈
   2.33). Could **not** establish a promotion by itself; its own prior is that a
   1.4-t mined-surface edge usually regresses. **FROZEN, NOT SCHEDULED, NOT
   RUN** — no agent may execute it without an explicit owner ORDER.
4. **Stopping / steady-state.** Zero compute, zero owner action. Preserves the
   negative results, the program's main product; the paper lane accrues forward
   evidence at ~1 window/week (no BEAT streak promotes) — years to significance
   at any honest bar.

**Any of these that touches new data, the holdout, or a promotion path is
owner-gated by construction.** This meta-analysis opens no such path: it reads
only already-committed data.

## Known not-measured items

Carried forward from the retrospective (§f), each per the ledger's own words —
none is a gap this doc fills, since filling them would require new runs:

- **Deflated Sharpe** — never computable (cross-trial variance / skew / kurtosis
  never persisted); the Bonferroni t bar was the declared substitute.
- **No merged post-Round-8 KEEP-dev list** — no committed doc states the
  combined surviving surface (the 4 Round-5 survivors + 3 Round-6 + 5 Round-7 +
  1 Round-7C + 3 Round-8 dev-KEEPs are never reconciled into one standing list;
  KEEP counts are non-additive by construction).
- **Per-lane OOS trade counts / exposure** through Round 3 — "a KEEP on few
  trades is indistinguishable from a KEEP on many."
- **Cost-drag / breakeven-bps** — gross-vs-net never recorded on hourly lanes.
- **239 unscored BTC-USD daily OOS bars** (and 208 hourly) — walk-forward tail
  discard left the freshest dev data unscored.
- **1 infrastructure UNGRADEABLE lane in Round 8** (`drawdown_reversion` · GLD
  hourly, `UNGRADEABLE_NAN`) — an infra fact (degenerate/flat stitched returns),
  reported per standing rule 3 and **never** treated as strategy evidence.

---

*Provenance: generated 2026-07-18 (UTC) from the cited committed results docs
and `experiments/sweeps/*/summary.json` at branch
`claude/cross-round-meta-analysis` off origin/main HEAD `32cbb5f`. The R6–R8
effect-size table is emitted by `scripts/aggregate_effect_sizes.py`
(pytest-pinned); all other figures are quoted from the linked committed docs.
This is a docs-only, in-sample synthesis — source code and merged results always
win over this page. See [research-program-dashboard.md](research-program-dashboard.md)
(P1 → Round 7 scoreboard) and
[research-program-retrospective.md](research-program-retrospective.md)
(narrative, Rounds 1–6) for the underlying detail, and each linked
`research-round-N-results.md` for per-round tables. Promotion CLOSED; holdout
SPENT and untouched. NOT investment advice.*
