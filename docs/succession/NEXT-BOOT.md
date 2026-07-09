# gen-2 next-boot — first 10 minutes

> **Status:** `reference` — succession doc for the fresh gen-2 session. Read this file second (after control/README.md). Everything here was paid for in gen-1 time; do not re-derive it.

## Read order (files, in order, one line of why)
1. `control/README.md` — the protocol: inbox-first, status-last, one writer per file.
2. `docs/succession/NEXT-BOOT.md` — this file: walls, skeleton check, read order.
3. `control/inbox.md` — your orders; execute status:new in priority order. NEVER edit this file.
4. `control/status.md` — where gen-1 ended; open ⚑ owner items live here.
5. `docs/founding-plan.md` — BINDING methodology: walk-forward, realistic costs, holdout untouched (HOLDOUT_START=2025-01-09, loader-enforced), variants-tried counted, buy-and-hold benchmark, negative results are deliverables.
6. `docs/AGENT_ORIENTATION.md` — exact verify commands.
7. `docs/p0-lab-guide.md` — data layer + the egress-proxy workaround for yfinance (already implemented in src/trading_lab/data.py; don't re-fight it).
8. `claims/README.md` — lane claim lifecycle (check → claim → work → delete).
9. `docs/p1-trend-following-results.md` — what's already swept and the honest read; don't re-run this lane.
10. `docs/retro/wind-down-review-2026-07-09.md` — gen-1's failure classes and what they cost.
11. Any `.sessions/*.md` card — the substrate-gate REQUIRES a session card touched by every PR's diff; copy the format (Status badge, Model + time lines, work log, close-out).

## Walking-skeleton check (before any real work)
Branch → append one line to your new session card → commit → push → open a READY PR → wait for the two checks (`tests`, `substrate-gate`; ~1–2 min each) → squash-merge. If any step fails, fix THAT first — you just found the day's real problem while it was cheap. Also run locally: `python3 -m pytest -q` (86 green at handoff) and `python3 bootstrap.py check --strict` (exit 0).

## Known walls — never probe these twice (exact texts)
- Setup-script provision death: `Setup script failed with exit code 1. ... fatal: not a git repository (or any of the parent directories): .git ... ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'` — env setup runs at cwd=/home/user with repos as SUBDIRECTORIES. The tested-safe script is `environments/setup-universal.sh`.
- Silent spawn death: a session that dies at provision emits NO failure event and stays listed "active". Rule: any session you spawn must show a first heartbeat within 10 minutes or you treat it as dead and respawn (the gen-2 blueprint tightens this to 5–10 min).
- New-doc gate failures: every new doc needs `> **Status:** \`<token>\`` in its first 12 lines AND a link from a reachable doc, or substrate-gate fails with `[badge] ... missing` / `[reachable] ... orphan`.
- Yahoo/proxy: default yfinance transport dies with `curl: (35) Recv failure: Connection reset by peer` (+ intermittent 429). Already solved in src/trading_lab/data.py; use the loader.
- Cross-session steering can be unavailable: `send_message: tool is not enabled for this organization` (appeared mid-day after working earlier). Brief every session self-terminal: land READY PRs and merge on green without needing a follow-up message.
- Sibling-lane experience (team memory): tag pushes, GitHub release creation, and branch deletion return 403 for agent sessions — plan those as owner actions.
- PR platform default is DRAFT; this fleet's convention is READY-never-draft, merge on green. State it in every brief.

## Where the science stands
P0 lab verified; P1 trend-following × 8 tickers × daily complete (177 variants; 7/32 lanes beat B&H OOS — weak under multiple testing). P2 candidates: AAPL donchian, META sma/ema/donchian. Open lanes in priority order: (1) finish/absorb the video-strategy lane (see queue), (2) mean-reversion family × daily, (3) trend × hourly, (4) P2 walk-forward validation of the candidates, (5) holdout hardening (segregate data/holdout/, gate-check reads, `data_end ≤ HOLDOUT_START` in every ledger row).
