# Selection-fair replay standing gate (round 6+)

> **Status:** `binding`
>
> Effective from **research round 6** onward, strictly forward-looking:
> no retroactive re-grading — round ≤5 results stand exactly as
> published, and no existing file's verdict changes. Adopted [D-0002].
> Code: `src/trading_lab/selection_gate.py`. Provenance: R5-D
> (`docs/research-round-5-results.md` § R5-D, PR #110).

## What the gate is

From round 6 onward a dev-lane **KEEP verdict requires two things**, not
one: (a) the searched walk-forward beats same-window buy-and-hold (the
existing rule), AND (b) a **selection-fair fixed-config replay** of the
lane's committed top full-period variant — one fixed config, no training
pick, replayed over the lane's exact committed walk-forward test windows
at the lane's costs — also beats the same-window benchmark. A lane
failing the gate is demoted to KILL at grade time.

**Why (measured, not vibes):** R5-D replayed the program's five best
KEEP-dev lanes selection-free and found `selection_gap > 0` on only 3/5
— two lanes' searched walk-forwards LOST to their own story-pinned fixed
config (SLV −0.313, META hourly −0.396). In-window re-selection can
flatter the searched number; the gate makes the selection-free floor a
standing requirement instead of a once-per-round slice.

## Exact pass rule

```
PASS iff fixed_sharpe and bench_sharpe are both non-NaN
     AND fixed_sharpe > bench_sharpe
     AND fixed_sharpe > 0
```

Ties and NaN fail. `fixed_sharpe` is the stitched OOS Sharpe of the
fixed-config replay; `bench_sharpe` is same-window buy-and-hold at the
same costs. Anything that prevents grading (see choice 2 below) is a
FAIL, never a skip.

## The seven recorded semantic choices

Where R5-D (an experiment slice) left a choice open, the standing gate
takes the **stricter** option. Each choice is recorded here so no future
runner re-litigates it:

1. **Replay window** — the lane's committed per-split test windows from
   its source summary (`walk_forward.per_split`). A lane without
   committed `per_split` windows is UNGRADEABLE. *Stricter: no window
   reconstruction, no approximation — the gate replays exactly what was
   committed or refuses.*
2. **UNGRADEABLE = FAIL** — missing windows, fidelity-guard failure,
   cache drift, missing data all FAIL the gate (demoting a KEEP), never
   a neutral skip. *Stricter than R5-D's SKIPPED, which was
   experiment-report semantics: a standing gate that skips is a gate a
   broken lane walks through. A lane the lab cannot reproduce cannot
   hold a KEEP.*
3. **Benchmark** — same-window buy-and-hold at the same costs, exactly
   as R5-D: the contiguous slice `windows[0][0]:windows[-1][1]`. The
   gate **hard-checks window contiguity** (each window's start must
   equal the previous window's end — verified against the actual
   committed r3 per-split layout, e.g. `[1008,1260],[1260,1512],…`) and
   treats non-contiguity as UNGRADEABLE → FAIL, since the slice-span
   benchmark would otherwise cover bars the strategy arm never traded.
   *Stricter: R5-D assumed contiguity; the gate enforces it.*
4. **Pass rule** — `fixed_sharpe > bench_sharpe` AND `fixed_sharpe > 0`,
   both non-NaN; ties and NaN fail. *The `> 0` conjunct is a deliberate
   strictness increase over R5-D (which only required beating B&H),
   aligning the gate with the r3 rule: a negative-Sharpe lane never
   keeps, even against a more-negative benchmark.*
5. **`selection_gap`** = `searched_stitched_sharpe −
   fixed_stitched_sharpe` stays **informational**: reported in every
   gate result, no registered threshold. (Registering a threshold would
   be a new rule needing its own pre-registration.)
6. **Fidelity guard** — as in R5-D: when a recorded searched stitched
   OOS Sharpe is provided, the searched-arm replay must reproduce it
   within `1e-8`, else UNGRADEABLE → FAIL. *Stricter downstream: in
   R5-D an irreproducible lane was SKIPPED; here it demotes (choice 2).*
7. **OFF for historical ledgers** — the gate is invoked explicitly by
   round-6+ runners; nothing retroactively re-labels existing results.
   Every `experiments/**` artifact and every round ≤5 verdict stays
   byte-identical. *Stricter where it matters (future grades), honest
   where it must be (published history is history).*

## How a round-6 runner calls it

```python
from trading_lab import promotion, selection_gate
from trading_lab.strategies import STRATEGIES

source = json.loads(Path(lane["source_file"]).read_text())
# Caller owns the R5-D cache-drift check first: data_start / data_end /
# n_bars of the loaded ohlcv vs the source JSON. On drift: gate FAIL
# with the drift reason (choice 2), do not call run_selection_gate.
result = selection_gate.run_selection_gate(
    ohlcv=ohlcv,                                  # dev rail, load_ohlcv
    strategy=STRATEGIES[source["family"]],
    per_split=source["walk_forward"]["per_split"],
    top_variant=lane["top_variant"],              # committed top config
    timeframe=source["timeframe"],
    costs=source["costs"],
    recorded_searched_sharpe=source["walk_forward"]["oos_metrics"]["sharpe"],
)
verdict = selection_gate.apply_gate(verdict, result)  # KEEP-dev → KILL on FAIL
lane_record["selection_gate"] = result               # machine-readable
```

`apply_gate` only demotes: a KEEP verdict
(`promotion.VERDICT_KEEP_DEV` or sweep-vocab `KEEP`) becomes `KILL` on
gate FAIL; `KILL` / `KILL-SIG` pass through unchanged; gate PASS changes
nothing.

## Provenance

- R5-D — selection-fair fixed-config replay:
  [`docs/research-round-5-results.md`](research-round-5-results.md)
  § R5-D, PR #110; replay machinery lifted from
  `scripts/run_r5d_selection_fair.py` (byte-untouched).
- Motivation: 2 of 5 top lanes with **negative** `selection_gap` (SLV
  −0.313, META hourly −0.396) — the searched walk-forward lost to its
  own fixed config on the program's best surface.
- Adoption decision: [D-0002] in [`docs/decisions.md`](decisions.md).
- Tests: `tests/test_selection_gate.py`.
