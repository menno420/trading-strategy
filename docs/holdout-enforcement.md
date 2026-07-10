# Holdout enforcement contract

> **Status:** `binding` — the locked-holdout rail, hardened 2026-07-10
> (lane `holdout-collab`, QUEUE item 5). Extends the founding-plan
> holdout rule in [docs/founding-plan.md](founding-plan.md).

## The constant

`HOLDOUT_START = "2025-01-09"` (`src/trading_lab/config.py`). Every bar
with `timestamp >= HOLDOUT_START` is locked until the P5 final review.
Do not change the constant; `tests/test_data.py::test_holdout_constant_unchanged`
pins it.

## Enforcement points

1. **Loader (first line of defense).** `trading_lab.data.load_ohlcv` is the
   single load path for all research code. It drops every bar
   `>= HOLDOUT_START` **before** applying `start=`/`end=` slicing, so:
   - `end=` past the boundary cannot reintroduce holdout bars;
   - `start=` inside the holdout returns an **empty frame**, never holdout bars;
   - the filter applies regardless of `data_dir=` — alternate caches such as
     `data/p2ext/` (used by `scripts/run_p2_validation.py`) get the same rail.

   `fetch_ohlcv` deliberately does **not** filter: the raw cache may contain
   holdout bars; the rail is at load time, not fetch time.

2. **Ledger (second line of defense).** `trading_lab.ledger` refuses to
   write any record whose `data_end >= HOLDOUT_START`:
   - `build_record(..., holdout_unlocked=False)` raises `ValueError` on a
     post-boundary `data_end`;
   - `write_run` re-checks every record at the choke point, including
     hand-built records that bypass `build_record`;
   - the only way through is the explicit `holdout_unlocked=True` kwarg,
     which stamps a visible `"holdout_unlocked": true` marker into the run
     file, and `rebuild_index` propagates it into `experiments/index.jsonl`
     — unlocked rows self-declare forever.

3. **CI audit.** `tests/test_ledger.py::TestCommittedLedgerAudit` parses
   every line of `experiments/index.jsonl` and every
   `experiments/runs/*.json` on every CI run and fails if any `data_end`
   (compared as a timestamp, not a string) reaches the boundary without the
   marker.

## What "unlock" means

`load_ohlcv(..., unlock_holdout=True)` (emits `HoldoutViolationWarning`)
and `ledger` `holdout_unlocked=True` exist ONLY for the roadmap-P5 final
report: the first and only evaluation against the holdout, done once. Any
appearance of the warning or the marker before P5 is a violation.

## Tests that pin the contract

- `tests/test_data.py::TestHoldoutLock` — default exclusion, explicit
  unlock warning, constant pin, `data_dir=` override, `end=` past the
  boundary, `start=` inside the holdout.
- `tests/test_ledger.py::TestHoldoutGuard` — build/write refusal, exclusive
  boundary (`2025-01-08` is the last legal `data_end` date), marker
  stamping + index propagation.
- `tests/test_ledger.py::TestCommittedLedgerAudit` — the committed ledger
  itself.

## Residual known bypass

Ad-hoc code that reads `data/**` directly (e.g. `pd.read_csv` on a cache
file) bypasses the rail silently. **Rule: all research code loads bars via
`load_ohlcv`.** (Test fixtures under `tests/fixtures/` are exempt — they
are synthetic and read raw only to verify the loader itself.)
