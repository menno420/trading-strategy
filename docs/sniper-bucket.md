# Sniper bucket — capped, paper-only, pre-registered opportunistic entries

> **Status:** `plan` — good-enough-now design doc (lane
> `paper-lane/design-docs`, written 2026-07-10). Volume-first per owner
> guidance Q-0266: correct over best — §7 lists exactly which
> refinements were deliberately skipped. This document designs a
> **paper-only** construct. It authorizes no real money, no brokerage or
> API signup, no data purchases, and no holdout access (the holdout is
> SPENT — [final-report.md](final-report.md) §Holdout, protocol §6 of
> [p5-holdout-protocol.md](p5-holdout-protocol.md): no re-runs, ever).

## 1. What it is, in one paragraph

The sniper bucket is a small, hard-capped, paper-only allocation for
opportunistic **rule-based** entries: occasional setups that are fully
specified and committed to the ledger *before* their outcome window
opens, then graded mechanically against buy-and-hold. It is a
pre-registration discipline for one-off trade ideas — the same
commit-before-you-look logic that governed the P5 holdout
([p5-holdout-protocol.md](p5-holdout-protocol.md) §Why
pre-registration), applied at single-trade granularity. It is **not** a
path to live trading and it is **not** an appeals court for the
program's negative result: after 590 configurations
([final-report.md](final-report.md) §What this lab tested), nothing
tested earned a statistically significant edge over buy-and-hold on any
window, including the holdout.

## 2. Scope

- **Paper only.** Every position is simulated with the standard engine
  conventions (t+1-open fills, 5 bps slippage + 1 bps commission per
  side, long/flat, no leverage, no shorts — identical to
  [p5-holdout-protocol.md](p5-holdout-protocol.md) §3). No brokerage
  account, no API signup, no order routing, no real money. There is no
  step in this design that requires an OWNER-ACTION, because there is
  no step that touches money or an external account; a hypothetical
  future live version would require one (§8) and is described there
  only, never executed.
