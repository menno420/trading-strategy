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
