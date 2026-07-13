#!/usr/bin/env python3
"""Round 4 slice R4-C — equal-weight committees of round-3 KEEP-dev survivors.

POST-HOLDOUT, DEV-ONLY (ORDER 012 generative rung, 2026-07-13 night-run
direct order "continue with some new ideas"). Promotion is closed: nothing
this script produces can be an out-of-sample claim; a committee that KEEPs
is a dev-candidate only, never a finding.

Pre-registration: ``docs/research-round-4-plan.md`` § "R4-C — Ensemble /
committee of survivors", merged to main BEFORE this script existed.
Registered method: per instrument with >= 2 KEEP-dev families, form an
equal-weight signal committee — **position = mean of member positions**
(``trading_lab.ensemble.committee_positions``) — and grade it vs (a) the
best single member and (b) B&H, on the same rail, costs, and walk-forward
windows as the members. Members are FROZEN as the lanes' already-committed
top variants (no re-search inside the committee). Registered rule: KEEP
(dev-candidate only) iff the committee beats BOTH the best single member
and the benchmark on stitched OOS Sharpe; otherwise KILL. Registered
hypothesis: diversification raises Sharpe modestly, but NO committee
clears t >= 2.64.

KEEP universe: the **58** ``new_verdict == "KEEP"`` lanes of
``experiments/sweeps/r4-killsig-regrade/summary.json`` (R4-A, PR #100) —
the same committed, machine-readable KEEP surface R4-B graded (PR #101).

Adopted conventions the plan is silent on (declared in the grid commit
BEFORE any committee ran; ``trading_lab.ensemble`` module docstring):

* **Grouping is instrument x timeframe** — averaging daily and hourly
  positions is not meaningful (different bar clocks and walk-forward
  windows), so committees never mix timeframes.
* **One member per family per committee** (the plan says "families");
  duplicate round-3 coverage (TLT and XOM ``donchian``, each KEEP in two
  sweeps) is deduped by a performance-blind lexicographic tiebreak. The
  deduped-out lanes still count in the **best-member comparison**, which
  uses ALL the group's KEEP lanes (committed stitched OOS Sharpes) — a
  superset that can only RAISE the bar the committee must clear.
* **Informational t at the round-standard K = 12** (bar
  ``min_tstat(12)`` ≈ 2.638): each committee is one pre-declared config,
  but the plan registers no other K for this slice and the bar is NEVER
  lowered, so the standard bar stands. ``classify_verdict`` is applied,
  so KILL-SIG (t <= −2.638) is possible.

NO RE-SEARCH, implemented literally (frozen-replay precedent PR #101):
each member's committed r3 per-lane summary records the walk-forward's
chosen params per split (``walk_forward.per_split[].params``) and the
exact positional test windows; the script recomputes those frozen
positions, VERIFIES every member reproduces its committed stitched OOS
Sharpe at baseline costs bit-for-bit (tolerance 1e-8, the R4-B fidelity
guard), asserts all members of a committee share identical test windows,
then averages the member positions per split, re-prices the committee at
baseline costs (5 bps + 1 bp per side), and stitches the OOS. The
benchmark is same-window same-cost buy-and-hold. Any member that cannot
be reproduced exactly makes its whole committee **SKIPPED with the
verbatim reason**, never approximated silently.

Fractional positions are expected (disagreement averages to e.g. 0.5) and
supported natively by ``trading_lab.engine.run_backtest`` (positions in
[-1, 1]; costs charged on |change in held position|, fractional included
— pinned by tests/test_ensemble.py).

Data ONLY via ``trading_lab.data.load_ohlcv`` on its default rail (holdout
bars >= 2025-01-09 excluded; ``data_end <= 2025-01-08`` asserted per
ticker); ``unlock_holdout`` is never passed. All prior
``experiments/sweeps/**`` files stay byte-untouched — this slice is
additive only, writing ``experiments/sweeps/r4-ensemble/``: per-committee
JSONs + one rollup ``summary.json``.

LEDGER DECISION (deliberate, splitting the R4-B/R4-F precedents): these
ARE ledgered — one row per committee, ``strategy =
"committee_equal_weight"``, ``variants_tried = 1``. Unlike R4-B's frozen
replay at different costs (report-only: same strategy, same params, same
instrument as existing rows), a committee is a genuinely NEW composite
run with a return stream no existing ledger row describes; like R4-F's
new family, new runs are ledgered. ``variants_tried = 1`` is the literal
count (each committee is one pre-declared config, no search); the
informational promotion grade in the sweep JSONs is nonetheless computed
at the round-standard K = 12, because the bar is never lowered.

Usage: python3 scripts/run_r4_ensemble_sweep.py
"""

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger, metrics, promotion, sweeps  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.engine import (BacktestResult, buy_and_hold_result,  # noqa: E402
                                run_backtest)
