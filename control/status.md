# trading-lab · status
updated: 2026-07-10T02:59:21Z
phase: gen-2 running — mean-reversion × daily lane (QUEUE § Next item 2) complete; next per QUEUE § Next: item 3 trend × hourly
health: green (pytest 125 green; bootstrap check --strict --require-session-log exit 0 on the lane card; sweep validated locally before push)
last-shipped: #17 — P1 mean-reversion lane: 3 sub-families (RSI-threshold / Bollinger z-score / pullback ± trend filter) × 144 variants × 8 tickers × daily, walk-forward OOS vs B&H at 5+1 bps, results doc + 24 sweep files + 24 ledger runs + lane wrap-up (claim deleted, QUEUE item 2 DONE, session-card amendment)
blockers: none
orders: acked=001 (= inbox ORDER 005) — done=005 items 1–3 (prior sessions); standing default in force (QUEUE § Next top-to-bottom): item 2 mean-reversion × daily DONE this session via PR #17. ORDER 005 item 4 (holdout hardening) remains DEFERRED = QUEUE item 5. Inbox re-read at origin/main HEAD 2026-07-10T02:59:21Z: no orders newer than ORDER 005.
lane-result: mean-reversion (QUEUE item 2) DONE — negative headline: 3/24 family × ticker lanes beat B&H OOS with 144 variants tried; Bollinger 0/8, pullback negative outright on GLD/SLV (dips kept dipping); long/flat reversion forgoes the decade's up-drift and pays the turnover tax. Survivors GOOGL-pullback (0.85 vs 0.72), META-rsi (0.79 vs 0.65), META-pullback (0.67 vs 0.65) are P2 candidates only, NOT findings. Full honest read: docs/p1-mean-reversion-results.md.
⚑ needs-owner: (1) env setup script — paste environments/setup-universal.sh into the environment config (tested; evidence in docs/succession/ENVIRONMENT.md); (2) one-time: tick "Allow auto-merge" in repo Settings→General→Pull Requests (GraphQL arm still fails; merging via REST squash on green instead); (3) archive the dead "ORDER 001 successor" session (still listed active).
next-update-by: 2026-07-10T10:59:21Z
notes: forward-only git preserved; wrap-up batched into the lane PR per orders (no separate status PR). Holdout untouched: all sweep data_end ≤ 2025-01-08 < HOLDOUT_START, loader-enforced, no network fetches (committed daily cache). No model identifiers in repo per session policy.
