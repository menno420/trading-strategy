# Overnight Planning Menu — 2026-07-17

> **Status:** menu (veto-ready) — authored 2026-07-16 overnight, RESEARCH-ONLY

This is a veto-ready planning menu, not a build queue: no M- or L-sized item below was built tonight (planning only), and nothing here spends the holdout, touches a broker/exchange, or configures a live API — every proposal reads only the committed dev caches via `trading_lab.data.load_ohlcv` or the paper rail via `load_paper_ohlcv`. Small, contained, reversible items (docs, linters, a coverage matrix) MAY be built on a claimed slice; anything M/L waits for an explicit owner pick from this list — vote by veto, the count is deliberately large so you strike what you don't want.

Grounding read tonight: `docs/research-round-7-plan.md` (R7-A `drawdown_reversion` / R7-B `high_proximity`, both PLAN-ONLY, not run), `docs/current-state.md` (paper-0001 WATCH/FLAT, 5,055 configs / 0 promoted, holdout SPENT), `CONSTITUTION.md`, `experiments/paper/ledger.md`, and the `src/trading_lab/` tree (32 strategy families; `sweeps.py`, `promotion.py`, `selection_gate.py`, `walkforward.py`, `paper.py`, `portfolio.py`, `ensemble.py`, `mtf.py`). Real surfaces referenced below: the 15-ticker daily basket `R7_INSTRUMENTS = R6_VOLUME_INSTRUMENTS = R4_SEASONALITY_INSTRUMENTS` (AAPL, AMZN, BTC-USD, GLD, GOOGL, JPM, META, MSFT, NVDA, QQQ, SLV, SPY, TLT, TSLA, XOM), the 8-ticker hourly cache (AAPL, AMZN, GLD, GOOGL, META, MSFT, NVDA, SLV), the 2-ticker `data/p2ext/daily/` extension (AAPL, GOOGL), and the XSEC-14 basket (`R3_XSEC_EXPANDED_INSTRUMENTS`). Every runnable proposal inherits the three standing rails: the selection-fair gate (`selection_gate.run_selection_gate` → `apply_gate`), the R5-D fixed-config row, and the `reason_class` UNGRADEABLE infra-alarm rollup; the promotion bar `promotion.min_tstat(K)` (~2.638 at K=12) is never lowered, and every KEEP is dev-candidate only (promotion CLOSED).

---

## 01. R7-C — drawdown × high-proximity conjunction band  · effort M

- **Pitch:** A genuinely new interaction family that neither R7-A nor R7-B tests alone: hold long only when a name is simultaneously deep in a trailing-peak drawdown AND has reclaimed to within `p` of its trailing N-bar close-max (a "washed-out but recovering" state). Distinct from A (pure depth state) and B (pure proximity state) — the conjunction is a new decision surface, not a re-run.
- **Effort:** M
- **Risk / reversibility:** Fully reversible — new grid `_R7C_CONJUNCTION_AXES` in `sweeps.py` + one strategy module + pinning tests; dev caches only, registers new configs honestly (K counted at the conjoined grid size).
- **Unblocks:** First interaction-family precedent for Round 7+; if it nulls (expected prior), it closes the "did we ever combine the two anomalies" question on record.

## 02. R7-D — cross-sectional drawdown ranking on XSEC-14  · effort M

- **Pitch:** Port the R7-A drawdown signal from single-name state to a cross-sectional lane: each rebalance, rank the XSEC-14 basket by depth-from-trailing-peak and go long the deepest quantile (a portfolio lane via `portfolio.py`, `R3_XSEC_EXPANDED_REBALANCE_EVERY`). Structurally distinct from `xsec_momentum`/`xsec_reversal` (return-ranked) — this ranks on drawdown depth, a signal no cross-sectional lane has used.
- **Effort:** M
- **Risk / reversibility:** Reversible — reuses the existing portfolio harness; new ranking function + grid + tests, XSEC-14 committed cache only.
- **Unblocks:** Tests whether the program's "only consistently observed effect" (drawdown) survives cross-sectionally where single-name lanes historically null.

## 03. R8 pre-registration — hourly companion to R7 families  · effort M