from trading_lab.ensemble import (committee_positions,  # noqa: E402
                                  enumerate_committees)
from trading_lab.strategies import STRATEGIES  # noqa: E402

SWEEP_NAME = "r4-ensemble"
SWEEP_DIR = config.EXPERIMENTS_DIR / "sweeps" / SWEEP_NAME
KEEP_UNIVERSE_FILE = config.REPO_ROOT / sweeps.R4_ENSEMBLE_KEEP_UNIVERSE

# Dev rail: the loader's default excludes holdout bars >= 2025-01-09.
DEV_DATA_END_MAX = "2025-01-08"

BASELINE_COSTS = {"slippage_bps": float(config.DEFAULT_SLIPPAGE_BPS),
                  "commission_bps": float(config.DEFAULT_COMMISSION_BPS)}

# Fidelity guard tolerance on each member's baseline stitched OOS replay.
REPLAY_TOL = 1e-8

VERDICT_KEEP = "KEEP (dev-candidate only)"
VERDICT_KILL = "KILL"
STATUS_SKIPPED = "SKIPPED"


class CommitteeSkip(Exception):
    """Committee cannot be built exactly — recorded verbatim, never
    approximated silently (the R4-B honesty rule, inherited)."""


def _clean(x):
    """NaN -> None for JSON."""
    if isinstance(x, float) and math.isnan(x):
        return None
    return x


def series_metrics(returns, equity, timeframe) -> dict:
    """Metrics computable from stitched OOS returns/equity alone (r3 shape)."""
    out = {
        "sharpe": metrics.sharpe(returns, timeframe),
        "sortino": metrics.sortino(returns, timeframe),
        "cagr": metrics.cagr(equity, timeframe),
        "total_return": metrics.total_return(equity),
        "max_drawdown": metrics.max_drawdown(equity),
        "n_bars": int(len(returns)),
    }
    return {k: _clean(v) for k, v in out.items()}


def frozen_positions(ohlcv, strategy_fn, per_split):
    """Recompute a member's already-chosen positions per test split
    (verbatim R4-B logic: frozen params + positional test windows from the
    committed r3 summary; indicators are causal, nothing >= test_end is
    seen; positions depend only on price data, never on costs)."""
    out = []
    for row in per_split:
        t0, t1 = int(row["test"][0]), int(row["test"][1])
        pos = strategy_fn(ohlcv.iloc[:t1], **row["params"]).iloc[t0:t1]
        out.append({"test": [t0, t1], "params": row["params"],
                    "positions": pos})
    return out


def replay_member_baseline(ohlcv, frozen, timeframe) -> float:
    """Stitched OOS Sharpe of a member's frozen positions at baseline costs
    (the fidelity-guard number)."""
    rets = []
    for row in frozen:
        t0, t1 = row["test"]
        res = run_backtest(ohlcv.iloc[t0:t1], row["positions"],
                           timeframe=timeframe, **BASELINE_COSTS)
        rets.append(res.returns)
    return metrics.sharpe(pd.concat(rets), timeframe)


def prepare_member(source: dict, lane_path: str, ohlcv):
    """Rebuild one member's frozen positions and run the fidelity guard.

    Raises CommitteeSkip with a verbatim reason on any mismatch."""
    fam = source["family"]
    if fam not in STRATEGIES:
        raise CommitteeSkip(f"member strategy {fam!r} not in "
                            f"trading_lab.strategies.STRATEGIES — original "
                            f"rail cannot be rebuilt ({lane_path})")
    for field, got in (("data_start", str(ohlcv.index[0])),
                       ("data_end", str(ohlcv.index[-1])),
                       ("n_bars", int(len(ohlcv)))):
        if got != source[field]:
            raise CommitteeSkip(f"cache drift vs committed lane {lane_path}: "
                                f"{field} recorded {source[field]!r}, loaded "
                                f"{got!r} — positional windows would "
                                f"misalign")
    frozen = frozen_positions(ohlcv, STRATEGIES[fam],
                              source["walk_forward"]["per_split"])
    got_sharpe = replay_member_baseline(ohlcv, frozen, source["timeframe"])
    rec_sharpe = source["walk_forward"]["oos_metrics"]["sharpe"]
    if not (abs(got_sharpe - rec_sharpe) <= REPLAY_TOL):
        raise CommitteeSkip(f"baseline replay mismatch for {lane_path}: "
                            f"replayed stitched OOS Sharpe {got_sharpe!r} vs "
                            f"recorded {rec_sharpe!r} (tol {REPLAY_TOL}) — "
                            f"refusing to build a committee on an "
                            f"unreproduced member")
    return frozen, got_sharpe


