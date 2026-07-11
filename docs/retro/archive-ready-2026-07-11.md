# Archive-ready 2026-07-11

> **Status:** `historical`
>
> Written 2026-07-11 as the coordinator project chat is archived. This is
> the durable close-out: true state, in-flight classification, every open
> owner action, and the resume runbook for whatever session picks the lane
> up next. Everything below is verified against source (code, ledgers,
> GitHub API), not against status docs. Companion:
> [self-review-2026-07-11.md](self-review-2026-07-11.md) (the ORDER-010
> self-review, moved durable, with the archive-prep evidence upgrades).

## True state (one paragraph)

The paper lane is operational: opened 2026-07-11 (`PAPER_LANE_START =
"2026-07-11"`, pinned in `src/trading_lab/config.py` and guard-tested),
strategy FLAT in its 15-bar warm-up (ledger row paper-0001 WATCH in
`experiments/paper/ledger.md`; donchian(15,5) channels build only from
lane bars, so the first evaluable entry signal comes ~early Aug 2026);
the first weekly grading pass is due 2026-07-17 (protocol §6,
`scripts/grade_paper.py`). Research round 2 is CLOSED: 5 KEEP / 9 KILL of
78 configs run (verified against `docs/research-round-2-results.md`),
program burden 668, promotion CLOSED — the only path past dev-candidate is
the owner-gated post-2026 OOS protocol PROPOSAL (filed in
`docs/final-report.md` POST-HOLDOUT DEV-ONLY section; agents never
schedule or run it). The holdout is SPENT (13 reads exactly, consumed
2026-07-10) and stays sealed forever. Inbox orders 001–010 are all
acked and done (`control/status.md`). No real money, no accounts, no
orders — ever.

## In-flight classification (verified from source 2026-07-11T19:33Z)

Enumerated from the GitHub API (open-PR list), `git ls-remote --heads
origin`, and the claims directories — not from status docs. Nothing is
unclassified.

