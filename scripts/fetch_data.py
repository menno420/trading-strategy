#!/usr/bin/env python3
"""Refresh the committed OHLCV cache for the whole universe.

Usage: python3 scripts/fetch_data.py [daily|hourly ...]

Fetches everything available (including holdout bars — the loader enforces
the holdout at read time) and writes data/{timeframe}/{ticker}.csv.gz.
"""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab import config  # noqa: E402
from trading_lab.data import refresh_cache  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

timeframes = tuple(sys.argv[1:]) or config.TIMEFRAMES
counts = refresh_cache(timeframes=timeframes)
for key, n in counts.items():
    print(f"{key}: {n} bars")
