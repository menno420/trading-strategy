#!/usr/bin/env python3
"""Run the three baseline strategies on daily data for the whole universe
(default parameters, pre-holdout dev data only) and write ledger entries.

Usage: python3 scripts/run_baselines.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config, ledger  # noqa: E402
from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.strategies import DEFAULT_PARAMS, STRATEGIES  # noqa: E402

TIMEFRAME = "daily"

for ticker in config.UNIVERSE:
    ohlcv = load_ohlcv(ticker, TIMEFRAME)  # holdout excluded by default
    for name in STRATEGIES:
        path = ledger.run_and_record(
            strategy=name,
            instrument=ticker,
            timeframe=TIMEFRAME,
            ohlcv=ohlcv,
            params=DEFAULT_PARAMS[name],
            variants_tried=1,  # single default-param run, honestly counted
            notes="P0 baseline run, default params, dev period (pre-holdout)",
        )
        print(path.name)

print("rebuilding index...")
print(ledger.rebuild_index())