def stitch_committee(ohlcv, member_frozen: list, timeframe: str):
    """Average the members' frozen positions per split, re-price at
    baseline costs, and stitch the OOS. Returns (BacktestResult over the
    stitched OOS, per-split rows). No selection of any kind happens here."""
    windows = [tuple(row["test"]) for row in member_frozen[0]]
    for frozen in member_frozen[1:]:
        if [tuple(r["test"]) for r in frozen] != list(windows):
            raise CommitteeSkip("members do not share identical walk-forward "
                                "test windows — committee undefined")
    rets, helds, trades, per = [], [], [], []
    for i, (t0, t1) in enumerate(windows):
        pos = committee_positions([frozen[i]["positions"]
                                   for frozen in member_frozen])
        res = run_backtest(ohlcv.iloc[t0:t1], pos, timeframe=timeframe,
                           **BASELINE_COSTS)
        rets.append(res.returns)
        helds.append(res.held)
        trades.append(res.trades)
        per.append({"test": [t0, t1],
                    "test_sharpe": _clean(metrics.sharpe(res.returns,
                                                         timeframe))})
    returns = pd.concat(rets)
    equity = (1.0 + returns).cumprod()
    result = BacktestResult(
        equity=equity, returns=returns, held=pd.concat(helds),
        trades=pd.concat(trades, ignore_index=True),
        cost_bps_per_side=(BASELINE_COSTS["slippage_bps"]
                           + BASELINE_COSTS["commission_bps"]),
        timeframe=timeframe,
        meta={**BASELINE_COSTS,
              "execution": "signal at bar t fills at bar t+1 open",
              "n_bars": int(len(returns))},
    )
    return result, per


def load_keep_universe() -> list[dict]:
    report = json.loads(KEEP_UNIVERSE_FILE.read_text())
    keeps = [r for r in report["lanes"] if r["new_verdict"] == "KEEP"]
    if len(keeps) != sweeps.R4_ENSEMBLE_EXPECTED_KEEPS:
        raise SystemExit(f"KEEP universe drifted: expected "
                         f"{sweeps.R4_ENSEMBLE_EXPECTED_KEEPS}, found "
                         f"{len(keeps)} in {KEEP_UNIVERSE_FILE}")
    return keeps


