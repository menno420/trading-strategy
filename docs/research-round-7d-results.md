# Research Round 7D — Results

> **Status:** `reference` — honest results of the single pre-registered
> Round-7D slice, against the protocol in
> [research-round-7d-plan.md](research-round-7d-plan.md) (merged as PR #147
> BEFORE any Round-7D outcome existed). **POST-HOLDOUT, DEV-ONLY: the
> holdout is SPENT and promotion is CLOSED.** Nothing on this page is an
> out-of-sample claim; a KEEP would mean *dev-candidate only*, and
> nulls/KILLs are first-class results. The multiple-testing bar is unchanged
> (`trading_lab.promotion.min_tstat`, ≈2.39 at the xsec K=6 convention; only
> ever rises). Round 7D is a PORTFOLIO lane graded by the Round-2 §6 rule
> (stitched portfolio-walk-forward OOS Sharpe > equal-weight basket
> buy-and-hold OOS Sharpe AND > 0) with the ORDER-007 informational t-bar,
> mirroring the Round-3 slice-7 xsec portfolio template
> (`scripts/run_r3_xsec_expanded.py`).

**Round headline: the registered null holds cleanly — cross-sectional
DRAWDOWN-depth ranking `xsec_drawdown` on the XSEC-14 basket yields
0 KEEP-dev / 6 KILL / 0 KILL-SIG across the 6 pre-registered lanes,
0 promoted, best informational t anywhere −0.74 (L63/k3) against the
unchanged K=6 bar ≈2.39. Every one of the 6 lanes underperforms the
equal-weight basket buy-and-hold benchmark (OOS Sharpe 1.193 over the same
8-split window): OOS Sharpe ranges 0.571 (L126/k2) to 0.930 (L63/k3), i.e.
0.26–0.62 Sharpe BELOW the benchmark — the same magnitude by which
`xsec_reversal` (the nearest return-ranked "buy the beaten-down names"
neighbour) went 6/6 KILL on this exact basket in Round 3, and consistent
with the single-name drawdown lanes (R7-A) mostly nulling. No lane is
significantly worse than the benchmark either — the most negative t is
−1.76 (L126/k2), inside the mirrored −2.39 bar, so there are 0 KILL-SIG
lanes: drawdown ranking is uninformative here, not actively value-destroying.
The registered MIRROR (deeper concentration — `k=2`, longer `L` — should
out-grade shallower `k=3`, shorter `L` if drawdown carried cross-sectional
information) did NOT clear and in fact ran the WRONG way: at every `L`,
`k=3` out-Sharped `k=2`, and the shortest `L=63` beat both longer windows —
no monotone concentration gradient survives, exactly as the plan predicted
the mirror would fail to clear the bar. Zero UNGRADEABLE lanes — no
infrastructure alarm. Round-7D burden: 6 new registered configs (portfolio
lane, configs = variants); program cumulative 5,595 → 5,601. Runtime nowhere
near the cap (2.1 s vs 900 s); no CAP-HIT, nothing truncated, all 6 lanes
ran.**

| Slice | Lanes | KEEP | KILL | KILL-SIG | Promoted | Best t vs bar | Runtime vs cap |
|---|---|---|---|---|---|---|---|
| R7-D `r7d-xsec-drawdown` (daily) | 6 | 0 | 6 | 0 | 0 | −0.74 vs 2.39 | 2.1 s / 900 s |
| **Round 7D** | **6** | **0** | **6** | **0** | **0** | **−0.74 vs 2.39** | none hit |

## Scope — what Round 7D added

- **One genuinely new PORTFOLIO family** (PR #147 pre-registered the plan;
  this run committed the code): `xsec_drawdown`, the first cross-sectional
  lane to rank the basket on DRAWDOWN DEPTH — depth from a trailing `L`-bar
  close peak, `depth[t,i] = close[t,i] / rolling(L).max()[t,i] − 1` (≤ 0),
  ascending (deepest first), hold the deepest-`k` equal-weight (1/k),
  monthly (21-bar) rebalance, long/flat, no leverage.
- **Declared adjacency**: `xsec_momentum` (long top-`k` by trailing return)
  and `xsec_reversal` (long bottom-`k` by trailing return). Structural
  difference: `xsec_drawdown` ranks on a drawdown STATE
  (`close/rolling(L).max()−1`), not on a point-to-point return
  (`close/close.shift(N)−1`); the two keys are not monotone transforms
  (a name can fall early then recover — deep trailing loss, shallow drawdown
   — or top mid-window and stay below it — mild trailing loss, deep
  drawdown), so it is not reducible to either return-ranked neighbour.
- **Basket XSEC-14** (the same tuple object as Round-3 slice 7): AAPL, AMZN,
  GLD, GOOGL, JPM, META, MSFT, NVDA, QQQ, SLV, SPY, TLT, TSLA, XOM —
  all-equity/ETF so the aligned common index stays on exchange trading days;
  BTC-USD deliberately excluded.

