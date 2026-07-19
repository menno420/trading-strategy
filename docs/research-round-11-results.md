# Research Round 11 — Results (Cross-Asset Regime Conditioning, continuous + causal)

> **Status:** `reference` — honest results of the pre-registered Round-11
> cross-asset regime conditioning sweep, against the protocol in
> [research-round-11-plan.md](research-round-11-plan.md) (merged as PR #158,
> main `bc710c7`, BEFORE any Round-11 outcome existed). **POST-HOLDOUT,
> DEV-ONLY: the holdout is SPENT and promotion is CLOSED.** Nothing on this page
> is an out-of-sample claim; a KEEP means *dev-candidate only*, and nulls/KILLs
> are first-class results. The multiple-testing bar is unchanged
> (`trading_lab.promotion.min_tstat`): per-lane **K=9 ≈ 2.54**, program-wide
> **K=27 ≈ 2.90** — only ever rises, never lowered. Round 11 is graded under the
> selection-fair standing gate ([selection-fair-gate.md](selection-fair-gate.md)):
> the gate ran on EVERY lane, and its result block is each lane's R5-D
> fixed-config row. The benchmark is the mandatory **unconditioned control arm** —
> plain buy-and-hold of the target (position ≡ 1.0) — so each lane's edge is its
> deviation from just holding, and the base-hold Sharpe is reported next to every
> lane.

**Round headline: conditioning a risk-leg's exposure on a CONTINUOUS, CAUSAL
cross-asset regime score does NOT beat just holding the leg on dev data, and the
mechanism is a structural exposure drag, not a regime edge. Across the 27
pre-registered lanes (3 causal signals × 3 windows × 3 targets SPY/QQQ/NVDA) the
conditioning yields 2 weak KEEP-dev / 25 KILL / 0 KILL-SIG, 0 promoted, best
informational t anywhere 0.675 (NVDA `xasset_breadth`/W252) — against the K=9 bar
2.54 and the program K=27 bar 2.90, barely a quarter of the nearest bar. The
mandatory unconditioned control arm is decisive: only 2 of the 27 conditioned
lanes even EXCEED their own base buy-and-hold Sharpe (both are NVDA
`xasset_breadth`, W126 +0.106 and W252 +0.175 Sharpe), and the median lane
UNDERPERFORMS its hold by −0.257 Sharpe (mean −0.260). The headline
LOOKAHEAD-CONTROL passes: the no-lookahead / prefix-invariance property
(`tests/test_xasset_regime.py::TestNoLookahead`) was re-asserted on the REAL
cached panels — 45 probes across all 3 signals × 3 windows, the regime score AND
the conditioned position at bar t bit-for-bit identical on the full panel vs the
panel truncated at bar t (max |diff| = 0.0) — so the regime labels are causal and
the (tiny, insignificant) edge on NVDA is NOT a hindsight artifact. The honest
mechanism: a causal rolling-percentile-rank position is ~uniform in [0, 1] by
construction, so its mean exposure is ~0.49 (`xasset_eq_bond_mom`,
`xasset_metals_riskoff`) to ~0.65 (`xasset_breadth`) — the lane is structurally
half-to-two-thirds invested and sheds a large fraction of the drift a hold rides
through the 2010–2025 bull. The regime did NOT preferentially cut exposure into
drawdowns; it cut exposure roughly uniformly, so it mostly kept you out at the
wrong times. No lane is degenerate / ≈-constant (conditioned-position std 0.30–
0.35, nunique 100s — genuinely continuous, NOT the binary R4 gate re-skinned).
The gate ran on all 27 lanes (4 PASS / 23 FAIL) with zero fidelity failures and
demoted 0 Round-2-rule KEEPs; 0 UNGRADEABLE lanes, no infrastructure alarm.
Runtime 36 s vs a 900 s cap; no CAP-HIT. Round-11 burden: 27 new registered
configs; program cumulative 5,913 → 5,940, still 0 promoted.**

