# 2026-07-13 — R4-B: execution-cost sensitivity re-grade of round-3 KEEPs

> **Status:** `complete` — Round-4 slice R4-B landed exactly as
> pre-registered (`docs/research-round-4-plan.md` § R4-B, merged before
> this session started): all **58** round-3 KEEP-dev lanes (the R4-A KEEP
> universe, PR #100) re-graded at **2×** (10 bps + 2 bp per side) and
> **4×** (20 bps + 4 bp) baseline costs, same rail, same walk-forward
> windows, same chosen variants — NO re-search, implemented literally as
> a frozen replay of each lane's committed per-split params. Honest
> result: **42 survive 2× / 25 survive 4× / 0 KILL-SIG at stress /
> 0 SKIPPED** — the pre-registered hypothesis ("most or all flip to
> KILL") is NOT confirmed (72% survive 2×), and hourly lanes die at twice
> the daily rate. Max t anywhere at 2× is 1.315 vs the unchanged 2.638
> bar. Report-only, NOT ledgered (deliberate, recorded). Every r3 file
> byte-untouched; holdout SPENT; promotion CLOSED. This card was born red
> (`in-progress`) and flipped `complete` as the deliberate last content
> change before push; the claim file is deleted in this same commit.

📊 Model: fable-5 · trading-research (worker session) · start 2026-07-13T09:48:37Z

💡 **Session idea:** the walk-forward summaries turned out to contain a
complete, replayable execution trace — frozen per-split params + exact
positional windows reproduced every one of 58 committed stitched OOS
Sharpes to 1e-8 from cold cache, which is what let this "128 re-runs"
slice finish in 8 seconds with zero re-search. That property is worth
pinning before it silently rots: a standing `replay` test (or bootstrap
subcommand) that re-derives N randomly-chosen committed lanes' OOS
Sharpes from their `per_split` blocks and fails on drift would (a) catch
cache or strategy-code drift that silently invalidates committed
verdicts, and (b) guarantee future robustness re-grades (R4-C committees
need exactly these frozen member positions) stay this cheap. Differs
from the r4-killsig card's tally-check idea: that reconciles *prose
aggregates* to artifacts; this reconciles *artifacts* to the code+data
that claim to reproduce them.

## Why this session exists

Round 4 slice R4-B (`docs/research-round-4-plan.md` @ main, pre-registered
and merged before this session started): the 58 round-3 KEEP-dev lanes
(the KEEP universe re-graded by R4-A, PR #100,
`experiments/sweeps/r4-killsig-regrade/summary.json`) were graded only at
baseline costs (5 bps slippage + 1 bp commission per side). KEEPs cluster
on weak benchmarks with small margins — exactly what realistic execution
costs erase. R4-B re-grades every KEEP-dev lane at two stressed cost tiers,
**2×** baseline (10 bps + 2 bp) and **4×** baseline (20 bps + 4 bp), on the
same rail, same walk-forward windows, same chosen variants (NO re-search:
stressing costs must not become a second selection pass — pre-registered).
Kill criterion per lane per tier: KILL iff stitched OOS Sharpe ≤ same-window
same-cost B&H Sharpe or ≤ 0. A lane keeps dev-candidate status only if it
survives the 2× tier; 4× is a robustness gradient. Pre-registered
hypothesis: most or all KEEPs flip to KILL. Owner mandate: ORDER 012
generative rung; bar unchanged; holdout SPENT; promotion CLOSED.

## Work log

- 2026-07-13T09:48Z — branch `claude/r4-cost-sensitivity` cut from
  origin/main HEAD (`08ddbd4`, the merged R4-A slice). Collision check:
  `control/claims/` at HEAD holds morning-tally + night-report +
  order-night-run — no overlap. Born-red FIRST commit `fcb2e2e` (this
  card `in-progress` + claim
  `control/claims/2026-07-13-r4-cost-sensitivity.md`), pushed before any
  implementation; PR **#101** opened READY (non-draft) immediately after,
  Before/After first, citing plan § R4-B, PR #100 (KEEP universe), and
  ORDER 012.
- 2026-07-13T09:52Z — method decision, recorded BEFORE running: the plan's
  registered clause "same chosen top variant per lane (no re-search:
  stressing costs must not become a second selection pass)" rules out
  re-running the train-window grid selection at stressed costs (that
  argmax IS a selection pass and would search for cost-robust variants).
  Implemented literally instead: the committed r3 per-lane JSONs record
  the walk-forward's chosen params per split plus exact positional test
  windows, so the script replays those FROZEN choices and re-prices the
  identical trades at each tier (positions depend only on prices, never
  costs). Verified first on 3 lanes (daily, hourly, gated): baseline
  replay reproduces the committed stitched OOS Sharpe exactly.
- 2026-07-13T09:55Z — commit `d20587b`, the whole slice:
  - `scripts/run_r4_cost_sensitivity.py` (docstring-first, POST-HOLDOUT
    DEV-ONLY banner, ORDER 012 + plan § R4-B citations): KEEP universe
    asserted = 58 from the R4-A report; per lane — dev-rail load via
    `load_ohlcv` (data_end ≤ 2025-01-08 asserted), cache-alignment check
    (data_start/data_end/n_bars vs committed), FIDELITY GUARD (baseline
    replay must reproduce the committed OOS Sharpe within 1e-8, else the
    lane is SKIPPED with the verbatim reason — never approximated
    silently), then 2×/4× replay + same-window same-cost B&H + the
    pre-registered kill rule + `grade_promotion` t-stat at the lane's own
    recorded K (informational) + `classify_verdict` KILL-SIG flag.
  - Ran it: **58/58 graded, 0 SKIPPED** (the guard fired nowhere — all 58
    baseline Sharpes reproduced), full sweep **8.2 s**. Result: **42
    survive 2×, 25 survive 4×** (gradient monotone lane-by-lane, no
    anomalies), **0 KILL-SIG** at either tier, max t at 2× = 1.315
    (BTC-USD bollinger_breakout) vs bar 2.638. Structure: hourly death
    rate 8/19 at 2× vs daily 8/39; all 5 BTC-USD daily KEEPs survive both
    tiers; flashy hourly lanes (AAPL rsi 1.788, GLD aroon 2.068) die at
    the first rung against their strong benchmarks.
  - Output `experiments/sweeps/r4-cost-sensitivity/`: 116 per-lane-per-tier
    detail JSONs (r3 schema core + `cost_tier`/`cost_multiplier`/
    `no_research`/`baseline` provenance) + rollup `summary.json` (per-lane
    baseline verdict, 2×/4× verdict+sharpe+benchmark+tstat, headline
    counts, runtime). LEDGER DECISION, deliberate: **report-only, NOT
    ledgered** — no new config was searched (frozen replay of committed
    choices), so top-variant rows would duplicate the 58 r3-ledgered rows
    at different costs; `experiments/index.jsonl` byte-untouched;
    rationale recorded in the rollup, the detail files, and the results
    doc.
  - 13 new tests (`tests/test_cost_sensitivity.py`): tiers exactly 2×/4×
    the committed baseline and the pre-registered bps verbatim; engine
    RECEIVES 10/2 and 20/4 per split (spy on `run_backtest`) and records
    them in `meta`; higher costs never increase net Sharpe on the same
    trades (engine-level and stitched-replay-level, strict drop with real
    turnover); frozen positions cost-independent; grade rule boundaries
    (tie → KILL, ≤0 → KILL, None/NaN → KILL); unknown strategy → LaneSkip
    before any data load; committed-artifact pin (aroon AAPL 2× detail
    reproduces from the committed r3 lane; rollup counts internally
    consistent). No existing test touched.
  - `docs/research-round-4-results.md` § R4-B appended: headline,
    hypothesis NOT confirmed stated up front, counts table, notable
    survivors with informational t-stats, notable deaths first-class, the
    64-vs-58 KEEP-universe scope reconciliation (same spirit as R4-A's
    302-vs-~312 note), ledger decision, and the explicit
    promotion-remains-CLOSED statement.
- 2026-07-13T09:56Z — verify: `python3 -m pytest -q` → **468 passed**
  (455 on main + 13 new); pre-flip `bootstrap.py check --strict
  --require-session-log --session-log <this card>` red ONLY on the
  designed born-red gate. Pushed `d20587b`.
- 2026-07-13T09:58Z — flip + claim-delete folded into this final commit.
  No merge action by this session; the auto-merge-enabler is the landing
  path.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r4-killsig.md`, Status
`complete`) landed PR #100 clean — the R4-A re-grade whose 58-KEEP report
is this session's entire input universe. Its verify block reproduces at
this session's start: 455 passed matches its claimed count exactly, and
its summary.json's KEEP rows carried every field this slice needed
(source_file, sweep, strategy, instrument, timeframe). Three observations
from building on it: (1) its machine-readable report is what made R4-B's
scope unambiguous — the plan says "64 after PR #95" KEEPs but the
committed KEEP surface is 58, and because R4-A had already normalized the
universe into one artifact this session could assert the count instead of
re-litigating prose (its own 💡, tally reconciliation, is validated a
second time by this exact gap); (2) its `classify_verdict` landed exactly
where R4-B needed it — applied per stressed tier here with zero adaptation,
and the "future runners emit the three-way verdict natively" forecast in
its Close-out came true one session later; (3) one mild friction: its
report rows carry `new_verdict` while the r3 lane files carry `verdict`
("KEEP (dev-candidate only)") — harmless, but a shared verdict-string
constant would have saved the `.startswith("KEEP")` matching this session
inherited from its script. No defect found in its work.

## Close-out

**Done:** on branch `claude/r4-cost-sensitivity` (PR #101) —

1. `scripts/run_r4_cost_sensitivity.py` — pre-registered R4-B executed
   literally: frozen replay of all 58 KEEP-dev lanes' committed
   walk-forward choices at 2× and 4× costs, same windows, identical
   trades, NO second selection pass; baseline fidelity guard (1e-8) with
   verbatim-reason SKIP semantics (0 fired).
2. `experiments/sweeps/r4-cost-sensitivity/` — 116 per-lane-per-tier
   detail JSONs + rollup `summary.json`: **42/58 survive 2× (keep
   dev-candidate status), 25/58 survive 4×, 0 KILL-SIG at stress,
   0 SKIPPED**; hypothesis "most or all flip" honestly NOT confirmed.
   Report-only, NOT ledgered (deliberate, rationale recorded);
   `experiments/index.jsonl` and every `experiments/sweeps/r3-*/` file
   byte-untouched.
3. `docs/research-round-4-results.md` § R4-B — headline, counts, named
   survivors with informational t-stats (max 1.315 vs bar 2.638), deaths
   first-class, scope reconciliation, promotion CLOSED restated.
4. 13 new tests (`tests/test_cost_sensitivity.py`); no existing test
   weakened or deleted; the multiple-testing bar untouched (each lane
   graded at its own recorded K).
5. This card (born-red first commit `fcb2e2e` → implementation `d20587b` →
   flipped `complete` last) — claim file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 468 passed (455 on main + 13 new).
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r4-cost-sensitivity.md`
→ green after this flip (pre-flip the only red was the designed born-red
gate). Integrity at close: diff touches only
`scripts/run_r4_cost_sensitivity.py` (new),
`experiments/sweeps/r4-cost-sensitivity/` (new),
`tests/test_cost_sensitivity.py` (new), `docs/research-round-4-results.md`
(appended section), `.sessions/`, `control/claims/` (deletion). Every
`experiments/sweeps/r3-*/` file and `experiments/runs/` byte-untouched
(additive only, as ordered), holdout (SPENT) untouched, `unlock_holdout`
never passed, `data/p5holdout/` untouched, `experiments/paper/**`
byte-untouched, paper grading never run, `control/inbox.md` +
`control/status.md` + `control/outbox.md` byte-untouched, no triggers
created or modified, no broker/order/exchange code, NO merge action taken
by this session.

**Next (guard recipe):** none owed for correctness. Follow-ups now
unblocked: the 42-lane 2×-surviving dev-candidate list is the natural
member pool for R4-C committees (and the frozen-replay helper here
computes exactly the per-split member positions R4-C needs); the 16
2×-deaths shrink the candidate list honestly before any composition work;
the replay-drift pin (this card's 💡) would keep committed verdicts
reproducible mechanically. Any OOS test of any survivor remains
OWNER-GATED on post-2026 data.

Session end: badge flipped `complete` in this final content commit before
push.
