# 2026-07-13 — R3 slice 3: new tickers (dev-only)

> **Status:** `complete` — six NEW instruments (SPY, QQQ, TSLA, JPM, XOM,
> TLT) fetched via the sanctioned data path, cached, baselined, and swept
> with three existing families on the standard dev rail; honest outcome
> **0 PROMOTED / 5 KEEP (dev-candidate only) / 13 KILL** of 18 lanes, zero
> data-unavailable rows. This card was born red (`in-progress`) and flipped
> `complete` as the deliberate last content change before push; the claim
> file is deleted in this same commit.

📊 Model: fable-5 · r3-new-tickers lane (worker session) · start 2026-07-13T01:22Z

💡 **Session idea:** the cache layer records no provenance — `save_cache`
writes only bars, so once a file lands in `data/daily/` nothing in the repo
says WHICH source produced it or when. That matters concretely: the stooq
fallback in `trading_lab.data` is dividend-UNADJUSTED and flags it only as
a transient log line (`_fetch_stooq`'s `logger.warning`), so a cache built
during a Yahoo outage would silently mix unadjusted prices into a universe
of adjusted ones, corrupting every subsequent backtest without a trace.
Adopt a provenance sidecar: `save_cache` also writes
`data/{timeframe}/{ticker}.meta.json` (source name, fetch UTC, bar count,
adjusted flag), `fetch_ohlcv` returns which source won, and
`check_integrity`/a new `test_data.py` check refuses an `adjusted: false`
cache for any instrument used in a sweep (anchor: `save_cache` +
`_fetch_stooq` in `src/trading_lab/data.py`). This session fetched 6 new
caches and could only assert "yfinance won" from its own terminal
scrollback — exactly the gap. Recent cards' ideas (sweep-runner
extraction, filter-off control arms, docs-gate advisory, in-flight decay
advisory) don't cover this.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slices 1-2 (PRs #81, #82) covered new strategies/indicators over
the existing 8-ticker universe; this slice covers NEW TICKERS: candidates
SPY, QQQ, TSLA, JPM, XOM, TLT (broad market, mega-cap growth outside the
universe, financials, energy, rates) to diversify the tech-heavy universe.
Fetch ONLY via the sanctioned `trading_lab.data.fetch_ohlcv` + `save_cache`
path (the same mechanism `scripts/fetch_data.py` uses); any fetch failure is
recorded verbatim as an honest "data unavailable" row — never fabricated,
never sourced elsewhere. Backtests run on the default `load_ohlcv` dev rail
(holdout ≥ 2025-01-09 excluded; the holdout is SPENT). `config.UNIVERSE`
stays frozen at 8 tickers — new instruments are declared lane-local in
`trading_lab.sweeps`. Promotion is CLOSED post-holdout: mostly-KILL is the
expected outcome and is recorded as a first-class result.

## Work log

- 2026-07-13T01:22Z — clone hard-synced to origin/main HEAD `06e79ae`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (new tickers). Collision check: `control/claims/` at HEAD contains only
  `README.md` + `2026-07-13-order-night-run.md` — no overlap with this
  scope. Branch `claude/r3-new-tickers`; this card + the claim
  `control/claims/2026-07-13-r3-new-tickers.md` are the born-red FIRST
  commit (`9e76d71`), pushed before any build work.
- 2026-07-13T01:24Z — fetch probes, one per candidate ticker, via
  `trading_lab.data.fetch_ohlcv(ticker, "daily")` + `save_cache` (the exact
  `scripts/fetch_data.py` mechanism; network through the environment
  proxy). **All 6 succeeded on the primary yfinance source** — SPY/QQQ/JPM/
  XOM/TLT 4154 bars each (2010-01-04 → 2026-07-10), TSLA 4032 bars
  (2010-06-29 IPO → 2026-07-10). Zero data-unavailable rows; no fallback
  source needed; no wall hit (nothing to append to docs/CAPABILITIES.md).
  Cache format verified byte-convention-identical to existing caches
  (header `timestamp,open,high,low,close,volume`); `load_ohlcv` round-trip
  + `check_integrity` clean, dev rail ends **2025-01-08** for all 6. Full
  history committed as with existing caches (the loader enforces the
  holdout rail). `config.UNIVERSE` untouched. Commit `0be66f1`.