| Slice | Lanes | KEEP | KILL | KILL-SIG | Gate PASS/FAIL | Best t (vs 2.54 / 2.90) | Beat base hold | Runtime vs cap |
|---|---|---|---|---|---|---|---|---|
| R11 `r11-xasset-regime` (daily) | 27 | 2 | 25 | 0 | 4 / 23 | 0.675 | 2 / 27 | 36 s / 900 s |
| **Round 11** | **27** | **2** | **25** | **0** | **4 / 23** | **0.675** | **2 / 27** | none hit |

Machine-readable rollup: `summary.json`, `results.csv`,
`base_hold_comparison.json`, and the 27 per-lane `<signal>__w<window>__<target>.json`
in the slice directory —
[`experiments/sweeps/r11-xasset-regime/`](../experiments/sweeps/r11-xasset-regime/)
(runner `scripts/run_r11_xasset_regime_sweep.py`).

## LOOKAHEAD CONTROL — the #1 failure mode, reported as a first-class result (plan §4)

Regime-detection lookahead is the single most common way a study of this class
manufactures a fake edge: a regime label that peeks at future data (a full-sample
percentile rank, a full-sample z-score) assigns each bar a "regime" it could only
know in hindsight, and the apparent edge evaporates live. Round 11 forecloses
this by construction — every score input is a trailing window and the
conditioning normalization is a ROLLING (never full-sample) percentile rank — and
the guarantee is a committed unit test, not a comment.

**The no-lookahead truncation test passes, and the RUN re-asserted it on the REAL
cached panels.** `tests/test_xasset_regime.py::TestNoLookahead` (prefix
invariance on synthetic panels) is green in the suite. Additionally, before
grading a single lane, the runner re-computed the property on the **actual dev
panels**: for a spread of bars t across ALL 3 signals × 3 windows, the regime
score AND the conditioned position at bar t are identical whether computed on the
full panel or on the panel truncated at bar t (`series.iloc[:t+1]`). Result:
**45 probes, PASS, max |score diff| = 0.0, max |position diff| = 0.0** (bit-for-bit,
`summary.json → prefix_invariance_control`). The causal regime labels use only
data with timestamp ≤ t; the engine then delays execution to bar t+1's open as
everywhere else. Therefore the (small, insignificant) exposure edge on NVDA
`xasset_breadth` is a real property of a causal rule, not a hindsight artifact —
which is exactly why it is honest to report it as "does not clear the bar" rather
than dismiss it as a leak.

## Reading the per-lane table

Each lane is a fixed-config evaluation: the regime signals and the fixed 252-bar
percentile window are FIXED (plan §3), so the full-dev-period backtest carries no
in-sample parameter selection, and the only searched axis is (signal, window) = 9
configs per target. `Sharpe` is the lane's full-dev-period net-of-cost Sharpe
(5 bps slippage + 1 bp commission), `base hold` the full-period buy-and-hold
Sharpe of the same target (the unconditioned control arm), `beat?` whether the
conditioned lane's Sharpe exceeds its base hold, `Δ` the Sharpe gap vs base hold,
`pos̄` / `σpos` the mean and std of the warmed conditioned position (exposure),
`t (K=9)` the ORDER 007 Lo-2002 Sharpe-delta t via `promotion.grade_promotion` at
the per-lane Bonferroni K=9 (bar 2.54). `fixed` and `gap` are the selection-fair
gate's R5-D row: `fixed` is the selection-free replay of THIS config over
contiguous 1008/252 walk-forward test windows, `gap = searched − fixed` where
`searched` is the target's BEST-of-9 (signal, window) config over the same
windows (plan §7 search dimension) — informational, no registered threshold.
Verdict = Round-2 rule, then `classify_verdict` (KILL-SIG at t ≤ −2.54), then
`apply_gate` (the gate only ever demotes). Every lane's t is ALSO reported
against the program K=27 bar 2.90 in `results.csv` — no lane comes within 2.2 t
of it.

