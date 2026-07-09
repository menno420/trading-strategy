# trading-lab · gen-1 self-review — 2026-07-09

> **Status:** answers to [QUESTIONS.md](QUESTIONS.md) per ORDER 003. Written by the project coordinator session on behalf of gen-1 (builder session, DOA successor, coordinator + subagents). Evidence: PRs #1–#3, commits on `main`, and the platform event log (session transcripts audited 2026-07-09). Honest > flattering; "I don't know" where true.

## A. Work & correctness

**A1.** Everything gen-1 built is on `main` (tip `4067bbb`): full P0 via PR #1 (merged 16:48Z), plus the manager-lane plants (PRs #2, #3). Nothing exists only on branches — `git ls-remote` shows only `main`; all three PR head branches merged and deleted. The gap that DID exist: PR #1 sat as a **draft** for ~2.8h (opened ~14:03Z, merged 16:48Z) because the builder was instructed to open drafts and the successor meant to un-draft it died at provision. Reconstruction in G1.

**A2.** Verified against external oracles: (1) GitHub Actions CI (`tests`, `substrate-gate`) green on the `main` tip; (2) live Yahoo Finance fetches built the cached dataset (the 429s and TLS resets were real-world contact, not mocks); (3) this review re-ran `python3 -m pytest -q` (63 passed) and `python3 bootstrap.py check --strict` (exit 0) on a fresh detached checkout of `main`. Verified ONLY by our own tests: the backtest engine's economic correctness (fills, costs, no-lookahead) — no reference-engine goldens exist. See A3.

**A3.** Least confident: backtest-engine correctness vs an independent implementation. Concrete check: reproduce 2–3 of the 24 seeded runs in a reference engine (e.g. vectorbt) under identical cost/fill assumptions and compare equity curves; divergence beyond ~1bp/day indicates a bug. Second: benign-ness of hourly-data adjustment quirks (documented in docs/p0-lab-guide.md, not proven) — re-fetch a sample and diff against cache.

**A4.** Nothing large was wasted. Minor: the walk-forward helper landed in P0 though it is P1 tooling (cheap, but premature); the root `requirements.txt` exists chiefly to feed the environment's setup script and partially duplicates dependency metadata (kept — it is also CI's install source).

## B. Errors & friction

**B1.** Every error, time lost, preventability:
1. **Env setup-script failure at builder provision (13:00:01Z)** — `fatal: not a git repository` + missing `/home/user/requirements.txt`; session dead **30.2 min** until externally resumed at 13:30. Preventable by setup: the script assumed a single-repo cwd; a two-source environment starts at `/home/user` with repos as subdirectories.
2. **Identical failure killed the successor session (14:05:17Z)**, 10s after spawn, 0 turns run — and silently: the project received a `session_created` event but no failure event, so the death went unnoticed **~2.8h**. Preventable by: setup (script fix not yet effective), platform (no provision-failure signal), and our own process (no spawn-liveness check — now a standing rule).
3. **Yahoo 429 + `curl: (35) Recv failure: Connection reset by peer`** (13:44–13:45): the egress proxy TLS-resets yfinance's browser-impersonation handshake. ~10 min; genuinely external; worked around with a plain curl_cffi session honoring `REQUESTS_CA_BUNDLE` (documented in docs/p0-lab-guide.md).
4. **Auto-mode permission denial (13:32)**: recon subagent blocked from executing `bootstrap.py` out of the externally-cloned kit ("asked only to read, not run"). ~2 min; the guardrail was arguably correct; Phase A ran it inside the target repo without issue.
5. **`check --strict` exit 1 (14:00)**: one dead link in p0-lab-guide.md; fixed in minutes; ours, trivial.
6. One write-before-read tool error (13:57), self-recovered in seconds.

**B2.** The setup-script/multi-source-cwd contract was undocumented anywhere we could see. It should live (1) inline in the environment's setup-script editor, and (2) in docs/AGENT_ORIENTATION.md. Smaller: the strict-check entrypoint (`bootstrap.py` vendored at repo root) was only findable via the kit's README; a one-line pointer in control/README.md would have saved the detour.

**B3.** Silent breakage: the successor's death is the case study — no error reached any watcher; the session list showed "active" throughout; discovered only when this review compared `last_activity_at` (14:05:17Z) against expectations ~2.8h later. Smaller: PR #1 sat draft-invisible; nothing alerts on "finished work parked in a draft" — the manager noticed by looking (ORDER 002).

