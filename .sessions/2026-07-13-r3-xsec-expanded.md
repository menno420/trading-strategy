# 2026-07-13 — R3 slice 7: cross-sectional lane on the expanded 14-ticker universe (dev-only)

> **Status:** `complete` — the lab's PORTFOLIO surface expanded: the
> existing `xsec_momentum` re-run on the 14-instrument all-equity/ETF
> basket `XSEC-14` (zero strategy-code change) plus the NEW
> `xsec_reversal` mirror thesis (weekly long-the-losers), dev rail only;
> honest outcome **0 PROMOTED / 6 KEEP (dev-candidate only, all
> xsec_momentum, best t 0.65 vs the 2.39 bar) / 6 KILL (all
> xsec_reversal)** of 12 configs. This card was born red (`in-progress`)
> and flipped `complete` as the deliberate last content change before
> push; the claim file is deleted in this same commit.

📊 Model: fable-5 · r3-xsec-expanded lane (worker session) · start 2026-07-13T02:21Z

💡 **Session idea:** the portfolio lanes' verdicts hinge on a benchmark
whose composition silently DRIFTS: `basket_buy_and_hold_result` buys
equal weights once and never rebalances, so by the end of a 2012→2025
window the "equal-weight" benchmark is in fact dominated by whatever
compounded hardest (NVDA/TSLA here), and "beat the benchmark" partly
measures "did the rule hold the winners the benchmark itself drifted
into". The record never shows this: `benchmark_*_metrics` carries
Sharpe/CAGR but nothing about what the benchmark had BECOME. Record
benchmark concentration alongside benchmark metrics — the drifted
end-weight vector, its HHI, and effective N (1/HHI) at window start/end
(the held_weights panel already computed at benchmark time has all of
it, zero new simulation) — and add a second, informational benchmark
arm: the PERIODICALLY-REBALANCED equal-weight basket at the same costs
(one extra `run_portfolio_backtest` call with decision rows every 21
bars), so every portfolio verdict is readable against both "buy once and
drift" and "stay equal-weight". Test targets: drifted end-HHI > start-HHI
on a diverging synthetic panel; effective-N bounds (1 ≤ 1/HHI ≤
n_instruments); rebalanced-arm turnover > B&H-arm turnover. Not covered
by recent cards' ideas (OOS activity line, cost-drag/breakeven bps,
sweep-verdicts index, sweep-runner extraction, control arms,
cache-provenance sidecar): those instrument the STRATEGY side of the
comparison; this instruments the benchmark side, which only exists in
the portfolio lanes and just became load-bearing (6 KEEPs cast against
a drifted basket this session).

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slices 1-6 (PRs #81-#86) are merged. This slice expands the
lab's only PORTFOLIO-level lane (Round 2 R3, `xsec_momentum` over the
9-instrument XSEC-9 basket) onto the expanded 14-ticker daily equity/ETF
surface (the frozen 8-ticker universe minus BTC-USD, plus the six slice-3
instruments SPY/QQQ/TSLA/JPM/XOM/TLT), and adds the mirror thesis:
short-term cross-sectional REVERSAL (long the k worst performers over the
past N days, weekly rebalance) — same portfolio plumbing, long/flat only.

## Work log

- 2026-07-13T02:21Z — clone hard-synced to origin/main HEAD `554cc52`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its "TRADING RESEARCH: expand the backtest surface" lane
  (slice 7, cross-sectional lane on the expanded universe). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-xsec-expanded`; this card + the claim
  `control/claims/2026-07-13-r3-xsec-expanded.md` are the born-red FIRST
  commit (`6a6fc24`), pushed before any build work. Read the whole Round-2
  R3 lane first (strategy, `trading_lab.portfolio`, script, XSEC-9
  summary) to mirror its methodology exactly.
- 2026-07-13T02:25Z — commit `529f798`: one NEW strategy + pre-declared
  grids + tests, all BEFORE the sweep ran. `xsec_reversal` (N, k): rank
  by trailing N-bar total return on the aligned common index, long
  equal-weight the BOTTOM-k, weekly (5-bar) rebalance frozen (monthly
  would time-average away the short-horizon signal), long/flat, no
  leverage; identical panel interface / NaN-row encoding / warm-up /
  anchored schedule / column-order tie-break as `xsec_momentum`
  (ambiguities resolved against the strategy, R2 convention).
  `xsec_momentum` needed NO code change — the universe was already a
  parameter of the panel interface. Grids in `trading_lab.sweeps`:
  momentum L {63,126,252} × k {2,3} (the Round-2 axes VERBATIM, asserted
  by test) = 6; reversal N {5,10,21} × k {2,3} = 6; portfolio
  accounting → 12 registered configs, basket `XSEC-14` = the 14
  all-equity/ETF daily caches, alphabetical (BTC-USD deliberately
  excluded to keep the common index on exchange trading days).
  18 new tests: `TestXsecReversal` mirrors `TestXsecMomentum` (bottom-k
  ranking, weekly schedule, equal-weighting, laggard rotation,
  tie-break, causality/prefix-invariance, validation, plus a
  momentum-complement mirror test) + `TestR3XsecExpandedGrid`.
- 2026-07-13T02:26Z — sweep run (`scripts/run_r3_xsec_expanded.py`,
  mirrors `run_r2_xsec_momentum.py` exactly: committed caches only, zero
  network fetches, `load_ohlcv` default rail with `data_end ≤ 2025-01-08`
  additionally asserted per ticker; costs 5 bps + 1 bp per side; aligned
  common index 3180 bars 2012-05-18 → 2025-01-08; per-config FIXED-rule
  walk-forward 1008/252, 8 splits, stitched OOS 2016-05-23 → 2024-05-24
  (2016 bars ≈ 8 years); benchmark = equal-weight XSEC-14 B&H, same
  costs, OOS Sharpe 1.193). **Short-history handling, stated honestly:**
  the R2 convention (index intersection starts at the latest-starting
  instrument — BTC-USD 2014 there) is reused unchanged; here the
  truncating instrument is **META (2012-05-18), not TSLA (2010-06-29)**
  — the task brief expected TSLA to bind, but META's IPO is 23 months
  later; both are recorded per-instrument in `instrument_first_bars`
  and the script asserts the common start equals the latest first bar.
  Honest verdicts (Round-2 §6 rule; ORDER 007 t-stat at Bonferroni K=6 →
  min t 2.39 recorded per config, informational only, promotion CLOSED):
  - `xsec_momentum`: **6/6 KEEP (dev-candidate only)** — OOS Sharpe
    1.219–1.425 vs bench 1.193, t 0.07–0.65. Honest read: a +0.03..+0.23
    Sharpe tilt on an already-strong benchmark, weaker in t-stat terms
    than the same rule on XSEC-9; nothing near promotable.
  - `xsec_reversal`: **6/6 KILL** — OOS Sharpe 0.515–0.918, every config
    0.28–0.68 below the benchmark, t −1.92..−0.78. Weekly long-only
    loser-buying on large caps at 6 bps/side in a momentum regime; the
    mirror thesis is dead on this surface and the KILL is the
    deliverable.
  - Cross-family: same basket/window/costs/plumbing — ranking DIRECTION
    swings stitched OOS Sharpe by ~0.9 while parameters move it ≤0.2.
    2 sweep summaries in `experiments/sweeps/r3-xsec-expanded/`, 2
    ledger rows (`XSEC-14`, `variants_tried=6` each), index rebuilt via
    `trading_lab.ledger.rebuild_index()`. Commit `592186a`.
- 2026-07-13T02:31Z — PR **#87** opened READY (non-draft) with the full
  honest results table; no merge action by this session (auto-merge-enabler
  is the landing path). Flip + claim-delete folded into this final commit.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-breakout.md`,