- **Pitch:** R7 explicitly declined hourly slices (round-6 confirmed hourly as a KILL amplifier). Pre-register a SEPARATE Round-8 plan that runs `drawdown_reversion` / `high_proximity` on the 8-ticker hourly cache with hypotheses + kill criteria fixed in advance, so the hourly question is answered under the same plan-before-outcome discipline rather than left as an informal "maybe".
- **Effort:** M (plan doc only; running is a further slice)
- **Risk / reversibility:** Zero code risk — a `docs/research-round-8-plan.md` with a `binding` badge; running remains a future claimed slice.
- **Unblocks:** Closes the declared-but-deferred hourly gap for the two newest families with a pre-registered null expectation.

## 04. Volatility-regime gating family (`vol_regime_trend`)  · effort M

- **Pitch:** A new family that conditions an existing trend entry (SMA/EMA/Donchian) on a realized-volatility regime: compute trailing-window realized vol, split into terciles, and only take trend signals in the low/mid tercile (or invert). Adjacency-declared vs `vol_filtered_trend` (R2, which filtered on a single vol threshold) — this uses a rolling-quantile REGIME label, not a fixed threshold.
- **Effort:** M
- **Risk / reversibility:** Reversible — new strategy module + a reusable `regime label` helper + grid + tests; daily caches only.
- **Unblocks:** First rolling-quantile regime family; also produces the reusable regime labeler that proposals 14 and 15 reuse.

## 05. Residualized / low-vol cross-sectional momentum  · effort M

- **Pitch:** Extend the XSEC-14 momentum lane with two documented refinements as new grid axes: (a) volatility-scaled momentum (rank on return/trailing-vol rather than raw return), and (b) a low-volatility tilt overlay. Both are structurally distinct from the raw `xsec_momentum` grid and let the cross-section speak to the classic vol-scaling anomaly.
- **Effort:** M
- **Risk / reversibility:** Reversible — additive grid axes on the existing XSEC portfolio harness + tests; XSEC-14 cache only.
- **Unblocks:** Tests whether vol-scaling rescues the cross-sectional lane that has nulled at raw-return ranking.

## 06. Pairs / statistical-arbitrage mean-reversion family  · effort L

- **Pitch:** A genuinely new relative-value family: form a spread on economically-linked committed pairs (GLD/SLV, SPY/QQQ, TLT/SPY, XOM vs the basket), z-score the spread on a trailing window, go long/short the spread at band extremes, exit at mean. Long-short and dollar-neutral — no burned family trades a spread; needs a small two-leg engine path.
- **Effort:** L (new two-leg backtest path + cointegration/z-score plumbing)
- **Risk / reversibility:** Reversible but larger surface — new engine code guarded by tests; dev caches only, no new tickers.
- **Unblocks:** Opens the entire relative-value / market-neutral class the program has never touched (all 32 families are single-name or long-only cross-sectional).

## 07. Volatility-adjusted breakout variants (`atr_donchian`, opening-range)  · effort M

- **Pitch:** Two breakout variants distinct from burned `donchian`/`channel_breakout`/`keltner_breakout`: (a) ATR-normalized Donchian where the channel width scales with trailing ATR, and (b) a daily opening-range-style band using the prior bar's range. Adjacency declared vs the fixed-width channel families.
- **Effort:** M
- **Risk / reversibility:** Reversible — new modules reusing the ATR helper already present in `atr_trailing.py`; grids + tests; daily caches.
- **Unblocks:** Tests whether normalizing breakout thresholds by volatility (a common practitioner fix) changes the program's uniformly-null breakout verdict.

## 08. Turn-of-month / event-window seasonality lane (adjacency-flagged)  · effort M

- **Pitch:** A calendar lane restricted to turn-of-month and month-boundary windows on the liquid ETFs (SPY, QQQ, TLT, GLD). Honesty up front: adjacency to R4-F, which burned the broad calendar class at 0/75 with 30 KILL-SIG — this is registered with an explicit null prior and is a LOW-priority "close it for good on the narrow window" lane, not an edge hunt.
- **Effort:** M
- **Risk / reversibility:** Reversible — `weekday_long.py` is the structural neighbor; new narrow-window grid + tests; daily caches.
- **Unblocks:** Puts the narrow turn-of-month sub-case on record so the calendar class is fully closed rather than "broad tested, narrow untested".

## 09. Cross-asset risk-on/off gate extension  · effort M