- **Rule-based only.** An entry is admissible only if it is a
  deterministic, parameter-frozen rule ("buy X at next open if
  condition C on bar t; exit by rule E or at date D"). "I feel like
  NVDA goes up" is not a setup. Discretionary overrides are prohibited
  — an overridden entry is graded on its original committed rule.
- **No holdout data, no data/ reads.** Setups run only on bars that
  accrue after their commit timestamp (genuinely new post-commit data).
  The spent holdout window is never re-read; `data/**` is not touched
  by this design.

## 3. Sizing cap — conservative, fixed, non-compounding

- The bucket is capped at **≤ 5% of the paper portfolio's inception
  notional** (e.g. €500 of a €10,000 paper book), split across at most
  **5 concurrent setups** of **fixed equal notional** (e.g. €100 each).
- **Fixed notional, no compounding:** paper gains do not enlarge the
  bucket or any position; paper losses do not trigger doubling-down.
  The cap is set once at inception and changes only by owner decision
  routed through [question-router.md](question-router.md) /
  `control/inbox.md`.
- Why this small: the program's evidence prior is against opportunistic
  edge — 13/13 subjects TRANSFER-FAILED at P4 and 0 of 13 holdout
  subjects cleared the significance bar even at K=1
  ([final-report.md](final-report.md) §Holdout). The bucket exists to
  practice pre-registration hygiene cheaply, not because an edge is
  expected.

## 4. Entry discipline — commit before the window opens

Each setup is committed to the ledger **before its outcome window
opens** — before the first bar on which the entry rule could fire. A
setup committed after its window opened is void and is recorded as an
integrity violation (§6).

**Ledger surface (proposed, mirrors the existing run ledger):** one
JSON record per setup in `experiments/paper/entries/*.json`, indexed in
`experiments/paper/index.jsonl` — append-only, same conventions as
`experiments/index.jsonl` + `experiments/runs/*.json` (the CI-audited
surface cited in [final-report.md](final-report.md) §Evidence index).
Each record carries, minimum:

| Field | Meaning |
|---|---|
| `committed_at` | UTC timestamp of the commit (must precede `window_start`) |
| `rule` | full deterministic entry/exit specification, params frozen verbatim |
| `instrument`, `timeframe` | subject of the setup |
| `window_start`, `window_end` | pre-declared outcome window |
| `notional` | fixed paper notional (§3) |
| `variants_considered` | how many setup ideas were looked at before this one was committed — the honest per-entry denominator |
| `graded_at`, `verdict` | filled once, after `window_end`, never edited |

## 5. Grading — mechanical, net of costs, vs B&H

Judged exactly the way P2/P5 verdicts were judged, so the standard
cannot drift ([p5-holdout-protocol.md](p5-holdout-protocol.md) §5):

- Per window: setup net-of-cost return series vs **buy-and-hold of the
  same instrument over the exact same window, same costs**. Verdict
  `BEAT` iff strategy Sharpe > B&H Sharpe (ties and
  "positive-but-below-B&H" are `MISS`).
- Verdicts are **descriptive, never promotions.** The aggregate line is
  `k of N setups beat B&H`, always reported next to the cumulative
  `variants_considered` sum and the program's inherited burden (§7).
  The pre-holdout base rates (7/32, 3/24, 5/32 lanes; 13/99 at P4;
  2/12 holdout secondaries) say scattered beats are what chance looks
  like — one S6-shaped beat (t = 0.81, still inside noise,
  [final-report.md](final-report.md) §Secondaries) proves nothing.

## 6. Kill criteria — pre-registered now, before any entry exists

- **Integrity kill (immediate, whole bucket):** any entry found
  committed after its window opened, edited after commit, or graded on
  anything but its committed rule → the bucket closes permanently and
  the violation is recorded in the ledger and `docs/decisions.md`.
- **Drawdown kill:** cumulative paper loss of the bucket reaches 20% of
  the bucket cap → bucket frozen, no new entries, post-mortem entry in
  `docs/decisions.md` before any owner-decided restart.
- **Futility kill:** after 20 graded windows, if the beat rate is at or
  below the ~13–22% chance base rates above, the bucket closes as
  negative-complete. Negative results are deliverables
  ([founding-plan.md](founding-plan.md)).
- Kills are terminal for the bucket instance; restarting is an owner
  decision, not an agent one.

## 7. Inherited multiple-testing burden — carried on every claim

Every sniper-bucket statistic inherits the program's burden and must be
reported with it: **590 configurations tried across the four P1 lanes
(177 trend-daily + 92 video + 144 mean-reversion-daily + 177
trend-hourly, plus per-split re-selection), and 13 program-wide holdout
verdicts, of which 0 cleared the significance bar even at K=1**
([final-report.md](final-report.md) §Ranked table "Burden" column and
§Holdout). A sniper entry is one more draw from the same well; its
per-entry `variants_considered` (§4) adds to, and never resets, this
denominator. No accumulation of paper wins inside this bucket can
promote anything to a finding.

**What would justify expanding the bucket:** only a **NEW, owner-gated,
pre-registered out-of-sample test on genuinely new post-2026 data** —
a fresh protocol in the shape of
[p5-holdout-protocol.md](p5-holdout-protocol.md), authorized by an
explicit owner ORDER in `control/inbox.md`, with the expansion
hypothesis and verdict rule written before any number is read. **Such a
test is never scheduled, triggered, or inferred by an agent** — the
owner gate of protocol §7.1 is the template. Absent that, the cap of §3
is permanent.

## 8. Skipped refinements (Q-0266: volume-first, correct over best)

Deliberately not done in this version, listed so nobody mistakes
absence for oversight:

- **No position-sizing scheme** beyond fixed equal notional — no Kelly,
  no volatility targeting. Sizing optimization is new selection.
- **No setup taxonomy or scoring** — entries are free-form rules
  meeting §2, not a curated playbook.
- **No power analysis** for the 20-window futility threshold — it is a
  round, conservative number, not an optimized one.
- **No automation** — no grading script, no scheduler; commits and
  grades are ordinary ledgered writes. Tooling can follow if the bucket
  survives its first kills.
- **No live version.** For completeness, the step this design will
  never take, in the six-field OWNER-ACTION form — described only,
  never executed: **action:** open/fund any real brokerage allocation
  for sniper entries; **why:** it would only ever be justified by the
  §7 expansion evidence, which does not exist; **cost:** real capital
  at risk plus account/fee overhead; **payback (pessimistic):** zero —
  nothing in this program cleared significance, so the expected edge is
  indistinguishable from noise and the realistic outcome is
  underperforming buy-and-hold after costs; **risk:** loss of the
  allocated capital (program MDDs ran −12% to −34% on holdout windows,
  −64% historically); **reversibility:** partially reversible (close
  positions, withdraw) but losses and fees are permanent.

## 9. Where records live — summary

- Setup commits + grades: `experiments/paper/entries/*.json`, indexed
  in `experiments/paper/index.jsonl` (§4).
- Kills, restarts, cap changes: `docs/decisions.md` entries.
- Evidence base cited: [final-report.md](final-report.md) (ranked
  table, §Holdout), [p5-holdout-protocol.md](p5-holdout-protocol.md).
