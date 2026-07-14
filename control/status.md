# trading-lab · status
seat: venture-lab-coordinator
session: night-close worker 2026-07-14T01 (ORDER 014 close-out heartbeat, coordinator-dispatched)
updated: 2026-07-14T01:13:55Z
main: 0d12515
phase: ORDER 014 COMPLETE — all 5 items landed and merged; night close-out heartbeat
health: green
last-shipped: #118 — round-6 run, all three pre-registered slices (merged 2026-07-13T23:12Z by the auto-merge enabler)
blockers: none
orders: acked=001–014 done=001–013 (014 all items complete this repo side; manager flips pending on inbox)
order014_close: ALL 5 ITEMS COMPLETE — 4 PRs enabler-merged green: #114 ack · #116 plan (c0e6459) · #118 run (0d12515) · #115 items 4+5 (d6e3cf9)
order014_item1_plan: DONE via #116 (c0e6459) — docs/research-round-6-plan.md (badge binding) pre-registers R6-A/B/C, 696 new configs; selection-fair gate (D-0002) + R5-D fixed-config row folded in as standing rules effective this round
order014_item2_run: DONE via #118 (0d12515) — 58/58 lanes ran top-down, no cap hits: 3 KEEP-dev / 47 KILL / 8 KILL-SIG / 0 promoted (best t 0.60 vs 2.638 bar); results docs/research-round-6-results.md
order014_item3: DONE via #116 — R5-D fixed-config-row convention standing in the round-6 plan alongside the selection-fair gate D-0002
order014_items4_5: DONE via #115 (d6e3cf9) — grading executor independently CONFIRMED (trig_01UsNU4JRps4b7jiAMdEfXNi · next fire 2026-07-17T09:05Z · this seat); foreign dup-fire risk concretely flagged in control/outbox.md; scripts/grade_paper.py dry-run CLEAN (exit 0, exact protocol §7 FLAT shape)
headline_null_1: overnight-gap family fails everywhere — 0/12 KEEP, t to −4.01; the sharpest null in program history (docs/research-round-6-results.md)
headline_null_2: volume confirmation adds nothing over pure OBV — R6-A registered hypothesis confirmed null
burden: multiple-testing burden 4359 → 5055 registered configs, exactly as pre-declared
grading_executor: LIVE — trig_01UsNU4JRps4b7jiAMdEfXNi · cron 0 9 * * 5 · next fire 2026-07-17T09:05Z · bound coordinator seat
rails: holdout never read · no fetches · no exchange-write code · promotion CLOSED · bar never lowered · paper lane intact · research-only intact
next_1: Friday 2026-07-17 grading pass — FLAT expected (warm-up)
next_2: round 7 awaits manager/owner direction
pointer_r6_plan: docs/research-round-6-plan.md (this repo)
pointer_r6_results: docs/research-round-6-results.md (this repo)
pointer_r5_results: docs/research-round-5-results.md (this repo)
pointer_r5c_proposal: docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md (this repo, owner-gated)
pointer_venture_retro: docs/retro/2026-07-13-coordinator-session.md (venture-lab repo)
kit: substrate-kit v1.15.0 (vendored bootstrap.py; main at PR #75 — v1.12.0→v1.12.1 via PR #63 (ea22323), v1.12.1→v1.13.0 via PR #72 (8cc0208), v1.13.0→v1.14.0 via PR #74, v1.14.0→v1.15.0 via PR #75 (b354548, current origin/main HEAD)).
