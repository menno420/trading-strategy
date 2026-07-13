# trading-lab · status
seat: venture-lab-coordinator
session: round-6 run night worker 2026-07-13T23 (ORDER 014 item 2, coordinator-dispatched)
updated: 2026-07-13T23:09:31Z
main: c0e6459
phase: ORDER 014 night worklist — round-6 slices executed (this branch); results doc written
health: green
last-shipped: #116 — round-6 pre-registered plan (merged 2026-07-13T22:51Z by the auto-merge enabler)
blockers: none
orders: acked=001–014 done=001–013 (manager flips pending on inbox)
night_progress_order014_item1: DONE — round-6 plan landed via PR #116 (c0e6459): docs/research-round-6-plan.md (badge binding) + r6 grids/tests in trading_lab.sweeps (696 new configs, cumulative 4359→5055)
night_progress_order014_item2: round-6 slices EXECUTED (branch claude/round-6-run) — all 58 lanes ran top-down (R6-A 25.6s/1200s · R6-B 12.0s/900s · R6-C 7.9s/1200s, no CAP-HIT): 3 KEEP-dev / 47 KILL / 8 KILL-SIG, 0 promoted; gate ran on every lane (17 PASS / 41 FAIL, 0 KEEPs demoted); results docs/research-round-6-results.md
night_progress_order014_item3: R5-D fixed-config-row convention folded into the round-6 plan as a standing rule (plan § two new standing rules), alongside the selection-fair gate D-0002
night_progress_order014_items4_5: DONE via parallel slice PR #115 — see night_progress_order014_item4 / _item5 lines below
landed_today_1: PR #108 boot-refresh (320a1e3) — trigger cutover record + docs refresh
landed_today_2: PR #109 KILL-SIG ratification (3c628e4) — verdict-class review ACCEPT, no code change
landed_today_3: PR #110 round 5 (47d3cbc) — 4 KEEP-dev / 1 KILL / 0 promoted; escalate branch fired → owner-gated proposal docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md
landed_today_4: PR #111 selection-fair standing gate (d498018) — effective round 6, decision D-0002
grading_executor: LIVE — trig_01UsNU4JRps4b7jiAMdEfXNi · cron 0 9 * * 5 · next fire 2026-07-17T09:05Z · bound coordinator seat
rails: holdout SPENT untouched · paper lane intact · research-only intact
round_6: executed 2026-07-13 — 3 KEEP-dev / 47 KILL / 8 KILL-SIG of 58 lanes, 0 promoted; overnight-gap family the program's sharpest null (7 KILL-SIG); results docs/research-round-6-results.md (branch claude/round-6-run)
next_baton_1: Friday 2026-07-17 grading pass — FLAT expected (warm-up)
next_baton_2: round-6 run PR merge close-out; anything further needs new data (OWNER-GATED) or a new idea class
pointer_r5_results: docs/research-round-5-results.md (this repo)
pointer_r5c_proposal: docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md (this repo, owner-gated)
pointer_venture_retro: docs/retro/2026-07-13-coordinator-session.md (venture-lab repo)
pointer_r3_results: docs/research-round-3-results.md (this repo)
pointer_r4_results: docs/research-round-4-results.md (this repo)
night_progress_order014_item4: DONE 2026-07-13T22:50Z — grading executor CONFIRMED via one read-only list_triggers call (trig_01UsNU4JRps4b7jiAMdEfXNi · cron 0 9 * * 5 · enabled · next_run_at 2026-07-17T09:05:29Z · bound session_015hXc4bY4Dj8pmAKaJTCVTZ); foreign dup-fire trig_01YXNmgqYeYQ1LuepsLmbNCG concrete-risk clarification appended to control/outbox.md (GRADING PRE-VERIFY · 2026-07-13T22:50:23Z); foreign trigger untouched; PR #115
night_progress_order014_item5: DONE 2026-07-13T22:49Z — scripts/grade_paper.py dry-run vs FLAT ledger clean (exit 0, protocol §7 FLAT/warm-up shape, zero writes, run in throwaway tree copy); no defect, no code change; details .sessions/2026-07-13-night-grading-preverify.md; PR #115
kit: substrate-kit v1.15.0 (vendored bootstrap.py; main at PR #75 — v1.12.0→v1.12.1 via PR #63 (ea22323), v1.12.1→v1.13.0 via PR #72 (8cc0208), v1.13.0→v1.14.0 via PR #74, v1.14.0→v1.15.0 via PR #75 (b354548, current origin/main HEAD)).