| Lane (target · signal/W) | Sharpe | base hold | beat? | Δ | pos̄ | σpos | t (K=9) | fixed | gap | gate | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NVDA · eq_bond_mom/W63 | 0.614 | 1.070 | no | -0.456 | 0.49 | 0.31 | -1.765 | 0.755 | 0.707 | FAIL | **KILL** |
| NVDA · eq_bond_mom/W126 | 0.622 | 1.070 | no | -0.448 | 0.48 | 0.32 | -1.734 | 0.696 | 0.767 | FAIL | **KILL** |
| NVDA · eq_bond_mom/W252 | 1.001 | 1.070 | no | -0.069 | 0.48 | 0.34 | -0.267 | 1.076 | 0.387 | FAIL | **KILL** |
| NVDA · metals_riskoff/W63 | 0.838 | 1.070 | no | -0.232 | 0.50 | 0.30 | -0.897 | 0.962 | 0.501 | FAIL | **KILL** |
| NVDA · metals_riskoff/W126 | 0.694 | 1.070 | no | -0.376 | 0.48 | 0.33 | -1.455 | 0.753 | 0.709 | FAIL | **KILL** |
| NVDA · metals_riskoff/W252 | 0.738 | 1.070 | no | -0.332 | 0.49 | 0.35 | -1.286 | 0.812 | 0.650 | FAIL | **KILL** |
| NVDA · breadth/W63 | 0.950 | 1.070 | no | -0.119 | 0.64 | 0.30 | -0.462 | 1.202 | 0.260 | FAIL | **KILL** |
| NVDA · breadth/W126 | 1.176 | 1.070 | **yes** | **+0.106** | 0.65 | 0.32 | +0.409 | 1.462 | 0.000 | PASS | **KEEP** |
| NVDA · breadth/W252 | 1.245 | 1.070 | **yes** | **+0.175** | 0.69 | 0.33 | +0.675 | 1.340 | 0.122 | PASS | **KEEP** |
| QQQ · eq_bond_mom/W63 | 0.354 | 0.943 | no | -0.589 | 0.49 | 0.31 | -2.281 | 0.235 | 0.644 | FAIL | **KILL** |
| QQQ · eq_bond_mom/W126 | 0.341 | 0.943 | no | -0.602 | 0.48 | 0.32 | -2.330 | 0.171 | 0.708 | FAIL | **KILL** |
| QQQ · eq_bond_mom/W252 | 0.615 | 0.943 | no | -0.328 | 0.48 | 0.34 | -1.270 | 0.492 | 0.387 | FAIL | **KILL** |
| QQQ · metals_riskoff/W63 | 0.747 | 0.943 | no | -0.196 | 0.50 | 0.30 | -0.760 | 0.671 | 0.208 | FAIL | **KILL** |
| QQQ · metals_riskoff/W126 | 0.588 | 0.943 | no | -0.356 | 0.48 | 0.33 | -1.376 | 0.376 | 0.503 | FAIL | **KILL** |
| QQQ · metals_riskoff/W252 | 0.656 | 0.943 | no | -0.287 | 0.49 | 0.35 | -1.111 | 0.477 | 0.402 | FAIL | **KILL** |
| QQQ · breadth/W63 | 0.686 | 0.943 | no | -0.257 | 0.64 | 0.30 | -0.996 | 0.685 | 0.194 | FAIL | **KILL** |
| QQQ · breadth/W126 | 0.845 | 0.943 | no | -0.098 | 0.65 | 0.32 | -0.378 | 0.879 | 0.000 | PASS | **KILL** |
| QQQ · breadth/W252 | 0.882 | 0.943 | no | -0.061 | 0.69 | 0.33 | -0.235 | 0.749 | 0.131 | FAIL | **KILL** |
| SPY · eq_bond_mom/W63 | 0.278 | 0.867 | no | -0.589 | 0.49 | 0.31 | -2.283 | 0.140 | 0.624 | FAIL | **KILL** |
| SPY · eq_bond_mom/W126 | 0.264 | 0.867 | no | -0.604 | 0.48 | 0.32 | -2.338 | 0.052 | 0.712 | FAIL | **KILL** |
| SPY · eq_bond_mom/W252 | 0.591 | 0.867 | no | -0.276 | 0.48 | 0.34 | -1.068 | 0.375 | 0.390 | FAIL | **KILL** |
| SPY · metals_riskoff/W63 | 0.755 | 0.867 | no | -0.113 | 0.50 | 0.30 | -0.437 | 0.621 | 0.144 | FAIL | **KILL** |
| SPY · metals_riskoff/W126 | 0.533 | 0.867 | no | -0.335 | 0.48 | 0.33 | -1.296 | 0.299 | 0.465 | FAIL | **KILL** |
| SPY · metals_riskoff/W252 | 0.650 | 0.867 | no | -0.218 | 0.49 | 0.35 | -0.843 | 0.430 | 0.335 | FAIL | **KILL** |
| SPY · breadth/W63 | 0.629 | 0.867 | no | -0.238 | 0.64 | 0.30 | -0.922 | 0.619 | 0.145 | FAIL | **KILL** |
| SPY · breadth/W126 | 0.767 | 0.867 | no | -0.101 | 0.65 | 0.32 | -0.390 | 0.764 | 0.000 | PASS | **KILL** |
| SPY · breadth/W252 | 0.837 | 0.867 | no | -0.030 | 0.69 | 0.33 | -0.117 | 0.642 | 0.122 | FAIL | **KILL** |

