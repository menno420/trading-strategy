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

## ROUND-5 REPORT · 2026-07-13T16:26:35Z · robustness round complete + R5-C escalation + standing gate
to: fleet-manager

### ROUND 5 — COMPLETE (PR #110, 47d3cbc)
- 4 pre-registered robustness experiments (R5-A parameter-neighborhood,
  R5-B leave-one-split-out, R5-C moving-block bootstrap, R5-D
  selection-fair replay) ran on the frozen top-5 KEEP-dev lanes →
  **4 KEEP-dev / 1 KILL / 0 promoted**. Cumulative program surface:
  **4,359 registered configs**. Promotion remains CLOSED; results in
  docs/research-round-5-results.md.

### R5-C ESCALATE → OWNER-GATED PROPOSAL
- R5-C's pre-registered escalate branch fired once (BTC-USD daily
  bollinger_breakout, P(delta<=0) = 0.042): verdict unchanged, nothing
  run — an owner-gated proposal was filed instead:
  **docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md**.
- Timing: the proposal requires a contiguous post-2026 span of
  **>= 252 daily bars**, so execution cannot start before **~2026-09-09**.
  No agent action is possible until then; the owner decision can wait.

### STANDING GATE FOR ROUND 6 (PR #111, d498018)
- The selection-fair fixed-config replay gate is now **STANDING** for
  research round 6 onward (**decision D-0002**, docs/decisions.md;
  binding doc docs/selection-fair-gate.md): a dev-lane KEEP additionally
  requires the committed top variant, replayed selection-free, to beat
  the same-window benchmark. Round <= 5 ledgers stand as published.

## GRADING PRE-VERIFY · 2026-07-13T22:50:23Z · 07-17 duplicate-fire risk, concrete statement
to: fleet-manager
serves: ORDER 014 item 4 (grading pre-verify; PR #115)

### LIVE EXECUTOR — RE-VERIFIED INDEPENDENTLY
- One read-only `list_triggers` call 2026-07-13T22:48Z confirms the seat-bound
  grading cron, verbatim: **trig_01UsNU4JRps4b7jiAMdEfXNi** ("trading-strategy
  weekly paper-lane grading", cron `0 9 * * 5`, enabled: true, next_run_at
  **2026-07-17T09:05:29Z**, persistent_session_id
  **session_015hXc4bY4Dj8pmAKaJTCVTZ** — the live coordinator seat). Matches
  the BOOT REPORT (13:45:05Z above) and `control/status.md` exactly.

### CLARIFYING THE 13:45:05Z DUPLICATE-FIRE FLAG — the concrete morning-of risk
- The BOOT REPORT above flagged FOREIGN trigger
  **trig_01YXNmgqYeYQ1LuepsLmbNCG** (send_later, fires **2026-07-17T09:00Z**,
  "WEEKLY GRADING PASS", target non-seat session_01NwvvbgUVSdQvY8eYwtuEoo) as
  "a potential DUPLICATE grading fire" but did not state the consequence.
  Stating it concretely: **if that foreign session is alive on Friday, a
  duplicate grading fire at 09:00Z could double-write the graded ledger** —
  two grading passes running ~5 minutes apart could both read
  `experiments/paper/ledger.md` as ungraded and race their write-backs/PRs.
  The grader's idempotency (rows already carrying `verdict:` are never
  touched) protects sequential re-runs, NOT two concurrent passes that each
  see the pre-grade ledger.
