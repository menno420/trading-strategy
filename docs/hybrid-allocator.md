# Hybrid allocator — B&H core / rule sleeve / cash buffer (paper)

> **Status:** `plan` — good-enough-now design doc (lane
> `paper-lane/design-docs`, written 2026-07-10). Volume-first per owner
> guidance Q-0266: correct over best — §8 lists exactly which
> refinements were deliberately skipped. This document designs a
> **paper-only** allocation. It authorizes no real money, no brokerage
> or API signup, and no holdout access (the holdout is SPENT —
> [final-report.md](final-report.md) §Holdout; per
> [p5-holdout-protocol.md](p5-holdout-protocol.md) §6 there are no
> re-runs, ever).

## 1. What it is, in one paragraph

A three-way **paper** portfolio that puts the program's honest
conclusion into allocation form: a **buy-and-hold core** holds the
majority (because nothing tested beat holding at statistical
significance), a small **rule-based sleeve** runs the single
confirmed-but-not-significant candidate (donchian × AAPL × daily,
entry=15 / exit=5 — [final-report.md](final-report.md) ranked table
rank 1), and a **cash buffer** absorbs rebalancing and keeps the
structure honest about uncertainty. The point is to *practice* running
a mixed allocation with pre-registered mechanics and mechanical
grading — not to capture an edge, because the evidence says there is
none to capture.

## 2. The three sleeves — concrete conservative split

| Sleeve | Share | Contents | Benchmark |
|---|---|---|---|
| B&H core | **70%** | buy-and-hold of a broad passive holding (paper; e.g. a world-equity ETF proxy, owner's pick) | itself — it *is* the null |
| Rule sleeve | **20%** | donchian × AAPL × daily, params frozen verbatim `{"entry": 15, "exit": 5}` (source: [p5-holdout-protocol.md](p5-holdout-protocol.md) §2 row P) | B&H AAPL, same window, same costs |
| Cash buffer | **10%** | paper cash, 0% return assumed (conservative — no interest modeled) | none |

Example on a €10,000 paper book: €7,000 core / €2,000 rule sleeve /
€1,000 cash. The split is **chosen conservative, not optimized** —
optimizing it against history would be one more fitted parameter (§8).

## 3. Why the rule sleeve stays small — the honest rationale

The sleeve runs the best thing this program produced, and the best
thing this program produced is **not distinguishable from noise**.
Verbatim evidence, [final-report.md](final-report.md) ranked-table
rank 1 and §Holdout headline:

- P5 holdout (2025-01-10 → 2026-07-10, 375 bars): Sharpe **0.759 vs
  B&H 0.740** — CONFIRMED by the mechanical pre-registered rule, but
  the +0.019 edge has Lo (2002) SE 0.819: **t = 0.02**, versus a 1.64
  minimum at the most lenient K=1 (3.45 at the lane burden K=177).
  Label: **RULE-PASS / candidate**, not a finding (ledger row
  `experiments/runs/20260710T164705692772Z-45c47f3e9649.json`).
- The P2 edge that preceded it was itself demoted at t = 0.42
  ([p2-regrade-aapl-donchian.md](p2-regrade-aapl-donchian.md)); P4
  transfer failed 1/8.
- The edge is **drawdown-shaped in all three windows**: Sharpe wins
  come from losing less in drawdowns while CAGR trails holding (P5:
  8.9% vs 20.3%; Sortino below B&H, 0.51 vs 0.76).

A t = 0.02 candidate gets a sleeve because it is the only subject that
passed its pre-registered rule out-of-selection twice — and it gets a
*small* sleeve because t = 0.02 is what pure noise looks like. If the
sleeve underperforms, that is the expected outcome, and it is a
deliverable, not a surprise. The sleeve share never grows on paper
performance (§6).

## 4. Rebalancing rule — simple, calendar-based, pre-registered here

- **When:** the first trading day of each calendar quarter (Jan / Apr /
  Jul / Oct), at t+1 open per the engine convention. No intra-quarter
  rebalancing, no drift bands, no discretion.
- **What:** restore 70/20/10 of current total paper value by simulated
  trades, each charged the standard 5 bps slippage + 1 bps commission
  per side ([p5-holdout-protocol.md](p5-holdout-protocol.md) §3).
- **Inside the rule sleeve:** the donchian rule runs long/flat as
  ledgered; when flat, the sleeve's notional idles as sleeve cash (0%
  assumed), not as extra core.
- This paragraph **is** the pre-registration: the calendar, the
  targets, and the costs are fixed before the first paper bar is
  scored. Changing any of them mid-flight voids the track record and
  restarts grading from zero.

## 5. Grading — per sleeve and whole-book, mechanical

Judged the way every program verdict was judged (net-of-cost Sharpe vs
B&H on the identical window — [p5-holdout-protocol.md](p5-holdout-protocol.md)
§5), reported per calendar quarter and cumulatively:

- **Rule sleeve:** vs B&H of AAPL over the same window, same costs.
  `BEAT`/`MISS` per window; descriptive only, never a promotion.