## Budget ledger

| Slice | PR | Sweep dir | Family × basket | Variants | Configs | Program cumulative |
|---|---|---|---|---|---|---|
| R7-D | (this run) | `r7d-xsec-drawdown` | `xsec_drawdown` × XSEC-14 (portfolio; configs = grid points) | 6 | 6 | 5,601 |

Portfolio config-counting: `configs = variants` — the 14 instruments do NOT
multiply the count (each grid point is ONE portfolio lane over the whole
basket, the Round-2/Round-3 portfolio-lane accounting). Program cumulative
**5,595 → 5,601**, 0 promoted anywhere in the program.

## Per-config table — every lane against the bar

Aligned common index: 3,180 daily bars 2012-05-18 → 2025-01-08 (truncated by
META's first bar, the Round-3 xsec short-history convention). Walk-forward:
train 1008 / test 252, 8 contiguous OOS splits, stitched OOS window
2016-05-23 → 2024-05-24. Benchmark: equal-weight XSEC-14 buy-and-hold, same
window, same costs (5 bps slippage + 1 bp commission per side). t =
informational ORDER-007 Bonferroni t on the stitched OOS Sharpe delta vs the
benchmark at K = 6 (bar ≈2.39, never lowered, promotion CLOSED).

Gate columns are sourced from the real selection-fair gate block recorded on
every lane (`selection_gate` in each `per_config` entry). This is a
1-config-per-lane portfolio slice, so `fixed_sharpe == searched_sharpe ==` the
lane's OOS Sharpe and `selection_gap = searched − fixed = 0.0` **by
construction** (no within-lane variant selection to replay); the gate is run
to honor standing rule 1 and coincides with the §6 rule here — see the
Reading note below.

| Slice | Family | Lane | OOS Sharpe | basket B&H Sharpe | t | bar (K=6) | Verdict | Gate | fixed / searched / gap |
|---|---|---|---|---|---|---|---|---|---|
| r7d-xsec-drawdown | xsec_drawdown | XSEC-14, L63/k2 | 0.919 | 1.193 | −0.78 | 2.39 | KILL | FAIL | 0.919 / 0.919 / 0.0 |
| r7d-xsec-drawdown | xsec_drawdown | XSEC-14, L63/k3 | 0.930 | 1.193 | −0.74 | 2.39 | KILL | FAIL | 0.930 / 0.930 / 0.0 |
| r7d-xsec-drawdown | xsec_drawdown | XSEC-14, L126/k2 | 0.571 | 1.193 | −1.76 | 2.39 | KILL | FAIL | 0.571 / 0.571 / 0.0 |
| r7d-xsec-drawdown | xsec_drawdown | XSEC-14, L126/k3 | 0.623 | 1.193 | −1.61 | 2.39 | KILL | FAIL | 0.623 / 0.623 / 0.0 |
| r7d-xsec-drawdown | xsec_drawdown | XSEC-14, L252/k2 | 0.706 | 1.193 | −1.38 | 2.39 | KILL | FAIL | 0.706 / 0.706 / 0.0 |
| r7d-xsec-drawdown | xsec_drawdown | XSEC-14, L252/k3 | 0.902 | 1.193 | −0.82 | 2.39 | KILL | FAIL | 0.902 / 0.902 / 0.0 |

All 6 gate decisions are `FAIL` with `reason_class = FAIL_UNDERPERFORM` (fixed
Sharpe positive but below same-window basket B&H) — folded through
`selection_gate.apply_gate` before the verdict is written; since every §6
verdict is already KILL the gate demotes nothing, but it is exercised and
recorded on every lane per standing rule 1.

Select-on-train stitch over the 6-config grid (BOOKKEEPING ONLY — not a
registered config, no verdict): OOS Sharpe 0.760, also below the benchmark.

### Reading — the selection-fair gate is degenerate on a 1-config-per-lane slice

For this portfolio slice each lane runs `portfolio_walk_forward` with a
**one-config grid**, so there is **no within-lane variant selection**. The
selection-fair gate is therefore exercised and recorded per lane (standing
rule 1) but is **degenerate**: `searched_sharpe == fixed_sharpe` (the lane's
own stitched OOS Sharpe), `selection_gap = 0.0`, and the fixed-config replay
IS the lane result — so the gate's fixed-vs-B&H test coincides exactly with
the §6 KEEP rule (OOS Sharpe > basket B&H AND > 0). It is run to honor
standing rule 1 and would **bite a future MULTI-variant portfolio lane**
(where an in-window re-selection could flatter the searched Sharpe over its
own fixed config, the R5-D pathology); here there is nothing for it to catch.
`run_selection_gate` is single-instrument-shaped, so the runner calls
`selection_gate.gate_decision` and builds the module-shaped block directly
(reusing the module's constants and reason strings).

### Counts

**0 KEEP-dev / 6 KILL / 0 KILL-SIG of 6 lanes; 0 promoted.** Every lane's
stitched OOS Sharpe is strictly below the equal-weight basket B&H benchmark
(1.193) — the §6 KILL condition — and none is significantly worse (most
negative t −1.76, inside the mirrored −2.39 bar), so no lane is classified
KILL-SIG. Best informational t anywhere is −0.74 (L63/k3), far below the
unchanged K=6 bar ≈2.39.

## reason_class rollup (all 6 lanes)

This rollup is now sourced directly from the `selection_gate` block recorded
on each of the 6 lanes (the `reason_class` field, one of
`selection_gate.REASON_CLASSES`) — not narrated. All 6 resolved to
`FAIL_UNDERPERFORM`; no per-lane fidelity/window pathology arose (all 6 graded
cleanly on the full 8-split OOS window), so every `UNGRADEABLE_*`
(infrastructure) class is zero. Standing rule 3 requires the UNGRADEABLE share
reported as an infrastructure alarm.

| reason_class | count | kind |
|---|---|---|
| `PASS` | 0 | strategy |
| `FAIL_UNDERPERFORM` (fixed Sharpe > 0 but ≤ basket B&H) | 6 | strategy |
| `FAIL_NONPOSITIVE` (fixed Sharpe ≤ 0) | 0 | strategy |
| `UNGRADEABLE_MISSING_WINDOWS` | 0 | infrastructure |
| `UNGRADEABLE_DRIFT` | 0 | infrastructure |
| `UNGRADEABLE_NONCONTIGUOUS` | 0 | infrastructure |
| `UNGRADEABLE_FIDELITY` | 0 | infrastructure |
| `UNGRADEABLE_NAN` | 0 | infrastructure |

**UNGRADEABLE share: 0 of 6 lanes (0.0%) — no infrastructure alarm.** Every
lane resolved to a strategy `reason_class` on clean, contiguous OOS windows;
no missing/non-contiguous window, NaN, or drift condition occurred. The 6/6
`FAIL_UNDERPERFORM` is a strategy result (drawdown ranking underperforms the
basket), never an infrastructure artefact. (`KILL-SIG` is a separate §6 /
`classify_verdict` concept — significantly worse than B&H — not a
`selection_gate` reason_class; 0 lanes are KILL-SIG, reported in Counts
above.)

## What this round says — and does NOT say

- **Says**: cross-sectional drawdown-depth ranking does not beat the
  equal-weight XSEC-14 buy-and-hold net of costs on any of the 6 registered
  lanes; the program's only consistently-observed effect (drawdown) does NOT
  carry benchmark-beating CROSS-SECTIONAL information here, mirroring the
  6/6 KILL of the return-ranked `xsec_reversal` and the mostly-null R7-A
  single-name drawdown lanes. The registered concentration mirror runs the
  wrong way (shallower `k=3`, shorter `L=63` out-Sharpe deeper/longer),
  offering no gradient to salvage.
- **Does NOT say**: anything out-of-sample (promotion CLOSED, holdout
  SPENT); that drawdown ranking is *harmful* (0 KILL-SIG — it is
  uninformative, not value-destroying); or that any longer-horizon or
  differently-concentrated variant would clear the bar (none registered).

## Reproducibility

- Plan (binding, pre-registered): `docs/research-round-7d-plan.md` (PR #147).
- Grid + pins: `trading_lab.sweeps._R7D_XSEC_DRAWDOWN_AXES` /
  `r7d_xsec_drawdown_variants` / `r7d_total_configs`;
  `tests/test_sweeps.py::TestR7DXsecDrawdown` (grid + counts + 5,595 → 5,601
  pinned before the run).
- Strategy + causality: `src/trading_lab/strategies/xsec_drawdown.py`;
  `tests/test_strategies.py::TestXsecDrawdown` (prefix-invariance, long-only
  sum-to-1, exactly-k-at-1/k, deepest-drawdown selection, tie-break,
  validation).
- Runner: `scripts/run_r7d_xsec_drawdown.py` (cloned from
  `scripts/run_r3_xsec_expanded.py`; SLICE `r7d-xsec-drawdown`, cap 900 s).
- Artifacts: `experiments/sweeps/r7d-xsec-drawdown/xsec_drawdown__XSEC-14.json`
  (per-config OOS metrics, per-split rows, benchmark OOS metrics, ORDER-007
  grade blocks, and the per-lane `selection_gate` block with
  `verdict_pre_gate`/`verdict`); ledger run
  `experiments/runs/20260718T154651954579Z-15fcf4d751d7.json`
  (top full-period config L63/k3, `instrument="XSEC-14"`, `variants_tried=6`);
  `experiments/index.jsonl`.
- Selection-fair gate (standing rule 1): built in
  `scripts/run_r7d_xsec_drawdown.py::selection_gate_block` via
  `trading_lab.selection_gate.gate_decision` and folded through
  `selection_gate.apply_gate`; degenerate on this 1-config-per-lane slice
  (`fixed == searched`, `selection_gap = 0`), see the Reading note above.
