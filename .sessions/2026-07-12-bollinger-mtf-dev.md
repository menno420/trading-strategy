# 2026-07-12 — MTF Bollinger mean-reversion (dev-only, null result)

> **Status:** `in-progress` — exploring the owner's multi-timeframe (MTF)
> Bollinger mean-reversion hypothesis on cached dev data. RESEARCH-ONLY /
> DEV-ONLY / ILLUSTRATIVE: NO holdout reads (`load_ohlcv` default rail, bars
> < 2025-01-09), NO network fetch, NO accounts, NO live/paper trading, NO
> ledger writes, `control/` untouched. Promotion is CLOSED (holdout SPENT) —
> nothing here is a FINDING or PROMOTED; a positive t-stat would be at most a
> "RULE-PASS candidate (dev, promotion-closed)". Deliverables: a causal MTF
> helper + tests, a research note, and an owner-gated preregistration draft.
> This card is born red (`in-progress`) and flips `complete` as the deliberate
> last content change before push.

📊 Model: opus-4.8 · claude/bollinger-mtf-dev lane · start 2026-07-12T11:32:26Z

💡 **Session idea:** The owner's MTF Bollinger claim has two testable parts —
(A) a lower-timeframe band break is MORE likely when the higher timeframe is
stretched beyond its own outer band, and (B) GIVEN a lower-band touch, reversion
to the mid-band is RELIABLE when the higher TF is in-range and FAILS when it is
stretched. We tested the MECHANISM FIRST (conditional probabilities across four
TF pairs), before any strategy P&L, because if the probabilities don't separate
the strategy has no foundation. They don't. Test A runs OPPOSITE to the
hypothesis (breaks are LESS likely when the higher TF is stretched — Δ ≈ −0.03
to −0.04 across all four pairs), and Test B shows no material/consistent split
(median success Δ in-range−stretched = −0.056, wrong sign, with tiny stretched
cells N=11–42). The pre-declared 12-config grid confirms it: every OOS Sharpe
delta vs buy-and-hold is negative, net of costs, uniformly across all three TF
pairs — all 12 KILLED, nothing reaches the ORDER 007 bar (nothing beat B&H).
Clean null; the honest deliverable is the negative plus a frozen, owner-gated
preregistration draft for any future minute-data OOS test.

## Why this session exists

