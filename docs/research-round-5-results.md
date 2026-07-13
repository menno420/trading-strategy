# Research Round 5 — Results

> **Status:** `reference` — honest results of the four pre-registered
> Round-5 slices, one dated section per slice, against the protocol in
> [research-round-5-plan.md](research-round-5-plan.md) (merged BEFORE any
> Round-5 outcome existed). **POST-HOLDOUT, DEV-ONLY: the holdout is
> SPENT and promotion is CLOSED.** Nothing on this page is an
> out-of-sample claim; a KEEP means *dev-candidate only*, and nulls/KILLs
> are first-class results. The multiple-testing bar is unchanged
> (`trading_lab.promotion.min_tstat`, ~2.638 at K=12; only ever rises).
> Target set: the plan's FROZEN top-5 KEEP-dev lanes — no swap-ins, no
> re-ranking after outcomes.

**Round headline: 4 of the top 5 KEEP-dev lanes survive all four
verdict-bearing stability slices and stay KEEP-dev; 1 is DEMOTED to KILL
(META hourly `stochastic_reversion`, killed by R5-B single-window luck);
0 KILL-SIG anywhere; and the R5-C escalate branch fired once (BTC-USD
daily `bollinger_breakout`, `P(delta <= 0) = 0.042`), producing the
owner-gated proposal
[proposals/r5c-btc-bollinger-breakout-oos-proposal.md](proposals/r5c-btc-bollinger-breakout-oos-proposal.md)
— verdict unchanged, nothing scheduled or run. Round-5 burden: 14 new
registered configs (the R5-A neighbors); program cumulative 4345 →
4359. Promotion remains CLOSED; nothing here is a finding.**

| Lane (sweep · strategy · instrument · TF) | R5-A | R5-B | R5-C | R5-D | Round-5 verdict |
|---|---|---|---|---|---|
| r3-btc-coverage · bollinger_breakout · BTC-USD · daily | KEEP | KEEP | KEEP + escalate | KEEP | **KEEP-dev** |
| r3-stoch-willr · williams_r_reversion · SLV · daily | KEEP | KEEP | KEEP | KEEP | **KEEP-dev** |
| r3-trix-ichimoku · ichimoku_trend · META · daily | KEEP | KEEP | KEEP | KEEP | **KEEP-dev** |
| r3-meanrev-hourly · stochastic_reversion · META · hourly | KEEP | **KILL** | KEEP | KEEP | **KILL (demoted by R5-B)** |
| r3-trend-new-tickers · ema_crossover · TLT · daily | KEEP | KEEP | KEEP | KEEP | **KEEP-dev** |

Machine-readable rollup:
[`experiments/sweeps/r5-rollup/summary.json`](../experiments/sweeps/r5-rollup/summary.json)
(`scripts/run_r5_rollup.py`, the plan's pre-registered ALL-FOUR
aggregation rule applied verbatim).

## R5-A — parameter-neighborhood stability (2026-07-13)

**Headline: no knife edges. All 14 pre-declared ±1-grid-step neighbors
of the five committed top variants beat same-window B&H in a
selection-free replay — every lane passes the ≥ 50% rule at 100%, so
5 KEEP / 0 KILL / 0 KILL-SIG. The pre-registered hypothesis ("for most
of the 5 lanes, a majority of neighbors still beat B&H") is confirmed,
stronger than stated: the top-5 configs are not grid artifacts. Best
neighbor t anywhere 1.66 (SLV `williams_r_reversion` period=21,
sell_above=−20) against the unchanged 2.638 bar — no neighbor comes near
significance, and no neighbor becomes a candidate (probes, not
entrants).**

- **Pre-declaration honored**: the neighborhoods were committed to
  `trading_lab.sweeps` (`R5A_TARGET_LANES` / `r5a_neighbors`) WITH tests
  BEFORE the sweep ran. The clipped neighborhood is 14 configs
  (2 BTC-USD + 4 SLV + 3 META daily + 3 META hourly + 2 TLT), inside the
  registered ≤ 8/lane, ≤ 40 total bound; every neighbor is a point of
  the source lane's committed Round-3 grid (pinned by tests — no new
  parameter territory).