- 2026-07-13T01:25Z — grids declared in `trading_lab.sweeps` BEFORE the
  sweep ran (`R3_NEW_TICKERS_*`: donchian entry {20,40,55} × exit {10,20};
  sma_crossover fast {10,20} × slow {50,100,200}; rsi_mean_reversion
  period {2,5,14} × oversold {30} × overbought {60,70} — 6 variants/family,
  every point a subset of the family's existing published axes, tested);
  instruments lane-local, disjointness from the frozen universe tested.
  Sweep run (`scripts/run_r3_new_tickers.py`, mirrors the slice-1/2
  scripts: `load_ohlcv` default rail, costs 5 bps + 1 bp per side,
  walk-forward 1008/252 contiguous stitched OOS vs same-window same-cost
  B&H; 108 registered configs, program cumulative 1172 = 1064 prior + 108;
  plus one B&H baseline ledger run per new ticker, variants_tried=1).
  Honest verdicts (Round-2 KEEP/KILL rule; ORDER 007 t-stat at Bonferroni
  K=6 → min t 2.39 recorded per lane, informational only, promotion
  CLOSED):
  - donchian: **4/6 KILL**; XOM KEEP (0.322 vs 0.294, t=0.09), TLT KEEP
    (0.285 vs 0.196, t=0.28).
  - sma_crossover: **4/6 KILL**; XOM KEEP (0.347 vs 0.294, t=0.17), TLT
    KEEP (0.414 vs 0.196, t=0.69).
  - rsi_mean_reversion: **5/6 KILL**; JPM KEEP (0.747 vs 0.645, t=0.32).
    Worst lane TLT (−0.521 vs 0.196, t=−2.27).
  - Honest pattern: on strong-uptrend instruments (SPY/QQQ/TSLA) every
    active family loses to B&H, exactly as on the tech universe; the KEEPs
    cluster where the benchmark itself is weak (XOM, TLT B&H OOS Sharpe
    ≤ 0.3) — a low bar cleared, not an edge. All five KEEPs deep inside
    noise vs the 2.39 bar; NOT findings, nothing promoted. 18 sweep
    summaries in `experiments/sweeps/r3-new-tickers/`, 24 ledger rows (18
    top-variant runs with `variants_tried=6` + 6 B&H baselines), index
    rebuilt via `trading_lab.ledger.rebuild_index()`. Commit `7173c03`.
- 2026-07-13T01:27Z — PR **#83** opened READY (non-draft) with the full
  honest results table; no merge action by this session (auto-merge-enabler
  is the landing path).

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-roc-adx.md`, Status
`complete`) landed PR #82 clean and is the template this slice mirrored:
born-red first commit, pre-declared grids, dev-rail sweep with honest
2 KEEP-dev / 14 KILL verdicts, flip+claim-delete folded into one final
commit — correct discipline throughout, and its verify block's claimed
counts (271 passed, bootstrap exit 0) reproduce at this session's start.
Its 💡 (every gated family's grid must include the filter-off control arm)
is sound and still unimplemented — no follow-up has added `adx_min: 0.0`
to `_R3_ROC_ADX_AXES` or the proposed `test_sweeps.py` gate-neutral check;
endorsed, though slice 1's older sweep-runner-extraction idea remains the
higher-leverage one: this session hand-copied the same ~200-line sweep
script a SEVENTH time. One transfer-note its close-out enables: its two
META KEEPs (and slice 1's) can now be cheaply sanity-checked on the six
new instruments this session cached — the founding plan's "survivors must
work on instruments they were not tuned on" — without touching any new
data rail.

## Close-out

**Done:** on branch `claude/r3-new-tickers` (PR #83) —

1. Six new daily caches (`data/daily/SPY|QQQ|TSLA|JPM|XOM|TLT.csv.gz`)
   fetched via the sanctioned `trading_lab.data.fetch_ohlcv` path only;
   zero data-unavailable rows; `config.UNIVERSE` untouched.
2. Pre-declared Round-3 slice-3 grids (`src/trading_lab/sweeps.py`) +
   tests (`tests/test_sweeps.py::TestR3NewTickersGrid`, 8 tests incl.
   universe-disjointness and published-axes-subset checks).
3. Sweep script `scripts/run_r3_new_tickers.py` + 18 lane summaries under
   `experiments/sweeps/r3-new-tickers/` + 24 ledger rows (18 top-variant +
   6 buy-and-hold baselines) + rebuilt `experiments/index.jsonl`.
4. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 279 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-new-tickers.md`
→ exit 0 after this flip. Integrity at close: dev rail only (every lane
`data_end = 2025-01-08`), holdout (SPENT) untouched, `unlock_holdout`
never passed, paper-lane files byte-untouched, `control/inbox.md` +
`control/status.md` byte-untouched, market data fetched ONLY via
`trading_lab.data.fetch_ohlcv`, no broker/order/exchange code, no
promotion/finding language beyond the recorded KILL/KEEP-dev verdicts, NO
merge action taken by this session.

**Next (guard recipe):** none owed for correctness. Follow-up candidates:
the sweep-runner extraction (slice 1's 💡, endorsed again — seventh copy),
the filter-off control-arm convention (slice 2's 💡), the cache-provenance
sidecar (this card's 💡), and the now-cheap transfer check of the
META/JPM/XOM/TLT dev-candidates across instruments they were not tuned on.
All five KEEPs are dev-candidates only; any OOS test of them is
OWNER-GATED behind a new pre-registered protocol on post-2026 data, per
docs/research-round-2-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
