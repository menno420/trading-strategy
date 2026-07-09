"""Central configuration for trading-lab.

Binding methodology lives in docs/founding-plan.md. The constants here
enforce two of its rails in code:

* ``HOLDOUT_START`` — the locked out-of-sample holdout boundary. The most
  recent 18 months of data (everything on or after this date) is untouchable
  until roadmap P5. ``trading_lab.data.load_ohlcv`` excludes those bars by
  default; the ``unlock_holdout=True`` escape hatch exists ONLY for the P5
  final review and logs a loud warning.
* Cost defaults — every backtest pays slippage + commission unless a
  zero-cost run is explicitly requested.
"""

from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------
# Instrument universe
# --------------------------------------------------------------------------
# Metals via GLD/SLV ETFs rather than GC=F/SI=F futures: cleaner free hourly
# data, regular equity sessions, no contract-roll artifacts. (Decide-and-flag.)
TECH_TICKERS = ["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN", "META"]
METAL_TICKERS = ["GLD", "SLV"]
UNIVERSE = TECH_TICKERS + METAL_TICKERS

# --------------------------------------------------------------------------
# Locked holdout (founding-plan: 18 months untouched until P5)
# --------------------------------------------------------------------------
# Bars with timestamp >= HOLDOUT_START are excluded by the data loader by
# default. Do not change this constant; do not read holdout bars before P5.
HOLDOUT_START = "2025-01-09"

# --------------------------------------------------------------------------
# Timeframes
# --------------------------------------------------------------------------
TIMEFRAMES = ("daily", "hourly")

# Annualization factors: 252 trading days; ~6.5 regular-session hours/day.
PERIODS_PER_YEAR = {
    "daily": 252.0,
    "hourly": 252.0 * 6.5,  # = 1638
}

# --------------------------------------------------------------------------
# Cost defaults (per side, in basis points of traded notional)
# --------------------------------------------------------------------------
DEFAULT_SLIPPAGE_BPS = 5.0
DEFAULT_COMMISSION_BPS = 1.0

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
EXPERIMENTS_DIR = REPO_ROOT / "experiments"
RUNS_DIR = EXPERIMENTS_DIR / "runs"

# Daily history fetched from this date onward.
DAILY_START = "2010-01-01"
