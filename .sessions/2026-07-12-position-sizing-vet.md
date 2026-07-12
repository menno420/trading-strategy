# 2026-07-12 — Position-sizing vet (dev-only, illustrative)

> **Status:** `complete` — vetting the owner's small-account position-sizing
> idea (80% / 40% fractional vs fixed stake) with fractional-Kelly math + a
> self-contained synthetic Monte Carlo. RESEARCH-ONLY / DEV-ONLY / ILLUSTRATIVE:
> NO holdout reads, NO market-data module imports, NO accounts, NO live/paper
> trading, NO new OOS/FINDING/PROMOTED claims. Research round 2 stays CLOSED.
> Deliverable = `docs/research/position-sizing-vet-2026-07-12.md` + a pure-numpy
> simulation script. Card flips `complete` as the deliberate last step.

📊 Model: opus-4.8 · position-sizing-vet research worker (Money-seat coordinator direction) · start 2026-07-12T11:00Z

💡 **Session idea:** The owner's experiment as designed — a €100–200 bot that
sizes 80% of account value per trade and compounds — measures LUCK + COST DRAG,
not edge. Position sizing scales an existing per-trade edge (μ) and its
volatility drag; it never CREATES edge. Our own final report is the load-bearing
fact: after 668 program-wide configs, 0/13 subjects cleared the ORDER 007
significance bar on the one-shot holdout, the sole rule-pass candidate read
t = 0.02, and every measured "edge" was a fraction of a Sharpe point. So the
honest base case for μ_net is ≤ 0, and at €100–200 round-trip costs (0.5–3% on
€80–160 positions) push net edge further negative. On a no-edge bot, higher
fractions just compound the loss faster with more variance; a fixed stake bleeds
roughly linearly instead of compounding away. The constructive answer to "what
would happen" is the frozen paper lane (grading from 2026-07-17) with €0 at risk,
gated behind the broker/go-live OWNER-ACTION.

## Why this session exists

The owner floated a position-sizing scheme for a small live account (€100–200):
one open trade at a time, sized ~80% of current account value, compounding; later
parallel bots at 40% fractional and at a fixed constant stake. The question is
honest, not rhetorical: *what actually happens?* This slice answers it with (1)
the fractional-Kelly growth math, (2) a cost-reality breakeven at €100–200, and
(3) a deterministic synthetic Monte Carlo over three sizing rules × four net-edge
scenarios — all self-contained (pure numpy + stdlib, no repo data modules, no
holdout, no market data). Deliverable is a research doc labelled DEV-ONLY /
ILLUSTRATIVE. Research-only rail throughout; nothing here promotes anything.

## Work log

- 2026-07-12T11:00Z — heartbeat: hard-synced to origin/main HEAD `3ba081c`
  (verified `git rev-parse HEAD` == `git ls-remote origin HEAD`). Default branch
  `main`. Branch `claude/position-sizing-vet`; this card is the first commit
  (born-red, Status `in-progress`). Read `control/inbox.md` (read-only, never
  edited): newest order is ORDER 011; nothing newer. Cited honest facts from
  `docs/final-report.md`, the ORDER 007 significance rule
  (`src/trading_lab/promotion.py`), the paper-lane protocol grading schedule
  (`docs/paper-lane-protocol.md` §6, weekly cadence, first re-armed pass
  2026-07-17), and the go-live OWNER-ACTION gate (`docs/sniper-bucket.md` §8 /
  `docs/founding-plan.md` RESEARCH-ONLY).
- Wrote `scripts/position_sizing_mc.py` (pure numpy + stdlib; verified it imports
  nothing from the repo — no `trading_lab`, no data loader, no market data, no
  holdout). Ran it (deterministic, seed 20260712, 10k paths, σ=3% base + 2%/5%
  sensitivity); captured the results table. Analytic drag matches MC exactly
  (µ=0, f=0.8, σ=3% → exp(−½·0.64·0.0009·200)=€94.4 vs MC median €94.43).
- Wrote `docs/research/position-sizing-vet-2026-07-12.md` (DEV-ONLY / ILLUSTRATIVE)
  with the plain-language owner verdict first, the fractional-Kelly math
  (g≈f·µ−½f²σ², f*=µ/σ², over-betting past 2f*), the €100–200 cost-reality
  breakeven table, the MC tables, and the constructive paper-lane alternative.
  Raw dump: `docs/research/position-sizing-mc-2026-07-12.json`.
- Linked the doc from the read-path doc `docs/current-state.md` §In flight (fixed
  the reachability orphan finding). 223 pytest green; `check --strict` green after
  this flip.

## Previous-session review

⟲ Previous-session review: the prior 2026-07-12 slice (`order-011-ack`) was a
record-keeping ack — it verified the terminal states of PRs #64/#65/#66 and
recorded the grading-executor trigger ids in `control/status.md`, confirming the
weekly paper-lane grading pass fires 2026-07-17T09:05:22Z (expected FLAT during
warm-up). That establishes exactly the constructive alternative this doc points
the owner toward: a zero-money forward lane already scheduled to answer "what
would happen." This session adds no orders work and touches neither
`control/inbox.md` nor `control/status.md`; it lands an illustrative research doc
+ a self-contained simulation on their own branch.

## Close-out

**Done:** on branch `claude/position-sizing-vet` —

1. `.sessions/2026-07-12-position-sizing-vet.md` — this card (first commit
   born-red → flipped `complete` as the deliberate last step).
2. `scripts/position_sizing_mc.py` — self-contained synthetic Monte Carlo
   (pure numpy + stdlib, no repo/data/holdout imports).
3. `docs/research/position-sizing-vet-2026-07-12.md` — the DEV-ONLY /
   ILLUSTRATIVE research note (owner verdict, math, cost reality, MC tables,
   paper-lane alternative) + `docs/research/position-sizing-mc-2026-07-12.json`.
4. `docs/current-state.md` §In flight — one bullet linking the doc (reachability).

**Verify:** `python3 bootstrap.py check --strict` → green after this card flips
`complete`. Integrity audit at close: zero `data/**` reads, zero market-data
module imports, no ledger rows added, `holdout_unlocked` count unchanged at 13,
`control/inbox.md` byte-untouched, `control/status.md` byte-untouched, no
promotion/finding language, no merge action.

**Next (guard recipe):** none owed by this slice.

Session end: badge flips `complete` in the final commit before push.