| Item | Finding | Classification |
|---|---|---|
| Open PRs | **0** open (kit upgrades #44–#60 and all lane PRs landed; latest merge #61, main `2dd955d`) | all LANDED |
| Remote branches | **1**: `main` only (plus this close-out's own `wrapup/archive-prep-2026-07-11`, which merges and dies with this PR) | nothing stranded |
| Claims (`claims/`, `control/claims/`) | READMEs only — **0** open claims | no open lanes |
| Kit lane-owed follow-ups (from kit-upgrade cards #51–#61) | (1) `kit:` heartbeat line stale at v1.7.1 — **PAID in this PR** (bumped to v1.12.0); (2) no live root `CLAUDE.md` (kit copy staged at `.substrate/claude/CLAUDE.md`); (3) `docs/CAPABILITIES.md` landing-constraints entry; (4) `docs/AGENT_ORIENTATION.md` manual merge of the v1.12.0 boot-set trim (delta in `.substrate/upgrade-report.md`) | (1) landed; (2)–(4) PARKED — one-line next step each: adopt the staged CLAUDE.md; append the landing-constraints entry; hand-merge the template delta. None blocks anything. |
| Weekly grading cadence | due 2026-07-17, currently has NO executor (see ⚑ (g)) | PARKED — top item in the resume runbook |

## ⚑ Open owner actions (six-field form: what / why / exact click / where / blocking? / fallback)

Mirrored in `control/status.md`; this file is the durable copy.

### (g) RE-ARM THE WEEKLY GRADING CADENCE — TRIGGER SUCCESSION (top risk, NEW 2026-07-11)

- **what:** two triggers are bound to the coordinator session
  `session_01NwvvbgUVSdQvY8eYwtuEoo`: (1) the 2-hourly failsafe cron
  `trig_01YBaVeKAW2fSD83S9F37s2d` ("trading-strategy failsafe wake", cron
  `0 */2 * * *`), and (2) the weekly grading wake
  `trig_01YXNmgqYeYQ1LuepsLmbNCG` (fires 2026-07-17T09:00:00Z, message:
  "run the weekly paper-lane grading pass"). When the coordinator chat is
  archived, BOTH die silently.
- **why:** the 2026-07-17 grading pass and inbox watching then have NO
  executor — the paper lane's §6 cadence stalls with no error anywhere.
- **exact click:** have the successor coordinator session (or an owner
  Routine) re-arm the weekly grading cadence — e.g. a Routine firing
  weekly from 2026-07-17T09:00Z with prompt "run the weekly paper-lane
  grading pass per docs/paper-lane-protocol.md §6–§7".
- **where:** claude.ai Routines / a new coordinator session for this
  project.
- **blocking?:** YES for the 2026-07-17 grading pass — the only ⚑ item
  that is time-critical.
- **fallback:** protocol §6 tolerates a late pass (missing a weekly pass
  delays grading, it does not corrupt it — WATCH/ENTRY rows are never
  mutated), and the first ~3 weeks are warm-up (expected FLAT). Late is
  recoverable; never is not.
- (Historical, already durable via PR #39 — do not duplicate: predecessor
  wake `trig_01Mvn5xRmqGmZJNRHgjqyLpN` was create-verify-then-deleted
  2026-07-10T21:03-05Z.)

### (b) ENV SETUP SCRIPT

- **what:** paste `environments/setup-universal.sh` into the project
  environment's setup-script field.
- **why:** fresh-environment sessions die silently at provision without it
  (setup runs at cwd=/home/user with repos as subdirectories).
- **exact click:** paste the file contents into the setup-script field and
  save. **where:** Claude environment config for this project.
- **blocking?:** no (current pinned env works).
- **fallback:** keep spawning into the pinned env; treat any child with no
  heartbeat within 10 min as dead → respawn.

### (c) ALLOW AUTO-MERGE TOGGLE

- **what:** tick "Allow auto-merge".
- **why:** auto-merge arm fails pending-side with "unstable status" while
  the toggle is off, so every merge needs an agent to poll-and-merge
  (reconfirmed on PR #36).
- **exact click:** Settings → General → Pull Requests → Allow auto-merge.
  **where:** GitHub → menno420/trading-strategy.
- **blocking?:** no.
- **fallback:** continue REST/MCP squash-merge on green (the path every
  merge to date used).

### (d) ARCHIVE DEAD GEN-1 SESSION

- **what:** archive the "ORDER 001 successor" session.
- **why:** it died at provision, emits no failure event, still lists as
  active — misleading.
- **exact click:** open the project's session list, locate "ORDER 001
  successor", archive it. **where:** claude.ai session list for this
  project.
- **blocking?:** no. **fallback:** ignore it — it consumes nothing.

### (f) DECIDE ON POST-2026 OUT-OF-SAMPLE PROTOCOL PROPOSAL

- **what:** decide whether to authorize a pre-registered OOS protocol
  draft for the 5 round-2 dev-candidates.
- **why:** their ONLY path past dev-candidate is a NEW owner-gated
  pre-registered protocol on genuinely new post-2026 data — recorded as a
  PROPOSAL in `docs/final-report.md` (POST-HOLDOUT DEV-ONLY) and
  `docs/research-round-2-results.md`; agents never schedule, initiate, or
  run it.
- **exact click:** if wanted, file an inbox ORDER authorizing a protocol
  draft (decision only — nothing runs on a yes until the protocol itself
  is owner-approved); if not wanted, no click needed.
  **where:** `control/inbox.md` via the manager.
- **blocking?:** no.
- **fallback:** dev-candidates stay labeled dev-only indefinitely —
  flag-only, this item never self-executes.

## Resume runbook (what a fresh session needs)

1. `git fetch origin main && git reset --hard origin/main`.
2. Read `control/inbox.md`, `control/status.md`,
   `docs/paper-lane-protocol.md` (BINDING), then this file and
   [self-review-2026-07-11.md](self-review-2026-07-11.md).
3. **Re-arm the weekly grading cadence first** (⚑ (g) above) — from the
   coordinator seat or an owner Routine; child sessions cannot arm
   triggers (no send_later tool — see the self-review's ops-knowledge
   section).
4. **Grade due windows before any research**: if any weekly window
   (first due 2026-07-17) has passed ungraded, run the grading pass per
   protocol §6–§7 (`scripts/grade_paper.py`) before touching anything
   else. Expected FLAT through warm-up (~3 weeks).
5. Hard rails carry over verbatim: holdout SPENT — never read `data/**`,
   never call `load_ohlcv` with unlock_holdout; lane data ONLY via
   `trading_lab.data.load_paper_ohlcv`; no real money, no accounts, no
   secrets; family-level model names only in committed files.

## Chat-only residue: confirmation

Checked at archive time: the trigger bindings (→ ⚑ (g)), the PR #41
webhook-observed timestamps, the ORDER-008 verdict-branch provenance, and
the coordinator ops knowledge (child send_later absence, classifier shape,
stand-down-by-ping) were the four facts living only in the coordinator
chat; all four are now committed (this file +
[self-review-2026-07-11.md](self-review-2026-07-11.md)). **Nothing
important remains chat-only.** Everything else a successor needs was
already durable: protocol, ledgers, final report, round-2 results, kit
conventions, and the heartbeat.
