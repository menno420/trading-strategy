# 2026-07-10 — holdout enforcement hardening + collaboration-model port (QUEUE items 5+6)

> **Status:** `complete` — full session closed: heartbeat (claim + card,
> PR #23), holdout enforcement hardening (PR #24, QUEUE item 5),
> collaboration-model port (PR #25, QUEUE item 6), and this wrap-up
> (status overwrite + claim released). Lane closed.

📊 Model: withheld per session policy · holdout-collab lane · start 2026-07-10T03:50:19Z

💡 **Session idea:** the standing default (QUEUE.md § Next, top to bottom)
resumes at item 5: holdout enforcement hardening — segregate `data/holdout/`,
add a gate check on holdout reads, and enforce `data_end ≤ HOLDOUT_START`
(HOLDOUT_START=2025-01-09, loader-enforced in `src/trading_lab/data.py`) in
every ledger row — then item 6: port the fleet's PR-lifecycle conventions
(READY-never-draft, auto-merge/REST-squash on green, session card in every
PR diff, claim lifecycle) into `docs/collaboration-model.md`. First step:
this heartbeat PR (claim + card → READY PR → tests + substrate-gate →
landed on green).

## Previous-session review

QUEUE items 1–4 are all DONE and merged: video-strategy lane (PRs #14/#15),
mean-reversion × daily (PRs #16/#17), trend × hourly (PRs #18/#19), and P2
validation of all 14 open candidates (PRs #20/#21, wrap-up #22 — 1
PROMOTED-TO-FINDING: AAPL-donchian daily; 1 KILLED; 12
UNVALIDATABLE-PRE-HOLDOUT). control/status.md reports orders acked=001–005
done=001–005 with item 5 named as next. Overlap check at claim time:
`claims/` held only its README; zero open PRs on the repo. Known walls
inherited: born-red cards cannot merge — badge is `complete` scoped to the
landed heartbeat phase; new docs need a Status badge + a link from a
reachable doc; READY-never-draft, merge on green; auto-merge arm can fail
"unstable status" (pending) and "already in clean status" (green) — REST
squash on green is the fallback; tag pushes / branch deletion are 403 for
agents; use the data loader for Yahoo (proxy workaround in
`src/trading_lab/data.py`).

## Work log

- 2026-07-10T03:50:19Z — heartbeat/skeleton: claimed the lane
  (`claims/holdout-collab.md`, QUEUE items 5+6), session card (this file),
  branch `session/20260710-0350-holdout-collab`, READY PR, merge on green.
- 2026-07-10T04:01:50Z — QUEUE item 5 (holdout enforcement hardening),
  branch `holdout-hardening`: ledger guard — `build_record` and the
  `write_run` choke point now raise `ValueError` on any
  `data_end >= HOLDOUT_START` unless `holdout_unlocked=True` stamps a
  visible `"holdout_unlocked": true` marker (P5-only; `rebuild_index`
  propagates it into index rows); new CI audit test parses every
  `experiments/index.jsonl` row + every `experiments/runs/*.json` for
  unmarked boundary violations; loader edge cases pinned in
  `tests/test_data.py` (`data_dir=` override incl. the p2ext pattern,
  `end=` past the boundary stays clipped, `start=` inside the holdout
  returns an empty frame — filter verified to run before start/end
  slicing, no data.py change needed); contract doc
  `docs/holdout-enforcement.md` (binding) linked from founding-plan;
  QUEUE item 5 marked DONE.
- 2026-07-10T04:12:08Z — QUEUE item 6 (collaboration-model port), branch
  `collab-model-pr-lifecycle`: `docs/collaboration-model.md` gains "PR
  lifecycle (as practiced)" + "Session lifecycle around PRs (as practiced)"
  — READY-never-draft, forward-only git, arm-at-creation with the two-way
  arm wall ("unstable status" / "already in clean status") and
  REST-squash-on-green fallback (the path that fired for every merge to
  date), written self-merge grant (ORDER 002/005), post-merge review via
  review-queue/Codex, terminal refusal branch, heartbeat-before-work,
  one-writer + claims lifecycle, status ender contract, substrate-gate
  interplay — all verified against merged PRs #14–#24. QUEUE item 6 marked
  DONE; new NEXT-BOOT wall appended (raw curl to api.github.com check-runs
  hangs to Bash timeout, exit 143 — poll checks via the GitHub MCP
  instead).

## Close-out (full session)

**Done:** all four phases of the session —

1. Heartbeat/skeleton (PR #23): lane claim `claims/holdout-collab.md` +
   this card, READY PR, tests + substrate-gate green, landed on green.
2. Holdout enforcement hardening (PR #24, QUEUE item 5): ledger guard —
   `build_record` and the `write_run` choke point raise on any
   `data_end >= HOLDOUT_START` unless `holdout_unlocked=True` stamps a
   visible marker (P5-only); CI audit test over every
   `experiments/index.jsonl` row and every `experiments/runs/*.json`;
   loader edge cases pinned in 3 new tests; contract doc
   `docs/holdout-enforcement.md` (`binding`) linked from founding-plan.
   QUEUE item 5 marked DONE.
3. Collaboration-model port (PR #25, QUEUE item 6): "PR lifecycle (as
   practiced)" + "Session lifecycle around PRs (as practiced)" sections in
   `docs/collaboration-model.md`, verified against merged PRs #14–#24;
   NEXT-BOOT wall appended for the curl check-runs hang (poll via the
   GitHub MCP instead). QUEUE item 6 marked DONE.
4. Wrap-up (this PR, branch `wrapup-holdout-collab`): inbox re-read at
   HEAD 4924a1b (no orders newer than ORDER 005), this card flipped to
   full-session close-out, claim `claims/holdout-collab.md` deleted (lane
   closed), `control/status.md` overwritten.

**Verify:** `python3 bootstrap.py check --strict --require-session-log
--session-log .sessions/2026-07-10-holdout-collab.md` → exit 0;
`python3 -m pytest` — 133 passed at PR #25.

**Next (guard recipe):** QUEUE.md § Next is exhausted (items 1–6 all
DONE). Next session pulls direction from NEXT-BOOT / the inbox; new
session = new claim + new card.

Session end: 2026-07-10T04:16:42Z. Badge stays `complete`.
