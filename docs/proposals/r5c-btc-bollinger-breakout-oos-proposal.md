# BTC-USD `bollinger_breakout` — post-2026 OOS protocol proposal (OWNER-GATED)

> **Status:** `plan` — **FROZEN PREREGISTRATION PROPOSAL. OWNER-GATED /
> FLAG-ONLY — never self-executing.** Written because the pre-registered
> Round-5 R5-C escalate branch fired
> ([research-round-5-plan.md](../research-round-5-plan.md) § R5-C:
> `P(delta <= 0) <= 0.10`): the BTC-USD daily `bollinger_breakout`
> dev-candidate's bootstrap `P(delta <= 0)` came in at **0.042**. Per the
> plan's standing-rails definition, this document only *proposes* a NEW
> pre-registered protocol on post-2026 data — it never touches the spent
> holdout, never schedules an OOS run, and changes NO verdict (the lane
> stays KEEP-dev, never a finding). The badge token is `plan` because the
> doc taxonomy has no `proposal` value; read it as a preregistration
> proposal. No agent may execute it autonomously, fetch data for it, or
> act on it without an explicit owner ORDER.

## 0. Why this document exists (and what it is NOT)

Round 5 deepened the top-5 KEEP-dev lanes
([research-round-5-results.md](../research-round-5-results.md)). The
BTC-USD daily `bollinger_breakout` lane (committed top full-period
variant `period=10, num_std=1.0`, walk-forward train 1008 / test 252,
baseline costs 5 bps + 1 bp per side) was the only lane to cross the
pre-registered escalate threshold: under a paired moving-block bootstrap
(block 21 bars, 1,000 resamples, seed 20260713) of its fidelity-guarded
frozen replay, `P(delta <= 0) = 0.042` — the resampled Sharpe edge over
same-window B&H is positive in ~96% of resamples. It also kept
dev-candidate status under all three other Round-5 slices (R5-A
neighborhood 2/2 neighbors beat B&H; R5-B worst-case leave-one-out delta
+0.326; R5-D selection-free fixed-config replay 1.072 vs B&H 0.821).

It is NOT a finding: the informational t is 1.378 against the 2.638 bar
at K=12 (the bootstrap 95th percentile of t is 2.67 — the distribution's
upper tail touches the bar, the point estimate does not approach it), the
dev data is spent by four rounds of search, and promotion is CLOSED.
The ONLY honest next step is data that did not exist when the config was
frozen.

## 1. Hypothesis (stated precisely)

On BTC-USD daily bars from a start date strictly after 2026-01-01 (data
that did not exist during Rounds 0–5), the frozen configuration below
beats same-window buy-and-hold on net-of-costs annualized Sharpe.

## 2. Frozen configuration (do NOT widen after seeing results)

- Strategy: `bollinger_breakout` (committed implementation at the
  Round-5 SHA — long on close crossing above the upper band, exit below
  the middle band), **`period=10, num_std=1.0`** — ONE config, K=1 for
  this protocol viewed alone; the honest program-level caveat in §4.
- Selection-free: NO walk-forward re-picking, NO grid. The R5-D
  selection-fair replay of exactly this config is the dev-side anchor
  (stitched OOS Sharpe 1.072 vs B&H 0.821).
- Costs: 5 bps slippage + 1 bp commission per side; signal at bar t
  fills at bar t+1 open (house conventions, unchanged).
- Annualization: lab-wide `PERIODS_PER_YEAR["daily"] = 252` (understates
  BTC Sharpe by a constant factor; same-window comparisons unaffected).

## 3. Evaluation window and rule

- Window: a contiguous post-2026 span of >= 252 daily bars, fixed by the
  owner ORDER before any bar of it is inspected.
- Rule: KEEP the hypothesis alive iff net Sharpe > same-window same-cost
  B&H Sharpe AND > 0; report the ORDER 007 t informationally. A
  significance claim additionally requires t >= `min_tstat(K)` at the
  honestly-counted K (§4).

## 4. Multiple-testing honesty

This lane is the best of 5 Round-5 targets, which were the best of 42
R4-B survivors, out of 4,359 registered configs. A single-lane OOS pass
at K=1 would therefore still be selection-tinged; the proposal recommends
the owner treat any pass as ONE pre-registered confirmation to be judged
against the program surface (at minimum K=5, the Round-5 target count —
bar `min_tstat(5)` ≈ 2.33 — and the owner may reasonably demand the full
program K). The bar is never lowered; K only ever rises.

## 5. Rails (unchanged)

Research-only paper evaluation; no broker/order/exchange-write code, no
live API configuration, no real money. `data/p5holdout/` stays untouched
(it is SPENT and is not the data this proposal asks for);
`unlock_holdout` is never passed. New data enters only via the
sanctioned `trading_lab.data.fetch_ohlcv` path under an explicit owner
ORDER, cached and committed before any evaluation runs.

## 6. Cost/benefit for the owner

Cheap: one fetch, one selection-free replay, no new code. The honest
prior is still unfavorable — a 1.4-t dev edge on a heavily-mined surface
usually regresses — but this is the only lane in five rounds whose
resampled edge was stable enough to trip the pre-registered escalate
threshold, and the protocol above makes the answer unambiguous either
way. Doing nothing is a perfectly acceptable owner choice; this document
merely makes the option concrete and p-hack-proof.
