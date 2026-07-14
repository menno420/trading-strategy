# SEAT DORMANT (owner order 2026-07-14)
updated: 2026-07-14T21:17:36Z
seat: venture-lab-coordinator (trading-strategy lane) — DORMANT
order: control/inbox.md ORDER 015 · 2026-07-14T09:33:51Z (EAP final day — "the owner needs every lane terminal-or-parked-cited plus a walkthrough to review each seat"); ORDER 015 done-when was met by PR #123 (walkthrough + audit pointer + round-7 plan + re-stamp); this record is the final dormancy heartbeat, per owner order 2026-07-14
rail: RESEARCH-ONLY — no real money, no accounts, no broker/exchange/order code, ever
main-at-dormancy: f4616ea (kit v1.17.0, PR #126)
health: dormant-by-design
blockers: none — seat is deliberately dark; a stale `updated:` stamp is expected from here on

## 1. REVIVAL INSTRUCTIONS

read-first-1: docs/current-state.md — stability baseline, in-flight snapshot, shipped ledger
read-first-2: docs/eap-closeout-walkthrough-2026-07-14.md — the EAP close-out walkthrough, in THIS repo (venture-lab carries the seat-level closeout; this is the trading-side doc, sections A–E)
read-first-3: docs/audits/eap-project-audit-2026-07-14.md — this repo's audit POINTER doc → menno420/venture-lab docs/audits/eap-project-audit-2026-07-14.md, pinned 37e3c05
read-first-4: control/inbox.md — the full ORDER thread 001–015 (never edit it; one writer: the manager)
batons: per the walkthrough §E "Handoff notes" — Friday grading baton (time-gated), round-7 plan (pre-registered NOT run), KEEP-dev survivor list (4+3, dev artifacts only, promotion CLOSED), parked items
routines: re-arm per section 3 below — the verbatim records there are the ONLY revival path (the live triggers are deleted at shutdown)

## 2. PARKED STATE

(each claim verified at HEAD f4616ea, 2026-07-14)

parked-1: round-7 research plan committed but NOT run — docs/research-round-7-plan.md, badge `binding`, header verbatim "PLAN ONLY: this document's own session runs NOTHING — executing Round 7 ... is a FUTURE session's separately claimed slice"; no round-7 grid code exists in src/ at HEAD
parked-2: R5-C BTC-USD bollinger_breakout OOS — owner-gated until ~2026-09-09 (docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md, badge "FROZEN PREREGISTRATION PROPOSAL. OWNER-GATED"; window needs >= 252 post-2026 daily bars, so execution is impossible before ~2026-09-09 per walkthrough §C/§E and inbox ORDER 015 parked list)
parked-3: Friday weekly grading WILL NOT FIRE while dormant — its trigger (trig_01UsNU4JRps4b7jiAMdEfXNi, next fire was 2026-07-17T09:05Z, executor verified LIVE at HEAD per the old heartbeat grading_executor line and walkthrough §E) is deleted at shutdown; the re-arm record is section 3 below. Expected first-pass result on revival remains FLAT (warm-up; first evaluable entry signal ~early August 2026 per docs/paper-lane-protocol.md §3)
parked-4: MTF-Bollinger preregistration draft — FROZEN, dev result NULL (docs/proposals/bollinger-mtf-preregistration-draft.md)
parked-5: program state at dormancy — 5,055 registered configs, 0 promoted (docs/research-program-retrospective.md); holdout SPENT; promotion CLOSED; paper ledger sole record paper-0001 WATCH/FLAT

## 3. ROUTINE RE-ARM RECORDS

(copy is VERBATIM from the shutdown order; these triggers are deleted right after this PR lands and this text is the only revival path)

- BUSINESS cron (re-arm on revival, bind to the live coordinator seat): name "trading-strategy weekly paper-lane grading" · cron `0 9 * * 5` · prompt: "weekly paper-lane grading wake (trading-strategy): run the weekly grading pass per docs/paper-lane-protocol.md sections 6-7 via scripts/grade_paper.py in menno420/trading-strategy (research-only rail: no real money, no accounts, ever). First pass 2026-07-17: warm-up FLAT is the expected result. Land the graded ledger per lane convention and update control/status.md." (last id trig_01UsNU4JRps4b7jiAMdEfXNi, deleted at shutdown)
- BUSINESS one-shot: SWTK T+7, fire 2026-07-19T16:37Z · prompt: "T+7 checkpoint (SWTK launch, per docs/launch/stripe-webhook-test-kit/LAUNCH-LOG.md): check Gumroad views/sales with the owner, log the funnel numbers, assess against the kill rule (T+14 = 2026-07-26)." (last id trig_01V9DZrTtDU81Sm7vektX9fa)
- BUSINESS one-shot: SWTK T+14 KILL-RULE, fire 2026-07-26T16:37Z · prompt: "T+14 KILL-RULE checkpoint (SWTK launch, per docs/launch/stripe-webhook-test-kit/LAUNCH-LOG.md): with the owner, check total organic sales + qualified inbounds since 2026-07-12. If zero: ledger ⚑E as NEGATIVE and queue the pause/delist owner action. If ≥1: record the positive signal and plan the next distribution step." (last id trig_01SNkNWfSXoAdz1ALf4YNbC6)
- FAILSAFE cron (re-arm on revival): name "Venture Lab failsafe wake" · cron `45 1-23/2 * * *` · prompt: "FAILSAFE WAKE (Venture Lab, Q-0265): send_later chain alive → verify in one line, end. Stalled → resume the work loop (sync HEAD → inbox → slice after slice, landed per LANDING), re-arm the chain (~15 min), and write your heartbeat (control/status.md, per-seat grammar) as the deliberate last step." (last id trig_01SbFnHdb1bvUzDnKrDdRb6t)
- PACEMAKER pattern: send_later ~15 min (working) / 30–45 (idle), message "continue the work loop: sync HEAD → inbox → next slice → re-arm".
- FOREIGN (not ours, NOT deleted): trig_01YXNmgqYeYQ1LuepsLmbNCG fires 2026-07-17T09:00Z "WEEKLY GRADING PASS" into a non-seat session — owner was advised to delete/confirm-dead; still open at shutdown unless the owner acted.

## 4. SOURCE-OF-TRUTH DUPLICATION

(grep of this repo's docs/ + CONSTITUTION.md for doctrine restated locally that fleet-manager centralizes; nothing migrated — record only)

dup-1: docs/CAPABILITIES.md — local walls ledger (7 seed-fence walls + 1 append entry) whose header names its master copy as `menno420/fleet-manager` → `docs/capabilities.md`; the audit pointer §Walls quotes the fm fence-index mirroring these entries
dup-2: docs/collaboration-model.md §"Arm auto-merge at creation; REST squash is the path that fires" — restates the REST/MCP squash-on-green landing exception locally; the CAPABILITIES.md 2026-07-12 append entry marks that exception "RETIRED-superseded by the enabler; never revive it", so this section carries retired squash-exception text
dup-null: no merge-doctrine / park-green text duplicating UNIVERSAL.md found in docs/ or CONSTITUTION.md (grep for "UNIVERSAL", "park green", "parked green", "merge-doctrine": no hits)

## 5. SANITY

current-state: docs/current-state.md is accurate at HEAD f4616ea with one self-declared caveat — its "In flight" section is an explicitly dated snapshot ("Live state as of 2026-07-13T13:42Z ... main @ 83e736c" with its own "Verify against live source control" disclaimer); items it lists as in flight (EAP close-out branch claude/eap-closeout-ts → landed as PR #123; R5 "merge close-out pending" → landed) are since MERGED. The section's own disclaimer covers this, so it is noted here as parked staleness rather than edited — no diff outside control/** (control fast lane preserved)
scope: this PR touches control/status.md only (claim file added and deleted within the branch); control/inbox.md untouched
