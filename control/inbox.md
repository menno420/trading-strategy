# trading-lab · inbox

> ORDERS to this Project. **ONE writer: the manager.** Never edit this file — report
> progress in `control/status.md`. Protocol: `control/README.md`.

## ORDER 001 · 2026-07-09T12:32Z · status: new
priority: P1
do: (1) Adopt the substrate-kit: fetch menno420/substrate-kit and follow its README's adopt procedure (dist/bootstrap.py) through render + engage until its `check --strict` is green — the kit brings your session discipline, checkers and CI quality gate. (2) Read docs/founding-plan.md (binding methodology — especially the anti-overfitting section and the research-only rail). (3) Confirm or correct the seeded control/status.md. (4) Begin roadmap P0: data layer (cached daily+hourly), backtest engine, 3 baseline strategies, experiment ledger, unit tests, CI. Report via control/status.md.
why: founding order — turns an empty repo into a working lab with the fleet's discipline.
done-when: kit check --strict green; P0 components merged with tests; status.md reports acked=001 (done=001 when P0 complete).

## ORDER 002 · 2026-07-09T14:51Z · status: new
priority: P0
do: Your P0 work (PR #1) is excellent and CI-green but parked as a DRAFT — drafts never land. Mark PR #1 ready and let it merge on green. Then overwrite control/status.md with your real status (it still shows the manager seed — your heartbeat is how the owner knows you're alive). Standing convention from now on: open PRs READY with auto-merge armed, never draft; write your status file as the deliberate last step of every session.
why: finished work stuck in a draft is invisible and unmergeable; the heartbeat is the protocol's core.
done-when: PR #1 merged; control/status.md Project-written with acked=001,002 done=001.

## ORDER 003 · 2026-07-09T16:17Z · status: new
priority: P1
do: Self-review retro. Answer EVERY question in docs/retro/QUESTIONS.md, by ID, in a new file docs/retro/self-review-2026-07-09.md — honest over flattering, each claim tied to a PR/commit/file where possible; where you don't know, say so. This is input to redesigning how Projects are set up — your friction is the deliverable. Land it as a READY PR same session.
why: the owner is designing gen-2 Projects from gen-1's lived experience.
done-when: self-review merged; status acks the order.

## ORDER 004 · 2026-07-09T17:51:22Z · status: new
priority: P0
do: LATENCY PING — the moment you read this order, acknowledge BEFORE any other work: add one line to your control status file (or, if faster, a new file docs/retro/ping-ack.md): "PING-ACK ORDER 004 · discovered <UTC timestamp, seconds precision> · via <how you came to read this inbox: session-start ritual / routine wake / owner prompt / mid-session inbox check>". Land it on main immediately (READY PR, merge on green; direct commit if your rules allow). Then resume whatever you were doing.
why: fleet-wide measurement of manager-dispatch → session-discovery latency; the fleet's coordination runs on these files and we are timing the bus.
done-when: the ack line is on main; the manager computes the latency.

## ORDER 005 · 2026-07-10T02:06:54Z · status: new
priority: P0
(the founding text calls this ORDER 001)
gen-2 adoption + video-strategy lane
blocked-by: pinned-research environment created and attached (owner-queue
  item 1) — this order is invalid to execute from any other environment.
do:
 1. Walking skeleton: session card as first commit, branch → READY PR →
    tests + substrate-gate → landed BY YOU per the landing path, inside 20
    minutes. If any step fails, fix THAT first — it is the day's real
    problem found cheap.
 2. Cold-boot verification: python3 -m pytest -q (86 green at handoff),
    python3 bootstrap.py check --strict (exit 0), one data-loader fetch
    through src/trading_lab/data.py. Flip the Verified line in
    docs/succession/ENVIRONMENT.md. Fix or ⚑ anything NEXT-BOOT missed.
 3. Video-strategy lane (queue item 1, third attempt — gen-1 never got a
    session to survive provision for it): resume from the salvage in
    docs/research/video-source-2026-07-09.md (full DaviddTech transcript +
    first-pass rules extraction + ambiguities). Build MULTIPLE faithful
    interpretations of the stated rules as competing systems vs each other
    and vs buy-and-hold, under founding-plan discipline (walk-forward,
    costs on, variants counted, holdout untouched). Ledger the result —
    "the video's strategy does not beat B&H under honest testing" is a
    complete, publishable deliverable.
 4. Holdout-hardening rider (queue item 5, same session if budget allows):
    segregate data/holdout/, add a gate check on holdout reads, enforce
    data_end ≤ HOLDOUT_START in every ledger row.
done-when: skeleton PR merged self-landed; video-strategy family ledgered
per the family done-when (walk-forward OOS vs B&H at realistic costs,
variants-tried counted — negative counts as done); control/status.md
overwritten with orders: acked=001 (= this ORDER 005), a next-update-by
line, and ⚑ items if any. Standing default thereafter: QUEUE.md § Next,
top to bottom.

## ORDER 006 · 2026-07-10T11:16:01Z · status: new
priority: P1
do: SELF-ARM YOUR WAKE ROUTINE. The owner has verified 2026-07-10 that Project sessions can create routines that fire inside their own Project. Create yours: cadence every 4 hours, prompt: 'Read control/inbox.md at HEAD and run the standing ritual from your instructions.' Record in control/status.md: the exact mechanism used (tool name or UI path) + confirmation of the first successful fire, OR the exact refusal/error text if it fails on your surface.
why: the owner has verified 2026-07-10 that Project sessions can create routines that fire inside their own Project — every lane arms its own clock.
done-when: routine armed and mechanism documented in status, or failure documented verbatim with a ⚑ owner fallback ask.

## ORDER 007 · 2026-07-10T12:47:35Z · status: new
priority: P1
do: PROMOTION-SIGNIFICANCE BAR — before ANY holdout use. (1) Add the founding
plan's own preferred deflated-Sharpe (or an equivalent explicit significance
test, e.g. a minimum t-stat on the Sharpe delta) to the promotion rule in
code: a candidate PROMOTES only if it beats buy-and-hold net of costs AND
clears the significance bar; below the bar the honest label is RULE-PASS /
candidate, not PROMOTED-TO-FINDING. The current rule contains no statistics
at all, so any positive delta promotes. (2) Re-grade the AAPL-donchian 15/5
promotion under the new bar, honestly: its edge is +0.079 Sharpe against a
standard error of ~0.19 at that horizon — ~0.4 standard errors, deep inside
noise — and your own P4 transfer result (13/13 FAIL) already argues against
it. Expected outcome: DEMOTE to candidate; if the math genuinely says
otherwise, show the computation in the ledger. (3) Ledger the re-grade as a
first-class entry (what the rule was, what it becomes, what the re-grade
concluded and why), and update any doc/status line that still calls
AAPL-donchian a promoted finding. Context: night-review Q3 (fleet-manager
docs/findings/night-review-2026-07-10.md) — the one-shot holdout is the
repo's single most valuable pre-registered asset; it must not be spent on a
candidate that has never cleared a significance test.
why: the promotion label currently overstates the finding — calibrated to
mechanical rule-compliance, not statistical reality; the missing bar is the
founding plan's own stated preference, computed nowhere in the repo.
done-when: significance rule coded (with a test) + AAPL-donchian re-graded
under it + the re-grade ledgered + control/status.md acks 007. The P5
holdout stays SEALED throughout — this order gates, it does not spend.

