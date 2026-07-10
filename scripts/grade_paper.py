#!/usr/bin/env python3
"""Run one paper-lane grading pass (docs/paper-lane-protocol.md §6-§7).

Usage: python3 scripts/grade_paper.py

Grades every closed, ungraded window in experiments/paper/ledger.md and
appends the verdict fields to the graded EXIT records. Idempotent: rows
already carrying a verdict are never touched; WATCH and ENTRY rows are
never mutated. Market data is read ONLY via trading_lab.data.load_paper_ohlcv
(bars >= PAPER_LANE_START only — no holdout access of any kind). Refresh
the cache first with scripts/fetch_data.py if fills are missing.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trading_lab.paper import main  # noqa: E402

raise SystemExit(main())