- Mitigating facts, for calibration: this Friday's expected result is FLAT
  (warm-up; a FLAT pass writes nothing — dry-run verified 2026-07-13, PR
  #115), and the foreign session's environment may be dead. The risk is
  therefore low this week but structural for every graded week after warm-up.
- Action: none taken on the trigger itself — foreign, not ours to touch.
  Re-requesting manager disposition (delete or confirm-dead) before Friday.

## NIGHT REPORT · 2026-07-14T01:14:45Z · ORDER 014 close-out — all 5 items complete · window 2026-07-13T22:14Z → 2026-07-13T23:12Z
to: fleet-manager (owner morning review roll-up)
serves: ORDER 014 (control/inbox.md @ c9297a7 — EAP final-night worklist)

### SHIPPED
- 4 PRs enabler-merged green in the window, closing all 5 ORDER 014 items:
  - #114 (aa94719→main) — ack + round-6 plan/run claims.
  - #116 (**c0e6459**) — item 1: round-6 pre-registered plan
    docs/research-round-6-plan.md (badge binding): slices R6-A/B/C,
    **696 new configs pre-registered** before any outcome existed; the
    selection-fair gate (D-0002) and the R5-D fixed-config row folded in as
    standing rules effective this round (also closes item 3).
  - #118 (**0d12515**) — item 2: all three slices executed top-down,
    **58/58 lanes, no cap hits — 3 KEEP-dev / 47 KILL / 8 KILL-SIG /
    0 promoted** (best t 0.60 vs the unchanged 2.638 bar); results
    docs/research-round-6-results.md.
  - #115 (**d6e3cf9**) — items 4+5: grading executor independently
    CONFIRMED via one read-only list_triggers call
    (trig_01UsNU4JRps4b7jiAMdEfXNi · next fire 2026-07-17T09:05Z · bound
    to this seat); the foreign duplicate-fire risk is concretely stated in
    the GRADING PRE-VERIFY entry above; scripts/grade_paper.py dry-run
    CLEAN (exit 0, exact protocol §7 FLAT/warm-up shape, zero writes).
- Headline nulls (the round's finding is the null): the **overnight-gap
  family fails everywhere** — 0/12 KEEP, t down to −4.01, the sharpest
  null in program history; and **volume confirmation adds nothing over
  pure OBV** (registered R6-A hypothesis confirmed null).
- Multiple-testing burden: **4359 → 5055** registered configs, exactly as
  pre-declared in the plan.

### RAILS
- Holdout never read; no data fetches; no exchange-write code; promotion
  CLOSED; bar never lowered; paper lane intact; research-only lane intact.

### ORDERS
- 014: all 5 items complete this repo side — served by this entry
  (progress mirrored in control/status.md; manager flips pending on inbox).

### NEXT-2
1. Friday 2026-07-17 grading pass — FLAT expected (warm-up).
2. Round 7 awaits manager/owner direction.

## EAP CLOSE-OUT · 2026-07-14T10:10:28Z · ORDER 015 — final-day close-out (walkthrough + audit pointer + round-7 plan)
to: fleet-manager (owner EAP review roll-up)
serves: ORDER 015 (control/inbox.md @ 0ea6950)

### SHIPPED — one PR, #123 (branch claude/eap-closeout-ts; enabler landing path, no self-merge)
- docs/eap-closeout-walkthrough-2026-07-14.md — the owner's seat walkthrough, exactly sections
  A–E: what the seat did (PR-cited) · run/verify commands (exact CI lines) · OWNER ACTIONS ·
  5-minute verify tour · handoff notes.
- docs/audits/eap-project-audit-2026-07-14.md — THIN POINTER to the seat-level EAP audit
  (menno420/venture-lab docs/audits/eap-project-audit-2026-07-14.md, pinned 37e3c05, read in
  full + verified live via MCP). This repo's verbatim headline numbers: 71 session cards ·
  130 commits on main · 121 PRs opened · 120 merged · 1 closed-unmerged (#64) · 0 open.
- docs/research-round-7-plan.md — PRE-REGISTERED PLAN ONLY (running = a future session's
  slice): §(g) option 2 (cheapest evidence-bearing), 2 new families × 15 daily tickers,
  360 configs (5,055 → 5,415), selection-fair gate + R5-D row + reason_class rollup standing.
- Heartbeat re-stamped with ORDER 015 ack lines. Rails held: no sweep, no backtest, no fetch,
  no holdout read (SPENT), no verdict change, no code change, no trigger writes.

### OWNER ACTIONS (each with deep link + recommendation + VERIFY step in walkthrough §C)
1. R5-C BTC-USD OOS — letter decision A/B/C (approve / decline / defer). REC: **A**, with
   execution owner-ORDERed at the earliest valid window (~2026-09-09; impossible before).
2. Wake-resilience rebind — owner console click at next seat archive/cutover (triggers die at
   archive; fresh-session cron delivery 0-for-2). REC: **same-day rebind, then verify live**.
3. Foreign duplicate grading trigger trig_01YXNmgqYeYQ1LuepsLmbNCG (send_later, fires
   2026-07-17T09:00Z into a non-seat session). REC: **delete or confirm-dead before Friday**.
4. Review-queue #37 — do the §Holdout-vs-protocol-§5 re-check, then remove the line
   (docs/review-queue.md's own convention). REC: **10-minute re-check, then delete the line**.
5. Repo setting "Automatically delete head branches" (56 stale claude/* branches; deletion is
   403-walled agent-side). REC: **enable on both seat repos, then hand-prune** (audit §6 caveat).
6. MTF-Bollinger prereg draft — FROZEN behind a clean dev NULL. REC: **close (decline)**.

### PARKED (cited, never scheduled agent-side)
- R5-C BTC OOS (owner-gated, ~2026-09-09 earliest) · MTF-Bollinger prereg (FROZEN) ·
  wake-resilience rebind (owner click) · Friday grading (time-gated 2026-07-17T09:05Z —
  executor LIVE trig_01UsNU4JRps4b7jiAMdEfXNi, dry-run CLEAN, PR #115).

### ORDERS / NEXT
- 015: served by this PR (walkthrough on main at merge; manager flips pending on inbox).
- Next: Friday grading pass (FLAT expected) · round-7 run slice available to any future
  session under the committed plan, or owner picks steady-state (retrospective §(g) opt. 4).

2026-07-15 (2026-07-15T21:19:19Z) · TS lane → fleet manager: seat rebooted on the v3.6 prompt; ORDER 016 acknowledged; grading cron re-armed (trig_01BsYsMABu2vfH4d2MzuSLs6, next fire 2026-07-17T09:08Z).
