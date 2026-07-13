# trading-lab · status
seat: venture-lab-coordinator
session: round-6 plan night worker 2026-07-13T22 (ORDER 014 items 1+3, coordinator-dispatched)
updated: 2026-07-13T22:46:50Z
main: d929972
phase: ORDER 014 night worklist — round-6 plan pre-registered (this branch); round-6 run slice claimed separately
health: green
last-shipped: #114 — ORDER 014 ack + round-6 claims (merged 2026-07-13T22:37Z by the auto-merge enabler)
blockers: none
orders: acked=001–014 done=001–013 (manager flips pending on inbox)
night_progress_order014_item1: round-6 plan pre-registered — docs/research-round-6-plan.md (badge binding) + r6 grids/tests in trading_lab.sweeps (696 new configs, cumulative 4359→5055) on branch claude/round-6-plan
night_progress_order014_item2: round-6 slice execution claimed (control/claims/2026-07-13-round-6-run.md) — runs only after the plan PR merges (plan-before-outcome)
night_progress_order014_item3: R5-D fixed-config-row convention folded into the round-6 plan as a standing rule (plan § two new standing rules), alongside the selection-fair gate D-0002
night_progress_order014_items4_5: queued to a parallel slice (grading pre-verify + grade_paper.py dry-run), per the #114 ack
landed_today_1: PR #108 boot-refresh (320a1e3) — trigger cutover record + docs refresh
landed_today_2: PR #109 KILL-SIG ratification (3c628e4) — verdict-class review ACCEPT, no code change
landed_today_3: PR #110 round 5 (47d3cbc) — 4 KEEP-dev / 1 KILL / 0 promoted; escalate branch fired → owner-gated proposal docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md
landed_today_4: PR #111 selection-fair standing gate (d498018) — effective round 6, decision D-0002
grading_executor: LIVE — trig_01UsNU4JRps4b7jiAMdEfXNi · cron 0 9 * * 5 · next fire 2026-07-17T09:05Z · bound coordinator seat
rails: holdout SPENT untouched · paper lane intact · research-only intact
round_6: ready behind the new selection-fair gate, awaiting direction
next_baton_1: Friday 2026-07-17 grading pass — FLAT expected (warm-up)
next_baton_2: round 6 on direction
pointer_r5_results: docs/research-round-5-results.md (this repo)
pointer_r5c_proposal: docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md (this repo, owner-gated)
pointer_venture_retro: docs/retro/2026-07-13-coordinator-session.md (venture-lab repo)
pointer_r3_results: docs/research-round-3-results.md (this repo)
pointer_r4_results: docs/research-round-4-results.md (this repo)
night_progress_order014_item4: DONE 2026-07-13T22:50Z — grading executor CONFIRMED via one read-only list_triggers call (trig_01UsNU4JRps4b7jiAMdEfXNi · cron 0 9 * * 5 · enabled · next_run_at 2026-07-17T09:05:29Z · bound session_015hXc4bY4Dj8pmAKaJTCVTZ); foreign dup-fire trig_01YXNmgqYeYQ1LuepsLmbNCG concrete-risk clarification appended to control/outbox.md (GRADING PRE-VERIFY · 2026-07-13T22:50:23Z); foreign trigger untouched; PR #115
night_progress_order014_item5: DONE 2026-07-13T22:49Z — scripts/grade_paper.py dry-run vs FLAT ledger clean (exit 0, protocol §7 FLAT/warm-up shape, zero writes, run in throwaway tree copy); no defect, no code change; details .sessions/2026-07-13-night-grading-preverify.md; PR #115
kit: substrate-kit v1.15.0 (vendored bootstrap.py; main at PR #75 — v1.12.0→v1.12.1 via PR #63 (ea22323), v1.12.1→v1.13.0 via PR #72 (8cc0208), v1.13.0→v1.14.0 via PR #74, v1.14.0→v1.15.0 via PR #75 (b354548, current origin/main HEAD)).