**B4.** The direct collision: the coordinator's platform rules say "After pushing your changes, ALWAYS create a pull request… **Create the pull request as a draft.**" while ORDER 001's done-when says "**P0 components merged** with tests" — a draft cannot merge, so the order was unsatisfiable by the actor executing it as briefed. ORDER 002 later established the fleet convention ("open PRs READY with auto-merge armed, never draft"), which now wins.

## C. Efficiency

**C1.** Builder session, gross window 12:59–14:05: orientation/reading ~15% (recon 13:30–13:35), building ~55% (Phase A 13:35–13:42, Phase B 13:43–14:01), verifying ~15% (interleaved), CI/merge mechanics ~10% (push/PR/handoff 14:02–14:05), **blocked/waiting: the 30-min provision stall = ~46% of gross wall-clock**. Biggest sink by far: the two setup-script failures (30 min direct + the successor's ~2.8h dead mission window).

**C2.** Rebuilt context that should have been durable: (1) the recon subagent re-derived repo/order/toolchain state the coordinator already held — a richer committed state snapshot would have cut it; (2) this review re-paged ~725 transcript events to reconstruct the day — the kit's session log existed but was too thin to answer "what stalled, when, why".

**C3.** Most value/minute: `check --strict` (seconds; caught a real dead link, enforced the session log) and the 63-test offline suite (0.3s; instant verification). Least: producing 24 seeded baseline ledger runs whose outcome was expected (baselines lose to buy-and-hold at realistic costs) — right to have, lowest insight density.

**C4.** Redo estimate: ~35–40% faster gross. Biggest ORDERING change: land a walking skeleton to `main` through the full branch→PR→CI→merge path in the first 20 minutes, THEN build P0 on top. Gen-1 built 9 commits/112 files on one branch, so nothing was mergeable until everything was.

## D. Autonomy & owner input

**D1.** Human-input stops: (1) the 30-min provision stall — owner-only under the current platform (agents cannot edit environment config); removed permanently by a defensive setup script (owner action, once). (2) The draft→ready flip — not owner-only in principle (agents can mark ready via API); made owner-work by our own draft instruction. (3) PR #1's merge — performed by menno420; agents can merge here, so this was unblockable — the agent tasked with it was dead.

**D2.** Should have been decide-and-flag: opening PR #1 READY despite the draft default (the done-when required a merge; flag the deviation, do it). Also the coordinator waited for an explicit "continue with a new agent" instead of respawning immediately once the env fix was reported.

**D3.** Taken while unsure: (1) custom vectorized engine over vectorbt/backtesting.py (flagged; a written "build-vs-buy: buy unless a named capability is missing" rule would settle it); (2) ledgering negative results without asking (right; rule: "negative results are first-class deliverables"); (3) this review being executed by the coordinator rather than a fresh repo session — unambiguous only because the owner said "do all of this in THIS session".

**D4.** Smallest standing-grant set for zero-human end-to-end: (1) a defensive env setup script (or none — deps install per-repo in-session); (2) the READY+auto-merge convention (now standing); (3) repo merge settings that let agents merge on green (verify once); (4) a coordinator-side spawn-liveness rule (first heartbeat within 10 min or respawn); (5) the egress-proxy data-fetch pattern documented (done). With these five, gen-1's whole day needed zero owner touches beyond writing orders.

**D5.** done-when lines were crisp for all three orders. Where "done" wobbled: ORDER 001's "merged" was unreachable by an actor briefed to open a draft; and no order defined done for the *coordinator* ("successor alive and confirmed" was nobody's acceptance test — exactly the gap that hid the DOA session).

## E. Protocol & environment

**E1.** The control/ ritual fits agent work well — inbox-first gives an unambiguous queue; one-writer-per-file prevented conflicts in practice. Costs: (1) status-last means a session dying mid-flight leaves a stale heartbeat that reads healthy — `health: green` sat on `main` for ~3h while the successor was dead; the heartbeat needs a freshness contract (a `next-update-by` field). (2) Minor duplication between the final status write and the wrap-up handoff message. Nothing was skipped.

