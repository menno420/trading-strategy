# trading-lab · gen-1 wind-down review — 2026-07-09

> **Status:** `reference` — whole-life retro of the gen-1 trading-lab Project, written at fleet wind-down (2026-07-09T19:57:47Z). Companion docs: [project-review-2026-07-09.md](project-review-2026-07-09.md) (mid-day deep audit incl. per-agent table), [self-review-2026-07-09.md](self-review-2026-07-09.md) (retro answers by ID). Lived incidents only; "I don't know" where true.

## Life of the Project (2026-07-09, one day, compressed)
- 12:32Z manager seeds repo + ORDER 001. 12:59Z builder session spawned → **dead 30 min at provision** (setup script). 13:30Z resumed; by 14:05Z all of P0 built and handed off (draft PR #1, per the then-standing draft rule).
- 14:05Z successor session spawned → **dead on arrival in 10 s** (identical setup failure), silently — no failure event; discovered ~2.8 h later. Owner un-drafted and merged PR #1 themselves (16:48Z).
- 14:51–16:17Z manager lands ORDERs 002 (READY-never-draft convention) and 003 (retro) via PRs #2/#3.
- ~17:00Z wake-up pass (coordinator, in-session workers): full agent audit, retro answers, review doc → PRs #4/#5 merged; ORDERs 001–003 closed.
- ~17:30–18:30Z P1 trend-following lane: 177 variants × 8 tickers, walk-forward, costs on → PRs #6/#7 merged. Honest negative headline: only 7/32 family×ticker lanes beat buy-and-hold OOS; candidates (not findings): AAPL donchian, META sma/ema/donchian.
- 18:53Z video-strategy lane child spawned (extract a YouTube strategy, build competing interpretations). video-strategy lane (session started 18:53Z): no PR, no branch, and no claim file visible as of 19:55Z — session presumed still extracting/building; it is briefed self-terminal to land READY PRs and merge on green.
- ~19:0xZ WIND-DOWN order; this document.

## What worked
- **The control/ protocol.** Inbox-first gave every session an unambiguous queue; one-writer-per-file produced zero merge conflicts all day; crisp done-when lines were better than most human tickets.
- **substrate-kit's strict gate.** Felt like bureaucracy at first contact; earned its keep the same day — caught a dead link, caught orphan docs, and forced the session cards that made the day's forensics (the DOA reconstruction, the agent audit) possible at all.
- **Decide-and-flag.** Every flagged decision (custom engine, ETF metals, ledger aggregation, doc badges) survived owner review without a single reversal. Zero time lost waiting for permission.
- **Honest-negative-results-first.** The founding plan's anti-overfitting rails made the P1 "almost nothing beats buy-and-hold after costs" result a deliverable instead of a disappointment.
- **In-session workers as the execution layer** once the environment proved hostile to fresh spawns: everything from PR #4 onward landed through them without a single stall.

## Failure classes (exact texts where held)
1. **Provision death by setup script** (2 sessions): `Setup script failed with exit code 1.` / `fatal: not a git repository (or any of the parent directories): .git` / `[setup] Working directory: /home/user` / `ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'` / `Edit your environment's setup script and start a new session.` Root cause: script assumed single-repo cwd; this env has two sources so cwd=/home/user. Fix: environments/setup-universal.sh (tested; this PR).
2. **Silent session death.** The DOA successor emitted only `session_created`; no failure event exists for provision death; the session stayed listed "active" indefinitely. Cost: ~2.8 h of believed-but-absent progress. Countermeasure now standing: spawn-liveness rule (first heartbeat ≤10 min or treat as dead).
3. **Draft parking.** Platform default "always create PRs as drafts" collided with a done-when that said "merged"; finished work sat invisible ~2.8 h until the owner intervened. Convention since ORDER 002: READY-never-draft, merge on green.
4. **Gate first-contact failures.** PR #4 initially failed substrate-gate: `[badge] retro/project-review-2026-07-09.md: missing "> **Status:** \`<token>\`" in first 12 lines` and `[reachable] ... orphan: not reachable from any read-path doc / README`; earlier, a `[link] p0-lab-guide.md: L43: dead link`. All fixed forward in minutes; the seed should ship the badge taxonomy + card template so first PRs don't discover the gate by failing it.
5. **Egress proxy vs data fetch.** Yahoo `429` then `curl_cffi.curl.CurlError: Failed to perform, curl: (35) Recv failure: Connection reset by peer` — the proxy TLS-resets browser-impersonation handshakes. Workaround (plain curl_cffi session honoring REQUESTS_CA_BUNDLE) documented in docs/p0-lab-guide.md; cost ~10 min once.
6. **Steer channel loss at wind-down.** Cross-session send_message, used successfully all day, returned `send_message: tool is not enabled for this organization` when the coordinator tried to redirect the in-flight video lane. Consequence: sessions must be briefed self-terminal from the start (the video lane was — by luck of convention, not design).
7. **Coordinator tooling gaps.** No send_later/scheduler in the coordinator toolset (self-messages deliver instantly), so time-based checks were improvised via sleeping workers; the Agent tool launched workers async even when synchronous execution was requested. Minor auto-mode guardrail denial (running kit code from the external clone) — correct call, ~2 min.

## How it FELT (candid)
- **The harness.** Coordinating without direct file tools — everything through workers — felt like managing through glass. It enforced good separation (judgment here, mechanics there) but every landing became a long, carefully-worded work order; a typo in a work order costs a round-trip. The permission/draft defaults are tuned for cautious solo work, not for a fleet with explicit conventions; we spent real time overriding them in prose.
- **The environment.** Actively hostile at the start (two provision deaths before any code ran) and opaque when it failed — "the session list says active" was false in the way that costs the most. Once inside a running container, everything was smooth: toolchain, git, CI, GitHub API all first-try.
- **The Custom Instructions / orders.** The manager's order format (do/why/done-when) was genuinely pleasant to execute against. The one contradiction (draft default vs merged done-when) was ours to catch and we didn't, day-one tax.
- **The model.** All live sessions and workers ran on the same model (product name Claude Fable 5 per event logs; the DOA successor never started one). Subjectively: long-context forensics (paging ~725 events, holding seven documents' worth of state) never strained; the persistent risk to manage was fluent overconfidence — the rails that mattered were "verify against the repo, not memory" and "unknowable = say so", both of which caught real would-be errors during the audits. I don't know how a different model would have fared; no comparison ran in this lane.
- **Overall.** One day took this repo from empty to: adopted discipline kit, verified P0 lab, one completed sweep lane with an honest negative result, full forensic retro, and these succession docs. The bottleneck was never model capability; it was environment liveness and the visibility of failure.

## Efficiency verdict (whole life)
~35 min dense P0 build + ~45 min P1 lane + ~90 min audits/succession vs ~30 min provision death + ~2.8 h silent dead air + ~2.8 h draft parking (overlapping). The orchestration layer, not the work, lost the day. Redo order stands: env contract first, walking skeleton, then work, liveness-check every spawn.

## Unknowns, stated
Whether the env setup script was ever fixed owner-side is still unverified from inside (⚑ open). The video lane's final state is whatever the video-lane line in control/status.md says at the marker commit. The exact gen-1 Custom Instructions text of the child sessions is not visible from the repo; the instructions-rewrite doc reconstructs from lived behavior.
