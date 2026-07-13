# trading-lab · status
seat: venture-lab-coordinator
session: session_01PuKfWNT3mL1hF77p2tpMDW (night-report worker)
updated: 2026-07-13T09:22:51Z
main: 08969bb
night_report: ORDER-013 served; window 2026-07-12T22:30Z→09:12Z: 18 PRs #80–#97 merged (#80 ORDER-012 landing · #81–#88+#90–#95 fourteen research slices · #89 synthesis · #96 morning tally de5a477 · #97 manager ORDER-013 inbox append 08969bb); full report: control/outbox.md § NIGHT REPORT 2026-07-13
open_prs: 0 (verified 2026-07-13T09:19Z, MCP + git ls-remote cross-check)
orders: acked=001–013 · done=001–012 (012 served: night run executed, morning tally #96) · 013 served by this report
surface_added: 11 strategies · 6 tickers (SPY QQQ TSLA JPM XOM TLT) · BTC-USD · hourly matrix complete
scoreboard: 3468 configs / 312 lanes → 0 PROMOTED / 64 KEEP-dev / 248 KILL; max_t 1.38 vs bar 2.64
notable_negatives: TSLA-RSI-reversion t=-3.01 worse-than-hold; vol-gate subtracts value (46/60 splits)
synthesis: docs/research-round-3-results.md (PR #89; covers slices 1–8, later slices' deltas in their #90–#95 cards)
ledger_rows_added: 309 (experiments/index.jsonl 242→551 over window); tests: 437 passing (main CI run 29238187572 @ 08969bb)
rails: holdout untouched · paper lane byte-untouched · grading 2026-07-17 intact · no exchange-write code
trigger_failsafe: trig_01HCLdpcX9QNUz4Y33efgt57 (45 1-23/2 * * *, coordinator) — fired on schedule overnight
trigger_grading: trig_01FRG4uUxPh5ZGncZGfRgF2F (0 9 * * 5, business cron — rebind never delete; next fire 2026-07-17)
trigger_swtk_t7: trig_01LfwTPMGzM1fqA9CTQLgHnD (2026-07-19T16:37Z)
trigger_swtk_t14: trig_01Muk6nrt2BdxsPmDVY4arwA (2026-07-26T16:37Z)
trigger_foreign: trig_01YXNmgqYeYQ1LuepsLmbNCG (unattributable grading duplicate, recorded not deleted)
next_1: weekly grading pass 2026-07-17 (warm-up FLAT expected)
next_2: KILL-SIG verdict class proposal (PR #91 card) — owner/manager review
next_3: next research round on manager/owner direction
kit: substrate-kit v1.15.0 (vendored bootstrap.py; main at PR #75 — v1.12.0→v1.12.1 via PR #63 (ea22323), v1.12.1→v1.13.0 via PR #72 (8cc0208), v1.13.0→v1.14.0 via PR #74, v1.14.0→v1.15.0 via PR #75 (b354548, current origin/main HEAD)).