- **B&H core:** reported as-is; it is the null hypothesis in portfolio
  form, and it needs no defense.
- **Whole book:** the 70/20/10 portfolio vs a 100% B&H-core portfolio
  over the same window, same costs — this is the number that answers
  "did the hybrid structure add anything over just holding?" The prior,
  stated now: **it will not**, and quarters where it does are chance
  until a new pre-registered test (owner-gated, post-2026 data —
  [sniper-bucket.md](sniper-bucket.md) §7 states the identical bar)
  says otherwise.

**Ledger surface:** quarterly grading rows in
`experiments/paper/index.jsonl` with per-quarter detail in
`experiments/paper/entries/*.json` — the same proposed paper surface as
[sniper-bucket.md](sniper-bucket.md) §4, mirroring the append-only,
CI-auditable conventions of `experiments/index.jsonl` +
`experiments/runs/*.json` ([final-report.md](final-report.md)
§Evidence index).

## 6. Kill / freeze criteria — pre-registered now

- **Rule-sleeve freeze:** if after 8 graded quarters the sleeve's
  cumulative Sharpe trails B&H AAPL, the sleeve goes flat-to-cash and
  the result is recorded as negative-complete in `docs/decisions.md`.
  No parameter tweak may rescue it — that would be tuning, and the
  candidate's parameters have been frozen since P1.
- **No promotion path from paper:** no run of paper quarters, however
  good, promotes the candidate or grows its share. The only path is a
  NEW owner-gated pre-registered out-of-sample protocol on post-2026
  data, authorized by an explicit owner ORDER in `control/inbox.md` —
  never scheduled or inferred by an agent.
- **Integrity kill:** any mid-flight change to targets, calendar,
  params, or costs voids the track record (§4).

## 7. Inherited multiple-testing burden — carried on every claim

Every number this allocator produces inherits the program's full
burden and is reported with it: **590 configurations across the four
P1 lanes (burdens 177 trend-daily / 92 video / 144
mean-reversion-daily / 177 trend-hourly, plus per-split re-selection)
and 13 program-wide holdout verdicts, 0 of which cleared the
significance bar even at K=1** ([final-report.md](final-report.md)
§Ranked table, §Holdout). The rule sleeve's candidate was selected by
that process; its paper track record is downstream of that selection
and can never launder it away.

## 8. Skipped refinements (Q-0266: volume-first, correct over best)

Deliberately not done in this version:

- **No split optimization** — 70/20/10 is a conservative convention,
  not a fitted allocation; no efficient frontier, no backtested weight
  search (that would be new selection against consumed data).
- **No volatility targeting, no drift-band rebalancing** — calendar
  quarters only.
- **No interest on cash**, no dividend modeling, no tax modeling, no FX
  modeling; costs are the flat 5+1 bps convention.
- **No multi-candidate sleeve** — S6 (rsi_mean_reversion × META,
  holdout t = 0.81, 0/8 at P4) was considered and excluded: one
  chance-level holdout beat from a 144-config lane does not earn an
  allocation ([final-report.md](final-report.md) §Secondaries).
- **No automation** — grading is an ordinary ledgered write, no
  scheduler.

## 9. Real-account touchpoints — OWNER-ACTION only, described never executed

Per owner guidance Q-0250, **DEGIRO remains a read-only manual
benchmark**: the owner may manually transcribe real-account statements
for side-by-side comparison; no agent reads, links, or automates that
account, and nothing in this design requires it. The only conceivable
real-money step, in the six-field OWNER-ACTION form for the record —
**described only, never executed, and not recommended**:

- **action:** fund a real-money version of this allocation (or link
  any brokerage/API, DEGIRO included, beyond manual read-only use);
- **why:** it would only be justified by a NEW pre-registered
  out-of-sample result clearing the significance bar, which does not
  exist;
- **cost:** real capital at risk, brokerage fees, spread/slippage
  likely worse than the modeled 6 bps/side, plus owner time;
- **payback (pessimistic):** zero or negative — the rule sleeve's edge
  is t = 0.02, so the realistic expectation is matching or trailing
  buy-and-hold after real costs;
- **risk:** capital drawdown (the candidate's ledgered MDDs: −11.8%
  holdout, −21.3% P1 OOS, −63.9% P2; the core's own B&H drawdowns run
  −30% to −82% on the same windows);
- **reversibility:** partially reversible (liquidate, withdraw), but
  realized losses, fees, and any tax events are permanent.

## 10. Where records live — summary

- Quarterly grades + rebalance records: `experiments/paper/index.jsonl`
  and `experiments/paper/entries/*.json` (§5; shared surface with
  [sniper-bucket.md](sniper-bucket.md)).
- Freezes, kills, split changes: `docs/decisions.md`.
- Evidence base cited: [final-report.md](final-report.md) rank 1 row,
  §Holdout headline and row P;
  [p2-regrade-aapl-donchian.md](p2-regrade-aapl-donchian.md);
  [p5-holdout-protocol.md](p5-holdout-protocol.md) §2, §3, §5.