Status `complete`) landed PR #86 clean — born-red first commit, grids
declared before the run, committed exit semantics stated up front,
flip+claim-delete folded into one final commit — correct discipline
throughout, and its verify block reproduces from this session's start:
its 336 passed + this session's 18 new tests = the 354 observed here,
and its 24 `r3-breakout` sweep JSONs are on main (all `variants_tried=12`,
`data_end=2025-01-08`) exactly as claimed. Its honest-pattern readings
transfer cleanly to this slice: "KILLs are deepest where B&H is
strongest" reappears at portfolio level (the basket benchmark's 1.193
OOS Sharpe is what makes every reversal config a KILL and every momentum
KEEP marginal), and its META observation gets a twist here — META is no
longer a KEEP-flatterer but the instrument whose IPO truncates the whole
lane's common window. Its 💡 (per-lane OOS activity line + LOW-ACTIVITY
qualifier via walk_forward exposing stitched test-window positions) is
sound and still unimplemented; endorsed — and noteworthy for THIS lane:
`portfolio_walk_forward` has the same blind spot (stitched OOS carries
returns only, no turnover/exposure), so the plumbing it proposes should
be built once for both walk-forwards. One nit: its OOS-window line in
the PR table ("2520 bars ≈ 10 years for 10 tickers") compresses per-
ticker differences into a footnote — this card's lane records
`instrument_first_bars` per instrument instead, which is the cleaner
honest form.

## Close-out

**Done:** on branch `claude/r3-xsec-expanded` (PR #87) —

1. One NEW portfolio strategy
   (`src/trading_lab/strategies/xsec_reversal.py`) + registration +
   family constant `R3_XSEC_EXPANDED_FAMILY` (`strategies/__init__.py`)
   + pre-declared grids (`src/trading_lab/sweeps.py`) + 18 new tests
   (`tests/test_strategies.py`, `tests/test_sweeps.py`). No change to
   `xsec_momentum` (universe already parameterized).
2. Sweep script `scripts/run_r3_xsec_expanded.py` (Round-2 R3 portfolio
   methodology mirrored exactly; per-ticker dev-rail assertion;
   short-history handling = R2's index-intersection convention, with the
   honest note that META, not TSLA, binds the common window) + 2 lane
   summaries under `experiments/sweeps/r3-xsec-expanded/` + 2 ledger
   rows + rebuilt `experiments/index.jsonl`.
3. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 354 passed.
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-xsec-expanded.md`
→ exit 0 after this flip (pre-flip the only red was the designed born-red
gate). Integrity at close: dev rail only (`data_end = 2025-01-08`,
asserted per ticker in-script), holdout (SPENT) untouched,
`unlock_holdout` never passed, paper-lane files byte-untouched,
`control/inbox.md` + `control/status.md` byte-untouched,
`config.UNIVERSE` untouched, committed caches only (zero network
fetches), no broker/order/exchange code, no promotion/finding language
beyond the recorded KILL/KEEP-dev verdicts, NO merge action taken by
this session.

**Next (guard recipe):** none owed for correctness. Follow-up candidates:
benchmark-drift instrumentation + rebalanced-EW benchmark arm (this
card's 💡 — portfolio lanes only), the OOS activity line (slice 6's 💡,
endorsed here; build the stitched-positions plumbing once for BOTH
walk-forwards), the sweep-verdicts index (slice 4's 💡). The 6 momentum
KEEPs are dev-candidates only; any OOS test of them is OWNER-GATED
behind a new pre-registered protocol on post-2026 data, per
docs/research-round-2-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
