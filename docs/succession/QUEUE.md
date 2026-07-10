# gen-1 → gen-2 queue state

> **Status:** `reference` — roadmap/queue at wind-down (2026-07-09T19:57:47Z). Nothing lives only in chat.

## Done (all merged to main, CI green)
- P0 lab: data layer (8 tickers, holdout-locked), vectorized engine (t+1-open, 5+1 bps), 3 baselines, ledger, walk-forward helper, 86 tests, 2 CI gates — PR #1.
- Gen-1 audits: PRs #4/#5 (agent audit incl. DOA forensics, retro answers, heartbeat).
- P1 trend-following × all8 × daily: PRs #6/#7 (177 variants, honest negative headline, claims protocol scaffolded).
- Wind-down succession: this PR + the marker PR.

## In flight
- video-strategy lane — **session DOA at provision 2026-07-09T18:53:14Z** (identical setup-script error, third kill; the env fix never took effect). The lane never started: no PR, no branch, no claim, no work. Lane inputs are now salvaged in `docs/research/video-source-2026-07-09.md` (full transcript of https://youtu.be/G6l6HfMbOLc, source metadata, similar-video candidates, first-pass rules extraction + ambiguities). Gen-2 resumes from there: build multiple faithful interpretations of the stated rules as competing systems vs each other and vs B&H, per founding-plan discipline.

## Next (priority order, from NEXT-BOOT §Where the science stands)
1. Video-strategy lane completion/absorption. **DONE/ABSORBED 2026-07-10**
   (gen-2, lane `video-strategy__btcusd__multi`): 3 interpretations × 92
   variants × BTC-USD × daily, walk-forward OOS vs B&H — see
   `docs/p1-video-strategy-results.md`; dual-EMA control negative-complete,
   supertrend_flip / macd_supertrend carried to P2 as candidates.
2. Mean-reversion × daily sweep. **DONE 2026-07-10** (gen-2, lane
   `mean-reversion__all8__daily`): 3 sub-families (RSI-threshold,
   Bollinger/z-score band reversion, pullback ± trend filter) × 144
   variants × 8 tickers × daily, walk-forward OOS vs B&H — see
   `docs/p1-mean-reversion-results.md`; 3/24 lanes beat B&H (the negative
   result is the headline), GOOGL-pullback / META-rsi / META-pullback
   carried to P2 as candidates only.
3. Trend × hourly. **DONE 2026-07-10** (gen-2, lane
   `trend-following__all8__hourly`): the daily trend grids (4 families ×
   177 variants) re-run on hourly bars × 8 tickers (committed cache
   2023-08 → 2025-01, ~2476 bars), walk-forward OOS vs B&H — see
   `docs/p1-trend-hourly-results.md`; 5/32 lanes beat B&H over a single
   ~8.5-month OOS regime (the negative result is the headline; MACD churn
   is cost-eaten at 1,638 bars/yr), GOOGL-sma/ema/donchian, AMZN-donchian,
   META-macd carried to P2 as candidates only.
4. P2 validation of AAPL-donchian + META-trend candidates (plus the
   mean-reversion candidates from item 2 and the trend-hourly candidates
   from item 3). **DONE 2026-07-10** (lane `p2-validation`): all 14 open
   candidates given verdicts with params frozen from the P1 sweep JSONs —
   1 PROMOTED-TO-FINDING (AAPL-donchian, Sharpe 0.62 vs B&H 0.54 on
   1980→2009 pre-consumption data), 1 KILLED (GOOGL-pullback), 12
   UNVALIDATABLE-PRE-HOLDOUT (P1 consumed every pre-holdout bar in their
   timeframes; exact math in the doc) — see
   [docs/p2-validation-results.md](../p2-validation-results.md).
5. Holdout enforcement hardening. **DONE 2026-07-10** (gen-2, lane
   `holdout-collab`): loader rail re-verified (filter runs before
   start/end slicing, applies under `data_dir=` overrides incl.
   `data/p2ext/`) and edge cases pinned in tests; ledger now refuses any
   record with `data_end >= HOLDOUT_START` at both `build_record` and the
   `write_run` choke point unless `holdout_unlocked=True` stamps a visible
   self-declaring marker (P5-only); a CI audit test parses every
   `experiments/index.jsonl` row and every `experiments/runs/*.json` for
   boundary violations; contract + residual-bypass rule ("all research
   code loads via `load_ohlcv`") documented — see
   [docs/holdout-enforcement.md](../holdout-enforcement.md). 6. Port PR-lifecycle conventions into docs/collaboration-model.md (carried over). **DONE 2026-07-10** (gen-2, lane `holdout-collab`): the conventions the repo demonstrably practices (READY-never-draft, arm-then-REST-squash-on-green with the two-way arm wall, self-merge grant, post-merge review, terminal refusal branch, heartbeat-before-work, claims lifecycle, status ender, substrate-gate interplay) ported as verified against PRs #14–#24 — see [docs/collaboration-model.md](../collaboration-model.md).
7. P4 cross-instrument transfer validation. **DONE 2026-07-10** (gen-2,
   lane `p4-transfer__multi__daily-hourly`): the 13 P2 subjects (12
   UNVALIDATABLE-PRE-HOLDOUT + the promoted AAPL-donchian) run with
   params frozen verbatim from the P1 sweep JSONs on every other
   committed instrument in their timeframe (daily × 8, hourly × 7; 99
   backtests, 0 new variants), full pre-holdout windows vs B&H,
   pre-registered ≥2/3 / ≥1/3 verdict rule — **13/13 TRANSFER-FAILED**
   (13/99 pairs beat B&H; even the P2-promoted AAPL-donchian failed 1/8;
   the negative result is the headline) — see
   [docs/p4-transfer-results.md](../p4-transfer-results.md). No transfer
   verdict promotes anything; holdout untouched.
8. P5 final-report prep: holdout unlock protocol + ranked report
   skeleton — ⚑ owner may want to gate the unlock.
   **PREP DONE 2026-07-10** (gen-2, lane `p5-prep`): pre-registered
   one-shot holdout evaluation protocol landed —
   [docs/p5-holdout-protocol.md](../p5-holdout-protocol.md) (closed
   13-subject list: primary AAPL-donchian 15/5 daily + 12 pre-registered
   secondaries, params frozen verbatim from the P1 sweep JSONs, engine
   defaults, holdout window 2025-01-09 → data end, verdict rules written
   before any holdout number exists, owner-gated mechanical unlock steps
   per docs/holdout-enforcement.md) — and the ranked final-report
   skeleton with every pre-holdout section fully written —
   [docs/final-report.md](../final-report.md) (ranked table of all
   candidates with variants-tried denominators, the sole P2 finding, the
   13/13 P4 transfer failures and all negative results as first-class
   content, §Holdout deliberately empty). **REMAINING (owner-gated,
   ⚑):** the explicit owner unlock + the one-shot holdout evaluation
   itself, per the protocol doc — no session runs it without a new
   owner ORDER; the holdout stayed sealed through this prep (no
   `holdout_unlocked` marker anywhere, all ledger rows
   `data_end ≤ 2025-01-08`).

## ⚑ Owner clicks outstanding
See control/status.md — env setup script verification (paste-ready script now at environments/setup-universal.sh), auto-merge tick, archive the DOA successor session.

## Next-session brief (2026-07-10 close-out)

Lab parked green. Sole roadmap step = **P5 one-shot holdout evaluation**,
which waits on an explicit owner ORDER in `control/inbox.md` naming
`docs/p5-holdout-protocol.md` as binding (§7). When that order lands,
dispatch a **FRESH dedicated session** (not the protocol author) to execute
it and finalize `docs/final-report.md` §Holdout. No other undone roadmap
items. **Amendment at close-out:** ORDER 007 (2026-07-10T12:47:35Z,
promotion-significance bar + AAPL-donchian re-grade) arrived after this
brief was commissioned and is OPEN / not started — it gates any holdout use
and must be executed before P5 (it gates, it does not spend, the holdout).
