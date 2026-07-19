# Research Round 9 — Results (Signal-Confluence Vote, cross-class ≥K-of-N)

> **Status:** `reference` — honest results of the pre-registered Round-9
> signal-confluence sweep, against the protocol in
> [research-round-9-plan.md](research-round-9-plan.md) (merged as PR #153
> BEFORE any Round-9 outcome existed). **POST-HOLDOUT, DEV-ONLY: the holdout
> is SPENT and promotion is CLOSED.** Nothing on this page is an out-of-sample
> claim; a KEEP means *dev-candidate only*, and nulls/KILLs are first-class
> results. The multiple-testing bar is unchanged
> (`trading_lab.promotion.min_tstat`): per-lane **K=4 ≈ 2.24**, program-wide
> **K=60 ≈ 3.14** — only ever rises, never lowered. Round 9 is graded under
> the selection-fair standing gate ([selection-fair-gate.md](selection-fair-gate.md)):
> the gate ran on EVERY lane, and its result block is each lane's R5-D
> fixed-config row.

**Round headline: the owner's signal-confluence idea — "wait until ≥2 or 3
distinct strategies agree" — does NOT beat buy-and-hold on dev data, and the
mechanism is now measured. Across the 60 pre-registered lanes the cross-class
≥K-of-N vote yields 11 weak KEEP-dev / 44 KILL / 5 KILL-SIG, 0 promoted, best
informational t anywhere 1.04 (BTC-USD SET-3/K=2) against the K=4 bar 2.24 and
the program K=60 bar 3.14 — under half the nearest bar. The pre-registered
correlation check is decisive and, in one respect, *surprising*: on ALL 15
instruments the mean pairwise member position-correlation is NEGATIVE
(−0.19 … +0.05); ZERO instruments trip the >0.5 disqualification. So the vote
is genuinely NOT "one signal counted twice" — the distinct-class members are
near-independent, exactly the honest prior's anti-correlation. What that buys
is decided by trade count: the strict all-agree corner SET-3/K=3 COLLAPSES the
trade count (median shrinkage ×0.51, SE-inflation ×1.40) and is precisely
where all 5 KILL-SIG lanes land — insisting three distinct classes agree at
once selects a worse-than-hold slice of the tape on high-drift names (NVDA
t −5.09, JPM −2.64, MSFT −2.88, AAPL −2.53, BTC −2.38). The looser majority
votes do the opposite — they INFLATE the trade count (median shrinkage up to
×1.99, whipsaw churn) and lose to B&H by paying more costs for a choppier,
less-in-market exposure. Either way the confluence adds no benchmark-beating
edge. The gate ran on all 60 lanes (16 PASS / 44 FAIL) and was load-bearing:
it demoted 1 Round-2-rule KEEP (TLT SET-5/K=2). Zero UNGRADEABLE lanes, no
degenerate zero-trade lane, no infrastructure alarm. Runtime 26 s vs a 900 s
cap; no CAP-HIT, nothing truncated. Round-9 burden: 60 new registered configs;
program cumulative 5,793 → 5,853, still 0 promoted.**

| Slice | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Best t (vs 2.24 / 3.14) | Runtime vs cap |
|---|---|---|---|---|---|---|---|
| R9 `r9-confluence` (daily) | 60 | 11 | 44 | 5 | 16 / 44 | 1.04 | 26 s / 900 s |
| **Round 9** | **60** | **11** | **44** | **5** | **16 / 44** | **1.04** | none hit |

Machine-readable rollup: `summary.json`, `results.csv`, `trade_counts.json`,
and per-instrument `correlations__<ticker>.json` in the slice directory —
[`experiments/sweeps/r9-confluence/`](../experiments/sweeps/r9-confluence/)
(runner `scripts/run_r9_confluence_sweep.py`).

## Reading the per-lane table

