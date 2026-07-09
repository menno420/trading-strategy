# gen-1 → gen-2 queue state

> **Status:** `reference` — roadmap/queue at wind-down (2026-07-09T19:57:47Z). Nothing lives only in chat.

## Done (all merged to main, CI green)
- P0 lab: data layer (8 tickers, holdout-locked), vectorized engine (t+1-open, 5+1 bps), 3 baselines, ledger, walk-forward helper, 86 tests, 2 CI gates — PR #1.
- Gen-1 audits: PRs #4/#5 (agent audit incl. DOA forensics, retro answers, heartbeat).
- P1 trend-following × all8 × daily: PRs #6/#7 (177 variants, honest negative headline, claims protocol scaffolded).
- Wind-down succession: this PR + the marker PR.

## In flight
- video-strategy lane (session started 18:53Z): no PR, no branch, and no claim file visible as of 19:55Z — session presumed still extracting/building; it is briefed self-terminal to land READY PRs and merge on green. Source video: https://youtu.be/G6l6HfMbOLc — task: transcript → precise rules + ambiguities → multiple interpretations as competing systems vs B&H. If its PR is open-ready-green at archive time, merging it is a one-click owner action; if it never landed, gen-2 re-runs the brief (it is fully specified in the session's founding message and reproduced here in essence).

## Next (priority order, from NEXT-BOOT §Where the science stands)
1. Video-strategy lane completion/absorption. 2. Mean-reversion × daily sweep. 3. Trend × hourly. 4. P2 validation of AAPL-donchian + META-trend candidates. 5. Holdout enforcement hardening. 6. Port PR-lifecycle conventions into docs/collaboration-model.md (carried over, still undone).

## ⚑ Owner clicks outstanding
See control/status.md — env setup script verification (paste-ready script now at environments/setup-universal.sh), auto-merge tick, archive the DOA successor session.
