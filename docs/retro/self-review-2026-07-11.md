# Self-review 2026-07-11 (ORDER 010) — durable copy

> **Status:** `historical`
>
> The ORDER-010 lane self-review, moved here 2026-07-11 from
> `control/status.md` (which is overwritten every session — retro files
> persist). Content is the merged ORDER-010 section (PR #59, ed8add3) plus
> three archive-prep upgrades marked **[archive-prep 2026-07-11]**: the
> PR #41 evidence upgrade, the ORDER-008 verdict-branch provenance line,
> and the ops-knowledge section for successors.

window: 2026-07-10 ~20:00Z → 2026-07-11 ~10:09Z (ORDER 010, P1,
owner-directed fleet self-review). Every claim below is verified against
git history, PR records, or check-run records unless explicitly labeled
session-reported.

## What shipped (all merged to main)

- Holdout final report landed: PR #37 merged by owner click
  2026-07-10T20:56:34Z (merge commit ffdd6f6); status un-staled same
  evening via PR #39 (efaedf6).
- Paper-lane foundation, lane opened 2026-07-11: PR #40 design docs
  (d0fc23b), PR #41 pre-registered protocol — BINDING, merged 21:40:26Z
  before any trade outcome was observable (8e512c1), PR #42 loader rail +
  ledger with opening row paper-0001 WATCH committed 2026-07-10T21:44:51Z
  (35cc0c1), PR #43 grading job (0f76e2e), PR #45 status close-out
  (c47f74d). First weekly grading due 2026-07-17 (protocol §6).
- Research round 2, pre-registered → executed → closed: PR #46
  pre-registration (8d0270f), PR #47 R1 vol_filtered_trend 0 KEEP / 4 KILL
  of 48 (4b890ba), PR #48 R2 keltner_breakout 2/2 of 24 (f842680), PR #49
  R3 xsec_momentum 3/3 of 6 (9b13b8a), PR #50 close-out (6799a4c).
  Headline 5 KEEP / 9 KILL of 78 configs run, program burden 668,
  promotion CLOSED — re-verified against docs/final-report.md
  (POST-HOLDOUT DEV-ONLY section) and docs/research-round-2-results.md.
- ORDER 009 hygiene: model-attribution convention + P1-drops annotation,
  PR #53 (f4d9669).
- Kit upgrades via the external kit-upgrade flow: v1.7.0→v1.7.1 PR #44
  (24649d7), →v1.8.0 PR #51 (d0d789e), →v1.9.0 PR #54 (3833fcc), →v1.10.0
  PR #55 (d3715d9) + claim release PR #56 (569fae8), →v1.10.1 PR #57
  (cd370ce).
- Manager writes, recorded for completeness (not this lane's work): PR #52
  ORDER 009 relay (39a5646), PR #58 ORDER 010 (4c1a316).

## What went wrong / friction

- substrate-gate CI red once each on the first head of two doc PRs, both
  self-diagnosed and fixed same-session, both PRs then merged green:
  PR #40 head 6c5949b (check run 86465144882, failure — badge taxonomy +
  orphaned read-path links; fixed in 2f3af3d) and PR #41 head 7df8ed6
  (check run 86466317457, failure — orphan link; fixed in da789c9).
- PR #41 additionally hit a merge conflict with PR #40's
  docs/current-state.md edit, resolved in merge commit c53fb5d (21:38:10Z)
  before merging at 21:40:26Z. **[archive-prep 2026-07-11] Evidence
  upgrade:** the ORDER-010 review filed PR #41's close/reopen sequence as
  "session-reported, unverified" (final closed_at equalled merged_at;
  timeline events were unreachable from that session's surfaces). It is
  now **coordinator-observed webhook evidence**: PR #41 closed-unmerged
  2026-07-10T21:35:30Z, reopened 2026-07-10T21:35:38Z, merged
  2026-07-10T21:40:26Z. The record is upgraded from session-reported to
  observed.
- Session-reported, unverifiable from the repo: the permission classifier
  blocked spawn-prompts that PRE-INSTRUCT self-merging; per-PR
  merge-after-green instructions passed. Handled decide-and-flag, no harm
  shipped. Consistent with the repo's recorded classifier precedent
  (PR #37 body; docs/review-queue.md line for #37), but these specific
  denials left no repo artifact.
- Session-reported environment limitation: worker child sessions had no
  send_later tool; continuation relied on the coordinator chain plus the
  2h failsafe cron (trig_01YBaVeKAW2fSD83S9F37s2d).

## Integrity provenance

- **[archive-prep 2026-07-11]** The ORDER-008 verdict branch —
  CONFIRMED → open the forward paper lane / REFUTED → harvest lessons +
  next research round — was pre-specified in the coordinator's founding
  brief BEFORE any holdout number was seen; the paper-lane branch was
  entered per that rule, not chosen after seeing the CONFIRMED result.
  (docs/p5-holdout-protocol.md pre-specifies the CONFIRMED/REFUTED
  *criteria*; the *consequence branch* lived only in the coordinator chat
  until this note.)

## Ops knowledge for successors

**[archive-prep 2026-07-11]** Coordinator-seat observations that survive
nowhere else once the coordinator chat is archived:

1. **Only the coordinator seat can arm triggers.** Child sessions in this
   project expose no send_later tool — every trigger/routine in this
   lane's history was armed from the coordinator seat, via subagent
   workers. A successor must plan continuation from the coordinator seat
   (or an owner Routine), never from a child.
2. **Classifier shape on merge instructions:** the permission classifier
   blocks spawn-prompts that pre-instruct self-merging, but per-PR
   merge-after-green instructions pass. Scope merge authorization to the
   specific PR, at the time it exists.
3. **Stand down idle children by ping.** Idle child sessions should be
   stood down by a coordinator ping rather than left polling — verified
   working 2026-07-11: the ORDER-009 session cancelled its pending loop
   trigger on request.

## Owner attention (⚑ mirrored in the control/status.md needs-owner list)

- Still open, owner-only clicks, none blocking: (b) env setup script,
  (c) allow auto-merge toggle, (d) archive dead gen-1 session — six-field
  detail in control/status.md.
- (f): decide on the post-2026 out-of-sample protocol PROPOSAL from the
  round-2 close-out — flag only; agents never schedule, initiate, or run
  it.
- **[archive-prep 2026-07-11]** (g) NEW, top risk: trigger succession —
  both lane triggers die silently when the coordinator chat is archived;
  full six-field form in control/status.md and
  [archive-ready-2026-07-11.md](archive-ready-2026-07-11.md).
- Resolved: (e) merge-PR-#37 — owner click confirmed, PR #37 merged
  2026-07-10T20:56:34Z by menno420.

## Health

one-liner: paper lane operational — opened 2026-07-11, strategy FLAT in
warm-up (ledger row paper-0001 WATCH), first weekly grading due
2026-07-17; research round 2 closed honestly (5 KEEP / 9 KILL of 78,
dev-only, promotion owner-gated); holdout SPENT and untouched (13 reads
exactly); inbox clear through ORDER 010.
