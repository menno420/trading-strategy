# trading-lab · status
updated: 2026-07-09T14:02:28Z
phase: P0 shipped on branch claude/order-001-p0 (PR #TBD awaiting merge); ready to start P1 known-indicator sweep
health: green
last-shipped: #TBD — substrate-kit adoption + full P0 (data layer, engine, 3 baselines, ledger, 63 tests, CI)
blockers: none
orders: acked=001 done=
⚑ needs-owner: none
notes: done=001 flips when PR #TBD merges (done-when requires P0 merged). Decide-and-flag: (1) custom vectorized pandas engine over vectorbt/backtesting.py — sweep-scale vectorization, controlled t+1-open fills + 5+1bps costs; (2) metals via GLD/SLV ETFs over futures — cleaner free hourly data; (3) integration mode `active`; (4) HOLDOUT_START=2025-01-09 enforced in loader (default-exclude, P5-only unlock); (5) experiments/index.jsonl regenerated, never appended. First honest read: SMA-crossover and RSI-mean-reversion defaults underperform buy-and-hold at realistic costs on most of the universe (negative results ledgered). ENV NOTE for the manager: this environment's setup script previously failed — it ran git/pip at /home/user (multi-repo root) where no requirements.txt exists; repo now has a root requirements.txt so a corrected setup script should install from trading-strategy/requirements.txt. Data quirks documented in docs/p0-lab-guide.md.