The owner floated an MTF Bollinger mean-reversion idea (trade a lower-timeframe
band touch, conditioned on the higher timeframe's band position). This slice
answers "does the mechanism hold?" on the cached dev window with three
deliverables: (1) a reusable, strictly-causal MTF helper
(`src/trading_lab/mtf.py`) with focused no-lookahead tests, (2) a Phase-1
conditioning study + Phase-2 pre-declared trading grid (both dev-only, costs on,
holdout untouched), and (3) a research note stating the null plainly plus an
owner-gated preregistration draft for a real post-2026 out-of-sample test. No
promotion, no finding, no live decision — research-only throughout.

## Work log

- 2026-07-12T11:32Z — heartbeat: on branch `claude/bollinger-mtf-dev`; rebased
  cleanly onto the live origin/main tip `d0449e0` (origin advanced past the
  brief's `3ba081c` → `1f9cbac` → `d0449e0`; re-verified via `git fetch` +
  `git merge-base --is-ancestor`). `control/` read-only, never edited. This card
  is the born-red first content state (Status `in-progress`).
- Built `src/trading_lab/mtf.py`: `resample_ohlcv` (open=first/high=max/low=min/
  close=last/volume=sum, `closed='right', label='right'` so each coarse bar is
  stamped at its close), `boll_z` (causal rolling z, NaN warm-up, 0 where std==0,
  mirrors `strategies.bollinger_reversion`), and `align_higher_to_lower` (maps a
  coarse-TF series onto the fine-TF timeline with a one-coarse-bar lag before a
  strictly-`<=` ffill; runtime asserts every fine bar's source coarse timestamp
  is strictly `< t`). Added `tests/test_mtf.py` (6 tests: resample aggregation,
  empty-bin drop, boll_z warm-up/std-zero, boll_z vs manual, no-lookahead
  alignment vs a naive-ffill leak, monotonic-index assertion).
- Phase 1 `scripts/mtf_conditioning_study.py` over {1h/4h, 1h/6h, 2h/daily,
  daily/weekly}. VERDICT: NULL — Test A P(touch) is lower in the stretched
  bucket for all four pairs (opposite the claim); Test B success Δ (in−stretched)
  median = −0.056 (wrong sign), stretched cells underpowered (N=11–42). Base
  reversion is 72–81% in EVERY regime (wide −3.5 stop + mid-band target), so the
  conditioning adds nothing. Raw: `scratchpad/mtf_conditioning_results.json`.
- Phase 2 `scripts/mtf_bollinger_grid.py` — 12 pre-declared configs (k∈{2,2.5},
  lookback∈{20,50}, pairs {1h/4h, 2h/daily, daily/weekly}), costs on, t+1-open.
  All 12 KILLED (every Δsharpe vs B&H negative); many-small-wins/rare-big-loss
  tail (worst trade dwarfs median win); win rate 66–80% but every config loses to
  B&H on Sharpe; Δsharpe negative uniformly → no lone-exotic artifact. 2h/daily
  yields 0 standard walk-forward splits (thin ~1238 bars) → reported as a single
  OOS, not WF. ORDER 007 not reached (nothing beat B&H). Raw:
  `scratchpad/mtf_grid_results.json`.
- Wrote `docs/research/bollinger-mtf-dev-2026-07-12.md` (Status `reference`,
  DEV-ONLY banner) with the plain-language null verdict, data/scope honesty
  (no minute data → 15m/45m impossible on cached data = owner decision), the
  Test A / Test B / grid tables, the ORDER 007 non-grading note, and the
  denominator. Wrote `docs/proposals/bollinger-mtf-preregistration-draft.md`
  (Status `plan`, OWNER-GATED / FLAG-ONLY banner) — a frozen protocol for any
  future post-2026 minute-data OOS run. Linked both from
  `docs/current-state.md` §In flight (reachability).

## Previous-session review

⟲ Previous-session review: the most recent prior card
(`.sessions/2026-07-12-position-sizing-vet.md`, Status `complete`) vetted the
owner's small-account position-sizing idea with fractional-Kelly math + a
self-contained synthetic Monte Carlo, landing the DEV-ONLY / ILLUSTRATIVE note
`docs/research/position-sizing-vet-2026-07-12.md`. Its honest through-line —
sizing scales edge and drag but never creates edge, and our own spent holdout
shows no positive net edge (0/13 cleared the ORDER 007 bar) — is the same
promotion-CLOSED discipline this slice inherits: a positive number here would be
at most a dev RULE-PASS candidate, never a finding. That card's guard recipe was
"none owed"; it left the read-path reachability clean by linking its doc from
`docs/current-state.md`, the recipe this slice reuses for its two new docs.

## Close-out

**Done:** on branch `claude/bollinger-mtf-dev` —

1. `.sessions/2026-07-12-bollinger-mtf-dev.md` — this card (first commit
   born-red `in-progress` → flipped `complete` as the deliberate last step).
2. `src/trading_lab/mtf.py` + `tests/test_mtf.py` — causal MTF helper (6 tests).
3. `scripts/mtf_conditioning_study.py` + `scripts/mtf_bollinger_grid.py` —
   Phase 1 conditioning study + Phase 2 pre-declared grid (dev-only, costs on).
4. `docs/research/bollinger-mtf-dev-2026-07-12.md` (Status `reference`) — the
   DEV-ONLY null-result research note. Raw JSON:
   `scratchpad/mtf_conditioning_results.json`, `scratchpad/mtf_grid_results.json`.
5. `docs/proposals/bollinger-mtf-preregistration-draft.md` (Status `plan`) —
   the OWNER-GATED / FLAG-ONLY frozen preregistration draft.
6. `docs/current-state.md` §In flight — two bullets linking the new docs
   (reachability).

**Verify:**
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-12-bollinger-mtf-dev.md`
→ exit 0 after this card flips `complete`. `python3 -m pytest -q` → green
(229 tests: 223 pre-existing + 6 new MTF). Integrity at close: zero `data/**`
holdout reads, `unlock_holdout` never passed, no ledger rows added, `control/`
byte-untouched, no promotion/finding language, no merge action taken.

**Next (guard recipe):** if extending the MTF work, start from
`src/trading_lab/mtf.py` (causal helpers) and `tests/test_mtf.py` (the
no-lookahead assertion is the load-bearing guard — an alignment change that
regresses causality reds `test_align_no_lookahead_naive_would_leak`). Any real
out-of-sample test is OWNER-GATED behind
`docs/proposals/bollinger-mtf-preregistration-draft.md` §7 — never
self-executing.

Session end: badge flips `complete` in the final commit before push.