- **Pitch:** Extend the existing `crossasset_gate.py` with a term-structure / flight-to-quality gate: use TLT and GLD trend state to gate equity-index (SPY/QQQ) exposure (risk-off → flat). Distinct grid from the R4 cross-asset sweep — this gates on a bond/gold composite rather than a single asset.
- **Effort:** M
- **Risk / reversibility:** Reversible — additive grid + composite-signal helper on the existing gate module; daily caches.
- **Unblocks:** Tests the classic macro risk-on/off overlay the R4 single-asset gate did not cover.

## 10. weekly-grading.yml executor workflow (PARKED — owner-gated)  · effort M

- **Pitch:** Land the authored-but-unpushed host-owned `.github/workflows/weekly-grading.yml`, mirroring PR #134's `main-cron-verify.yml` shape: cron `'0 9 * * 5'` + `workflow_dispatch`, `permissions: contents:write` + `pull-requests:write`, checkout `main`, Python 3.11, `pip install -r requirements.txt`, run `python3 scripts/grade_paper.py` (NO args — verified contract, no `--dry-run` flag exists), §7 output to `$GITHUB_STEP_SUMMARY`, and on grade-landed runs preserve the mutated `experiments/paper/ledger.md` + `reviews.md` to a dated `claude/grading-run-*` branch + PR + always-on artifact. RESEARCH-ONLY compliant (paper rail only).
- **Effort:** M (design authored; landing is the blocked step)
- **Risk / reversibility:** Reversible workflow file — but currently WALLED. **Named blocker (exact):** auto-mode classifier "[Unauthorized Persistence]" denial (2 attempts, the second under the overnight order) + ORDER 016's "do NOT re-arm routines yet; wait for owner per-seat go." **Unblock = literally one explicit owner per-seat go line** (plus, if needed, a mode/settings change). Friday-heartbeat fallback until then: any live session runs `scripts/grade_paper.py` in-session (idempotent, no persistence); miss impact ≈ zero until ~August.
- **Unblocks:** Autonomous Friday 09:00 grading of the paper ledger without a live session — the standing weekly grading pass.

## 11. §7 reporting: auto-computed FLAT-week rollup + heartbeat line  · effort S

- **Pitch:** `paper.py` already notes the `m weeks reviewed, of which f FLAT` rollup is computable from the repo alone. Ship the small function + a one-line heartbeat/README emitter so the FLAT-week count is derived from the ledger rather than hand-appended, removing a manual step from every weekly pass.
- **Effort:** S
- **Risk / reversibility:** Fully reversible, contained — a pure read-only function over the committed ledger + tests; decides no verdict.
- **Unblocks:** Removes a hand-maintenance step and a drift source before the first 2026-07-17 grading pass.

## 12. Paper-ledger linter CLI  · effort S

- **Pitch:** A `scripts/lint_paper_ledger.py` that validates the append-only ledger schema without grading: strict ENTRY/EXIT alternation (max one open position), required §5 signal-side bullets present, no edited/backdated rows, and late-commit (MISS) detection surfaced as warnings. Reuses `paper.parse_records`.
- **Effort:** S
- **Risk / reversibility:** Fully reversible — read-only linter + tests; never mutates the ledger.
- **Unblocks:** Catches a malformed ledger row before the grader runs, protecting the tamper-evidence discipline.

## 13. Program-wide research results dashboard generator  · effort M

- **Pitch:** A generator that aggregates the per-round results docs (rounds 1–7) into one `docs/research-program-dashboard.md`: cumulative registered-configs ledger (→ 5,055, → 5,415 after R7), KEEP-dev/KILL/KILL-SIG tallies per round, best informational t vs the 2.638 bar, and the promoted count (0). One canonical scoreboard instead of seven docs to stitch.
- **Effort:** M
- **Risk / reversibility:** Reversible — docs-generation script + a rendered doc + tests on the aggregation; changes no verdict.
- **Unblocks:** Fresh-seat and owner get the whole program's honest scoreboard in one file; feeds proposal 25.

## 14. Reusable regime-detection module (`trading_lab.regime`)  · effort M