(Verdict counts: **2 KEEP-dev / 25 KILL / 0 KILL-SIG**. Note the 4 gate PASS
lanes are not the 2 KEEPs: QQQ `breadth`/W126 and SPY `breadth`/W126 clear the
selection-free walk-forward replay — a PASS on the R5-D fixed row — but their
full-period conditioned Sharpe still trails their base hold, so the Round-2 rule
KILLs them; `apply_gate` only ever demotes, never promotes.)

## The unconditioned CONTROL ARM — the decisive comparison (plan §5, headline)

The benchmark for every conditioned lane is plain **buy-and-hold** of the same
target (position ≡ 1.0). The base-hold Sharpes are NVDA **1.070**, QQQ **0.943**,
SPY **0.867** (the 2010-01-04 → 2025-01-08 dev window, net of the same costs). The
question the round exists to answer is whether conditioning exposure on the
cross-asset regime beats those numbers, and the answer, lane by lane, is
overwhelmingly no:

- **Only 2 of the 27 conditioned lanes beat their own base hold** — NVDA
  `xasset_breadth`/W126 (+0.106 Sharpe) and NVDA `xasset_breadth`/W252 (+0.175
  Sharpe). Both are the SAME signal on the SAME (highest-drift) target, and both
  are wildly insignificant (t 0.41 and 0.675 vs the K=9 bar 2.54).
- **The median conditioned lane loses −0.257 Sharpe to its hold** (mean −0.260);
  the worst lane, SPY `xasset_eq_bond_mom`/W126, gives up −0.604 Sharpe vs simply
  holding SPY. 25 of 27 lanes are net-negative vs the control.

Conditioning that fails to beat its own control is reported as such, not as a
candidate. Even the 2 "beats" are a fraction of a t from zero and confined to one
name — the control arm is what turns a superficially-positive NVDA Sharpe into an
honest KILL/near-KEEP, and it is why the round promotes nothing. Full base-hold
comparison table in `base_hold_comparison.json`.

## The honest mechanism — why conditioning loses to holding

