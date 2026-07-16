# 2026-07-16 — Routine cutover heartbeat + trigger-persistence WALLS entry

> **Status:** `in-progress`

- **📊 Model:** fable-5 · high · docs-only

⚑ Scope (branch `claude/routine-cutover-heartbeat`, coordinator-delegated
worker, owner authorized live in-session 2026-07-16): record the
coordinator-verified trigger registry in the `control/status.md` heartbeat
(replacing the "coordinator re-arming failsafe+pacemaker post-archive"
placeholder material) and ledger the trigger-persistence classifier wall in
`docs/CAPABILITIES.md`. Docs + control only; the CAPABILITIES touch makes
this NOT control-only, so this card rides the PR born-red per the
substrate-gate discipline. Rails: research-only, holdout SPENT and
untouched, NO trigger create/delete/fire/send_later calls by this worker
(the facts below were verified by the coordinator, not re-verified here),
`control/inbox.md` byte-untouched, no broker/exchange/live-API code.

## Work log

TRUTH bar — every fact below names its evidence:

- Trigger registry facts: coordinator's full `list_triggers` pagination,
  2026-07-16T01:0xZ (relayed in the task brief; this worker made no
  trigger MCP calls).
  - `trig_01Er6TUtwybs9D9EuHCH32qX` "Venture Lab failsafe wake",
    cron `45 1-23/2 * * *`, bound to live coordinator
    `session_01PtpASRtZJrPnyhJkV2R3Mk`, enabled, next fire
    2026-07-16T01:45Z (create succeeded 00:56Z, before the denials).
  - Pacemaker NOT armed — `send_later` denied by the platform auto-mode
    permission classifier; coordinator runs on the 2h failsafe beat +
    event wakes.
  - `trig_01GeQiMM3nHMQTyuLMsWj7q3` (stale failsafe) still enabled,
    bound to ARCHIVED 2026-07-15 coordinator
    `session_01EGUrpAETfZMffp4XfN3tDT`; `delete_trigger` denied by
    classifier; left armed; owner cleanup queued (VENUE:hub /
    routines UI).
  - `trig_01BsYsMABu2vfH4d2MzuSLs6` (grading cron, `0 9 * * 5`) bound to
    the same archived session — first fire 2026-07-17T09:08Z, delivery
    NOT expected (triggers die at archive); `create_trigger` rebind
    denied by classifier; executor plan is in-session dispatch at first
    wake after Fri 09:00Z (failsafe fires 09:45Z) per
    `docs/paper-lane-protocol.md` §6–§7 (`scripts/grade_paper.py`).
  - `trig_01YXNmgqYeYQ1LuepsLmbNCG` foreign, fires 2026-07-17T09:00Z,
    not ours, untouched.
- Heartbeat edit: replaced ONLY the routines/trigger block in
  `control/status.md` (the seven lines from `trigger_failsafe:` through
  `routines:`, which carried the pre-verification placeholder "coordinator
  re-arming failsafe+pacemaker post-archive") with the verified key:value
  registry above; all other heartbeat content byte-untouched. Superseded
  historical trigger notes (`trig_01YBaVeKAW2fSD83S9F37s2d` inert record,
  `trig_01UsNU4JRps4b7jiAMdEfXNi` / `trig_015aNMg5ncoSE2Roe4MKjQnr`
  supersession note) remain readable in git history (PR #132 heartbeat,
  main `9fc7ad5`).
- WALLS ledger: appended the 2026-07-16 trigger-persistence classifier
  entry to the `docs/CAPABILITIES.md` append log (newest first).
  Verbatim denial texts (Reason-clause excerpts) live in this branch's
  landing PR body, per the entry's pointer.
- Repo-shape notes: `docs/conventions.md` does NOT exist in this repo
  (verified at HEAD `fb741e1`); the paper-lane protocol lives at
  `docs/paper-lane-protocol.md` (NOT `docs/operations/…` — the
  operations/ dir holds only `auto-merge-guards.md`).

## Close-out

**Previous-session review:** the 2026-07-16 post-reboot restamp session
(PR #132, merge `9fc7ad5`) landed a clean living-ledger re-stamp with a
complete card and exemplary carried-verbatim trigger records — its one
open loose end was exactly the placeholder this session replaces: the
heartbeat promised "coordinator re-arming failsafe+pacemaker
post-archive" with ids to follow next heartbeat; this session records the
verified outcome of that re-arming attempt (one create succeeded, three
persistence calls classifier-denied).

💡 **Session idea (deduped against prior cards — distinct from the
restamp card's scheduled-CI idea, the eap-closeout card's owner-actions
surface, and the night-research-infra card's grading-pass watchdog):**
the heartbeat's trigger registry is now verified-but-perishable — nothing
detects drift between `control/status.md` trigger lines and live
`list_triggers` output at the next boot. Contained fix: a boot-checklist
line in `control/README.md` (anchor: the heartbeat-format section)
requiring the coordinator to diff its `list_triggers` output against the
heartbeat's `failsafe_new`/`grading_cron` lines and restamp on mismatch;
verify target: the next boot card citing that diff.

**Verify:** `python3 bootstrap.py check --strict` — expected result at
this commit: all checks pass except the intended born-red HOLD from this
in-progress card (flips at the final commit).

Session end: pending — badge flips `complete` in the deliberate final
commit after the PR is open.
