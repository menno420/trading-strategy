# Research Round 10 — Results (Inverse-Confluence EXIT Vote, go-flat when cross-class ≥K-of-N agree)

> **Status:** `reference` — honest results of the pre-registered Round-10
> inverse-confluence exit-vote sweep, against the protocol in
> [research-round-10-plan.md](research-round-10-plan.md) (merged as PR #155,
> main `025d9c9`, BEFORE any Round-10 outcome existed). **POST-HOLDOUT,
> DEV-ONLY: the holdout is SPENT and promotion is CLOSED.** Nothing on this page
> is an out-of-sample claim; a KEEP means *dev-candidate only*, and nulls/KILLs
> are first-class results. The multiple-testing bar is unchanged
> (`trading_lab.promotion.min_tstat`): per-lane **K=4 ≈ 2.24**, program-wide
> **K=60 ≈ 3.14** — only ever rises, never lowered. Round 10 is graded under the
> selection-fair standing gate ([selection-fair-gate.md](selection-fair-gate.md)):
> the gate ran on EVERY lane, and its result block is each lane's R5-D
> fixed-config row. The benchmark is **buy-and-hold** — the exit vote is a
> de-risking overlay ON the hold, so each lane's edge is its deviation from
> holding.

**Round headline: the INVERSE of the owner's idea — "use ≥2 or 3 distinct
strategies agreeing to decide when to STEP ASIDE (go flat)" — does NOT beat
buy-and-hold on dev data, and the mechanism is the mirror image of Round 9.
Across the 60 pre-registered lanes the cross-class ≥K-of-N EXIT vote yields 11
weak KEEP-dev / 40 KILL / 9 KILL-SIG, 0 promoted, best informational t anywhere
1.04 (BTC-USD SET-3/K=2) — identical to R9's best, as the De Morgan dual
demands — against the K=4 bar 2.24 and the program K=60 bar 3.14, under half the
nearest bar. The pre-registered correlation check CONFIRMS the Pearson identity
`corr(1-x,1-y) = corr(x,y)` to machine precision: the member EXIT-signal
correlation EQUALS the R9 member POSITION correlation on every one of the 15
instruments (max |exit_corr − pos_corr| = 1.3e-15), so the exit-signal
correlations are negative on all 15 names (−0.19 … +0.05) and ZERO instruments
trip the >0.5 disqualification — a correctness check on the round that also
re-confirms the members are near-independent. What that near-independence buys
is decided by the exit count, and here the two K corners fail from OPPOSITE
sides: the strict all-agree exit (SET-3/K=3) steps aside on a median of only
**8.5% of bars** (median SE-inflation ×3.43) — it barely deviates from
buy-and-hold, so its informational t collapses toward zero (JPM t −0.02, META
−0.05, near-indistinguishable from the hold), an edge you cannot grade AS an
edge; the loose exit (SET-5/K=2) steps aside on a median of **85% of bars** — it
sheds nearly all of the drift a hold rides, and is precisely where 8 of the 9
KILL-SIG lanes land (NVDA t −4.07, MSFT −3.34, JPM −2.89, GOOGL −2.67). Either
way the exit vote adds no benchmark-beating edge. The gate ran on all 60 lanes
(14 PASS / 46 FAIL) with zero fidelity failures; it demoted 0 Round-2-rule KEEPs
this round (it concurred with the Round-2 rule on every lane). Zero UNGRADEABLE
lanes, and no lane produced ~0 exits — the sparsest (JPM SET-3/K=3, 12
step-asides) is still gradeable — so 0 degenerate lanes and no infrastructure
alarm. Runtime 27 s vs a 900 s cap; no CAP-HIT, nothing truncated. Round-10
burden: 60 new registered configs; program cumulative 5,853 → 5,913, still 0
promoted.**

| Slice | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Best t (vs 2.24 / 3.14) | Runtime vs cap |
|---|---|---|---|---|---|---|---|
| R10 `r10-exit-confluence` (daily) | 60 | 11 | 40 | 9 | 14 / 46 | 1.04 | 27 s / 900 s |
| **Round 10** | **60** | **11** | **40** | **9** | **14 / 46** | **1.04** | none hit |

