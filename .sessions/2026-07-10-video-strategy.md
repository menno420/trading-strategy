# 2026-07-10 — video-strategy lane (QUEUE item 1, third attempt)

> **Status:** `complete` — walking-skeleton phase landed; lane work continues
> via amendments to this card (wind-down-card precedent) or a follow-up card.

📊 Model: withheld per session policy · video-strategy lane · start 2026-07-10T02:15:22Z

💡 **Session idea:** Resume the video-strategy lane from the salvage in
`docs/research/video-source-2026-07-09.md` (full DaviddTech transcript +
first-pass rules extraction + ambiguities). Build multiple faithful
interpretations of the stated rules — dual-EMA 400/45 control plus
SuperTrend-flip/EMA/MACD variants — as competing systems vs each other and vs
buy-and-hold under founding-plan discipline (walk-forward, costs on, variants
counted, holdout untouched), and ledger the result. A negative result is a
complete deliverable. First step per ORDER 005: this walking-skeleton PR
(claim + born-red card → READY PR → tests + substrate-gate → self-landed).

## Previous-session review

Gen-1 wound down cleanly (PR #9 succession docs, PR #10 status marker,
PR #11 ping-ack, PR #12 video-lane DOA truth + salvage, PR #13 ORDER 005
adoption). The video-strategy lane itself never started — three sessions died
at provision with the identical setup-script error; the lane's inputs were
salvaged to `docs/research/video-source-2026-07-09.md`. P1 trend-following ×
all8 × daily is complete (177 variants, honest negative headline) — do not
re-run. Known walls inherited from `docs/succession/NEXT-BOOT.md`: use the
data loader for Yahoo (proxy workaround already implemented), new docs need
badge + reachable link, READY-never-draft PRs, branch deletion/tags are 403
for agents.

## Work log

- 2026-07-10T02:15:22Z — walking skeleton: claimed the lane
  (`claims/video-strategy__btcusd__multi.md`), session card (this file),
  branch `session/2026-07-10-video-strategy-skeleton`, READY PR, merge on
  green.
- 2026-07-10T02:16Z — skeleton found the day's real problem cheap, as ORDER
  005 intended: a born-red (`in-progress`) card CANNOT merge —
  `bootstrap.py check --strict --require-session-log --session-log <card>`
  (the exact substrate-gate CI command) exits 1 with
  `a completed Status (badge still says in-progress)`. Gen-1's cards all
  flipped to `complete` inside their own PR before merge; later work landed
  as Amendment sections (see `.sessions/2026-07-09-wind-down.md`). This card
  follows that precedent.

## Close-out (skeleton phase)

**Done:** walking skeleton — lane claim + this card, READY PR, tests +
substrate-gate green, self-landed by squash merge.

**Verify:** `python3 bootstrap.py check --strict --require-session-log
--session-log .sessions/2026-07-10-video-strategy.md` → exit 0;
`python3 -m pytest -q` green.

**Next (guard recipe):** the `.sessions/README.md` born-red convention
conflicts with `bootstrap.py` `IN_PROGRESS_TOKENS` (line ~1458) +
`substrate-gate.yml` diff-gating: any PR that touches an `in-progress` card
fails the gate. Until reconciled, flip the card to `complete` (scoped to the
landed phase) in the same PR, and append amendments for later phases. Lane
work resumes from `docs/research/video-source-2026-07-09.md` §Rules
extraction; delete `claims/video-strategy__btcusd__multi.md` when the lane's
ledgered results merge.
