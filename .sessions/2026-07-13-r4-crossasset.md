# 2026-07-13 — R4-E: cross-asset exposure gate

> **Status:** `complete` — Round-4 slice R4-E landed exactly as
> pre-registered (`docs/research-round-4-plan.md` § R4-E, merged before
> this session started): TLT/XOM/GLD momentum exposure gates on the
> frozen SPY/QQQ trend component (new `crossasset_gate` strategy — the
> program's FIRST cross-asset strategy, gate series aligned onto the
> equity index lookahead-free) graded head-to-head against the MANDATORY
> ungated control arm with a machine-readable `control_arm_delta` per
> lane. Honest result: the registered null holds, hardest of the round's
> three conditioning slices — **2 lanes, 0 KEEP / 2 KILL / 0 KILL-SIG**;
> the gated arm lost to its own ungated control on BOTH lanes (deltas
> SPY **−0.302**, QQQ **−0.635**) and to B&H on both; best informational
> t **−1.91** (SPY) vs the K=13 bar **2.665**. The conditioning arc is
> now 0/2 + 3/3 + 0/6-KEEP across three axes with zero candidates. This
> session also CLOSED OUT Round 4 in the results doc (all six slices,
> PRs #100–#105: 0 promoted, burden 4148 → 4345, promotion CLOSED,
> holdout SPENT, round-5 stack synthesized). 2 new ledger rows + rebuilt
> index. This card was born red (`in-progress`) and flipped `complete`
> as the deliberate last content change before push; the claim file is
> deleted in this same commit.

📊 Model: fable-5 · trading-research (worker session) · start 2026-07-13T11:03:14Z

💡 **Session idea:** when a slice's HYPOTHESIS names a specific config,
report that config's selection-free walk-forward as its own
machine-readable row. R4-E's registered hypothesis literally names "a
TLT-momentum exposure gate", but the registered grid searched 12
variants and the walk-forward's in-sample favourite was the XOM gate
(11/20 split picks vs TLT's 5/20), while the full-period in-sample
winner was GLD 126 on both lanes — so the lane verdict actually answers
"does searching over cross-asset gates beat the control?" and only
indirectly the named question "does TLT momentum warn equity trend?".
A fixed-variant walk-forward (no per-split selection) of the ONE
hypothesis-named config costs zero new registered configs (it is
already in the grid and K) and would separate "the named story fails"
from "story-search fails". This session also measured the cost of the
confound's other half across slices: the r4-regime SPY control
(2-variant walk-forward, 0.382) underperformed this slice's FIXED
1-variant control (0.460) on the IDENTICAL OOS window, components
overlapping — ~0.08 Sharpe lost to selecting between just two variants.
Complementary to (not duplicating) the r4-regime card's
cardinality-matched-control idea: that equalizes grid sizes; this pins
the named story. Folded into the round-5 stack in the closing tally.

## Why this session exists

Round 4 slice R4-E (`docs/research-round-4-plan.md` @ main, pre-registered
and merged before this session started) — the LAST open Round-4 run slice:
the round-3 universe expansion committed TLT, XOM and GLD caches (PRs
#90–#92) but used them only as standalone lanes; cross-asset information
(bond/commodity momentum as an equity risk gate) is an untested idea
class, and the round's two conditioning results so far (PR #92's vol-gate
control winning 6/6; PR #104's trend-strength control splitting 3/3 with
conditioning still producing zero candidates) make the prior informed.
R4-E gates the exposure of existing SPY/QQQ trend-family variants on the
momentum sign of a DIFFERENT instrument (TLT, plus XOM and GLD as
pre-declared alternates), with the **ungated control arm** committed in
the same grid and a machine-readable `control_arm_delta` per lane.
Pre-registered kill criterion (same control-arm rule as R4-D): KILL iff
gated stitched OOS Sharpe ≤ the ungated control's; a KEEP additionally
requires beating B&H. Pre-registered hypothesis: **null expected**.
Engine/rail note: this is the program's first strategy that consumes a
SECOND instrument's OHLCV — gate-series alignment onto the equity's index
must be lookahead-free (gate signal at bar t uses gate-asset data ≤ t,
applied to the equity fill at t+1 per house convention), pinned by tests.
Owner mandate: ORDER 012 generative rung; holdout SPENT; promotion CLOSED
— any KEEP is a dev-candidate only, never a finding. This session also
closes out Round 4 in the results doc (all six slices now landed).

## Work log

- 2026-07-13T11:03Z — branch `claude/r4-crossasset` cut from origin/main
  HEAD (`7778ddb`, the merged R4-D slice). Collision check:
  `control/claims/` at HEAD holds morning-tally + night-report +
  order-night-run — no overlap. Born-red FIRST commit `060d832` (this
  card `in-progress` + claim
  `control/claims/2026-07-13-r4-crossasset.md`), pushed before any
  implementation; PR **#105** opened READY (non-draft) immediately
  after, Before/After first, citing plan § R4-E, PR #104 (control-arm
  sibling), PR #92, ORDER 012.
