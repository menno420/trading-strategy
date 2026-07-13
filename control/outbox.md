# trading-lab · outbox

> Reports FROM this Project to the fleet manager / owner. **One writer: this
> Project.** Append-only — new entries go at the bottom; never rewrite or
> delete prior entries (forward-only git, per `control/README.md`'s
> one-writer-per-file rule). Order progress still lives in
> `control/status.md`; this file carries manager-addressed narrative reports.

## NIGHT REPORT · 2026-07-13T09:22:51Z · window 2026-07-12T22:30Z → 2026-07-13T09:12Z
to: fleet-manager (owner morning review roll-up)
serves: ORDER 013 (control/inbox.md @ 08969bb)

### SHIPPED
- 18 PRs merged to main first-parent in the window, #80–#97 (window-start main
  135f937 → 08969bb):
  - #80 (23b0005) — owner ORDER 012 (night-run) landed verbatim in inbox.
  - #81–#88 — Round-3 research slices 1–8 (new families: stochastic/Williams-R
    reversion, ROC momentum, ADX-filtered SMA, Aroon, CCI, Bollinger breakout,
    ATR trailing, xsec reversal, TRIX, Ichimoku; 6 new ticker caches;
    first hourly mean-reversion sweep).
  - #89 (374651a) — Round-3 synthesis docs/research-round-3-results.md
    (slices 1–8: 1,752 configs / 166 lanes → 0 PROMOTED / 41 KEEP-dev /
    125 KILL, best t 1.04 vs Bonferroni bar 2.64).
  - #90–#95 — Round-3 slices 9–14 (trend/mean-reversion/gated families ×
    new tickers, BTC-USD coverage, trend × hourly, hourly-matrix completion).
  - #96 (de5a477) — ORDER 012 morning tally heartbeat re-stamp.
  - #97 (08969bb) — manager append of ORDER 013 (this report's order).
- Research-round headline (full night, per the #96 tally, status.md@de5a477):
  **3,468 configs / 312 graded lanes → 0 PROMOTED / 64 KEEP-dev / 248 KILL;
  max t-stat 1.38 vs promotion bar 2.64** — honest null: nothing overnight is
  a finding, and that is the deliverable. Notable significant negative:
  TSLA rsi_mean_reversion t = −3.01 (worse than buy-and-hold; #91 card).
- Ledger: +309 rows (experiments/index.jsonl 242 → 551 over the window,
  measured at 135f937 vs 08969bb).
- Tests: **437 passed** (pytest line, main CI run 29238187572 @ 08969bb,
  2026-07-13T09:12Z; substrate-gate run 29238187586 also green).
- Rails held: holdout and paper lane byte-untouched over the window (no
  holdout/paper path in `git diff 135f937..08969bb --name-only`); no
  exchange-write code (research-only lane).

### OPEN PRs
- None. Verified 2026-07-13T09:19Z via GitHub MCP (state=open → empty),
  cross-checked against `git ls-remote origin main` (08969bb).

### ORDERS
- 001–011: done (manager flips pending on inbox — statuses there still read
  `new`; the manager owns that file).
- 012: served — night run executed through the night, morning tally posted
  05:06Z (#96, de5a477), inside the ~06:00Z MORNING clause.
- 013: served by this entry (report also mirrored in control/status.md).
- Outstanding: none beyond owner-gated queue items (holdout re-arm and any
  new OOS protocol are owner actions, not schedulable by agents).

### SIM-REQUESTs / ASKS PENDING
- Per ORDER 013's text: idea-engine local ORDERs 005/006 = 9 queued
  SIM-REQUESTs (relayed fact from the order; not re-verifiable from this
  repo's files).
- This lane: no new SIM-REQUESTs raised overnight.

### PENDING
- Friday 2026-07-17 grading pass (warm-up FLAT expected) — business cron
  trig_01FRG4uUxPh5ZGncZGfRgF2F, next fire 2026-07-17.
- KILL-SIG verdict-class proposal awaiting manager/owner review
  (.sessions/2026-07-13-r3-meanrev-new-tickers.md, PR #91 card: add
  KEEP / KILL / KILL-SIG three-way verdict from the already-computed
  promotion_grade t-stat).
- Next research round awaits manager/owner direction.

### STALLS / DENIALS
- None material overnight in this lane.
- Shared-infra notes: `sleep` is harness-blocked (known, worked around with
  event-driven waits); raw api.github.com returns proxy-403 (recorded wall —
  the MCP path works fine and was used instead).

### WAKE-CHAIN HEALTH
- Failsafe trigger trig_01HCLdpcX9QNUz4Y33efgt57 (cron 45 1-23/2 * * *):
  fired on schedule all night.
- Pacemaker: paused 06:03Z post-run; resumed at ORDER service.
- Grading trigger trig_01FRG4uUxPh5ZGncZGfRgF2F: next fire 2026-07-17
  (business cron — rebind, never delete).
- SWTK checkpoints: T+7 trig_01LfwTPMGzM1fqA9CTQLgHnD (2026-07-19),
  T+14 trig_01Muk6nrt2BdxsPmDVY4arwA (2026-07-26).

### NEXT-3
1. Friday 2026-07-17 grading pass (warm-up FLAT expected).
2. KILL-SIG verdict-class proposal review (#91 card).
3. Next research round on manager/owner direction.

## BOOT REPORT · 2026-07-13T13:45:05Z · trigger cutover + ORDER 011 grading-executor verification
to: fleet-manager
serves: ORDER 011 (grading-executor verification) — verification satisfied

### GRADING EXECUTOR — VERIFIED LIVE
- The 2026-07-13 trigger cutover is complete (coordinator verified via
  list_triggers today): the weekly grading executor is a NEW business cron
  **trig_01UsNU4JRps4b7jiAMdEfXNi** ("trading-strategy weekly paper-lane
  grading", cron 0 9 * * 5), **bound to the coordinator seat**
  (session_015hXc4bY4Dj8pmAKaJTCVTZ), **next fire 2026-07-17T09:05Z**.
- This satisfies ORDER 011's grading-executor verification. The old
  grading-trigger id referenced by ORDER 011 / docs (trig_015aNMg5…) and
  the ender-recorded trig_01FRG4uUxPh5ZGncZGfRgF2F are SUPERSEDED — the
  old cron is confirmed deleted, along with the old failsafe
  (trig_01HCLdpcX9QNUz4Y33efgt57) and old SWTK one-shots
  (trig_01LfwTPMGzM1fqA9CTQLgHnD, trig_01Muk6nrt2BdxsPmDVY4arwA); new
  seat-bound replacements are on record in control/status.md.

### FLAG FOR MANAGER ROUTING — potential duplicate grading fire
- FOREIGN trigger **trig_01YXNmgqYeYQ1LuepsLmbNCG** — a send_later firing
  **2026-07-17T09:00Z**, titled "WEEKLY GRADING PASS (trading-strategy
  paper lane)", targeting non-seat session_01NwvvbgUVSdQvY8eYwtuEoo. It
  would fire 5 minutes BEFORE the seat-bound grading cron — a potential
  DUPLICATE grading fire on 07-17. Not ours to delete: recorded only,
  untouched. Requesting manager routing/disposition before Friday.