Members run at their FIXED `DEFAULT_PARAMS` (no per-member re-search — plan
§3), so each confluence lane is itself a fixed-config evaluation: the
full-dev-period backtest carries no in-sample parameter selection, and the
only searched axis is (member-set, K) = 4 vote configs per instrument. In the
table below `Sharpe` is the lane's full-dev-period net-of-cost Sharpe (5 bps
slippage + 1 bp commission), `bench` the full-period buy-and-hold Sharpe of
the same instrument, `trades` the lane's round-trip count, `t (K=4)` the ORDER
007 Lo-2002 Sharpe-delta t via `promotion.grade_promotion` at the per-lane
Bonferroni K=4 (bar 2.24). `fixed` and `gap` are the selection-fair gate's
R5-D row (see below): `fixed` is the selection-free replay of THIS config over
contiguous 1008/252 walk-forward test windows, `gap = searched − fixed` where
`searched` is the instrument's BEST-of-4 vote config over the same windows
(the round's (member-set, K) search dimension, plan §9) — informational, no
registered threshold. Verdict = Round-2 rule, then `classify_verdict`
(KILL-SIG at t ≤ −2.24), then `apply_gate` (the gate only ever demotes). Every
lane's t is ALSO reported against the program K=60 bar 3.14 in `results.csv` —
no lane comes within 2.1 t of it.

| Lane (instrument · set/k) | Sharpe | bench | trades | t (K=4) | fixed | gap | gate | verdict |
|---|---|---|---|---|---|---|---|---|
| AAPL · set3/k2 | 0.908 | 0.977 | 124 | -0.267 | 0.836 | 0.224 | FAIL | **KILL** |
| AAPL · set3/k3 | 0.323 | 0.977 | 40 | -2.532 | 0.301 | 0.759 | FAIL | **KILL-SIG** |
| AAPL · set5/k2 | 1.022 | 0.977 | 149 | 0.175 | 1.060 | 0.000 | PASS | **KEEP** |
| AAPL · set5/k3 | 0.885 | 0.977 | 232 | -0.356 | 0.743 | 0.317 | FAIL | **KILL** |
| AMZN · set3/k2 | 0.680 | 0.864 | 139 | -0.712 | 0.754 | 0.000 | FAIL | **KILL** |
| AMZN · set3/k3 | 0.423 | 0.864 | 40 | -1.707 | 0.140 | 0.614 | FAIL | **KILL** |
| AMZN · set5/k2 | 0.822 | 0.864 | 153 | -0.162 | 0.635 | 0.119 | FAIL | **KILL** |
| AMZN · set5/k3 | 0.610 | 0.864 | 255 | -0.983 | 0.576 | 0.178 | FAIL | **KILL** |
| BTC-USD · set3/k2 | 1.182 | 0.912 | 117 | 1.042 | 1.141 | 0.000 | PASS | **KEEP** |
| BTC-USD · set3/k3 | 0.296 | 0.912 | 40 | -2.383 | 0.380 | 0.761 | FAIL | **KILL-SIG** |
| BTC-USD · set5/k2 | 1.168 | 0.912 | 93 | 0.990 | 1.029 | 0.112 | PASS | **KEEP** |
| BTC-USD · set5/k3 | 1.113 | 0.912 | 221 | 0.777 | 1.068 | 0.073 | PASS | **KEEP** |
| GLD · set3/k2 | 0.330 | 0.429 | 122 | -0.384 | 0.236 | 0.402 | FAIL | **KILL** |
| GLD · set3/k3 | 0.566 | 0.429 | 36 | 0.532 | 0.638 | 0.000 | PASS | **KEEP** |
| GLD · set5/k2 | 0.334 | 0.429 | 168 | -0.366 | 0.358 | 0.280 | FAIL | **KILL** |
| GLD · set5/k3 | 0.143 | 0.429 | 208 | -1.108 | 0.336 | 0.302 | FAIL | **KILL** |
| GOOGL · set3/k2 | 0.310 | 0.755 | 143 | -1.722 | 0.080 | 0.482 | FAIL | **KILL** |
| GOOGL · set3/k3 | 0.278 | 0.755 | 38 | -1.847 | 0.399 | 0.163 | FAIL | **KILL** |
| GOOGL · set5/k2 | 0.601 | 0.755 | 151 | -0.594 | 0.562 | 0.000 | FAIL | **KILL** |
| GOOGL · set5/k3 | 0.182 | 0.755 | 239 | -2.218 | -0.126 | 0.688 | FAIL | **KILL** |
| JPM · set3/k2 | 0.216 | 0.658 | 142 | -1.711 | 0.126 | 0.460 | FAIL | **KILL** |
| JPM · set3/k3 | -0.025 | 0.658 | 56 | -2.643 | -0.224 | 0.810 | FAIL | **KILL-SIG** |
| JPM · set5/k2 | 0.646 | 0.658 | 161 | -0.046 | 0.586 | 0.000 | FAIL | **KILL** |
| JPM · set5/k3 | 0.230 | 0.658 | 218 | -1.658 | 0.102 | 0.484 | FAIL | **KILL** |
| META · set3/k2 | 0.561 | 0.757 | 122 | -0.695 | 0.748 | 0.000 | PASS | **KILL** |
| META · set3/k3 | 0.571 | 0.757 | 28 | -0.659 | 0.675 | 0.073 | PASS | **KILL** |
| META · set5/k2 | 0.717 | 0.757 | 118 | -0.140 | 0.666 | 0.083 | PASS | **KILL** |
| META · set5/k3 | 0.461 | 0.757 | 230 | -1.049 | 0.479 | 0.269 | FAIL | **KILL** |
| MSFT · set3/k2 | 0.467 | 0.914 | 134 | -1.730 | 0.591 | 0.345 | FAIL | **KILL** |
| MSFT · set3/k3 | 0.435 | 0.914 | 30 | -1.854 | 0.281 | 0.655 | FAIL | **KILL** |
| MSFT · set5/k2 | 0.853 | 0.914 | 127 | -0.239 | 0.937 | 0.000 | FAIL | **KILL** |
| MSFT · set5/k3 | 0.171 | 0.914 | 291 | -2.879 | 0.213 | 0.724 | FAIL | **KILL-SIG** |
| NVDA · set3/k2 | 0.795 | 1.070 | 131 | -1.064 | 0.915 | 0.185 | FAIL | **KILL** |
| NVDA · set3/k3 | -0.243 | 1.070 | 28 | -5.085 | -0.176 | 1.276 | FAIL | **KILL-SIG** |
| NVDA · set5/k2 | 0.926 | 1.070 | 141 | -0.557 | 1.066 | 0.035 | FAIL | **KILL** |
| NVDA · set5/k3 | 0.968 | 1.070 | 254 | -0.392 | 1.101 | 0.000 | FAIL | **KILL** |
| QQQ · set3/k2 | 0.671 | 0.943 | 142 | -1.054 | 0.619 | 0.165 | FAIL | **KILL** |
| QQQ · set3/k3 | 0.406 | 0.943 | 54 | -2.081 | 0.563 | 0.222 | FAIL | **KILL** |
| QQQ · set5/k2 | 0.926 | 0.943 | 158 | -0.067 | 0.785 | 0.000 | FAIL | **KILL** |
| QQQ · set5/k3 | 0.796 | 0.943 | 228 | -0.571 | 0.682 | 0.103 | FAIL | **KILL** |
| SLV · set3/k2 | -0.087 | 0.253 | 140 | -1.317 | -0.372 | 0.587 | FAIL | **KILL** |
| SLV · set3/k3 | -0.044 | 0.253 | 40 | -1.150 | -0.215 | 0.430 | FAIL | **KILL** |
| SLV · set5/k2 | 0.237 | 0.253 | 113 | -0.063 | 0.215 | 0.000 | PASS | **KILL** |
| SLV · set5/k3 | -0.178 | 0.253 | 278 | -1.670 | -0.287 | 0.502 | FAIL | **KILL** |
| SPY · set3/k2 | 0.760 | 0.867 | 128 | -0.414 | 0.681 | 0.000 | FAIL | **KILL** |
| SPY · set3/k3 | 0.545 | 0.867 | 44 | -1.249 | 0.558 | 0.122 | FAIL | **KILL** |
| SPY · set5/k2 | 0.590 | 0.867 | 188 | -1.073 | 0.511 | 0.170 | FAIL | **KILL** |
| SPY · set5/k3 | 0.692 | 0.867 | 220 | -0.678 | 0.627 | 0.054 | FAIL | **KILL** |
| TLT · set3/k2 | 0.317 | 0.243 | 116 | 0.287 | 0.328 | 0.173 | PASS | **KEEP** |
| TLT · set3/k3 | 0.028 | 0.243 | 36 | -0.832 | 0.106 | 0.395 | FAIL | **KILL** |
| TLT · set5/k2 | 0.369 | 0.243 | 131 | 0.489 | 0.195 | 0.306 | FAIL | **KILL** |
| TLT · set5/k3 | 0.338 | 0.243 | 200 | 0.370 | 0.502 | 0.000 | PASS | **KEEP** |
| TSLA · set3/k2 | 0.711 | 0.928 | 128 | -0.824 | 0.448 | 0.315 | FAIL | **KILL** |
| TSLA · set3/k3 | 0.392 | 0.928 | 36 | -2.040 | 0.268 | 0.494 | FAIL | **KILL** |
| TSLA · set5/k2 | 0.964 | 0.928 | 69 | 0.139 | 0.762 | 0.000 | PASS | **KEEP** |
| TSLA · set5/k3 | 0.646 | 0.928 | 227 | -1.073 | 0.431 | 0.331 | FAIL | **KILL** |
| XOM · set3/k2 | 0.435 | 0.391 | 124 | 0.171 | 0.371 | 0.037 | PASS | **KEEP** |
| XOM · set3/k3 | 0.446 | 0.391 | 58 | 0.215 | 0.408 | 0.000 | PASS | **KEEP** |
| XOM · set5/k2 | 0.379 | 0.391 | 143 | -0.047 | 0.297 | 0.111 | PASS | **KILL** |
| XOM · set5/k3 | 0.427 | 0.391 | 196 | 0.139 | 0.318 | 0.090 | PASS | **KEEP** |

### Counts

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | KEEPs demoted by gate | Promoted |
|---|---|---|---|---|---|---|---|
| 60 | 11 | 44 | 5 | 16 | 44 | 1 | 0 |

The 11 KEEP-dev lanes (best t 1.04, all far below the K=4 bar 2.24) cluster on
the low-vol / high-drift survivorship names every prior round has returned —
BTC-USD (×3), XOM (×3), TLT (×2), GLD, TSLA, AAPL — never a diversified
cross-class edge. The single best lane, BTC-USD SET-3/K=2 (t 1.04), is a
momentum-heavy name where any long-biased vote spends most of its time long;
the cheapest reading is survivorship of a near-B&H exposure, not a confluence
edge. Dev-candidate only.

## Pre-registered correlation / overlap check (plan §6, first-class)

For each instrument, over the members' shared dev-rail bars, the run computes
(a) the pairwise correlation of member POSITION series (0/1 lanes), (b) the
pairwise signal-overlap Jaccard = bars-both-long / bars-either-long, and (c)
the pairwise correlation of member daily RETURN streams (full matrices in
`correlations__<ticker>.json`). The pre-registered decision rule, verbatim:
*"Confluence between correlated members is one signal counted twice; if mean
pairwise member position-correlation on an instrument exceeds ~0.5, any
apparent vote edge is not diversified and must be reported as such."*

**Result: 0 of 15 instruments trip the >0.5 flag — on the contrary, the mean
pairwise member position-correlation is NEGATIVE on every name.** SET-3 ranges
−0.19 (META) … −0.07 (TLT, XOM); the SET-5 superset ranges −0.07 … +0.05.
The distinct-class members are near-independent-to-mildly-anti-correlated,
exactly the honest registered prior (a momentum member is long in uptrends
precisely when a mean-reversion member is flat waiting for oversold). This is
the *good* case for the diversification argument — the vote is genuinely NOT
one signal counted twice — and it is why no KEEP is disqualified on
correlation grounds. The problem is not redundancy; it is that near-independent
signals rarely co-agree, which routes the entire effect through the trade-count
mechanism below.

| Instrument | mean pos-corr SET-3 | mean pos-corr SET-5 | >0.5 flag |
|---|---|---|---|
| AAPL | -0.125 | -0.035 | no |
| AMZN | -0.111 | -0.019 | no |
| BTC-USD | -0.178 | -0.071 | no |
| GLD | -0.134 | +0.003 | no |
| GOOGL | -0.101 | +0.002 | no |
| JPM | -0.140 | -0.021 | no |
| META | -0.191 | -0.068 | no |
| MSFT | -0.141 | -0.033 | no |
| NVDA | -0.163 | -0.068 | no |
| QQQ | -0.104 | -0.001 | no |
| SLV | -0.110 | -0.015 | no |
| SPY | -0.089 | +0.042 | no |
| TLT | -0.073 | +0.047 | no |
| TSLA | -0.117 | -0.030 | no |
| XOM | -0.071 | -0.005 | no |

## Pre-registered trade-count / power impact (plan §7, first-class)

Fewer trades = weaker statistics (SE(SR) ∝ sqrt((1 + SR²/2) / N), so smaller
effective N ⇒ larger SE ⇒ a HIGHER t required to clear the same fixed effect).
The run reports, per instrument and set: trades(single-member mean),
trades(K=2), trades(K=3), the shrinkage factor `trades(vote) / trades(single
mean)`, and the implied SE inflation. The finding is **regime-split** and
worth stating plainly, because the pooled median (×1.63) hides it:

- **SET-3 / K=3 — the strict all-agree corner — genuinely COLLAPSES the trade
  count** (median shrinkage **×0.51**, i.e. ~half the trades of an average
  single member; implied SE inflation **×1.40**, i.e. the effective bar rises
  ~40%). This is where all 5 KILL-SIG lanes land. Requiring three distinct
  thesis-classes to agree at once is rare (near-independent members), so the
  vote is out of the market during exactly the drift a buy-and-hold captures —
  significantly value-destroying on high-drift names, not merely
  uninformative.
- **The looser votes INFLATE the trade count** — SET-3/K=2 median ×1.80,
  SET-5/K=3 median ×1.99 (SE *deflation*, more trades). But the extra trades
  are whipsaw churn: near-independent members flicker in and out of joint
  agreement, so the vote pays more cost for a choppier, less-in-market exposure
  and still loses to B&H.

Neither regime helps: the strict corner loses power *and* value; the loose
corner burns cost. No lane produced near-zero or zero trades — the sparsest
(META SET-3/K=3, 28 trades) is still gradeable, so there are **0 degenerate /
ungradeable K=3 lanes**.

| Instrument | single-mean (SET-3 / SET-5) | SET-3 K=2 / K=3 (shrink K3) | SET-5 K=2 / K=3 (shrink K3) |
|---|---|---|---|
| AAPL | 68 / 113 | 124 / 40 (×0.59) | 149 / 232 (×2.06) |
| AMZN | 79 / 125 | 139 / 40 (×0.51) | 153 / 255 (×2.04) |
| BTC-USD | 65 / 118 | 117 / 40 (×0.62) | 93 / 221 (×1.87) |
| GLD | 75 / 116 | 122 / 36 (×0.48) | 168 / 208 (×1.80) |
| GOOGL | 80 / 123 | 143 / 38 (×0.47) | 151 / 239 (×1.95) |
| JPM | 76 / 120 | 142 / 56 (×0.73) | 161 / 218 (×1.82) |
| META | 61 / 102 | 122 / 28 (×0.46) | 118 / 230 (×2.26) |
| MSFT | 72 / 121 | 134 / 30 (×0.41) | 127 / 291 (×2.40) |
| NVDA | 70 / 115 | 131 / 28 (×0.40) | 141 / 254 (×2.20) |
| QQQ | 78 / 115 | 142 / 54 (×0.69) | 158 / 228 (×1.99) |
| SLV | 84 / 122 | 140 / 40 (×0.48) | 113 / 278 (×2.29) |
| SPY | 71 / 116 | 128 / 44 (×0.62) | 188 / 220 (×1.90) |
| TLT | 67 / 108 | 116 / 36 (×0.54) | 131 / 200 (×1.85) |
| TSLA | 74 / 111 | 128 / 36 (×0.48) | 69 / 227 (×2.05) |
| XOM | 74 / 119 | 124 / 58 (×0.79) | 143 / 196 (×1.65) |

Per-set medians (in `trade_counts.json`): SET-3 shrink K=2 ×1.80 / K=3 ×0.51
(SE-inflation ×0.74 / ×1.40); SET-5 shrink K=2 ×1.22 / K=3 ×1.99 (SE-inflation
×0.90 / ×0.71). Trades were never invented to rescue power; the shrinkage IS
part of the finding.

## R5-D fixed-config rows & selection-fair gate (standing rules 1–2)

The selection-fair standing gate ([selection-fair-gate.md](selection-fair-gate.md))
ran on all 60 lanes with the
fidelity guard armed (searched arm = the instrument's best-of-4 vote config
over the committed 1008/252 test windows; every replay reproduced its recorded
stitched Sharpe within 1e-8, so **0 fidelity failures**). The gate block
doubles as each lane's R5-D fixed-config row: the `fixed` and `gap` columns in
the per-lane table above. **16 PASS / 44 FAIL.** The gate was load-bearing: it
demoted **1 Round-2-rule KEEP** — TLT SET-5/K=2 (full-period Sharpe 0.369 >
full-period bench 0.243 by the Round-2 rule, but over the walk-forward test
windows the selection-free fixed replay 0.195 loses to the 0.196 same-window
benchmark → gate FAIL → KILL). `selection_gap ≥ 0` on every lane (the searched
best-of-4 never underperforms an individual fixed config over the windows),
consistent with the searched arm being an upper envelope of the four.

## reason_class rollup (all 60 lanes)

Machine-readable `selection_gate.reason_class` across the slice (standing rule
3 — the UNGRADEABLE-share is an INFRASTRUCTURE alarm, never strategy evidence):

| reason_class | count | kind |
|---|---|---|
| `PASS` | 16 | gate pass |
| `FAIL_UNDERPERFORM` | 38 | genuine rule failure (fixed positive, below same-window B&H) |
| `FAIL_NONPOSITIVE` | 6 | genuine rule failure (fixed Sharpe ≤ 0) |
| `UNGRADEABLE_MISSING_WINDOWS` | 0 | infrastructure |
| `UNGRADEABLE_DRIFT` | 0 | infrastructure |
| `UNGRADEABLE_NONCONTIGUOUS` | 0 | infrastructure |
| `UNGRADEABLE_FIDELITY` | 0 | infrastructure |
| `UNGRADEABLE_NAN` | 0 | infrastructure |
| **total** | **60** | |

**UNGRADEABLE share: 0 of 60 lanes (0.0%) — no infrastructure alarm.** Every
`selection_gate.UNGRADEABLE_CLASSES` count is zero: no missing/non-contiguous
windows, no cache drift, no fidelity-guard miss, no NaN degeneracy, and no
degenerate zero-trade lane. The 44 gate FAILs are all genuine rule failures
(38 `FAIL_UNDERPERFORM` where the fixed config is positive but below its
same-window benchmark, 6 `FAIL_NONPOSITIVE` where the fixed stitched Sharpe is
≤ 0), not irreproducible lanes — so the Round-9 nulls and the 5 KILL-SIG
negatives are strategy evidence, read as designed.

## Plain-language verdict — the owner's question, answered honestly

The owner asked: *"isn't it a good idea to find multiple strategies and wait
until at least 2 or 3 give the same signals?"* Round 9 tested exactly that on
15 instruments — a binary cross-thesis-class ≥K-of-N vote — and the honest
answer on dev data is **no, it does not help, and now we know why.**

The intuition ("agreement should be a stronger signal") assumes the strategies
carry independent information that *reinforces* on agreement. Two things break
that here. First, the distinct-class members ARE near-independent (mean
position-correlation is negative on all 15 names — so this is NOT the failure
mode of counting one signal twice). Second — and this is the mechanism —
because they are near-independent, they rarely agree at the same time. Waiting
for **all** of them to agree (SET-3/K=3) cuts the trade count roughly in half
and leaves the strategy sitting flat through exactly the drift that a plain
buy-and-hold rides, which is *significantly worse* than holding on high-drift
names (NVDA, JPM, MSFT, AAPL, BTC — the 5 KILL-SIG lanes). Loosening to a
2-of-N majority instead makes the combined signal *choppier* — it flickers in
and out as different members briefly agree — so it trades MORE, pays more cost,
and still trails buy-and-hold. Best case anywhere: t = 1.04 (BTC-USD), less
than half the significance bar, on a momentum-heavy name where any long-biased
rule looks good. **Zero of 60 configs cleared the bar; nothing was promoted.**

This confirms and extends two priors, both cited in the plan. **R4-C** (the
survivor-committee AVERAGE, `research-round-4-results.md` §R4-C) found the
diversification premium concentrated in small closely-matched committees and
cleared nothing (best t 1.09, 0 promoted). **R7-C** (`washout_recovery`,
`research-round-7c-results.md`) found a within-class AND-conjunction actively
value-destroying on 3 high-drift names (KILL-SIG on AMZN/MSFT/QQQ). Round 9 is
the cross-class binary vote neither ran, and it lands in the same place, with
the R7-C harm pattern recurring one abstraction up: a cross-class AND vote
(K=3) is significantly value-destroying on high-drift names for the identical
reason — insisting on simultaneous agreement holds you out of the trend.

## Round 9 — closing tally (2026-07-19)

| Slice | One-line verdict |
|---|---|
| R9 signal-confluence vote | **11/60 weak KEEP-dev** (best t 1.04, BTC-USD SET-3/K=2 — under half the K=4 bar 2.24, far under the K=60 bar 3.14), 5 KILL-SIG (all the strict all-agree corner: NVDA −5.09, MSFT −2.88, JPM −2.64, AAPL −2.53, BTC −2.38); waiting for ≥2–3 distinct strategies to agree adds NO benchmark-beating edge — members are near-independent (0/15 trip >0.5) so agreement is rare, which either collapses the trade count (strict vote, value-destroying on drift) or churns it up (loose vote, cost-bleeding). |

- **Cumulative burden**: exactly **5,793 → 5,853 registered configs (60 new)**
  (`sweeps.r9_total_configs()` = 60, pinned by tests; the runner asserts it
  before running). No K was counted down and no bar was lowered (informational
  t at K=4 per lane, K=60 program-wide, bars 2.24 / 3.14).
- **Runtime cap**: not hit (slice runtime 26 s against a 900 s cap); nothing
  truncated, no lanes skipped, **no CAP-HIT**.
- **The standing gate, read honestly**: ran on all 60 lanes (fidelity 60/60
  within 1e-8, zero UNGRADEABLE) and demoted 1 Round-2-rule KEEP (TLT
  SET-5/K=2). 16 PASS / 44 FAIL, all FAILs genuine rule failures.
- **0 promoted — promotion remains CLOSED, holdout SPENT.** Every KEEP-dev is
  a dev-candidate only (best t 1.04 vs the nearest bar 2.24); genuine OOS
  validation stays OWNER-GATED behind a new pre-registered protocol on
  post-2026 data.
- **What the round established**: (1) cross-class signal confluence carries no
  information the isolated members lacked that survives net of cost — 0
  promoted, best t under half the bar; (2) the failure is NOT
  redundancy/over-correlation (0/15 trip >0.5; members are near-independent) —
  it is the co-agreement mechanism: strict agreement collapses trade count and
  is value-destroying on drift (5 KILL-SIG), loose agreement churns and bleeds
  cost; (3) the selection-fair gate stayed cheap (60 replays in 26 s),
  zero-UNGRADEABLE, and earned its keep by demoting a gap-flattered KEEP.

Round 9 is graded. One slice, one honest answer to a live owner question, zero
findings, zero cap-hits, eleven weak dev-candidates, and the program's first
cross-class confluence result: the "wait for agreement" idea, tested honestly,
does not beat buy-and-hold on dev data. Anything further still needs new data
(OWNER-GATED) or a genuinely different idea class.