- **Pitch:** Factor the vol/trend regime labeling (rolling-quantile vol terciles, trend up/down/flat by a slope sign) into one tested `regime.py` module with causal (no-lookahead) guarantees, so families 04/09 and any future conditional lane share one audited labeler instead of re-implementing regime logic per strategy.
- **Effort:** M
- **Risk / reversibility:** Reversible — pure library module + causality tests; no run, no verdict.
- **Unblocks:** De-duplicates regime logic across proposals 04/09 and future conditional families; one place to audit for lookahead.

## 15. Data-quality / cache-integrity manifest + CI check  · effort S

- **Pitch:** Extend `data.check_integrity` into a committed `data/MANIFEST.md` (or JSON) recording each cache's ticker, timeframe, row count, date span, and a content hash, plus a CI assertion that caches match the manifest (no silent gaps, no accidental holdout bleed, no post-`PAPER_LANE_START` bar in a dev cache).
- **Effort:** S
- **Risk / reversibility:** Fully reversible — manifest + a test/CI check; read-only over committed caches.
- **Unblocks:** Reproducibility guard — any future cache refresh that changes data is caught, protecting every backtest that reads it.

## 16. Cache coverage matrix doc  · effort S

- **Pitch:** A one-page `docs/data-coverage.md` table of ticker × timeframe × date-span across `data/daily/` (15), `data/hourly/` (8), and `data/p2ext/daily/` (2), so a fresh seat instantly knows what surfaces exist before proposing a sweep on a ticker that has no cache.
- **Effort:** S
- **Risk / reversibility:** Fully reversible — a generated doc; read-only.
- **Unblocks:** Prevents wasted proposals against absent caches; complements proposals 15 and 25.

## 17. Full deflated-Sharpe implementation (Bailey & López de Prado 2014)  · effort M

- **Pitch:** ORDER 007 currently ships a min-t-stat proxy because the ledger did not record the cross-trial Sharpe variance the full deflated Sharpe needs. Implement the true deflated Sharpe ratio as an INFORMATIONAL companion (skew/kurtosis-aware SE + expected-max-of-N term from the actual trial Sharpes now recorded per round), reported alongside — never replacing — the standing `min_tstat` bar.
- **Effort:** M
- **Risk / reversibility:** Reversible — additive function in `promotion.py` + tests; informational only, the promotion bar is unchanged so no bar-lowering.
- **Unblocks:** Delivers the "prefer deflated Sharpe" half of ORDER 007 that the proxy deferred, without altering the decision rule.

## 18. Purged & embargoed walk-forward CV  · effort M

- **Pitch:** Add a López-de-Prado purged/embargoed variant to `walkforward.generate_splits`: purge train bars whose label windows overlap the test window and embargo a gap around the boundary, so leakage from overlapping horizons is removed. Offered as an alternative geometry reported alongside the standing contiguous 1008/252 split, not a replacement.
- **Effort:** M
- **Risk / reversibility:** Reversible — new split generator + tests; the standing geometry stays default so no round's comparability breaks.
- **Unblocks:** A leakage-hardened CV geometry available for future rounds that use overlapping-horizon labels.

## 19. Block / stationary bootstrap CI on the Sharpe delta  · effort M

- **Pitch:** Generalize the R5-C bootstrap (`run_r5c_bootstrap.py`) into a reusable stationary/moving-block bootstrap that returns a confidence interval on the annualized Sharpe delta vs B&H, preserving autocorrelation the i.i.d. Lo SE ignores. Reported as an informational band next to the t-stat.
- **Effort:** M
- **Risk / reversibility:** Reversible — library function + tests; informational, no bar change.
- **Unblocks:** A dependence-aware uncertainty estimate for every lane, hardening the "is this inside noise" read.

## 20. Benjamini-Hochberg FDR companion to the Bonferroni bar  · effort S

- **Pitch:** Add a Benjamini-Hochberg false-discovery-rate rollup as an INFORMATIONAL companion to the standing Bonferroni `min_tstat` bar: across a round's K lanes, report how many would clear at a controlled FDR alongside the (unchanged, more conservative) family-wise bar. Pure reporting, decides nothing.
- **Effort:** S
- **Risk / reversibility:** Fully reversible — a rollup function + tests; the promotion bar is untouched.
- **Unblocks:** A second, standard multiple-testing lens on results without weakening the conservative promotion rule.

## 21. Backtest speed + reproducible run-manifest layer  · effort M