- 2026-07-13T11:10Z — pre-declaration commit `040f65d`, all logic before
  any outcome exists (grids-before-run rail, precedent PRs #102–#104):
  - `src/trading_lab/strategies/crossasset_gate.py` — NEW family, the
    program's first cross-asset strategy: frozen equity component
    `ema_crossover` 20/100 (the committed PR #90 grid point on BOTH
    instruments — the identical freeze PR #104 used; subset relation
    pinned by tests) exposed ONLY while the gate asset's trailing
    momentum (`gate_close/gate_close.shift(lookback) − 1`, computed on
    the gate asset's OWN calendar) is > 0. Alignment is a
    strictly-backward `reindex(equity_index, method="ffill")` — the
    gate value applied at equity bar t uses gate-asset data ≤ t ONLY;
    undefined gate (warm-up / pre-history) resolves against the
    strategy: flat (the `vol_filtered_trend` convention). `gated=False`
    is the MANDATORY ungated control arm — the same component, no gate;
    it never loads or computes gate data (invariance pinned by tests).
    Gate series loaded via the dev rail `load_ohlcv` default (holdout
    excluded), module-cached; tests inject synthetic `gate_close`.
  - `sweeps.py` `R4_CROSSASSET_*`: 12 gated variants (gate asset
    {TLT, XOM, GLD} × momentum lookback {21, 63, 126, 252} bars,
    ~1/3/6/12 months; gate rule and warm-up convention FIXED in the
    grid commit) + 1 control variant × {SPY, QQQ} = 26 registered
    configs; **K = 13** counts EVERY config this lane tries incl. the
    control — the bar RISES to min_tstat(13) ≈ 2.665 above the
    round-standard 2.638 (PR #104 precedent; K never counted down).
  - 27 new tests (+2 auto-parametrized instances in
    `test_strategies.py`'s all-STRATEGIES loops): gate-momentum
    arithmetic; NO-LOOKAHEAD alignment (gate-series prefix invariance —
    truncating the gate series at t leaves positions ≤ t unchanged;
    delaying the gate series one bar shifts every gate decision exactly
    one bar; misaligned sparser gate calendars ffill from the most
    recent gate bar ≤ t; equity bars before gate history are flat);
    gate routing identity per bar; strict sign rule (momentum == 0 is
    closed); control-arm identity (`gated=False` ≡ plain ema_crossover)
    + invariance to gate_asset/gate_lookback/gate_close; validation;
    grid pinning incl. the committed-r3-grid-point and PR #104-freeze
    subset relations. No existing test touched.
  - `scripts/run_r4_crossasset_sweep.py` — docstring-first
    (POST-HOLDOUT DEV-ONLY banner, plan § R4-E + ORDER 012 +
    PR #90/#92/#104 citations): per instrument — dev-rail `load_ohlcv`
    (data_end ≤ 2025-01-08 asserted for the equities AND all three gate
    assets), both arms walk-forwarded 1008/252/252 with splits asserted
    identical, stitched OOS vs same-window same-cost B&H (5 bps + 1 bp),
    machine-readable `control_arm_delta`, pre-registered KILL iff gated
    ≤ control, `classify_verdict` applied (KILL-SIG possible), gated
    arm's top full-period variant ledgered.
- 2026-07-13T11:11Z — ran the sweep (2.2 s), commit `9486b60`:
  - **2 lanes — 0 KEEP / 2 KILL / 0 KILL-SIG.** `control_arm_delta`:
    SPY **−0.302** (gated 0.158 vs control 0.460), QQQ **−0.635**
    (gated 0.197 vs control 0.832) — the gated arm lost to its own
    ungated control on BOTH lanes and to B&H on both (0.761/0.871).
    Best t −1.91 (SPY), QQQ −2.13; negative on both lanes but neither
    crosses the mirrored −2.665 bar. Mechanism in the per-split picks:
    the gated walk-forward churned 5 (SPY) and 8 (QQQ) distinct
    variants over 10 splits, in-sample favouring the XOM gate (11/20
    picks) over the hypothesis-named TLT (5/20), while the full-period
    in-sample winner was GLD 126 on both lanes — three different
    answers to "which gate asset" = noise, and the selection-free
    control won anyway.
  - Output `experiments/sweeps/r4-crossasset/`: 2 per-lane JSONs (BOTH
    arms' full walk-forward blocks, `control_arm_delta`,
    `gate_alignment` provenance note, K=13 informational grade) +
    rollup `summary.json`. Ledger: 2 rows — the GATED arm's top
    full-dev-period variant per lane (round-3 convention, post-hoc
    in-sample selection flagged in notes, `variants_tried = K = 13`);
    `experiments/index.jsonl` rebuilt.
- 2026-07-13T11:13Z — docs commit `b7c48fd`:
  `docs/research-round-4-results.md` § R4-E appended (headline,
  `control_arm_delta` table, the conditioning-arc reading) AND
  **§ Round 4 — closing tally**: all six slices' one-line verdicts
  (R4-A 4 KILL-SIG of 302; R4-B 42/58 survive 2×, 25/58 4×; R4-C 5/12
  beat best member, max t 1.09; R4-D null 0/6; R4-F null 0/75 at K=75;
  R4-E null 0/2), cumulative burden 4148 → 4345 (+197), the explicit
  "0 promoted — promotion remains CLOSED, holdout SPENT" line, and the
  round-5 stack synthesized from the six session cards' 💡 blocks
  (selection-fair controls/story-pinned configs, replay pin, prose-tally
  reconciliation, pairwise committees, exposure-ratio column, deferred
  infra).
- 2026-07-13T11:14Z — verify: `python3 -m pytest -q` → **572 passed**
  (543 on main at branch time + 29 new); pre-flip `bootstrap.py check
  --strict --require-session-log --session-log <this card>` red ONLY on
  the designed born-red gate.
- 2026-07-13T11:15Z — flip + claim-delete folded into this final commit.
  No merge action by this session; the auto-merge-enabler is the landing
  path.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r4-regime.md`,
Status `complete`) landed PR #104 clean — the R4-D regime-conditional
slice. Its claims reproduce at this session's start: 543 passed matches
this session's pre-change baseline exactly (572 − 29 new);
`experiments/sweeps/r4-regime/` holds exactly 7 files (6 per-lane +
rollup) and the rollup reads 0 KEEP / 6 KILL / 0 KILL-SIG with
conditional-beats-control 3/6 and deltas SPY +0.021 / QQQ −0.099 /
TSLA +0.168 / JPM +0.036 / XOM −0.453 / TLT −0.074, verbatim as the
card claims. Three observations from building on it: (1) its
control-arm machinery (both-arms walk-forward on asserted-identical
splits + machine-readable `control_arm_delta` + KILL-iff-≤-control)
transplanted to the cross-asset axis with zero design changes — the
runner is structurally a sibling, which is exactly what committing the
convention in a precedent PR is for. (2) Its 💡 (cardinality-matched
controls — `control_arm_delta` confounds conditioning with selection
variance) gained hard cross-slice evidence here: its SPY control
(2-variant walk-forward, stitched OOS 0.382) underperformed this
slice's FIXED 1-variant control (0.460) on the IDENTICAL OOS window
(2014-01-06 start, both containing ema 20/100) — ~0.08 Sharpe is
attributable to selecting between just two variants, so the confound it
flagged is real and measurable. (3) Its K-decision (count control
variants INTO K, 14 > 12) was reused verbatim (13 > 12 here), keeping
the round's rule crisp: K never moves toward leniency. One nit, not a
defect: its card's date-stamping suggestion for baselines (from its own
previous-session review) was adopted here — "543 on main at branch
time" — closing the loop it opened. No defect found in its work.

## Close-out

**Done:** on branch `claude/r4-crossasset` (PR #105) —

1. `src/trading_lab/strategies/crossasset_gate.py` — NEW cross-asset
   momentum exposure gate (the program's first two-instrument strategy)
   with its mandatory ungated control arm built into the same strategy
   (`gated=False`); equity component frozen at the committed r3/PR #104
   grid point; gate rule, warm-up convention and lookahead-free
   alignment fixed in the grid commit; registered in
   `STRATEGIES`/`DEFAULT_PARAMS`/`R4_CROSSASSET_FAMILY`.
2. `sweeps.py` `R4_CROSSASSET_*` — 12 gated + 1 control variant ×
   {SPY, QQQ} = 26 registered configs, K = 13 (bar ≈ 2.665, raised
   above the round-standard 2.638, never lowered); committed BEFORE the
   sweep ran (`040f65d`); pinned by tests.
3. `scripts/run_r4_crossasset_sweep.py` — standard rail (1008/252/252,
   5 bps + 1 bp, stitched OOS vs same-window same-cost B&H), both arms
   on asserted-identical windows, dev rail asserted for equities AND
   gate assets, machine-readable `control_arm_delta`, pre-registered
   KILL iff gated ≤ control, `classify_verdict` applied.
4. `experiments/sweeps/r4-crossasset/` — 2 per-lane JSONs + rollup:
   **0 KEEP / 2 KILL / 0 KILL-SIG; gated beat control 0/2 (deltas
   −0.302, −0.635); 0/2 beat B&H; best t −1.91 vs 2.665 — the
   pre-registered null holds**, closing the round's conditioning arc at
   zero candidates across three axes. 2 new ledger rows + rebuilt
   `experiments/index.jsonl`.
5. `docs/research-round-4-results.md` § R4-E + **§ Round 4 — closing
   tally**: six one-line verdicts (PRs #100–#105), burden 4148 → 4345,
   "0 promoted — promotion remains CLOSED, holdout SPENT" explicit,
   round-5 stack synthesized from the six cards' session ideas.
6. 27 new tests + 2 auto-parametrized instances (572 total); no
   existing test weakened or deleted; the multiple-testing bar
   untouched anywhere and explicitly RAISED for this slice (K=13
   counts the control arm).
7. This card (born-red first commit `060d832` → pre-declaration
   `040f65d` → run `9486b60` → docs `b7c48fd` → flipped `complete`
   last) — claim file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 572 passed (543 on main at branch time + 29
new).
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r4-crossasset.md`
→ green after this flip (pre-flip the only red was the designed born-red
gate). Integrity at close: diff touches only
`src/trading_lab/strategies/crossasset_gate.py` (new),
`src/trading_lab/strategies/__init__.py` (registration),
`src/trading_lab/sweeps.py` (appended R4-E block),
`scripts/run_r4_crossasset_sweep.py` (new),
`tests/test_crossasset_gate.py` (new), `tests/test_sweeps.py` (appended
class), `experiments/sweeps/r4-crossasset/` (new), `experiments/runs/`
(2 new rows), `experiments/index.jsonl` (rebuilt, additive),
`docs/research-round-4-results.md` (appended sections), `.sessions/`,
`control/claims/` (deletion). Every `experiments/sweeps/r3-*/` and prior
`r4-*/` file byte-untouched, holdout (SPENT) untouched, `unlock_holdout`
never passed, `data/p5holdout/` untouched, `experiments/paper/**`
byte-untouched, paper grading never run, `control/inbox.md` +
`control/status.md` + `control/outbox.md` byte-untouched, no triggers
created or modified, no broker/order/exchange code, NO merge action
taken by this session. (Note: the container carried a pre-existing
uncommitted `.substrate/guard-fires.jsonl` modification from earlier
sessions' checks — not this session's work, left uncommitted.)

**Next (guard recipe):** none owed for correctness. Round 4 is CLOSED
(six slices, zero findings, zero promotions); the round-5 stack is
written into the results doc's closing tally and ranked there. Nothing
reopens promotion; any OOS claim remains OWNER-GATED on post-2026 data.

Session end: badge flipped `complete` in this final content commit before
push.