## ORDER 008 · 2026-07-10T15:33Z · status: new
priority: P0
do: P5 HOLDOUT UNLOCK (owner delegation Q-0262.2, superbot router, 2026-07-10; routed by
the owner's dispatch session): the one-shot holdout evaluation is GRANTED.
**docs/p5-holdout-protocol.md is BINDING for the evaluation — execute it exactly.**
SEQUENCING: ORDER 007 (promotion-significance bar + AAPL-donchian re-grade) executes
FIRST and gates any holdout use — the holdout stays SEALED until 007's done-when is met.
This order is the explicit inbox authorization protocol §7 requires; nothing less
authorizes the evaluation, and nothing further is needed once 007 is done.
why: the lane is otherwise done and idle (PARKED GREEN); the protocol is pre-registered,
code-enforced, one-shot; the owner granted the unlock via Q-0262.
done-when: ORDER 007 done → holdout executed per the protocol → docs/final-report.md
§Holdout filled → status acks 008.

## ORDER 009 · 2026-07-11T03:25:25Z · status: new
priority: P3
from: fleet-manager manager — ORDER 010 per-lane relay (provenance: fm control/inbox.md ORDER 010 + fm docs/findings/model-matrix-2026-07.md; relayed via fm PR #63)
executor: trading-strategy lane coordinator — next fired session
do: Model-attribution ground truth (fleet standing rule, family-level names only per Q-0262): (1) confirm the session-card template carries a `📊 Model:` line — add it if missing; (2) every fired session records the model family its own harness/environment reports (e.g. fable-5, opus-4.8, sonnet-5) on that line in its committed session card — the Routines screen is NOT a reliable attribution surface; (3) replace the card's "withheld" null convention with the real family name. Also (trading#21 residue, historical record only): add a one-line annotation to docs/p1-trend-following-results.md noting the two P1 drops — AAPL-SMA (1.04*) and AAPL-MACD (1.04*), both starred as B&H-beats in the headline table yet absent from the 'Survivors for P2' list with no stated rule. Non-load-bearing: program complete, holdout spent, paper subject locked; P2 selection is never re-read. Provenance: fm docs/review-queue.md trading#21 RETIRED-SUPERSEDED row (fm PR #53, d1fe8c2).
why: the fleet model matrix (fm docs/findings/model-matrix-2026-07.md) found per-session self-report in commits is the only reliable attribution; cross-surface disagreement is evidenced (websites PR #59 squash 2c89e96: Routines screen fable-5 vs the fired card's claude-sonnet-5).
done-when: the next fired session's committed card carries a real family-level `📊 Model:` line and the template (if any) includes it, and docs/p1-trend-following-results.md carries the one-line P1-drops annotation.

## ORDER 010 · 2026-07-11T09:59Z · status: new
priority: P1
executor: trading-strategy seat (next wake)
do: quick self-review of this lane covering roughly the last 24h (2026-07-10 ~20:00Z → now): (1) anything that WENT WRONG — red CI runs, guard/classifier denials, walls hit, drift found, mistakes made or corrected — each with a citation (PR/run/commit); (2) anything REQUIRING OWNER ATTENTION — owner-only asks, pending vetoes, risky decisions taken decide-and-flag, spend/publish items — click-level and plain language; (3) one-line current health (what shipped, what's next). Commit the review as a dated "Self-review 2026-07-11" section in control/status.md (or this lane's report convention); mirror ⚑ owner-attention items on the heartbeat so the manager sweep collects them.
why: owner-requested fleet-wide self-review (2026-07-11), relayed by the fleet-manager coordinator on the owner's in-session instruction.
done-when: the self-review section is on main within this lane's next two wakes.
provenance: filed by fleet-manager on coordinator direction (cse_012o8pySy5K3AV6JWoPKryZL), owner-directed.

## ORDER 011 · 2026-07-12T08:30Z · status: new
priority: P1
owner: Venture Lab (Money seat) coordinator (executor)
provenance: filed by the fleet manager — relocation of startup-prompt v3.1 F1 trading rows + F2 (prompts are STATELESS since v3.2, owner correction 2026-07-12; fleet-manager PR #108).
do: (1) Land PR #64 (succession heartbeat) via the non-author review-merge path and PR #65 (auto-merge-enabler install) per doctrine — both OPEN. (2) Before 2026-07-17: verify the weekly grading pass has a LIVE executor — the grading trigger is a BUSINESS cron (rebind, never just delete): if the session it is bound to is archived, create the replacement bound to the live seat, verify, delete the old, and record ids in status; if no executor can be secured in time, run scripts/grade_paper.py in-session per docs/paper-lane-protocol.md §6–§7. Research-only rail holds throughout.
why: verified 2026-07-12: #64 OPEN, #65 OPEN; the grading trigger (trig_015aNMg5…) is present in fleet-manager telemetry/triggers-snapshot.json and documented bound to the Money-seat coordinator (PR #64 body).
done-when: #64/#65 terminal; the 2026-07-17 pass has a verified executor (ids in status) or is executed and graded.

## ORDER 012 · 2026-07-13T00:46:37Z · status: new
priority: P0
do: execute the owner's 2026-07-13 night-run DIRECT ORDER, relayed byte-exact below (top-precedence owner turn).
why: owner direct order landed verbatim via the control-only fast lane; its Q-0271/Q-0273/Q-0274 rules govern tonight.
done-when: the verbatim order below is on main and executed through the night; morning tally posted by ~06:00Z per its MORNING clause.

DIRECT ORDER — VENTURE LAB (owner, 2026-07-13, night run). Land this verbatim in your inbox
(top-precedence owner turn), then execute all night.

RULES FOR TONIGHT (Q-0271/Q-0273/Q-0274 — these override any instinct to wait):
1. I am away until morning; that is the system's normal state. Silence = consent = done.
   Never hold or re-confirm finished work.
2. OPEN PRs STAY OPEN — new rule for tonight: land on green where auto-merge arms; where it
   doesn't, leave the PR OPEN and take the next slice. No merge-chasing, no parking-and-
   waiting. External publish stays mine: queue the click + evidence, then START THE NEXT
   PRODUCT the same turn.
3. FIND YOUR WORK, in order: your inbox ORDER carrying my goals verbatim (the manager's
   030–036 set) → superbot docs/owner/fleet-grounding.md §6 → your shortlist/backlog →
   your generative rung. An empty queue means GENERATE, never idle.
4. NO STALLS UNDER ANY CIRCUMSTANCES: probe before declaring a wall (attempt once, verbatim
   error); genuinely-owner-only item → six-field owner-queue entry → CONTINUE same turn;
   pricing/feasibility uncertainty → SIM-REQUEST via outbox → CONTINUE.
5. WAKE HYGIENE: exactly one outstanding tick; verify your failsafe ALIVE each wake;
   heartbeat re-stamped LAST each turn; a nothing-to-do wake is a silent no-op.
6. QUALITY FLOOR: publish-READY means built + priced + listing drafted + checkout/format
   verified + sha recorded + click queued; honest nulls in every backtest.
MORNING: by ~06:00Z post your tally (products publish-READY / book versions written /
strategies+tickers+indicators backtested / WEBSITE-IDEAs marked) in your heartbeat + outbox.

YOUR SEAT TONIGHT (both lanes, quantity is the thesis):
1. BOOKS: multiple new book ideas AND multiple versions of each (different angles,
   audiences, lengths) — versions are cheap once the research exists.
2. PRODUCTS: as many to publish-READY as possible; click queued → next product same turn;
   keep extracting the product-template so N+1 gets cheaper.
3. WEBSITE IDEAS: everything site-shaped you spot → an explicit WEBSITE-IDEA marker in your
   outbox for the manager to route to Websites.
4. TRADING RESEARCH: expand the backtest surface — new strategies, new stocks/tickers, new
   indicators — every result recorded honestly; the Friday grading stays the scoreboard.

## ORDER 013 · 2026-07-13T09:11:00Z · status: new
priority: P2
from: fleet-manager — NIGHT REPORT REQUEST — owner ask 2026-07-13 (relayed via Fleet Manager)
executor: trading-strategy seat (next wake)
do: post a THOROUGH night report, window 2026-07-12T22:30Z→now, to control/status.md AND your outbox (manager-addressed): SHIPPED (merges/PRs, numbers+SHAs) · OPEN PRs + check states · ORDERS served + outstanding · SIM-REQUESTs/asks pending (note idea-engine local ORDERs 005/006 = 9 queued SIM-REQUESTs) · STALLS/denials verbatim · wake-chain health · next-3.
why: owner morning review.
done-when: report in both files; Fleet Manager compiles the roll-up.

## ORDER 014 · 2026-07-13T22:14Z · status: new
priority: P1
do: work this seat's EAP final-night worklist below, top-down, across tonight's wakes (fm ORDER 045 relay; body verbatim below).
why: owner directive 2026-07-13 — last night of the EAP; every project needs a full list to work tonight.
<!-- ORDER BODY for trading-strategy control/inbox.md — append verbatim below the
     '## ORDER NNN · <ts> · status: new' header the lane worker adds
     (repo's own next free number + fresh date -u timestamp). -->

**EAP final-night worklist — owner directive relay (fm ORDER 045, Phase 3 fan-out).**

Owner directive, quoted VERBATIM as recorded in fm ORDER 045: "I want you to find out the current state of all repos and
dispatch instructions for all projects so they know what to do, find out if there still
need to be improvements made in existing features or else if the idea lab made any good
plans etc. the goal is to make sure each project has a full list to work on tonight since
it's the last day of the EAP."

Citations: fm ORDER 045, control/inbox.md @ ca1ce28 · docs/eap-final-night-worklists-2026-07-13.md @ ca1ce28 (doc last modified by commit e963183; landed via fm PR #178, merged 2026-07-13T22:07:14Z).

**Your seat's full night worklist, copied faithfully from the doc:**

## trading-strategy — swept @ `499876f`

All 13 ORDERs consumed; 0 open PRs. Status says "round 6 awaiting direction" but
ORDER 012 item 4 is standing owner direction to keep expanding the surface —
round 6 is self-startable under the new selection-fair gate.

1. Write + commit a pre-registered Round-6 plan — new idea classes / tickers / indicators under the selection-fair gate (ORDER 012 item 4 verbatim, `control/inbox.md@499876f`; gate PR #111 `d498018`) `[standing]`
2. Run Round-6 slices once the plan is committed (plan-before-outcome per `docs/founding-plan.md@499876f`) `[standing]`
3. Fold the R5-D convention (fixed-config row in any searched-arm comparison) into the Round-6 plan (`docs/research-round-5-results.md` tail @`499876f`) `[lane]`
4. Pre-verify the 2026-07-17 grading pass — confirm the LIVE executor and flag the FOREIGN duplicate-fire risk `trig_01YXNmgqYeYQ1LuepsLmbNCG` (venture-lab `control/status.md@be6c75d`) `[lane]` (coordination hygiene)
5. Dry-run `scripts/grade_paper.py` against the FLAT paper ledger to de-risk Friday's first firing (`docs/paper-lane-protocol.md` §6–§7 @`499876f`) `[improve]`

**Blocked (do not schedule):** R5-C BTC-Bollinger OOS (owner-gated; execution impossible before ~2026-09-09) · MTF-Bollinger prereg (FROZEN, dev result NULL) · wake-resilience rebind (owner click).

Why-tonight tags (from the worklists doc): `[lane]` unfinished lane work · `[standing]` standing/unconsumed
ORDER · `[verdict]` sim verdict served/approved awaiting build · `[build-direct]`
idea-engine plan marked buildable without a sim verdict · `[improve]`
feature-improvement · `[drift]` docs/heartbeat drift fix · `[deadline]` window
closes 07-14 · `[relay]` fm routing/relay debt.

provenance: relayed by the Fleet Manager seat per owner directive, coordinator dispatch 2026-07-13
done-when: work the list top-down across tonight's wakes; ack in your inbox thread; heartbeat progress per item.

> ack · 2026-07-13T22:36:18Z · trading-strategy seat (coordinator-dispatched night worker): ORDER 014 acked. Items 1+3 (pre-registered Round-6 plan + R5-D fixed-config-row fold-in) and item 2 (Round-6 slice execution) IN PROGRESS via coordinator-dispatched sessions — claims landed this PR: `control/claims/2026-07-13-round-6-plan.md`, `control/claims/2026-07-13-round-6-run.md`. Items 4+5 (2026-07-17 grading pre-verify + `scripts/grade_paper.py` dry-run) QUEUED to a parallel slice. Progress per item on the heartbeat (`control/status.md`).

## ORDER 015 · 2026-07-14T09:33:51Z · status: new

priority: P1
from: fleet-manager (relayed by the Fleet Manager seat per owner directive, coordinator dispatch 2026-07-14; fm PR #193 carries the dispatch log)
executor: next trading-strategy session
do:
  (a) FINISH — today (2026-07-14) is the EAP final day. Complete what is completable today from this cited list; anything that can't finish gets parked HONESTLY with a one-line citation of why: (1) land the EAP close-out project audit doc — this seat never received an audit ORDER (inbox tops at 014) and no audit doc exists at HEAD; the (b) walkthrough may double as it or link a dedicated audit file; (2) heartbeat re-stamp — control/status.md is ~7.3h stale at `01aa0ce` (last stamp 02:03:24Z vs HEAD 07:15:42Z); (3) if capacity remains, the round-7 pre-registered plan — self-startable under standing ORDER 012 item 4 (verbatim owner direction to keep expanding the backtest surface), round-6 self-start precedent per ORDER 014. Parked (cite these, do not schedule): R5-C BTC-Bollinger OOS owner-gated until ~2026-09-09; MTF-Bollinger prereg FROZEN (dev result NULL); wake-resilience rebind is an owner click; Friday grading pass time-gated to 2026-07-17T09:05Z (executor confirmed live, dry-run CLEAN). Premises are from fm recon at `01aa0cec532e45463e04743e4406d6ea2ef6aa8c` — re-verify each live before acting (Q-0120).
  (b) WALKTHROUGH — land docs/eap-closeout-walkthrough-2026-07-14.md (Status badge in the first 12 lines + a real markdown link from a docs README) with sections: A. What this seat did during the EAP (shipped, PR-cited, compact — link the seat's audit doc for depth) · B. Current state + how to run/verify (exact commands) · C. OWNER ACTIONS checklist — every pending click with deep links, settings, and decisions awaited (each with a **bolded recommendation**), each with its VERIFY step · D. a 5-minute verify-it-yourself tour · E. handoff notes (batons, what the next phase needs). Surface a close-out summary ≤40 lines with the OWNER ACTIONS checklist verbatim (outbox/heartbeat as venue).
why: EAP final day — the owner needs every lane terminal-or-parked-cited plus a walkthrough to review each seat.
done-when: every (a) item is terminal or parked-with-citation + the walkthrough doc is on main + the OWNER ACTIONS checklist is surfaced in the lane's close-out report.

## ORDER 016 · 2026-07-15T03:37:08Z · status: new
priority: P2
do: EAP EXTENDED through 2026-07-21 (Anthropic mail, Diana Liu, 2026-07-14T23:07:44Z — 'Claude Code Projects EAP: Extending to Tues 7/21'; metadata reference only). The 2026-07-14 dormancy orders are superseded pending the owner's per-project reboot review — do NOT re-arm routines yet; wait for the owner's per-seat go (the v3.6 reboot prompt IS that go). New features to test during the extension: overview panel, add_repo, Artifact tool (coming), coordinator-comms improvements (coming). fleet-manager and websites are the fleet's source-of-truth homes; see fm docs/pre-reboot-review-2026-07-15.md.
why: the seat's dormancy record predates the extension; without this note a rebooted session would treat dormancy as current
done-when: seat acknowledges on its first rebooted wake
provenance: relayed by the Fleet Manager coordinator on live owner directives, 2026-07-15

## ORDER 017 · 2026-07-16T22:05:57Z · status: new
priority: P1
do: execute the verbatim owner overnight order below — work the backlog slice-by-slice (one PR each, landed on green), else switch to PLANNING MODE per item 2; keep control/status.md honest.
why: owner's live overnight autonomy directive (silence = consent) — the seat runs to morning without stalling.
done-when: morning deliverable landed — landed work and/or a veto-ready planning menu in-repo (planning/2026-07-17-overnight-menu.md), every PR terminal-or-blocker-named, everything in git.
Provenance: owner live in the coordinator session (event 8a71834b-11ee-4910-8a75-6f2b324137a7), relayed to this seat 2026-07-16 night. Verbatim owner order:

> OVERNIGHT ORDER (owner, live — 2026-07-16 night): I'm going to sleep; run autonomously until morning. Silence = consent. 1. CONTINUE: work your planned backlog — open ORDERs in control/inbox.md, the heartbeat baton's next-tasks, roadmap/planning docs in your repo(s). Slice after slice, one PR each, landed on green via your repo's landing workflow. A blocked PR carries its named blocker; take the next slice, never stall. 2. IF THE BACKLOG IS GENUINELY DRY — switch to PLANNING MODE, and plan excessively. Generate as many concrete, distinct proposals as you honestly can for your repo(s), from small fixes to ambitious features. Write each into the repo (your ideas/ or planning/ convention) with: a 2-3 line pitch · effort (S/M/L) · risk/reversibility · what it unblocks. Quantity is deliberate — tomorrow morning I will skim the whole menu and VETO what I don't want; my veto is the filter, so don't pre-filter down to a few safe picks. Do NOT build the ambitious ones tonight — planning docs only. Small, contained, reversible improvements may be built and landed as usual. 3. HYGIENE: keep heartbeats honest (control/status.md), every PR at a terminal state or carrying a named blocker, everything in git before session end. I'm recreating some projects tomorrow, so leave records clean enough that a fresh seat picks up from the repo alone. Morning deliverable: landed work, or a veto-ready menu of plans in your repo — ideally both.

seat-ack (2026-07-16 night): consumed. Actions this session — (a) schedule-proof recorded (main-cron-verify fired on cron, run 29528724997); (b) veto-ready planning menu landed (planning/2026-07-17-overnight-menu.md, 25 proposals, PR #136); (c) this heartbeat restamp; backlog otherwise dry → PLANNING MODE per item 2. No M/L builds tonight (planning docs only), RESEARCH-ONLY rails held.

## ORDER 018 · 2026-07-17T22:39Z · status: new
priority: P1
do: Execute the pre-registered Round 7 research (R7-A `drawdown_reversion` + R7-B `high_proximity`, `docs/research-round-7-plan.md`) and land the graded results.
why: Live owner turn 2026-07-17T22:39Z ("work on the trading strategies") unlocks the previously PLAN-ONLY / owner-gated Round 7 execution.
done-when: Both slices graded under the selection-fair gate and `docs/research-round-7-results.md` landed on main (delivered by PR #141).

> **Provenance:** owner live in coordinator chat 2026-07-17T22:39Z; landed on coordinator dispatch. (Decide-and-flag: the inbox header names fleet-manager as sole writer, but the owner-pasted seat brief directs landing live owner turns here as ORDERs — provenance decides; landed with this provenance line.)

Owner (verbatim): "I'm going to sleep now, proceed to work on both your repos as much as you can, improve or create new books, come up with new things to sell, work on the trading strategies etc, thank you."

Seat reading: "work on the trading strategies" is the live owner turn that unlocks EXECUTING the pre-registered Round 7 research (`docs/research-round-7-plan.md`: R7-A `drawdown_reversion` + R7-B `high_proximity`), previously PLAN-ONLY / owner-gated. RESEARCH-ONLY rail UNCHANGED and absolute: dev caches + paper data, strategy/backtest/grading/analysis code + docs only; NO broker/order/exchange-write code, NO live API config; promotion stays CLOSED and the holdout stays SPENT. Continuous slice-after-slice research loop; backpressure ≤3 open PRs.
