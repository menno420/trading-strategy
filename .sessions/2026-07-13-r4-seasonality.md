# 2026-07-13 — R4-F: day-of-week seasonality sweep

> **Status:** `complete` — Round-4 slice R4-F landed exactly as
> pre-registered (`docs/research-round-4-plan.md` § R4-F, merged before
> this session started): a new `weekday_long` calendar family swept
> across all **15** committed daily tickers on the standard rail, with
> the significance K counted honestly at ALL day×ticker combos —
> **K = 75**, bar `min_tstat(75)` = **3.209** (risen from 2.638 at K=12,
> never lowered). Honest result: **the pre-registered null HOLDS** —
> 0 of 75 combos significant at K=75 (`significant_at_k75` false
> everywhere), best t anywhere **0.317** (TSLA Friday) vs the 3.209 bar;
> 0 KEEP / 45 KILL / 30 KILL-SIG at the registered rule; all 15 lane
> walk-forwards KILL under the standard Round-2 rule with one lane-level
> KILL-SIG (TLT, t = −3.43). 15 new ledger rows (new family = new runs,
> unlike R4-B) + rebuilt index. Holdout SPENT; promotion CLOSED. This
> card was born red (`in-progress`) and flipped `complete` as the
> deliberate last content change before push; the claim file is deleted
> in this same commit.

📊 Model: fable-5 · trading-research (worker session) · start 2026-07-13T10:04:04Z

💡 **Session idea:** R4-A's KILL-SIG class met its first low-exposure
family here and the result is diagnostic dilution: 30 of 75 combos are
"significantly harmful", but the harm is mostly an exposure mismatch —
a rule long one session per week (~20% exposure, weekly round-trip cost
drag) benchmarked against fully-invested B&H over a rising dev window
*must* lose big, whatever the calendar says. R4-A found 4 KILL-SIGs in
302 lanes and each meant something; this slice alone minted 30 that
mostly mean "less exposure than the benchmark". Worth a follow-up
INFORMATIONAL column (no grading change): record the strategy/benchmark
average-|held| exposure ratio per lane, and optionally an
exposure-matched secondary benchmark, so a KILL-SIG reader can separate
"harmful timing" from "structurally under-invested". Differs from the
r4-cost-sensitivity card's replay-pin idea (artifact↔code fidelity) —
this one is about keeping a verdict CLASS meaningful as it meets new
strategy shapes.

## Why this session exists

