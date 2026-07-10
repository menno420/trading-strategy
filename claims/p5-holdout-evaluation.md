# Claim — P5 one-shot holdout evaluation (ORDER 008)

- session: https://claude.ai/code/session_01GXuCNmyssjJzCUJ2iko1HP
- started-at: 2026-07-10T16:29:53Z
- branch: `p5-holdout-evaluation` (PR opens READY off this claim commit)
- order: ORDER 008 (control/inbox.md, 2026-07-10T15:33Z — P5 holdout unlock,
  owner delegation Q-0262.2; sequencing gate ORDER 007 satisfied, PR #36)
- binding procedure: docs/p5-holdout-protocol.md (pre-registered, one shot)
- scope: the closed §1 subject list — 13 subjects (1 primary AAPL-donchian
  daily + 12 secondaries across trend-daily, video-daily,
  mean-reversion-daily, trend-hourly lanes) + 13 B&H benchmarks, frozen §2
  params, §3 engine settings, §4 window (2025-01-09 → data end), verdicts
  by §5, denominators by §6, ledger rows stamped `holdout_unlocked=True`,
  results into docs/final-report.md §Holdout. Nothing else; the unlock
  kwargs appear nowhere outside this lane.
- release: this file is deleted in the lane's final PR when the report
  lands (claim lifecycle per claims/README.md).