def main() -> None:
    t_start = time.monotonic()
    SWEEP_DIR.mkdir(parents=True, exist_ok=True)
    keeps = load_keep_universe()
    committees = enumerate_committees(
        keeps, min_members=sweeps.R4_ENSEMBLE_MIN_MEMBERS)
    n_single = len(keeps) - sum(len(c["group_lanes"]) for c in committees)
    print(f"KEEP universe: {len(keeps)} lanes -> {len(committees)} "
          f"committees (instrument x timeframe, >= "
          f"{sweeps.R4_ENSEMBLE_MIN_MEMBERS} members; {n_single} "
          f"single-survivor lanes excluded)")
    rollup_rows, skipped, ledger_files = [], [], []

    for i, com in enumerate(committees, 1):
        tick, tf = com["instrument"], com["timeframe"]
        tag = f"{tick} {tf} ({len(com['members'])} members)"
        row = {
            "instrument": tick, "timeframe": tf,
            "member_count": len(com["members"]),
            "members": [{"strategy": m["strategy"], "sweep": m["sweep"],
                         "source_file": m["source_file"]}
                        for m in com["members"]],
            "deduped_out": [{"strategy": m["strategy"], "sweep": m["sweep"],
                             "source_file": m["source_file"]}
                            for m in com["deduped_out"]],
        }
        try:
            ohlcv = load_ohlcv(tick, tf)  # dev rail: holdout excluded
            data_end = str(ohlcv.index[-1])
            assert data_end[:10] <= DEV_DATA_END_MAX, \
                f"{tick}: dev rail breached (data_end {data_end})"
            sources, member_frozen, member_rows = [], [], []
            for m in com["members"]:
                source = json.loads(
                    (config.REPO_ROOT / m["source_file"]).read_text())
                frozen, replayed = prepare_member(source, m["source_file"],
                                                  ohlcv)
                sources.append(source)
                member_frozen.append(frozen)
                member_rows.append({
                    "strategy": m["strategy"], "sweep": m["sweep"],
                    "source_file": m["source_file"],
                    "committed_oos_sharpe":
                        source["walk_forward"]["oos_metrics"]["sharpe"],
                    "replayed_oos_sharpe": replayed,
                    "replay_matches_committed": True,
                    "per_split_params": [
                        {"test": r["test"], "params": r["params"]}
                        for r in source["walk_forward"]["per_split"]],
                })
            committee_result, per_split = stitch_committee(
                ohlcv, member_frozen, tf)
        except CommitteeSkip as exc:
            row["status"] = STATUS_SKIPPED
            row["skip_reason"] = str(exc)
            skipped.append(row)
            rollup_rows.append(row)
            print(f"[{i}/{len(committees)}] {tag}: SKIPPED — {exc}")
            continue

        # Best-member comparison over ALL the group's KEEP lanes (committed
        # stitched OOS Sharpes; superset incl. deduped-out duplicates —
        # can only raise the bar).
        group_sharpes = {}
        for lane in com["group_lanes"]:
            src = json.loads(
                (config.REPO_ROOT / lane["source_file"]).read_text())
            group_sharpes[lane["source_file"]] = \
                src["walk_forward"]["oos_metrics"]["sharpe"]
        best_file = max(group_sharpes, key=group_sharpes.get)
        best_member_sharpe = group_sharpes[best_file]
        best_lane = next(l for l in com["group_lanes"]
                         if l["source_file"] == best_file)

        oos_lo = member_frozen[0][0]["test"][0]
        oos_hi = member_frozen[0][-1]["test"][1]
        oos_slice = ohlcv.iloc[oos_lo:oos_hi]
        bench = buy_and_hold_result(oos_slice, timeframe=tf,
                                    **BASELINE_COSTS)
        oos_m = series_metrics(committee_result.returns,
                               committee_result.equity, tf)
        bench_m = {k: _clean(v)
                   for k, v in metrics.compute_all(bench).items()}
        com_sharpe = oos_m["sharpe"]
        beats_best = (com_sharpe is not None
                      and com_sharpe > best_member_sharpe)
        beats_bench = (com_sharpe is not None and bench_m["sharpe"] is not None
                       and com_sharpe > bench_m["sharpe"])
        keep = bool(beats_best and beats_bench and com_sharpe > 0)
        verdict = VERDICT_KEEP if keep else VERDICT_KILL
        grade = promotion.grade_promotion(
            strategy_sharpe=com_sharpe, benchmark_sharpe=bench_m["sharpe"],
            n_periods=oos_m["n_bars"], timeframe=tf,
            variants_tried=sweeps.R4_ENSEMBLE_K)
        sweep_verdict = promotion.classify_verdict(keep, grade["tstat"],
                                                   grade["min_tstat"])

        # Ledger: one row per committee — a genuinely NEW composite run
        # (see module docstring). variants_tried=1 is the literal count.
        led_record = ledger.build_record(
            strategy=sweeps.R4_ENSEMBLE_STRATEGY_NAME,
            params={"weighting": "equal",
                    "min_members": sweeps.R4_ENSEMBLE_MIN_MEMBERS,
                    "members": [f"{m['strategy']}@{m['sweep']}"
                                for m in com["members"]]},
            instrument=tick, timeframe=tf, ohlcv=oos_slice,
            result=committee_result, benchmark=bench, variants_tried=1,
            notes=("R4-C survivor committee (docs/research-round-4-plan.md "
                   "§ R4-C; post-holdout DEV-ONLY, promotion closed). "
                   "Stitched walk-forward OOS composite of frozen KEEP-dev "
                   "members (position = mean of member positions); metrics "
                   "are over the stitched OOS window, not a single-window "
                   "run. Informational t graded at the round-standard K=12 "
                   "in the sweep JSON (bar never lowered)."))
        ledger_files.append(str(ledger.write_run(led_record)
                                .relative_to(config.REPO_ROOT)))

        record = {
            "schema_version": 1,
            "sweep": SWEEP_NAME,
            "created_utc": datetime.now(timezone.utc)
                                   .isoformat(timespec="seconds"),
            "git_sha": ledger.git_sha(),
            "family": sweeps.R4_ENSEMBLE_STRATEGY_NAME,
            "instrument": tick,
            "timeframe": tf,
            "post_holdout_dev_only": True,
            "order": "ORDER 012 night-run (control/inbox.md)",
            "preregistered_in": ("docs/research-round-4-plan.md § R4-C — "
                                 "Ensemble / committee of survivors"),
            "costs": BASELINE_COSTS,
            "execution": "signal at bar t fills at bar t+1 open",
            "committee": {
                "weighting": "equal (position = mean of member positions)",
                "member_count": len(com["members"]),
                "members": member_rows,
                "deduped_out": row["deduped_out"],
                "grouping": ("instrument x timeframe — committees never "
                             "mix timeframes (adopted convention, plan "
                             "silent; declared in the grid commit)"),
                "dedup": ("one member per family; performance-blind "
                          "lexicographic (sweep, source_file) tiebreak; "
                          "deduped-out lanes still count in the "
                          "best-member comparison"),
            },
            "no_research": ("frozen replay of each member's committed "
                            "walk-forward per-split params on the same "
                            "test windows; the committee (the mean) is the "
                            "only new object — no search of any kind"),
            "fidelity_guard": {
                "rule": ("every member's baseline replay must reproduce "
                         "its committed stitched OOS Sharpe within "
                         f"{REPLAY_TOL}"),
                "all_members_reproduced": True,
            },
            "data_start": str(ohlcv.index[0]),
            "data_end": str(ohlcv.index[-1]),
            "n_bars": int(len(ohlcv)),
            "walk_forward": {
                "train_size": sources[0]["walk_forward"]["train_size"],
                "test_size": sources[0]["walk_forward"]["test_size"],
                "n_splits": sources[0]["walk_forward"]["n_splits"],
                "oos_start": sources[0]["walk_forward"]["oos_start"],
                "oos_end": sources[0]["walk_forward"]["oos_end"],
                "oos_metrics": oos_m,
                "benchmark_oos_metrics": bench_m,
                "per_split": per_split,
            },
            "best_member": {
                "strategy": best_lane["strategy"],
                "sweep": best_lane["sweep"],
                "source_file": best_file,
                "oos_sharpe": best_member_sharpe,
                "note": ("best committed stitched OOS Sharpe over ALL the "
                         "group's KEEP lanes (superset incl. deduped-out "
                         "duplicates — can only raise the bar)"),
            },
            "member_oos_sharpes": {f"{m['strategy']}@{m['sweep']}":
                                   m["committed_oos_sharpe"]
                                   for m in member_rows},
            "committee_oos_sharpe": com_sharpe,
            "benchmark_oos_sharpe": bench_m["sharpe"],
            "beats_best_member": beats_best,
            "beats_benchmark": beats_bench,
            "kill_criterion": ("KEEP (dev-candidate only) iff committee "
                               "stitched OOS Sharpe > best single member "
                               "AND > same-window same-cost B&H AND > 0; "
                               "ties/ambiguity KILL"),
            "verdict": verdict,
            "sweep_verdict": sweep_verdict,
            "promotion_grade": {
                "note": ("ORDER 007 bar at the round-standard K=12 — "
                         "INFORMATIONAL ONLY, promotion is CLOSED "
                         "post-holdout (nothing here is a finding); the "
                         "committee is one pre-declared config but the "
                         "bar is never lowered"),
                **grade,
            },
            "ledger": ("ledgered: one row per committee, strategy "
                       f"{sweeps.R4_ENSEMBLE_STRATEGY_NAME!r}, "
                       "variants_tried=1 — a committee is a genuinely new "
                       "composite run (unlike the R4-B replay, which was "
                       "report-only)"),
            "ledger_file": ledger_files[-1],
        }
        out = SWEEP_DIR / f"committee__{tick}__{tf}.json"
        out.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
        row.update({
            "status": "GRADED",
            "committee_oos_sharpe": com_sharpe,
            "best_member_sharpe": best_member_sharpe,
            "best_member": f"{best_lane['strategy']}@{best_lane['sweep']}",
            "benchmark_oos_sharpe": bench_m["sharpe"],
            "beats_best_member": beats_best,
            "beats_benchmark": beats_bench,
            "verdict": verdict,
            "sweep_verdict": sweep_verdict,
            "tstat": _clean(grade["tstat"]),
            "min_tstat": grade["min_tstat"],
            "detail_file": str(out.relative_to(config.REPO_ROOT)),
        })
        rollup_rows.append(row)
        print(f"[{i}/{len(committees)}] {tag}: committee "
              f"{com_sharpe:.3f} vs best member {best_member_sharpe:.3f} "
              f"({row['best_member']}) vs bench {bench_m['sharpe']:.3f} "
              f"-> {verdict} [{sweep_verdict}] t={grade['tstat']:.2f}")

    graded = [r for r in rollup_rows if r["status"] == "GRADED"]
    counts = {
        "keep_universe": len(keeps),
        "committees": len(committees),
        "graded": len(graded),
        "skipped": len(skipped),
        "keep": sum(1 for r in graded if r["verdict"] == VERDICT_KEEP),
        "kill": sum(1 for r in graded if r["verdict"] == VERDICT_KILL),
        "kill_sig": sum(1 for r in graded
                        if r["sweep_verdict"] == promotion.SWEEP_KILL_SIG),
        "beats_best_member": sum(1 for r in graded if r["beats_best_member"]),
        "beats_benchmark": sum(1 for r in graded if r["beats_benchmark"]),
    }
    ledger.rebuild_index()
    elapsed = time.monotonic() - t_start
    report = {
        "schema_version": 1,
        "slice": SWEEP_NAME,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "git_sha": ledger.git_sha(),
        "order": "ORDER 012 (generative rung)",
        "preregistered_in": ("docs/research-round-4-plan.md § R4-C — "
                             "Ensemble / committee of survivors"),
        "post_holdout_dev_only": ("holdout SPENT, promotion CLOSED; every "
                                  "KEEP is a dev-candidate only, never a "
                                  "finding"),
        "keep_universe": (f"the {sweeps.R4_ENSEMBLE_EXPECTED_KEEPS} "
                          f"new_verdict==KEEP lanes of "
                          f"{sweeps.R4_ENSEMBLE_KEEP_UNIVERSE} (R4-A, "
                          f"PR #100)"),
        "costs": BASELINE_COSTS,
        "rule": ("per committee: KEEP (dev-candidate only) iff stitched "
                 "OOS Sharpe > best single member AND > same-window "
                 "same-cost B&H AND > 0; otherwise KILL (KILL-SIG at "
                 "t <= -min_tstat(12) via classify_verdict); t "
                 "informational only at the round-standard K=12"),
        "grouping": ("instrument x timeframe with >= "
                     f"{sweeps.R4_ENSEMBLE_MIN_MEMBERS} KEEP-dev lanes; "
                     "committees never mix timeframes; one member per "
                     "family (performance-blind dedup; best-member "
                     "comparison uses the full group superset)"),
        "no_research": ("members frozen at their committed walk-forward "
                        "per-split params; the equal-weight mean is the "
                        "only new object; no selection pass anywhere"),
        "fidelity_guard": (f"every member's baseline replay reproduced its "
                           f"committed stitched OOS Sharpe within "
                           f"{REPLAY_TOL}; any irreproducible member skips "
                           f"its whole committee with the verbatim reason"),
        "ledger_decision": ("ledgered (deliberate): one row per committee, "
                            f"strategy {sweeps.R4_ENSEMBLE_STRATEGY_NAME!r}"
                            ", variants_tried=1 — a committee is a "
                            "genuinely new composite run, unlike the R4-B "
                            "frozen replay (report-only); "
                            "experiments/index.jsonl rebuilt"),
        "ledger_files": ledger_files,
        "runtime_seconds": round(elapsed, 1),
        "counts": counts,
        "committees": rollup_rows,
    }
    out = SWEEP_DIR / "summary.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(f"\nsummary: {counts['committees']} committees — "
          f"{counts['keep']} KEEP / {counts['kill']} KILL "
          f"({counts['kill_sig']} KILL-SIG), "
          f"{counts['beats_best_member']} beat their best member, "
          f"{counts['beats_benchmark']} beat the benchmark, "
          f"{counts['skipped']} skipped ({elapsed:.1f}s) -> {out}")
    for r in skipped:
        print(f"  SKIPPED: {r['instrument']} {r['timeframe']} — "
              f"{r['skip_reason']}")


if __name__ == "__main__":
    main()