Round 4 slice R4-F (`docs/research-round-4-plan.md` @ main, pre-registered
and merged before this session started): Round 3 varied families,
parameters, tickers, and timeframes but never *calendar* structure.
Day-of-week is the cheapest calendar hypothesis and a classic
multiple-testing trap — which makes it the right stress test of the
round's correction discipline. This slice sweeps a long-on-one-weekday
rule across the **15 committed daily tickers**; K counts ALL day×ticker
combos tested: 5 weekdays × 15 tickers = **K = 75**, so the bar RISES to
`min_tstat(75)` ≈ **3.21** (vs 2.64 at K=12) — the bar is never lowered,
K is never counted down. Pre-registered hypothesis: **null after
correction** — no day×ticker combo clears the K=75 bar. Pre-registered
rule: KEEP (dev-candidate only) iff a combo clears BOTH the Round-2
benchmark rule and t ≥ 3.21 at K=75; everything else KILL (or KILL-SIG at
t ≤ −3.21, R4-A having landed in PR #100). Owner mandate: ORDER 012
generative rung; holdout SPENT; promotion CLOSED.

## Work log

- 2026-07-13T10:04Z — branch `claude/r4-seasonality` cut from origin/main
  HEAD (`01a75a3`, the merged R4-B slice). Collision check:
  `control/claims/` at HEAD holds morning-tally + night-report +
  order-night-run — no overlap. Born-red FIRST commit `b717248` (this
  card `in-progress` + claim
  `control/claims/2026-07-13-r4-seasonality.md`), pushed before any
  implementation; PR **#102** opened READY (non-draft) immediately after,
  Before/After first, citing plan § R4-F and ORDER 012.
- 2026-07-13T10:08Z — pre-declaration commit `1397071`, grids before any
  outcome exists (the standing rail's "grid commit before running"):
  - `src/trading_lab/strategies/weekday_long.py` — the program's first
    calendar family; t/t+1 semantics stated explicitly in the docstring
    (the variant labeled weekday=d fills at the next bar's open and is
    exposed to the session AFTER each day-d bar; the five variants tile
    the trading week, so no calendar effect can hide between labels).
    Registered in `STRATEGIES` per the existing pattern.
  - `sweeps.py` `R4_SEASONALITY_*`: 5 weekday variants × 15 instruments
    (the FULL committed daily surface — frozen universe + slice-3 six +
    BTC-USD — so no post-hoc instrument selection is possible) = 75
    registered configs; `R4_SEASONALITY_K = 75` declared as the
    registered significance K. BTC-USD's weekend bars (dayofweek 5/6)
    are NOT registered; the five variants stay flat on them and K stays
    75.
  - 20 new tests: grid pinning in `tests/test_sweeps.py` (counts, K=75 ==
    total configs, bar RISES and rounds to 3.21, instruments exactly the
    committed daily surface, weekdays exactly 0–4) +
    `tests/test_weekday_long.py` (positions exactly on the chosen
    weekday, engine fill convention verified economically on a synthetic
    open-jump frame, causality prefix property, 7-day BTC-like index,
    cost drag, invalid-weekday rejection). No existing test touched.
  - `scripts/run_r4_seasonality_sweep.py` — docstring-first (POST-HOLDOUT
    DEV-ONLY banner, plan § R4-F + ORDER 012 citations, K accounting
    section): per ticker — dev-rail load via `load_ohlcv` (data_end ≤
    2025-01-08 asserted), 5 full-period bookkeeping rows, walk-forward
    1008/252/252 over the 5-variant lane grid vs same-window same-cost
    B&H (Round-2 KEEP/KILL, lane-local K=5 t informational, registered
    K=75 verdict via `classify_verdict`), PLUS per-combo fixed-weekday
    walk-forwards (grid of one — no selection) over the SAME windows so
    all 75 registered combos carry their own t vs 3.209 and a
    `significant_at_k75` boolean nothing is expected to set.
- 2026-07-13T10:11Z — ran the sweep (23.3 s), commit `9bc1e3f`:
  - **Null confirmed exactly as pre-registered**: 0/75 combos
    significant at K=75; best t 0.317 (TSLA Fri), worst −5.840 (GOOGL
    Thu); registered-rule verdicts 0 KEEP / 45 KILL / 30 KILL-SIG.
    Lanes: 0/15 KEEP standard rule; TLT lane KILL-SIG at K=75
    (t = −3.43). The only positive-t combos are three Fridays (TSLA
    0.317, AAPL 0.135, XOM 0.120) — they pass the standard benchmark
    rule but the K=75 bar is the only significance bar this slice
    registered and they miss it by an order of magnitude.
  - Output `experiments/sweeps/r4-seasonality/`: 15 per-lane JSONs (r3
    schema + `combos` block + `verdict_k75` block) + rollup
    `summary.json` (headline counts, best/worst combos, runtime). LEDGER
    DECISION: these ARE new runs (new family, new configs — unlike
    R4-B's replay), so each lane's top full-dev-period variant is
    ledgered (15 rows, `variants_tried=5`, post-hoc-selection caveat in
    notes) and `experiments/index.jsonl` rebuilt.
  - `docs/research-round-4-results.md` § R4-F appended: headline null
    first-class, explicit K=75 accounting, counts table, the KILL-SIG
    exposure-artifact reading stated honestly, burden ledger
    4148 → 4223.
- 2026-07-13T10:12Z — verify: `python3 -m pytest -q` → **488 passed**
  (468 on main + 20 new); pre-flip `bootstrap.py check --strict
  --require-session-log --session-log <this card>` red ONLY on the
  designed born-red gate. Pushed `9bc1e3f`.
- 2026-07-13T10:13Z — flip + claim-delete folded into this final commit.
  No merge action by this session; the auto-merge-enabler is the landing
  path.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r4-cost-sensitivity.md`,
Status `complete`) landed PR #101 clean — the R4-B cost re-grade. Its
verify block reproduces at this session's start: 468 passed matches its
claimed count exactly, and its committed artifacts reconcile —
`experiments/sweeps/r4-cost-sensitivity/` holds exactly 117 files (116
per-lane-per-tier details + rollup) and the rollup's counts block reads
`{graded: 58, survive_2x: 42, survive_4x: 25, kill_sig: 0/0, skipped: 0}`
verbatim as the card claims, with 58 lane rows present. Three
observations from building on it: (1) its "report-only, NOT ledgered"
decision forced this session to make the opposite call *deliberately* —
R4-F ledgeres because these are genuinely new configs, and having the
prior card's rationale written down is what made the distinction crisp
rather than cargo-culted; (2) its cost-tier schema additions
(`cost_tier`/`no_research` provenance on an r3-schema core) validated the
"r3 schema + slice-specific blocks" pattern this session reused for the
`combos` and `verdict_k75` blocks; (3) its 💡 (a standing replay-drift
pin) would have been genuinely useful here too — the per-combo replays in
this slice are exactly the kind of committed artifact that idea would
keep reproducible — second consecutive session where that follow-up would
have paid rent, which strengthens the case for actually building it. No
defect found in its work.

## Close-out

**Done:** on branch `claude/r4-seasonality` (PR #102) —

1. `src/trading_lab/strategies/weekday_long.py` + registration — the
   program's first calendar family, t/t+1 fill semantics documented.
2. `sweeps.py` `R4_SEASONALITY_*` — 5 weekdays × 15 tickers = 75
   registered configs, `R4_SEASONALITY_K = 75`, committed BEFORE the
   sweep ran (`1397071`); pinned by tests.
3. `scripts/run_r4_seasonality_sweep.py` — standard rail (1008/252/252,
   5 bps + 1 bp, stitched OOS vs same-window same-cost B&H), lane-local
   informational t at K=5 AND registered K=75 verdict per lane, all 75
   combos individually graded vs the 3.209 bar, `significant_at_k75`
   recorded, `classify_verdict` applied (KILL-SIG possible and
   observed).
4. `experiments/sweeps/r4-seasonality/` — 15 per-lane JSONs + rollup:
   **null HOLDS, 0/75 at K=75; best t 0.317 vs 3.209; 0 KEEP / 45 KILL /
   30 KILL-SIG registered-rule; 0/15 lanes KEEP standard-rule; TLT lane
   KILL-SIG (−3.43)**. 15 new ledger rows + rebuilt
   `experiments/index.jsonl`.
5. `docs/research-round-4-results.md` § R4-F — null first-class, explicit
   K=75 accounting, counts table, exposure-artifact reading of the
   KILL-SIG mass, burden 4148 → 4223.
6. 20 new tests; no existing test weakened or deleted; the
   multiple-testing bar untouched anywhere and RAISED (3.209) for this
   slice's own verdicts, per pre-registration.
7. This card (born-red first commit `b717248` → pre-declaration
   `1397071` → run+results `9bc1e3f` → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 488 passed (468 on main + 20 new).
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r4-seasonality.md`
→ green after this flip (pre-flip the only red was the designed born-red
gate). Integrity at close: diff touches only
`src/trading_lab/strategies/weekday_long.py` (new),
`src/trading_lab/strategies/__init__.py` (registration),
`src/trading_lab/sweeps.py` (appended R4-F grid),
`scripts/run_r4_seasonality_sweep.py` (new),
`tests/test_weekday_long.py` (new), `tests/test_sweeps.py` (appended
class), `experiments/sweeps/r4-seasonality/` (new),
`experiments/runs/` (15 new rows), `experiments/index.jsonl` (rebuilt,
additive), `docs/research-round-4-results.md` (appended section),
`.sessions/`, `control/claims/` (deletion). Every
`experiments/sweeps/r3-*/` and `r4-*/` prior file byte-untouched, holdout
(SPENT) untouched, `unlock_holdout` never passed, `data/p5holdout/`
untouched, `experiments/paper/**` byte-untouched, paper grading never
run, `control/inbox.md` + `control/status.md` + `control/outbox.md`
byte-untouched, no triggers created or modified, no broker/order/exchange
code, NO merge action taken by this session.

**Next (guard recipe):** none owed for correctness. Follow-ups now
unblocked: the exposure-ratio diagnostic column for KILL-SIG readers
(this card's 💡); the standing replay-drift pin (r4-cost-sensitivity's 💡,
now twice-validated); R4-C/R4-D/R4-E remain the open pre-registered
slices. Nothing from this slice is a candidate for anything — the null is
the deliverable. Any OOS claim about any calendar effect remains
OWNER-GATED on post-2026 data.

Session end: badge flipped `complete` in this final content commit before
push.
