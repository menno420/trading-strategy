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