- **Method** (registered): each neighbor replayed SELECTION-FREE (one
  fixed config, no training pick) over the lane's exact committed
  positional test windows at baseline costs (5 bps + 1 bp), vs
  same-window B&H stitched OOS Sharpe. Fidelity guard first: all five
  lanes' baseline replays reproduced their committed stitched OOS Sharpe
  within 1e-8 — 0 lanes SKIPPED.
- **Neighbor spread, read honestly**: neighbors degrade smoothly, as a
  real-if-weak effect should — BTC-USD 1.024/1.088 around the committed
  1.258 (bench 0.821); SLV 0.443–0.694 around 0.500 replayed searched
  (bench 0.170, and three of four neighbors beat the searched
  walk-forward itself); META daily 0.912–0.994 around 0.993 (bench
  0.653); META hourly 0.708–1.792 around 1.529 (bench 0.494 — the widest
  relative spread of the five, consistent with its R5-B death below);
  TLT 0.329–0.419 around 0.482 (bench 0.196).
- **Deviation recorded (interpretation, not method change)**: the plan's
  "KILL-SIG per `classify_verdict` if any lane-level t crosses the
  mirrored bar" is mechanized as: a KILLed lane is KILL-SIG iff its
  WORST neighbor's informational t (graded at the lane's committed
  K=12; the bar never lowered) ≤ −2.638. No lane KILLed and no
  neighbor t was below −2.638 (worst anywhere: +0.19), so the
  interpretation is not load-bearing this round.
- **Artifacts**: 5 per-lane JSONs + rollup in
  [`experiments/sweeps/r5-neighborhood/`](../experiments/sweeps/r5-neighborhood/);
  every `experiments/sweeps/r3-*/` file byte-untouched. **Ledger
  decision (deliberate, the R4-C side of the R4-B/R4-C precedent):
  LEDGERED** — each neighbor replay is a genuinely new run with a return
  stream no existing row describes (r3 ledgered only the searched top
  variant per lane), so 14 rows, `variants_tried=1` (the literal count —
  no search inside a probe), probe-not-entrant caveat in the notes;
  `experiments/index.jsonl` rebuilt. Runtime **1.4 s** (cap 600 s — not
  hit).
- **Burden ledger**: 14 new registered configs; program cumulative
  4345 → **4359**.

### Counts

| Lanes | KEEP | KILL | KILL-SIG | neighbors replayed | neighbors beating B&H |
|---|---|---|---|---|---|
| 5 | 5 | 0 | 0 | 14 | 14 |

## R5-B — time-split stability / leave-one-split-out (2026-07-13)

**Headline: the round's one demotion. 4 KEEP / 1 KILL / 0 KILL-SIG —
META hourly `stochastic_reversion` is DEMOTED to KILL as single-window
luck: its full stitched delta vs B&H (+1.035, the largest of the five)
collapses to −0.164 when its single best split is removed. The other
four lanes keep a positive stitched delta after losing their best split
(worst-case leave-one-out deltas +0.091 to +0.326), exactly the
distributed-edge profile the hypothesis asked for.**

- **Method** (registered): frozen replay of each lane's committed
  per-split params on the identical positional test windows (fidelity
  guard first — all five reproduced within 1e-8, 0 SKIPPED), then the
  stitched OOS Sharpe delta vs same-window B&H recomputed leaving each
  test split out in turn (N = 5–10 per lane). One same-window same-cost
  B&H over the full stitched span, its per-bar returns dropped
  positionally alongside the strategy's — so the leave-nothing-out delta
  equals the committed stitched delta exactly (it does, all five lanes).
