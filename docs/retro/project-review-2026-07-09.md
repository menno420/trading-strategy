# trading-lab · project review + wake-up pass — 2026-07-09

> **Status:** `audit` — owner-facing review per the wake-up ORDER (full self-review pass). Written by the project coordinator session; facts verified against the repo and the platform event log at 2026-07-09T17:04:36Z, not from memory. Companion: [self-review-2026-07-09.md](self-review-2026-07-09.md) (retro answers by ID).

## (a) What this Project is, and its TRUE current state

**Mission** (README + docs/founding-plan.md): a research-only trading-strategy lab — systematic, cost-aware, anti-overfitting search for robust signals across 8 instruments (AAPL MSFT NVDA GOOGL AMZN META GLD SLV). No live trading. Roadmap P0 scaffold → P1 known-indicator sweep → P2 walk-forward validation → P3 novel combos → P4 robustness → P5 holdout-unlocked final report.

**True state, verified 2026-07-09 (each item checked against the repo, not recalled):**
- `main` tip `4067bbb`; 5-commit history; CI fully green on tip (`tests` and `substrate-gate` both success at ~16:49Z).
- Independently re-verified this session on a fresh detached checkout: `python3 -m pytest -q` → **63 passed**, exit 0; `python3 bootstrap.py check --strict` → exit 0.
- All 3 PRs merged, no open PRs, no live branches besides `main`.
- P0 is COMPLETE and on main: cached data layer (daily 2010→now + hourly ~2.9y, 1.6 MB, HOLDOUT_START=2025-01-09 enforced in the loader), vectorized backtest engine (t+1-open fills, 5bps slippage + 1bp commission/side), 3 baselines, experiment ledger (24 seeded runs + index.jsonl), walk-forward helper, 2 CI workflows.
- ORDER status at review start: 001 done in substance (P0 merged); **002 half-done** (PR #1 was marked ready and merged at 16:48Z by menno420 — no project session was alive then — but the status heartbeat was never rewritten; `control/status.md` on main still says `acked=001 done=` with a 14:03Z timestamp); **003 not started** (`docs/retro/self-review-2026-07-09.md` did not exist). Both are closed out by this review's PRs.
- **P1 has not started**: the ledger holds exactly the 24 seeded baseline runs; no `claims/` directory exists yet (the founding plan describes lane claims but the path was never scaffolded).
- First scientific result (honest, negative): SMA-crossover and RSI-mean-reversion at default parameters underperform buy-and-hold at realistic costs on most of the universe — ledgered per the founding plan.

## (b) Agent audit — every session, agent, and subagent

Model note: model names below are as recorded in the platform event log, normalized to product names (a session policy keeps raw model-id strings out of committed artifacts; the event log retains them).

| # | Actor | Model | Tasked with | Actually delivered (verified) | Stalls / deaths / silence |
|---|-------|-------|-------------|-------------------------------|---------------------------|
| 1 | Coordinator session (project front door; author of this review) | Claude Fable 5 (1M context; Opus 4.8 configured fallback, no observed use) | Dispatch, monitoring, this review pass | Spawned #2 and #6; diagnosed env failure; handoff order; this review + heartbeat PRs | No stalls of its own. **Failure: never verified successor liveness → 2.8h blind spot.** Cause: (a) our process + (b) platform (no provision-failure event). |
| 2 | Builder session `cse_01SJkzUE6XSNKp2eiEXv7hWg` ("ORDER 001: adopt kit + P0") | Claude Fable 5 (event-log model field on every assistant event) | ORDER 001 end-to-end | All of P0 as PR #1 — verified by re-running tests + strict check on main this session | **Dead 13:00→13:30 (30.2 min) at provision** — setup-script failure, verbatim in self-review G2. Cause: (a) setup. Recovered by external resume. |
| 3 | └ subagent "Recon repo and orders" (worker) | Claude Fable 5 (inherited; no override in task events) | Read-only recon of both repos + orders | Structured recon report | One auto-mode permission denial (running kit code from the external clone) — (b) platform guardrail, correct call, ~2 min. |
| 4 | └ subagent "Adopt substrate-kit (Phase A)" (worker) | Claude Fable 5 (inherited) | Kit adoption to strict-green | Kit v1.1.0 adopted; check green | None observed. |
| 5 | └ subagent "Build P0 lab (Phase B)" (worker) | Claude Fable 5 (inherited) | Full P0 build | Data layer, engine, baselines, ledger, 63 tests | Yahoo 429 + proxy TLS reset (~10 min, (b) platform egress; worked around, documented); one dead-link strict-check fail ((c) normal work, minutes). |
| 6 | └ subagent "Push + draft PR (Phase C)" (worker) | Claude Fable 5 (inherited) | Status write, push, PR | Branch pushed, draft PR #1 opened, handoff sent | Opened DRAFT per its brief — the root of the 2.8h parked-work gap ((a) our instructions; see G1). |
| 7 | Successor session `cse_01PSBjfqwoLvFMtv9Hij5cwi` ("verify, merge, P1") | **None — cannot determine further: Claude Code never started; the only model string in its 15 events is a synthetic error stub** | Verify handoff, merge PR #1, flip status, start P1 | **Nothing. 0 turns.** | **DOA: died 10s after spawn (14:05:17Z) on the identical setup-script failure — after the fix had been reported.** Cause: (a) setup (fix not effective at provision time), aggravated by (b) platform: no failure event to the project, session listed "active" — silent for ~2.8h. |
| 8 | Coordinator's review subagents today (repo recon; transcript audit; landing worker for these PRs) | Claude Fable 5 (inherited) | Evidence gathering + landing this review | The verified facts in this document; these PRs | None. |

PRs #2 and #3 were authored by the manager lane (owner side), not by any session audited here — listed for completeness.

**Unknowables, stated plainly:** whether the env setup script is fixed *now* is not determinable from inside a running session (setup runs only at provision); the successor's "active" status may persist indefinitely despite being dead; who clicked ready/merge on PR #1 is taken from the GitHub API `merged_by` field (menno420) — the event logs of this project's sessions show none of them did it.

## (c) Retro answers

All questions in docs/retro/QUESTIONS.md answered by ID in [self-review-2026-07-09.md](self-review-2026-07-09.md) (same PR).

## (d) Efficiency verdict — where the time actually went

Timeline 12:59Z (first spawn) → 2026-07-09T17:04:36Z: **~35 minutes of dense, high-quality building** (9 commits, 112 files, tests green first try after one dead-link fix) versus **~30 minutes of provision death + ~2.8 hours of silent dead air** where the only live actor believed work was proceeding. The model-work was efficient; **the orchestration layer lost the day** — two environment-script deaths and one unverified spawn. The draft-PR convention added a further ~2.8h of parked-but-finished work (overlapping the dead air; the manager un-stuck it manually).

Redo order: (1) prove the environment contract (setup script vs multi-source checkout) before any spawn; (2) walking skeleton through the full merge path in minutes; (3) P0 build; (4) every spawn gets a liveness check; (5) READY PRs with auto-merge from the first commit. Decisions taken this pass, decide-and-flag: **D-1** coordinator executes ORDERs 002-remainder/003 itself ("do all in THIS session" + decide-and-flag); **D-2** one PR for both retro files (same deliverable class); **D-3** no lane suffix on filenames (single-lane repo — control files are unsuffixed); **D-4** status written with `acked=001,002,003 done=001,002,003` as the final PR (every done-when verifiable at its merge); **D-5** scaffold `claims/` without an explicit order (founding plan describes it; P1 requires it); **D-6** P1 opens with the trend-following lane (best-understood family; establishes the sweep pattern); **D-7** model names in this committed doc are product names, raw ids kept to the event log/chat (session policy).

## (e) ⚑ OWNER ACTIONS (only things an agent cannot do)

1. **Verify the environment setup script is REALLY fixed.** Evidence it wasn't: the successor died at 14:05:07Z provision with the identical error, after the fix was reported. Exact steps: open **claude.ai/code** → left sidebar **Environments** → select this project's environment → **Setup script** → select-all, delete, paste exactly:
```bash
#!/bin/bash
# Multi-source env: cwd is /home/user; each repo is a subdirectory.
set -u
for repo in trading-strategy substrate-kit; do
  if [ -f "$repo/requirements.txt" ]; then
    echo "[setup] installing $repo/requirements.txt"
    pip install -r "$repo/requirements.txt" || echo "[setup] pip failed for $repo (non-fatal)"
  fi
done
[ -f requirements.txt ] && pip install -r requirements.txt
exit 0
```
→ **Save**. Unblocks: every future spawned session provisioning alive instead of DOA. (Optional proof: start any throwaway session in this environment; if it says "Setup script failed", the fix didn't save.)
2. **Repo merge settings (one-time check).** github.com/menno420/trading-strategy → **Settings** → **General** → *Pull Requests*: tick **Allow auto-merge**. If you later protect `main` (**Settings → Branches → Add rule**): require status checks `tests` and `substrate-gate`, but do NOT enable "Restrict who can push", or agent merges stop working. Unblocks: the standing READY+auto-merge convention. (If this review's two PRs merged without you, agent merges already work and only the auto-merge tick matters.)
3. **Archive the dead successor session.** In the project's session list: session titled "ORDER 001 successor: verify, merge, P1" → its **⋮ menu → Archive**. It is dead but listed active; leaving it misleads fleet status. Unblocks: honest fleet dashboards.

## (f) CONTINUATION — next, without the owner

Starting immediately after this document lands (all in the current coordinator session per the standing order): (1) land the status-heartbeat PR closing ORDERs 002/003 — the deliberate last step of this review; (2) scaffold `claims/` + a ledger-schema note (P1 prerequisites, D-5); (3) **start P1**: claim the trend-following lane (SMA/EMA/MACD/Donchian parameter grids × 8 tickers × daily, walk-forward, realistic costs, variants-tried counted for multiple-testing discipline), results as ledger entries via READY PRs; (4) port the PR-lifecycle conventions into docs/collaboration-model.md. Negative results will be ledgered as first-class outcomes, per the founding plan.

## Appendix — platform walls

None hit while landing this review. (If any appear below, they were appended at landing time with exact error text.)
