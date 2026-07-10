"""Experiment ledger: one JSON file per backtest run.

One-file-per-run is the conflict-avoidance mechanism — parallel sessions
never contend on a shared file. The human-readable index
(``experiments/index.jsonl``) is REGENERATED from the run files by
:func:`rebuild_index` (``python3 -m trading_lab.ledger``) rather than
appended, so it can never conflict either. (Decide-and-flag: regenerate
beats append because it is idempotent and self-heals after merges.)

Every record carries ``variants_tried`` (multiple-testing discipline) and
benchmark buy-and-hold metrics for the same instrument/period
(founding-plan rails).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from . import config, metrics
from .engine import BacktestResult, buy_and_hold_result, run_backtest
from .strategies import STRATEGIES

SCHEMA_VERSION = 1

REQUIRED_FIELDS = [
    "schema_version", "run_id", "created_utc", "git_sha", "config_hash",
    "strategy", "params", "instrument", "timeframe", "data_start", "data_end",
    "n_bars", "costs", "execution", "metrics", "benchmark_metrics",
    "variants_tried",
]


def config_hash(payload: dict) -> str:
    """Stable short hash of a run configuration."""
    blob = json.dumps(payload, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], capture_output=True, text=True,
            check=True, cwd=config.REPO_ROOT,
        ).stdout.strip()
    except Exception:
        return "unknown"


def _enforce_holdout(data_end: str, holdout_unlocked: bool) -> None:
    """Refuse ledger records whose data reaches into the locked holdout.

    The loader rail (``trading_lab.data.load_ohlcv``) is the first line of
    defense; this is the second: no record with
    ``data_end >= config.HOLDOUT_START`` can be written unless the caller
    passed ``holdout_unlocked=True`` explicitly, in which case the record
    must carry a visible ``"holdout_unlocked": true`` marker so ledger rows
    self-declare. Reserved for the P5 final review (docs/founding-plan.md,
    docs/holdout-enforcement.md).
    """
    if pd.Timestamp(data_end) >= pd.Timestamp(config.HOLDOUT_START) \
            and not holdout_unlocked:
        raise ValueError(
            f"ledger record has data_end={data_end!r} inside the locked "
            f"holdout (>= {config.HOLDOUT_START}). This is forbidden before "
            "the P5 final review; if this IS the P5 final review, pass "
            "holdout_unlocked=True so the record carries the visible "
            "'holdout_unlocked' marker (docs/holdout-enforcement.md).")


def build_record(*, strategy: str, params: dict, instrument: str,
                 timeframe: str, ohlcv: pd.DataFrame, result: BacktestResult,
                 benchmark: BacktestResult, variants_tried: int,
                 notes: str = "", holdout_unlocked: bool = False) -> dict:
    cfg = {
        "strategy": strategy, "params": params, "instrument": instrument,
        "timeframe": timeframe,
        "slippage_bps": result.meta.get("slippage_bps"),
        "commission_bps": result.meta.get("commission_bps"),
        "data_start": str(ohlcv.index[0]), "data_end": str(ohlcv.index[-1]),
    }
    _enforce_holdout(str(ohlcv.index[-1]), holdout_unlocked)
    record = {
        "schema_version": SCHEMA_VERSION,
        "run_id": None,  # filled by write_run
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git_sha": git_sha(),
        "config_hash": config_hash(cfg),
        "strategy": strategy,
        "params": params,
        "instrument": instrument,
        "timeframe": timeframe,
        "data_start": str(ohlcv.index[0]),
        "data_end": str(ohlcv.index[-1]),
        "n_bars": int(len(ohlcv)),
        "costs": {"slippage_bps": result.meta.get("slippage_bps"),
                  "commission_bps": result.meta.get("commission_bps")},
        "execution": result.meta.get("execution"),
        "metrics": metrics.compute_all(result),
        "benchmark_metrics": metrics.compute_all(benchmark),
        "variants_tried": int(variants_tried),
        "notes": notes,
    }
    if holdout_unlocked:
        # Visible marker: unlocked rows must self-declare (P5 only).
        record["holdout_unlocked"] = True
    return record


def write_run(record: dict, runs_dir: Path | None = None) -> Path:
    """Write one run record to ``experiments/runs/<utc-stamp>-<hash>.json``."""
    missing = [f for f in REQUIRED_FIELDS if f not in record]
    if missing:
        raise ValueError(f"ledger record missing fields: {missing}")
    # Choke point: every record on disk passes the holdout rail, even ones
    # not built via build_record.
    _enforce_holdout(record["data_end"], bool(record.get("holdout_unlocked")))
    runs = Path(runs_dir) if runs_dir is not None else config.RUNS_DIR
    runs.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run_id = f"{stamp}-{record['config_hash']}"
    record = dict(record, run_id=run_id)
    path = runs / f"{run_id}.json"
    path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    return path


def run_and_record(*, strategy: str, instrument: str, timeframe: str,
                   ohlcv: pd.DataFrame, params: dict | None = None,
                   variants_tried: int = 1,
                   slippage_bps: float = config.DEFAULT_SLIPPAGE_BPS,
                   commission_bps: float = config.DEFAULT_COMMISSION_BPS,
                   runs_dir: Path | None = None, notes: str = "",
                   holdout_unlocked: bool = False) -> Path:
    """Convenience wrapper: backtest + benchmark + ledger write."""
    params = params or {}
    positions = STRATEGIES[strategy](ohlcv, **params)
    result = run_backtest(ohlcv, positions, slippage_bps=slippage_bps,
                          commission_bps=commission_bps, timeframe=timeframe)
    benchmark = buy_and_hold_result(ohlcv, slippage_bps=slippage_bps,
                                    commission_bps=commission_bps,
                                    timeframe=timeframe)
    record = build_record(strategy=strategy, params=params,
                          instrument=instrument, timeframe=timeframe,
                          ohlcv=ohlcv, result=result, benchmark=benchmark,
                          variants_tried=variants_tried, notes=notes,
                          holdout_unlocked=holdout_unlocked)
    return write_run(record, runs_dir=runs_dir)


def rebuild_index(experiments_dir: Path | None = None) -> Path:
    """Regenerate ``experiments/index.jsonl`` from the per-run files."""
    exp = Path(experiments_dir) if experiments_dir is not None else config.EXPERIMENTS_DIR
    runs = sorted((exp / "runs").glob("*.json"))
    lines = []
    for path in runs:
        rec = json.loads(path.read_text())
        lines.append(json.dumps({
            "run_id": rec["run_id"],
            "strategy": rec["strategy"],
            "params": rec["params"],
            "instrument": rec["instrument"],
            "timeframe": rec["timeframe"],
            "data_start": rec["data_start"],
            "data_end": rec["data_end"],
            "sharpe": rec["metrics"].get("sharpe"),
            "cagr": rec["metrics"].get("cagr"),
            "max_drawdown": rec["metrics"].get("max_drawdown"),
            "benchmark_sharpe": rec["benchmark_metrics"].get("sharpe"),
            "variants_tried": rec["variants_tried"],
            "file": f"runs/{path.name}",
            # propagate the unlock marker so index rows self-declare too
            **({"holdout_unlocked": True} if rec.get("holdout_unlocked") else {}),
        }, sort_keys=True))
    out = exp / "index.jsonl"
    out.write_text("\n".join(lines) + ("\n" if lines else ""))
    return out


if __name__ == "__main__":
    path = rebuild_index()
    print(f"rebuilt {path}")
