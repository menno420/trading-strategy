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
