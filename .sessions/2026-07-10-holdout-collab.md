# 2026-07-10 — holdout enforcement hardening + collaboration-model port (QUEUE items 5+6)

> **Status:** `complete` — heartbeat phase landed (claim + card, READY PR,
> merge on green); the session itself is in progress — lane work (QUEUE
> items 5 and 6) continues via amendments to this card or follow-up PRs
> (wind-down-card precedent).

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

## Close-out (heartbeat phase)

**Done:** lane claim + this card landed via READY PR with tests +
substrate-gate green. Lane work (QUEUE items 5 and 6) follows in this
session's next PRs; this card flips to a full-session close-out when the
lane closes (claim deleted at close).

**Next (guard recipe):** QUEUE item 5 implementation (holdout hardening),
then item 6 (`docs/collaboration-model.md`), then wrap-up PR: card
close-out, claim release, `control/status.md` overwrite.