Machine-readable rollup: `summary.json`, `results.csv`, `exit_counts.json`,
and per-instrument `correlations__<ticker>.json` in the slice directory —
[`experiments/sweeps/r10-exit-confluence/`](../experiments/sweeps/r10-exit-confluence/)
(runner `scripts/run_r10_exit_confluence_sweep.py`).

## Reading the per-lane table

Members run at their FIXED `DEFAULT_PARAMS` (no per-member re-search — plan §3),
so each exit-vote lane is itself a fixed-config evaluation: the full-dev-period
backtest carries no in-sample parameter selection, and the only searched axis is
(member-set, K) = 4 exit-vote configs per instrument. In the table below
`Sharpe` is the lane's full-dev-period net-of-cost Sharpe (5 bps slippage + 1 bp
commission), `bench` the full-period buy-and-hold Sharpe of the same instrument,
`exits` the number of step-aside EVENTS (held→flat transitions — the count of
times the lane goes to cash), `trades` the lane's round-trip count, `t (K=4)`
the ORDER 007 Lo-2002 Sharpe-delta t via `promotion.grade_promotion` at the
per-lane Bonferroni K=4 (bar 2.24). `fixed` and `gap` are the selection-fair
gate's R5-D row: `fixed` is the selection-free replay of THIS config over
contiguous 1008/252 walk-forward test windows, `gap = searched − fixed` where
`searched` is the instrument's BEST-of-4 exit-vote config over the same windows
(the round's (member-set, K) search dimension, plan §9) — informational, no
registered threshold. Verdict = Round-2 rule, then `classify_verdict` (KILL-SIG
at t ≤ −2.24), then `apply_gate` (the gate only ever demotes). Every lane's t is
ALSO reported against the program K=60 bar 3.14 in `results.csv` — no lane comes
within 1.9 t of it.

| Lane (instrument · set/k) | Sharpe | bench | exits | trades | t (K=4) | fixed | gap | gate | verdict |
|---|---|---|---|---|---|---|---|---|---|
| AAPL · set3/k2 | 0.908 | 0.977 | 63 | 124 | -0.267 | 0.836 | 0.124 | FAIL | **KILL** |
| AAPL · set3/k3 | 0.949 | 0.977 | 21 | 41 | -0.107 | 0.960 | 0.000 | FAIL | **KILL** |
| AAPL · set5/k2 | 0.497 | 0.977 | 54 | 106 | -1.860 | 0.387 | 0.573 | FAIL | **KILL** |
| AAPL · set5/k3 | 0.885 | 0.977 | 117 | 232 | -0.356 | 0.743 | 0.217 | FAIL | **KILL** |
| AMZN · set3/k2 | 0.680 | 0.864 | 70 | 139 | -0.712 | 0.754 | 0.000 | FAIL | **KILL** |
| AMZN · set3/k3 | 0.797 | 0.864 | 26 | 51 | -0.258 | 0.633 | 0.121 | FAIL | **KILL** |
| AMZN · set5/k2 | 0.266 | 0.864 | 66 | 130 | -2.316 | 0.075 | 0.678 | FAIL | **KILL-SIG** |
| AMZN · set5/k3 | 0.610 | 0.864 | 128 | 255 | -0.983 | 0.576 | 0.178 | FAIL | **KILL** |
| BTC-USD · set3/k2 | 1.182 | 0.912 | 59 | 117 | 1.042 | 1.141 | 0.000 | PASS | **KEEP** |
| BTC-USD · set3/k3 | 1.119 | 0.912 | 16 | 31 | 0.800 | 1.080 | 0.061 | PASS | **KEEP** |
| BTC-USD · set5/k2 | 0.262 | 0.912 | 101 | 199 | -2.513 | 0.138 | 1.003 | FAIL | **KILL-SIG** |
| BTC-USD · set5/k3 | 1.113 | 0.912 | 111 | 221 | 0.777 | 1.068 | 0.073 | PASS | **KEEP** |
| GLD · set3/k2 | 0.330 | 0.429 | 62 | 122 | -0.384 | 0.236 | 0.105 | FAIL | **KILL** |
| GLD · set3/k3 | 0.401 | 0.429 | 32 | 62 | -0.109 | 0.341 | 0.000 | FAIL | **KILL** |
| GLD · set5/k2 | 0.086 | 0.429 | 40 | 78 | -1.326 | 0.072 | 0.269 | FAIL | **KILL** |
| GLD · set5/k3 | 0.143 | 0.429 | 105 | 208 | -1.108 | 0.336 | 0.005 | FAIL | **KILL** |
| GOOGL · set3/k2 | 0.310 | 0.755 | 72 | 143 | -1.722 | 0.080 | 0.436 | FAIL | **KILL** |
| GOOGL · set3/k3 | 0.539 | 0.755 | 28 | 55 | -0.835 | 0.516 | 0.000 | FAIL | **KILL** |
| GOOGL · set5/k2 | 0.065 | 0.755 | 61 | 120 | -2.671 | -0.296 | 0.813 | FAIL | **KILL-SIG** |
| GOOGL · set5/k3 | 0.182 | 0.755 | 120 | 239 | -2.218 | -0.126 | 0.642 | FAIL | **KILL** |
| JPM · set3/k2 | 0.216 | 0.658 | 72 | 142 | -1.711 | 0.126 | 0.417 | FAIL | **KILL** |
| JPM · set3/k3 | 0.654 | 0.658 | 12 | 23 | -0.015 | 0.543 | 0.000 | FAIL | **KILL** |
| JPM · set5/k2 | -0.089 | 0.658 | 62 | 122 | -2.892 | -0.270 | 0.812 | FAIL | **KILL-SIG** |
| JPM · set5/k3 | 0.230 | 0.658 | 110 | 218 | -1.658 | 0.102 | 0.440 | FAIL | **KILL** |
| META · set3/k2 | 0.561 | 0.757 | 62 | 122 | -0.695 | 0.748 | 0.000 | PASS | **KILL** |
| META · set3/k3 | 0.743 | 0.757 | 13 | 25 | -0.048 | 0.675 | 0.073 | PASS | **KILL** |
| META · set5/k2 | 0.731 | 0.757 | 45 | 88 | -0.089 | 0.595 | 0.153 | FAIL | **KILL** |
| META · set5/k3 | 0.461 | 0.757 | 116 | 230 | -1.049 | 0.479 | 0.269 | FAIL | **KILL** |
| MSFT · set3/k2 | 0.467 | 0.914 | 68 | 134 | -1.730 | 0.591 | 0.393 | FAIL | **KILL** |
| MSFT · set3/k3 | 0.818 | 0.914 | 24 | 47 | -0.371 | 0.984 | 0.000 | FAIL | **KILL** |
| MSFT · set5/k2 | 0.051 | 0.914 | 56 | 110 | -3.344 | 0.194 | 0.790 | FAIL | **KILL-SIG** |
| MSFT · set5/k3 | 0.171 | 0.914 | 146 | 291 | -2.879 | 0.213 | 0.771 | FAIL | **KILL-SIG** |
| NVDA · set3/k2 | 0.795 | 1.070 | 66 | 131 | -1.064 | 0.915 | 0.185 | FAIL | **KILL** |
| NVDA · set3/k3 | 0.918 | 1.070 | 24 | 47 | -0.587 | 1.100 | 0.001 | FAIL | **KILL** |
| NVDA · set5/k2 | 0.018 | 1.070 | 48 | 94 | -4.075 | 0.115 | 0.986 | FAIL | **KILL-SIG** |
| NVDA · set5/k3 | 0.968 | 1.070 | 128 | 254 | -0.392 | 1.101 | 0.000 | FAIL | **KILL** |
| QQQ · set3/k2 | 0.671 | 0.943 | 72 | 142 | -1.054 | 0.619 | 0.153 | FAIL | **KILL** |
| QQQ · set3/k3 | 0.863 | 0.943 | 17 | 33 | -0.309 | 0.772 | 0.000 | FAIL | **KILL** |
| QQQ · set5/k2 | 0.236 | 0.943 | 43 | 84 | -2.739 | 0.425 | 0.347 | FAIL | **KILL-SIG** |
| QQQ · set5/k3 | 0.796 | 0.943 | 115 | 228 | -0.571 | 0.682 | 0.091 | FAIL | **KILL** |
| SLV · set3/k2 | -0.087 | 0.253 | 71 | 140 | -1.317 | -0.372 | 0.548 | FAIL | **KILL** |
| SLV · set3/k3 | 0.214 | 0.253 | 35 | 68 | -0.149 | 0.176 | 0.000 | PASS | **KILL** |
| SLV · set5/k2 | -0.224 | 0.253 | 72 | 142 | -1.847 | -0.322 | 0.498 | FAIL | **KILL** |
| SLV · set5/k3 | -0.178 | 0.253 | 140 | 278 | -1.670 | -0.287 | 0.463 | FAIL | **KILL** |
| SPY · set3/k2 | 0.760 | 0.867 | 65 | 128 | -0.414 | 0.681 | 0.133 | FAIL | **KILL** |
| SPY · set3/k3 | 0.916 | 0.867 | 19 | 37 | 0.188 | 0.814 | 0.000 | PASS | **KEEP** |
| SPY · set5/k2 | 0.299 | 0.867 | 50 | 98 | -2.201 | 0.315 | 0.499 | FAIL | **KILL** |
| SPY · set5/k3 | 0.692 | 0.867 | 111 | 220 | -0.678 | 0.627 | 0.187 | FAIL | **KILL** |
| TLT · set3/k2 | 0.317 | 0.243 | 59 | 116 | 0.287 | 0.328 | 0.173 | PASS | **KEEP** |
| TLT · set3/k3 | 0.342 | 0.243 | 22 | 43 | 0.386 | 0.301 | 0.201 | PASS | **KEEP** |
| TLT · set5/k2 | -0.044 | 0.243 | 45 | 88 | -1.110 | -0.038 | 0.540 | FAIL | **KILL** |
| TLT · set5/k3 | 0.338 | 0.243 | 101 | 200 | 0.370 | 0.502 | 0.000 | PASS | **KEEP** |
| TSLA · set3/k2 | 0.711 | 0.928 | 65 | 128 | -0.824 | 0.448 | 0.343 | FAIL | **KILL** |
| TSLA · set3/k3 | 0.975 | 0.928 | 26 | 51 | 0.181 | 0.790 | 0.000 | PASS | **KEEP** |
| TSLA · set5/k2 | 0.219 | 0.928 | 81 | 160 | -2.699 | 0.200 | 0.591 | FAIL | **KILL-SIG** |
| TSLA · set5/k3 | 0.646 | 0.928 | 114 | 227 | -1.073 | 0.431 | 0.359 | FAIL | **KILL** |
| XOM · set3/k2 | 0.435 | 0.391 | 63 | 124 | 0.171 | 0.371 | 0.005 | PASS | **KEEP** |
| XOM · set3/k3 | 0.438 | 0.391 | 18 | 35 | 0.183 | 0.376 | 0.000 | PASS | **KEEP** |
| XOM · set5/k2 | 0.291 | 0.391 | 67 | 132 | -0.386 | 0.217 | 0.159 | FAIL | **KILL** |
| XOM · set5/k3 | 0.427 | 0.391 | 99 | 196 | 0.139 | 0.318 | 0.058 | PASS | **KEEP** |

### Counts

| Lanes | KEEP | KILL | KILL-SIG | gate PASS | gate FAIL | KEEPs demoted by gate | Promoted |
|---|---|---|---|---|---|---|---|
| 60 | 11 | 40 | 9 | 14 | 46 | 0 | 0 |

The 11 KEEP-dev lanes (best t 1.04, all far below the K=4 bar 2.24) cluster on
the low-vol / high-drift survivorship names every prior round has returned —
BTC-USD (×3), TLT (×3), XOM (×3), SPY, TSLA — and, tellingly, 8 of the 11 are
the **strict / rare-exit corner** (SET-3/K=3 or SET-5/K=3): the lanes that step
aside least and therefore sit closest to buy-and-hold. The single best lane,
BTC-USD SET-3/K=2 (t 1.04), is the SAME lane and SAME t as R9's best — the two
rounds are a proven De Morgan pair, and the best exit overlay is simply
survivorship of a near-B&H exposure on a momentum-heavy name, not a de-risking
edge. Dev-candidate only.

## Pre-registered correlation / overlap check (plan §6, first-class)

For each instrument, over the members' shared dev-rail bars, the run computes on
the member **EXIT-signal series** (the members' FLAT-bars, the "out" votes):
(a) the pairwise correlation of member EXIT-signal series (the 0/1 flat lanes),
(b) the pairwise signal-overlap Jaccard = bars-both-flat / bars-either-flat, and
(c) the pairwise correlation of member daily RETURN streams (full matrices in
`correlations__<ticker>.json`). The pre-registered decision rule, verbatim:
*"Confluence between correlated members is one signal counted twice; if mean
pairwise member exit-signal-correlation on an instrument exceeds ~0.5, any
apparent vote edge is not diversified and must be reported as such."*

**The Pearson identity is confirmed to machine precision.** For 0/1 series
`corr(1-x, 1-y) = corr(x, y)`, so the member EXIT-signal (flat-bar) correlation
must EQUAL the R9 member POSITION (long-bar) correlation already reported. The
run computes both matrices per instrument and reports the largest off-diagonal
deviation: **max |exit_corr − pos_corr| = 1.3e-15 across all 15 instruments**
(all ≤ 1.3e-15, floating-point noise). The mean pairwise exit-signal
correlations below are therefore IDENTICAL to R9's position-correlation table,
number for number — this is a correctness check on the round (R10 really is the
De Morgan dual of R9 over one identical panel), not a re-derivation of a
different number.

**Result: 0 of 15 instruments trip the >0.5 flag — the mean pairwise member
exit-signal correlation is NEGATIVE on every name.** SET-3 ranges −0.19 (META)
… −0.07 (TLT, XOM); the SET-5 superset ranges −0.07 … +0.05. The distinct-class
members are near-independent-to-mildly-anti-correlated (a momentum member is
flat in downtrends precisely when a mean-reversion member is long buying the
dip), so the exit vote is genuinely NOT one signal counted twice, and no KEEP is
disqualified on correlation grounds. The problem is not redundancy; it is that
near-independent members rarely co-agree to exit, which routes the entire effect
through the exit-count mechanism below.

| Instrument | mean exit-corr SET-3 | mean exit-corr SET-5 | max\|exit−pos\| | >0.5 flag |
|---|---|---|---|---|
| AAPL | -0.125 | -0.035 | 4.4e-16 | no |
| AMZN | -0.111 | -0.019 | 5.6e-16 | no |
| BTC-USD | -0.178 | -0.071 | 7.8e-16 | no |
| GLD | -0.134 | +0.003 | 6.7e-16 | no |
| GOOGL | -0.101 | +0.002 | 7.8e-16 | no |
| JPM | -0.140 | -0.021 | 3.3e-16 | no |
| META | -0.191 | -0.068 | 7.8e-16 | no |
| MSFT | -0.141 | -0.033 | 1.1e-15 | no |
| NVDA | -0.163 | -0.068 | 1.1e-15 | no |
| QQQ | -0.104 | -0.001 | 1.1e-15 | no |
| SLV | -0.110 | -0.015 | 4.4e-16 | no |
| SPY | -0.089 | +0.042 | 8.9e-16 | no |
| TLT | -0.073 | +0.047 | 7.8e-16 | no |
| TSLA | -0.117 | -0.030 | 7.8e-16 | no |
| XOM | -0.071 | -0.005 | 1.3e-15 | no |

## Pre-registered exit-count / power impact (plan §7, first-class)

Fewer / opposite trades = weaker or degenerate statistics (SE(SR) ∝
sqrt((1 + SR²/2) / N), so smaller effective N ⇒ larger SE ⇒ a HIGHER t required
to clear the same fixed effect). The exit overlay differs from buy-and-hold only
on the bars it steps aside, so the effective sample carrying the edge is ~ the
flat fraction × N; the run reports, per instrument and set, the number of EXITS
fired (step-aside events) and the flat fraction at K=2 and K=3. Because the
members are near-independent (§6), the two exit corners fail from OPPOSITE
directions — this is the mechanism the honest prior (plan §1) named, and it is
the mirror image of Round 9:

- **The strict all-agree exit (SET-3/K=3) ≈ buy-and-hold.** Requiring all three
  distinct classes to be flat at once is rare on near-independent members, so
  the lane steps aside on a median of only **8.5% of bars** (SE-inflation
  median **×3.43** — the highest of any corner). It barely deviates from the
  hold, so its informational t collapses toward zero: JPM t −0.02, META −0.05,
  SPY +0.19, TSLA +0.18 — an edge indistinguishable from holding, ungradeable AS
  an edge (this is where most KEEP-devs sit, on a near-B&H exposure, not a
  finding).
- **The loose exit (SET-5/K=2) sheds the drift.** Requiring only 2 of 5 members
  flat is easy — some member is almost always flat — so the lane steps aside on
  a median of **85% of bars**: it is OUT of the market most of the time and
  sheds nearly all of the drift a hold rides. This is precisely where **8 of the
  9 KILL-SIG lanes land** (NVDA t −4.07, MSFT −3.34, JPM −2.89, GOOGL −2.67,
  QQQ −2.74, TSLA −2.70, BTC-USD −2.51, AMZN −2.32; MSFT SET-5/K=3 −2.88 is the
  ninth). Stepping aside through the up-days is significantly value-destroying
  on high-drift names, not merely uninformative.

Neither corner helps: the strict exit adds nothing (near-B&H, near-zero t); the
loose exit sheds drift (KILL-SIG). **No lane produced ~0 exits** — the sparsest
is JPM SET-3/K=3 at 12 step-asides (215 flat bars), still gradeable — so there
are **0 degenerate / indistinguishable-from-B&H lanes** flagged in the
reason_class rollup, and no exits were ever invented to rescue power. (Note the
strict SET-3/K=3 corner is the *closest* to B&H by a wide margin — median flat
fraction 8.5% — and is reported as the near-hold, low-power corner, distinct
from a literally-zero-exit degenerate lane.)

| Instrument | SET-3: exits/flat-frac (K=2 · K=3) | SET-5: exits/flat-frac (K=2 · K=3) |
|---|---|---|
| AAPL | 63 / 0.47 · 21 / 0.08 | 54 / 0.85 · 117 / 0.47 |
| AMZN | 70 / 0.47 · 26 / 0.09 | 66 / 0.83 · 128 / 0.41 |
| BTC-USD | 59 / 0.51 · 16 / 0.08 | 101 / 0.80 · 111 / 0.38 |
| GLD | 62 / 0.61 · 32 / 0.12 | 40 / 0.88 · 105 / 0.57 |
| GOOGL | 72 / 0.50 · 28 / 0.09 | 61 / 0.82 · 120 / 0.45 |
| JPM | 72 / 0.48 · 12 / 0.06 | 62 / 0.85 · 110 / 0.47 |
| META | 62 / 0.45 · 13 / 0.06 | 45 / 0.87 · 116 / 0.40 |
| MSFT | 68 / 0.47 · 24 / 0.08 | 56 / 0.89 · 146 / 0.47 |
| NVDA | 66 / 0.50 · 24 / 0.08 | 48 / 0.87 · 128 / 0.41 |
| QQQ | 72 / 0.42 · 17 / 0.05 | 43 / 0.86 · 115 / 0.46 |
| SLV | 71 / 0.64 · 35 / 0.14 | 72 / 0.81 · 140 / 0.53 |
| SPY | 65 / 0.41 · 19 / 0.05 | 50 / 0.86 · 111 / 0.46 |
| TLT | 59 / 0.57 · 22 / 0.14 | 45 / 0.85 · 101 / 0.53 |
| TSLA | 65 / 0.55 · 26 / 0.10 | 81 / 0.78 · 114 / 0.40 |
| XOM | 63 / 0.51 · 18 / 0.09 | 67 / 0.80 · 99 / 0.47 |

Per-set medians (in `exit_counts.json`): SET-3 flat-fraction K=2 0.50 / K=3 0.08
(SE-inflation ×1.41 / ×3.43); SET-5 flat-fraction K=2 0.85 / K=3 0.46
(SE-inflation ×1.08 / ×1.48). Buy-and-hold trades once and holds; the exit lanes
add 12–146 round-trips each. The shrinkage/degeneracy IS part of the finding; it
is never buried and trades are never invented to rescue power.

## R5-D fixed-config rows & selection-fair gate (standing rules 1–2)

The selection-fair standing gate ([selection-fair-gate.md](selection-fair-gate.md))
ran on all 60 lanes with the fidelity guard armed (searched arm = the
instrument's best-of-4 exit-vote config over the committed 1008/252 test
windows; every replay reproduced its recorded stitched Sharpe within 1e-8, so
**0 fidelity failures**). The gate block doubles as each lane's R5-D
fixed-config row: the `fixed` and `gap` columns in the per-lane table above.
**14 PASS / 46 FAIL.** The gate demoted **0 Round-2-rule KEEPs** this round — on
every lane the Round-2 rule and the gate agreed (each lane whose full-period
Sharpe beat the full-period benchmark also cleared the selection-free
walk-forward replay), so unlike R9 (which demoted TLT SET-5/K=2) there was no
gap-flattered KEEP to catch. `selection_gap ≥ 0` on every lane (the searched
best-of-4 never underperforms an individual fixed config over the windows),
consistent with the searched arm being an upper envelope of the four.

## reason_class rollup (all 60 lanes)

Machine-readable `selection_gate.reason_class` across the slice (standing rule 3
— the UNGRADEABLE-share is an INFRASTRUCTURE alarm, never strategy evidence):

| reason_class | count | kind |
|---|---|---|
| `PASS` | 14 | gate pass |
| `FAIL_UNDERPERFORM` | 39 | genuine rule failure (fixed positive, below same-window B&H) |
| `FAIL_NONPOSITIVE` | 7 | genuine rule failure (fixed Sharpe ≤ 0) |
| `UNGRADEABLE_MISSING_WINDOWS` | 0 | infrastructure |
| `UNGRADEABLE_DRIFT` | 0 | infrastructure |
| `UNGRADEABLE_NONCONTIGUOUS` | 0 | infrastructure |
| `UNGRADEABLE_FIDELITY` | 0 | infrastructure |
| `UNGRADEABLE_NAN` | 0 | infrastructure |
| **total** | **60** | |

**UNGRADEABLE share: 0 of 60 lanes (0.0%) — no infrastructure alarm.** Every
`selection_gate.UNGRADEABLE_CLASSES` count is zero: no missing/non-contiguous
windows, no cache drift, no fidelity-guard miss, no NaN degeneracy, and no
degenerate ~0-exit lane. The 46 gate FAILs are all genuine rule failures (39
`FAIL_UNDERPERFORM` where the fixed config is positive but below its same-window
benchmark, 7 `FAIL_NONPOSITIVE` where the fixed stitched Sharpe is ≤ 0), not
irreproducible lanes — so the Round-10 nulls and the 9 KILL-SIG negatives are
strategy evidence, read as designed.

## Plain-language verdict — the owner's inverted question, answered honestly

The owner asked whether waiting for *multiple strategies to agree* is a good
idea; Round 9 tested the ENTRY framing (agree to get IN), and Round 10 tests the
inverted complement the coordinator authorized on the same live owner turn:
**does using strategy-agreement to decide when to STEP ASIDE (go flat) beat just
holding?** Round 10 tested exactly that on 15 instruments — hold long by default,
go to cash when ≥K distinct thesis-class members agree they want out — and the
honest answer on dev data is **no, it does not beat holding, and the mechanism
is the exact mirror of Round 9.**

The intuition ("agreement to de-risk should sidestep the bad regimes") assumes
the members collectively flag genuine drawdowns — that their joint flat-signal
lands disproportionately in the losses a hold suffers. It does not. Two things
break it, and they are the De Morgan reflection of R9's two failures. First, the
distinct-class members ARE near-independent (the exit-signal correlation is
negative on all 15 names, and EQUALS R9's position correlation to 1e-15 — so
this is genuinely NOT the failure mode of counting one signal twice). Second —
and this is the mechanism — because they are near-independent, ≥K agreement to
exit is either rare or constant, never well-timed. Requiring **all** of them to
agree (SET-3/K=3) fires so rarely (flat 8.5% of the time) that the overlay is
indistinguishable from buy-and-hold: it adds nothing, its t sits at zero, and
the KEEP-devs it produces are just survivorship of a near-hold exposure.
Loosening to a 2-of-5 majority (SET-5/K=2) fires almost constantly (flat 85% of
the time): it steps aside through exactly the drift a hold rides, so it is
*significantly worse* than holding on high-drift names (NVDA, MSFT, JPM, GOOGL,
QQQ, TSLA, BTC, AMZN — 8 of the 9 KILL-SIG lanes). Best case anywhere: t = 1.04
(BTC-USD), the SAME lane and value as R9, less than half the significance bar, on
a momentum-heavy name where any near-B&H rule looks good. **Zero of 60 configs
cleared the bar; nothing was promoted.**

This is the clean inverse of Round 9 and confirms/extends three cited priors.
**R9** (the entry vote, `research-round-9-results.md`) failed because the STRICT
corner (K=3 to ENTER) sat in cash through the drift — waiting for agreement to
enter cost the rise. R10 shows the dual: the entry vote's harm lived in the
strict corner, the exit vote's harm lives in the LOOSE corner (K=2 to EXIT),
because both amount to *being out of the market through the drift* — R9 by rarely
entering, R10 by frequently exiting. **R4-C** (the survivor-committee AVERAGE,
`research-round-4-results.md` §R4-C) found the diversification premium
concentrated in small closely-matched committees and cleared nothing (best t
1.09, 0 promoted). **R7-C** (`washout_recovery`, `research-round-7c-results.md`)
found a within-class AND-conjunction actively value-destroying on 3 high-drift
names. Round 10 is the cross-class binary EXIT vote none of them ran, and it
lands in the same place, with the R7-C harm pattern recurring one abstraction up:
a loose cross-class exit is significantly value-destroying on high-drift names
for the mirror reason — agreeing to step aside holds you out of the trend.

## Round 10 — closing tally (2026-07-19)

| Slice | One-line verdict |
|---|---|
| R10 inverse-confluence exit vote | **11/60 weak KEEP-dev** (best t 1.04, BTC-USD SET-3/K=2 — the SAME lane/value as R9, under half the K=4 bar 2.24, far under the K=60 bar 3.14), 9 KILL-SIG (8 the loose SET-5/K=2 exit: NVDA −4.07, MSFT −3.34, JPM −2.89, GOOGL −2.67; the ninth MSFT SET-5/K=3); using ≥2–3 distinct strategies agreeing to STEP ASIDE adds NO benchmark-beating edge — members are near-independent (0/15 trip >0.5, exit-corr = R9 pos-corr to 1e-15) so ≥K exit agreement is either rare (strict K=3 ≈ buy-and-hold, adds nothing) or constant (loose K=2 sheds the drift, value-destroying). |

- **Cumulative burden**: exactly **5,853 → 5,913 registered configs (60 new)**
  (`sweeps.r10_total_configs()` = 60, pinned by tests; the runner asserts it
  before running). No K was counted down and no bar was lowered (informational
  t at K=4 per lane, K=60 program-wide, bars 2.24 / 3.14).
- **Runtime cap**: not hit (slice runtime 27 s against a 900 s cap); nothing
  truncated, no lanes skipped, **no CAP-HIT**.
- **The standing gate, read honestly**: ran on all 60 lanes (fidelity 60/60
  within 1e-8, zero UNGRADEABLE) and demoted 0 Round-2-rule KEEPs (it concurred
  with the Round-2 rule on every lane). 14 PASS / 46 FAIL, all FAILs genuine
  rule failures.
- **0 promoted — promotion remains CLOSED, holdout SPENT.** Every KEEP-dev is a
  dev-candidate only (best t 1.04 vs the nearest bar 2.24); genuine OOS
  validation stays OWNER-GATED behind a new pre-registered protocol on
  post-2026 data.
- **What the round established**: (1) cross-class EXIT confluence carries no
  regime-timing information that survives net of cost — 0 promoted, best t under
  half the bar; (2) the failure is NOT redundancy/over-correlation (0/15 trip
  >0.5; the exit-signal correlation is confirmed EQUAL to R9's position
  correlation to machine precision — R10 is a proven De Morgan dual of R9) — it
  is the co-agreement mechanism, mirrored from R9: strict exit ≈ buy-and-hold
  (adds nothing), loose exit sheds drift (9 KILL-SIG); (3) the selection-fair
  gate stayed cheap (60 replays in 27 s), zero-UNGRADEABLE, and concurred with
  the Round-2 rule on every lane.

Round 10 is graded. One slice, one honest answer to the inverted owner question,
zero findings, zero cap-hits, eleven weak dev-candidates, and the program's
first cross-class EXIT-confluence result: using strategy-agreement to decide when
to step aside, tested honestly, does not beat buy-and-hold on dev data — for the
mirror-image reason the entry vote failed. Anything further still needs new data
(OWNER-GATED) or a genuinely different idea class.