- **Deviation recorded (interpretation, not method change)**: the plan's
  "best split" is mechanized as the argmin over the N leave-one-out
  stitched deltas (the removal that hurts most) — identical to the
  plan's own equation of "worst-case leave-one-out delta" with "best
  split removed", and robust to the ambiguity of ranking splits by
  per-split delta instead.
- **The kill, read honestly**: META hourly's per-split deltas are
  +4.05, +0.34, −0.49, −0.97, +1.55 — the entire stitched edge lives in
  split 0 (strategy +2.22 vs benchmark −1.83 on the first 252 hourly
  test bars) plus a helping of split 4. Drop split 0 and the survivor
  is negative. With only 5 splits (the hourly cache is short), one hot
  window carried a 1.5-Sharpe stitched lane; this is precisely the
  failure mode the slice was registered to catch. A Round-5 KILL of a
  round-3 KEEP is a demotion of a dev-candidate, recorded here and in
  the rollup.
- **The keeps**: BTC-USD worst LOO +0.326 (best split #5 removed, of
  10), SLV +0.166 (#9, of 10), META daily +0.152 (#6, of 8), TLT +0.091
  (#8, of 10). Informational t (lane's committed K=12, replayed full
  set): 1.38, 1.04, 0.96, 0.90 — unchanged from the committed values,
  as a faithful replay must be; nothing near the bar.
- **Artifacts**: 5 per-lane JSONs (per-split deltas + all N
  leave-one-out deltas) + rollup in
  [`experiments/sweeps/r5-split-stability/`](../experiments/sweeps/r5-split-stability/).
  Report-only, NOT ledgered (R4-B precedent: 0 new configs, pure
  replay/re-aggregation); `experiments/index.jsonl` untouched. Runtime
  **0.3 s** (cap 300 s — not hit).
- **Burden ledger**: 0 new registered configs.

### Counts

| Lanes | KEEP | KILL | KILL-SIG | worst-case LOO delta > 0 |
|---|---|---|---|---|
| 5 | 4 | 1 | 0 | 4 |

## R5-C — moving-block bootstrap of the Sharpe-delta t (2026-07-13)

**Headline: the pre-registered hypothesis holds on both halves — every
lane's bootstrap delta distribution is centered where its point estimate
says (medians within 0.03 of the points), NO lane's distribution comes
near the promotion bar (bootstrap t 95th percentiles 2.14–2.67 vs the
2.638 bar — only BTC-USD's upper tail touches it), and no lane crosses
the KILL threshold: 5 KEEP / 0 KILL / 0 KILL-SIG. One lane crosses the
ESCALATE threshold: BTC-USD daily `bollinger_breakout` at
`P(delta <= 0) = 0.042` ≤ 0.10 — per the registered branch this produces
an owner-gated proposal doc and changes NO verdict.**

- **Method** (registered, verbatim): paired moving-block bootstrap of
  each lane's fidelity-guarded frozen-replay stitched OOS strategy and
  benchmark per-bar returns — identical resampled block indices applied
  to both series — block length 21 bars daily / 63 hourly, 1,000
  resamples, RNG seed **20260713** fixed in the runner (a fresh
  `numpy.random.default_rng(20260713)` per lane, so each lane's draw is
  order-independent and reproducible). Guard: all five lanes reproduced
  within 1e-8, 0 SKIPPED.
- **Per-lane `P(delta <= 0)`**: BTC-USD **0.042** (escalate), TLT 0.107,
  META daily 0.116, SLV 0.133, META hourly 0.247 — all below the 0.60
  KILL bar, none but BTC-USD at or below the 0.10 escalate bar. The
  ordering is the honest story: the highest-t lane is also the most
  resampling-stable, and the R5-B casualty (META hourly) has the
  shakiest resampled edge (delta std 1.13 vs 0.24–0.30 for the daily
  lanes) — the two slices agree about which lane is fragile.
- **Escalate branch, executed as registered**: the owner-gated proposal
  [proposals/r5c-btc-bollinger-breakout-oos-proposal.md](proposals/r5c-btc-bollinger-breakout-oos-proposal.md)
  recommends a NEW pre-registered selection-free protocol on post-2026
  BTC-USD data (frozen config `period=10, num_std=1.0`, K accounting
  stated). It touches no holdout, schedules nothing, runs nothing, and
  the lane's verdict is unchanged KEEP-dev. It is a proposal the owner
  may freely ignore.
- **Artifacts**: 5 per-lane JSONs (full delta and t distributions:
  mean/std/percentiles + `P(delta <= 0)`) + rollup in
  [`experiments/sweeps/r5-bootstrap/`](../experiments/sweeps/r5-bootstrap/).
  Report-only, NOT ledgered (R4-B precedent: 0 new configs, resampling
  of committed replays); `experiments/index.jsonl` untouched. Runtime
  **0.6 s** (cap 600 s — not hit).
- **Burden ledger**: 0 new registered configs.

### Counts

| Lanes | KEEP | KILL | KILL-SIG | escalate-to-owner | P(delta<=0) range |
|---|---|---|---|---|---|
| 5 | 5 | 0 | 0 | 1 (BTC-USD) | 0.042 – 0.247 |

## R5-D — selection-fair fixed-config replay (2026-07-13)

**Headline: the edge is not a re-selection artifact — all five lanes'
committed top variants beat same-window B&H selection-free (5 KEEP /
0 KILL / 0 KILL-SIG) — but the pre-registered hypothesis is only HALF
confirmed: `selection_gap > 0` on just 3 of 5 lanes, and two lanes'
searched walk-forwards LOST to their own fixed config (SLV −0.313, META
hourly −0.396). On this surface, in-window grid re-picking is closer to
noise than to signal — the round-4 conditioning lesson ("selection
variance, not signal") now measured on the survivors themselves.**

- **Method** (registered): the committed top full-period variant (the
  plan's frozen table) replayed selection-free over the lane's exact
  committed test windows at baseline costs; fidelity guard on the
  searched arm first (all five within 1e-8, 0 SKIPPED);
  `selection_gap = searched_stitched_sharpe − fixed_stitched_sharpe`
  recorded machine-readably per lane, informational only (no registered
  threshold).
- **Per-lane** (fixed vs B&H; gap): BTC-USD 1.072 vs 0.821 (gap
  +0.185); SLV 0.813 vs 0.170 (gap **−0.313**); META daily 0.984 vs
  0.653 (gap +0.010); META hourly 1.925 vs 0.494 (gap **−0.396**); TLT
  0.468 vs 0.196 (gap +0.014). Informational t of the fixed replays
  (lane's committed K=12): 0.79–2.03; the highest (SLV fixed, 2.03) is
  still below the 2.638 bar, and as a selection-free probe of an
  already-selected lane it is not a candidate for anything.
- **Read honestly, both directions**: the positive result is that no
  lane's edge *requires* re-selection — the story-pinned config alone
  beats B&H everywhere, which is what the round-4 synthesis item asked
  to be measured. The negative result is for walk-forward searching
  itself: only BTC-USD gained visibly from re-picking (+0.185), two
  lanes were actively hurt by it, and two were flat (≈ +0.01). Nothing
  here reopens promotion; the fixed configs remain dev-candidates
  inside their lanes, not new entrants.
- **Artifacts**: 5 per-lane JSONs + rollup in
  [`experiments/sweeps/r5-selection-fair/`](../experiments/sweeps/r5-selection-fair/).
  Report-only, NOT ledgered (R4-B precedent: the fixed config is the
  lane's already-ledgered committed variant — a new row would duplicate
  it); `experiments/index.jsonl` untouched. Runtime **0.5 s** (cap
  300 s — not hit).
- **Burden ledger**: 0 new registered configs (the R5-A grid commit
  covers the only new configs this round).

### Counts

| Lanes | KEEP | KILL | KILL-SIG | selection_gap > 0 |
|---|---|---|---|---|
| 5 | 5 | 0 | 0 | 3 |

## Round 5 — closing tally (2026-07-13)

All four pre-registered Round-5 slices have landed against the plan
merged before any outcome existed. One-line verdicts:

| Slice | One-line verdict |
|---|---|
| R5-A neighborhood | **No knife edges: 5/5 KEEP**, all 14 pre-declared neighbors beat B&H; best neighbor t 1.66 vs 2.638 |
| R5-B split stability | **4/5 KEEP, 1 KILL** — META hourly `stochastic_reversion` demoted (single-window luck: worst-case LOO delta −0.164); survivors' worst-case LOO deltas +0.09 to +0.33 |
| R5-C bootstrap | **5/5 KEEP, 0 KILL**, 1 escalate-to-owner (BTC-USD, P(delta≤0)=0.042 → owner-gated proposal, verdict unchanged); no bootstrap distribution near the bar |
| R5-D selection-fair | **5/5 KEEP** — every committed top variant beats B&H selection-free; but `selection_gap > 0` on only 3/5 (searched search lost to its own fixed config on SLV and META hourly) |

**Round-level aggregation (pre-registered ALL-FOUR rule): 4 KEEP-dev /
1 KILL of the top 5.** The demoted lane (META hourly
`stochastic_reversion`) exits the dev-candidate surface; the
machine-readable record is
[`experiments/sweeps/r5-rollup/summary.json`](../experiments/sweeps/r5-rollup/summary.json).

- **Cumulative burden**: Round 5 registered **14 new configs** (all
  R5-A neighbors; R5-B/C/D registered zero — replays, resamples and
  re-aggregations of committed choices), taking the program cumulative
  from 4345 to **4359**. No K was counted down and no bar was lowered
  (informational t graded at each lane's committed K=12 throughout).
- **Runtime caps**: none hit (slice runtimes 0.3–1.4 s against caps of
  300–600 s); nothing was truncated.
- **Deviations from the pre-registration**: none of method. Two points
  the plan left ambiguous were mechanized and are recorded in their
  slice sections: the R5-A lane-level KILL-SIG t (worst-neighbor t at
  the lane's committed K) and the R5-B "best split" (argmin
  leave-one-out delta). Neither was load-bearing for any verdict this
  round. One adopted convention: R5-A is LEDGERED (R4-C
  genuinely-new-run precedent — 14 probe rows, `variants_tried=1`,
  flagged as probes) while R5-B/C/D are report-only (R4-B precedent).
- **0 promoted — promotion remains CLOSED, holdout SPENT.** No Round-5
  verdict promoted anything; the four surviving KEEP-devs are
  dev-candidates only, and genuine OOS validation of any of them stays
  OWNER-GATED behind a new pre-registered protocol on post-2026 data —
  of which the R5-C escalate proposal for BTC-USD is now a concrete,
  ignorable example.
- **What the round actually established**: (1) the top of the surviving
  surface is NOT knife-edged — parameter neighborhoods degrade smoothly
  everywhere; (2) split-concentration is the sharpest killer available
  at zero new-config cost — it found the one fragile lane the other
  three slices each passed; (3) resampling agrees with the point
  estimates and with R5-B about which lane is fragile, and puts exactly
  one lane (BTC-USD) in stable-enough territory to trip the
  pre-registered escalate branch; (4) walk-forward re-selection on this
  surface adds roughly as much noise as signal (`selection_gap` +0.19
  to −0.40) — future rounds comparing searched arms should carry the
  R5-D fixed-config row by default.

Round 5 is closed. Four slices, four honest answers, zero findings, one
demotion, one owner-gated proposal. The top of the KEEP-dev surface is
now stability-tested as well as cost-stressed; anything further still
needs new data (OWNER-GATED) or a genuinely different idea class.