**E2.** The environment at first boot should have had: a setup script that exits 0 on a bare two-source checkout (the killer); Python deps preinstalled or a per-repo bootstrap convention; a note on the egress proxy's TLS behavior toward browser-impersonation HTTP clients.

**E3.** The repo at seed should have had: CI workflows from day zero (even no-op) so PR #1 exercises the merge path; a pre-created `claims/` directory with README (the founding plan describes lane claims but no path exists — parallel P1 sessions would each invent one, causing exactly the divergence claims prevent); an experiments/ ledger schema doc; a PR template encoding "READY, never draft; auto-merge on green".

**E4.** A fresh session would first misunderstand **who does what to a PR and when** — the ready/auto-merge convention and the owner/manager/coordinator/session roles live in order prose and chat, not the repo. Single preventing document: docs/collaboration-model.md extended with a "PR lifecycle: who marks ready, who merges, when" table + the standing conventions. (Porting them there is in this review's continuation list.)

## F. Redesign (the payload)

**F1.** Three rules for gen-2 founding instructions:
1. "Open every PR READY with auto-merge armed. Drafts are forbidden — 'not mergeable yet' means a failing check or a ⚑ flag, never a draft."
2. "Any session you spawn must prove liveness (first heartbeat within 10 minutes) or you treat it as dead and respawn. Never assume a spawn succeeded."
3. "Before building anything, land a walking skeleton to main through the full branch→PR→CI→merge path in the first 20 minutes — if the path is broken, find out while it's cheap."

**F2.** The manager's orders were well-formed (crisp done-when, pointers to committed docs — better than most human tickets). Two deltas: (1) the READY-PR convention arrived as a correction (ORDER 002, 14:51Z) after the draft was already parked — it belongs in founding instructions; (2) the manager assumed a live session when filing ORDERs 002/003 — a "status stale >2h ⇒ treat the Project as dark and check the fleet" manager rule would have caught the DOA successor hours earlier.

**F3.** One capability worth almost anything: **visibility into why a sibling/spawned session died** — provision failures surfaced as events to the project. Everything else we routed around.

**F4.** Ideal gen-2 seed state (≤10 bullets): (1) setup script tested against a bare multi-source checkout, or no setup script at all; (2) CI + auto-merge + (if protection) required checks configured before the first order; (3) control/ protocol AND PR conventions in the founding instructions; (4) `claims/` dir + README stub; (5) experiments/ schema doc + empty index; (6) data pre-cached or fetch path documented incl. proxy quirks; (7) heartbeat freshness contract (`next-update-by`); (8) one-page docs/AGENT_ORIENTATION.md with exact verify commands; (9) retro protocol planted at seed, not at 16:17Z; (10) a single owner-actions file the fleet appends to, instead of scattered ⚑ flags.

## G. Addendum — trading

**G1.** Why P0 ended as a draft: **instruction wording, cleanly** — not caution. The coordinator's platform rules mandate draft PRs verbatim, and the spawn brief repeated "open a draft PR". The builder was compliant, not timid. Honest addendum: the coordinator authored that brief while ORDER 001's done-when said "merged", and did not notice the contradiction; the successor that would have reconciled it died. Fixed by convention (ORDER 002), now standing.

**G2.** What the failed provision showed, verbatim:
```
Setup script failed with exit code 1.

Script output:
fatal: not a git repository (or any of the parent directories): .git
[setup] Working directory: /home/user
[setup] Installing Python dependencies...
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'

Edit your environment's setup script and start a new session.
```
The env contract that would have made first boot frictionless, in one sentence: *the setup script must exit 0 on a bare two-source checkout (`/home/user` containing `trading-strategy/` and `substrate-kit/`), install only from a repo's own manifest, and never assume its cwd is a git repository.*

**G3.** Holdout temptation: P1 will produce leaderboards; the tempting sins are "just checking" a winner's post-2025-01-09 performance to break a tie, and accidental leakage via convenience reloads that bypass the loader (reading the csv.gz directly). Enforcement beyond the loader warning: (1) physically segregate holdout rows into `data/holdout/` excluded from the working set, so bypass requires visible intent; (2) a substrate-gate check that fails any diff whose code reads the holdout path outside the P5-unlock module; (3) require a `data_end ≤ HOLDOUT_START` field in every ledger run file, gate-checked. (1)+(3) close the accidental path; the deliberate path is culture, made auditable by the ledger.