- **Pitch:** Two contained infra wins: (a) a parquet/feather cache layer beside the gzip CSVs to cut load time on repeated sweeps, and (b) a per-run manifest (git SHA, grid hash, config counts, wall-time, library versions) written next to each run's JSON so any result is reproducible and cap-hit accounting is automatic.
- **Effort:** M
- **Risk / reversibility:** Reversible — additive cache path + manifest writer + tests; gzip CSVs remain the source of truth.
- **Unblocks:** Faster sweeps and a machine-checkable reproducibility record for every run, supporting the runtime-cap discipline.

## 22. Config-grid registry linter (anti-drift pin check)  · effort S

- **Pitch:** A test/CI linter that asserts every `_R*_AXES` grid in `sweeps.py` is pinned by a matching count/value test in `tests/test_sweeps.py` and that `r*_total_configs()` matches the declared cumulative ledger (e.g. 5,055 → 5,415 for R7). Catches a silently added or narrowed grid before it corrupts the honest config count.
- **Effort:** S
- **Risk / reversibility:** Fully reversible — a meta-test over `sweeps.py`; read-only.
- **Unblocks:** Structurally enforces the "grids in code, pinned by tests, before any run" rail against accidental drift.

## 23. Fresh-seat onboarding quickstart ("first 15 minutes")  · effort S

- **Pitch:** A `docs/onboarding-quickstart.md` that a cold seat reads to be productive fast: the RESEARCH-ONLY hard rail and holdout-SPENT status up top, the read-order (working agreement → current-state → constitution), the key module map (`load_ohlcv` / `load_paper_ohlcv` / `sweeps` / `selection_gate` / `promotion`), how to run a sweep + grade, and the plan-before-outcome ritual.
- **Effort:** S
- **Risk / reversibility:** Fully reversible — a doc; no code.
- **Unblocks:** Cuts fresh-seat spin-up and reduces the chance a new seat trips the holdout or persistence rails.

## 24. Strategy-family catalog doc  · effort S

- **Pitch:** A `docs/strategy-catalog.md` table of all 32 families in `src/trading_lab/strategies/` — one-line thesis each, the round that tested it, and its standing verdict class (KILL / KILL-SIG / KEEP-dev / burned-class) — so proposals cite adjacency accurately instead of re-deriving it from seven results docs.
- **Effort:** S
- **Risk / reversibility:** Fully reversible — a doc generated from the tree + results; read-only.
- **Unblocks:** Makes every future "new family vs variant" adjacency declaration cheap and accurate; complements proposal 13.

## 25. Reproducibility "one-command replay" doc + smoke script  · effort S

- **Pitch:** Document and script the minimal end-to-end replay of a single past lane (load a committed cache → run one grid config → walk-forward → gate → verdict) as a `scripts/replay_smoke.py` a fresh seat runs to confirm the whole rail is wired, without launching a full round. Complements the CI suite with a human-facing "prove it still works" path.
- **Effort:** S
- **Risk / reversibility:** Fully reversible — a thin smoke script + doc over dev caches; runs nothing new, promotes nothing.
- **Unblocks:** A fast trust-check of the research rail for any new seat or after any refactor.

---

## Not proposed tonight (out of rail)

Deliberately excluded so the honesty is on record — none of the following appear above, and none will be built or scheduled from this menu:

- **Broker / exchange-write capability** — no order-placement, no brokerage account, no execution API of any kind (paper lane is mock-only, `experiments/paper/**` is signal-side only).
- **Live API configuration / real-money credentials / secrets** — no live data-vendor keys, no live trading endpoints, no host provisioning of trading credentials.
- **Holdout re-open** — `data/p5holdout/` stays SPENT and unread; `unlock_holdout` is never passed; `HOLDOUT_START = 2025-01-09` enforcement is untouched.
- **Promotion to live / finding on OOS** — promotion is CLOSED; every KEEP anywhere above is dev-candidate only; no proposal lowers `min_tstat` or makes an OOS validation claim.
- **Owner-gated fetches / new tickers / R5-C BTC-USD OOS execution** — committed caches only; nothing here schedules a fetch or the R5-C escalation.
- **Re-arming routines / persistence** — no routine is armed tonight (proposal 10's workflow is parked on the exact ORDER 016 / "[Unauthorized Persistence]" wall until an owner per-seat go line).