A causal rolling-percentile-rank is, by construction, ~uniformly distributed in
[0, 1] over any long window (that is what a rank IS). So the conditioned position
is NOT a gate that mostly holds you fully invested and occasionally steps aside —
it is a continuous exposure whose **mean sits near 0.5**, not near 1.0. The
per-lane `pos̄` column bears this out: `xasset_eq_bond_mom` and
`xasset_metals_riskoff` average **0.48–0.50** exposure, and `xasset_breadth`
averages **0.64–0.69** (its raw score is a fraction of legs above their SMA,
which skews risk-on in a bull, lifting the rank's mean). The consequence is
mechanical: over 2010–2025 the targets drift strongly upward, and a rule that is
half-to-two-thirds invested on average **structurally sheds a large slice of that
drift**. That exposure drag — not any regime mis-timing subtlety — is the
dominant term, and it explains the whole ordering of the results:

- **`xasset_eq_bond_mom` (lowest mean exposure, ~0.48) is the worst signal**: its
  9 lanes give the most-negative t's (SPY/QQQ W63 and W126 reach t −2.28 … −2.34),
  because it is the most flat and sheds the most drift. (None crosses the mirrored
  −2.54 KILL-SIG bar, so 0 KILL-SIG — but it is the closest the round comes to
  significant HARM.)
- **`xasset_breadth` (highest mean exposure, ~0.65) is the least-bad signal** and
  the ONLY one that ever beats a hold — and only on NVDA, the highest-drift target,
  where staying more-invested-than-average is rewarded. This is survivorship of a
  higher average exposure on a momentum-heavy name, not evidence the regime
  separated good bars from bad.

Crucially, the regime did NOT preferentially cut exposure during drawdowns and
hold it during rallies (which is what would beat a hold). Because the rank is
~uniform, it cut exposure roughly *uniformly across regimes* — so it mostly kept
you out at the wrong times as often as the right ones, netting the structural
half-invested drag with no timing premium to offset it. That is the honest answer
to "does the regime beat holding": it barely varies exposure in a way that tracks
the drawdowns, so it just gives back drift.

## No degenerate / ≈-constant lanes (plan §5)

A conditioning study must flag any lane whose position is ~constant (the regime
rarely varies), because such a lane is indistinguishable from buy-and-hold and its
"edge" is a non-result. Here the conditioned-position std is **0.30–0.35 on every
lane** (nunique in the hundreds — full range of the [0, 1] rank exercised), so
**0 of 27 lanes are degenerate / ≈-constant**. This is the continuous form
working exactly as designed: the exposure genuinely varies bar to bar (it is NOT
the burned R4 binary gate re-skinned). The lanes lose to their hold not because
they collapse to a constant, but because their *varying* exposure averages ~0.5
and does not time the drawdowns — a substantive null, not an artifact.

## R5-D fixed-config rows & selection-fair gate (standing rules 1–2)

The selection-fair standing gate ([selection-fair-gate.md](selection-fair-gate.md))
ran on all 27 lanes with the fidelity guard armed (searched arm = the target's
best-of-9 (signal, window) config over the committed 1008/252 test windows; every
replay reproduced its recorded stitched Sharpe within tolerance, so **0 fidelity
failures**). The gate block doubles as each lane's R5-D fixed-config row: the
`fixed` and `gap` columns above. **4 PASS / 23 FAIL.** The gate demoted **0
Round-2-rule KEEPs** this round — the 2 KEEPs (NVDA `xasset_breadth` W126/W252)
both also PASS the gate, so there was no gap-flattered KEEP to catch. The 4 gate
PASSes exceed the 2 KEEPs precisely because the gate grades the selection-free
walk-forward replay, on which QQQ and SPY `xasset_breadth`/W126 clear their
same-window benchmark even though their full-period conditioned Sharpe does not —
`apply_gate` correctly leaves those as KILL (it only demotes). `selection_gap ≥ 0`
on every lane (the best-of-9 searched arm never underperforms an individual fixed
config over the windows), consistent with the searched arm being an upper envelope
of the nine.

## reason_class rollup (all 27 lanes)

Machine-readable `selection_gate.reason_class` across the slice (standing rule 3 —
the UNGRADEABLE-share is an INFRASTRUCTURE alarm, never strategy evidence):

| reason_class | count | kind |
|---|---|---|
| `PASS` | 4 | gate pass |
| `FAIL_UNDERPERFORM` | 23 | genuine rule failure (fixed positive, below same-window B&H) |
| `FAIL_NONPOSITIVE` | 0 | genuine rule failure (fixed Sharpe ≤ 0) |
| `UNGRADEABLE_MISSING_WINDOWS` | 0 | infrastructure |
| `UNGRADEABLE_DRIFT` | 0 | infrastructure |
| `UNGRADEABLE_NONCONTIGUOUS` | 0 | infrastructure |
| `UNGRADEABLE_FIDELITY` | 0 | infrastructure |
| `UNGRADEABLE_NAN` | 0 | infrastructure |
| **total** | **27** | |

**UNGRADEABLE share: 0 of 27 lanes (0.0%) — no infrastructure alarm.** Every
`selection_gate.UNGRADEABLE_CLASSES` count is zero: no missing/non-contiguous
windows, no cache drift, no fidelity-guard miss, no NaN degeneracy. All 23 gate
FAILs are genuine rule failures (`FAIL_UNDERPERFORM`: the fixed config is positive
but its selection-free walk-forward replay trails its same-window benchmark), not
irreproducible lanes — so the Round-11 nulls are strategy evidence, read as
designed.

## How the continuous form compares to the burned R4 binary gate (plan §2)

Cross-asset conditioning is a **burned class**
([strategy-catalog.md](strategy-catalog.md)): R4 `crossasset_gate` (§R4-E, a
frozen EMA-cross component gated on the SIGN of another instrument's momentum) was
**0 KEEP / 2 KILL**, and R4 `regime_switch` (§R4-D, a trend/reversion switch on a
trend-strength tercile) was **0 KEEP / 6 KILL** — in both the unconditioned
control beat the gate. Round 11 tested whether the CONTINUOUS form the memo (§2.1)
flagged as untested — a causal rolling-percentile-rank exposure, not a binary
on/off switch — does any better. **It does not, in the way that matters.** The
continuous form produced 2 nominal KEEP-dev where the binary gate produced 0, but
both are (a) wildly below the significance bar (t 0.41, 0.675 vs 2.54), (b)
confined to the single highest-drift target (NVDA), and (c) explained entirely by
one signal (`xasset_breadth`) carrying a higher *average exposure*, not by any
regime-timing edge. The verdict is the same null the binary gate earned, for a
mechanically-related reason: the binary gate lost because its on/off timing was
uninformative; the continuous conditioner loses because its ~uniform exposure
averages ~0.5 and gives back drift. The meta-analysis line "conditioning loses to
its own controls, on every axis tested" now extends to the continuous,
causally-normalized cross-asset form — the last conditioning shape that had not
been graded with its unconditioned control reported alongside.

## Plain-language verdict — does conditioning on a cross-asset regime beat holding?

The new-data-source direction named cross-asset / macro-regime as the lowest-cost,
self-serve first step: *can a regime built from the relationships BETWEEN assets
(equities vs bonds, gold being bid, cross-asset breadth) tell you when to dial a
risk leg's exposure up or down, and does that beat just holding the leg?* Round 11
tested exactly that — SPY, QQQ, and NVDA, each sized continuously by the causal
rolling-percentile-rank of three cross-asset regime scores over three lookbacks —
and the honest answer on dev data is **no, it does not beat holding.**

The appealing intuition ("scale down in risk-off regimes, sidestep the drawdowns,
keep the drift") assumes the regime score lands its low readings disproportionately
on the bad bars. It does not. Two things break it. First — and this is the whole
mechanism — normalizing the score into a *rank* makes the exposure ~uniform in
[0, 1], so the lane is only ~half invested on average and structurally sheds a
large share of the upward drift the targets ride; that drag is worth about −0.26
Sharpe per lane vs simply holding. Second, the rank cut exposure roughly evenly
across regimes rather than concentrating the cuts in drawdowns, so there was no
timing premium to pay for the drag back. The single least-bad configuration —
NVDA sized by `xasset_breadth` (the signal with the highest average exposure, on
the highest-drift name) — squeaks +0.18 Sharpe over holding NVDA, at t = 0.675,
about a quarter of the bar and confined to one name: survivorship of a
higher-than-average exposure, not a regime edge. **Zero of 27 configs cleared the
bar; nothing was promoted.** And critically, this is NOT a lookahead illusion: the
no-lookahead truncation control passed bit-for-bit on the real panels, so the null
is a property of a genuinely causal rule, not an artifact waiting to evaporate.

This confirms and extends the cited priors. It reproduces the **burned R4
cross-asset classes** (`crossasset_gate` 0/2, `regime_switch` 0/6) with a
materially different, continuous, causally-normalized instrument and its
unconditioned control reported alongside — same null, one abstraction richer. It
matches the **cross-round meta-analysis** verdict that conditioning "loses to its
own controls, on every axis tested." And it is consistent with the program's
standing result across 10 prior rounds: no price/volume-derived signal, and now no
self-serve cross-asset regime built from the existing cache, separates the
drawdowns a hold suffers from the drift it rides net of cost.

## Round 11 — closing tally (2026-07-19)

| Slice | One-line verdict |
|---|---|
| R11 cross-asset regime conditioning | **2/27 weak KEEP-dev** (both NVDA `xasset_breadth`, best t 0.675 at W252 — a quarter of the K=9 bar 2.54, far under the K=27 bar 2.90), 0 KILL-SIG; conditioning a risk leg's exposure on a CONTINUOUS, CAUSAL cross-asset regime does NOT beat holding — only 2 of 27 lanes beat their own base hold (median lane −0.257 Sharpe), because a rank-normalized exposure averages ~0.5 and structurally sheds the drift; no lookahead (truncation control PASS on the real panels, 45 probes, 0 diff); no degenerate lanes; same null as the burned R4 binary gate, mechanism reported. |

- **Cumulative burden**: exactly **5,913 → 5,940 registered configs (27 new)**
  (`sweeps.r11_total_configs()` = 27, pinned by `tests/test_sweeps.py`; the runner
  asserts it before running). No K was counted down and no bar was lowered
  (informational t at K=9 per lane, K=27 program-wide, bars 2.54 / 2.90).
- **Lookahead control**: the no-lookahead / prefix-invariance property
  (`tests/test_xasset_regime.py::TestNoLookahead`) is green in the suite AND was
  re-asserted on the REAL cached panels before grading (45 probes, max |diff| =
  0.0). The reported edge (such as it is) is causal, not a hindsight artifact.
- **Runtime cap**: not hit (slice runtime 36 s against a 900 s cap); nothing
  truncated, no targets skipped, **no CAP-HIT**.
- **The standing gate, read honestly**: ran on all 27 lanes (fidelity 27/27, zero
  UNGRADEABLE) and demoted 0 Round-2-rule KEEPs (both KEEPs also PASS the gate).
  4 PASS / 23 FAIL, all FAILs genuine rule failures (`FAIL_UNDERPERFORM`).
- **Control arm**: only 2 of 27 conditioned lanes beat their own unconditioned
  buy-and-hold; the median lane underperforms its hold by −0.257 Sharpe. The
  control is the benchmark, and the conditioning loses to it.
- **0 promoted — promotion remains CLOSED, holdout SPENT.** Every KEEP-dev is a
  dev-candidate only (best t 0.675 vs the nearest bar 2.54); genuine OOS
  validation stays OWNER-GATED behind a new pre-registered protocol on post-2026
  data.
- **What the round established**: (1) a continuous, causally-normalized
  cross-asset regime conditioner carries no exposure-timing edge that survives net
  of cost — 0 promoted, best t a quarter of the bar; (2) the failure is a
  structural exposure drag (rank-normalized exposure averages ~0.5, sheds drift),
  not a lookahead artifact (truncation control PASS) and not a degenerate
  ≈-constant lane (position std 0.30–0.35); (3) the continuous form reproduces the
  burned R4 binary-gate null with the unconditioned control reported alongside —
  the last untested conditioning shape, now graded and null.
