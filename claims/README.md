# Lane claims — parallel-session coordination

> **Status:** `protocol` — the lane-claim mechanism from
> [docs/founding-plan.md](../docs/founding-plan.md) §Parallel-session lanes.

Sessions claim a lane before starting sweep work so parallel sessions never
duplicate or collide. A **lane** = strategy-family × instrument-set ×
timeframe (e.g. `trend-following__all8__daily`).

## Lifecycle

1. **Check first.** Before picking a lane, list this directory. A claim file
   that already exists means the lane is taken — pick another lane.
2. **Claim at start.** Create `claims/<family>__<instruments>__<timeframe>.md`
   in your first commit on the lane branch, containing: session id, started-at
   (UTC), and the lane scope (families, tickers, timeframe, grids).
3. **Delete when finished.** When the lane's results are merged, delete the
   claim file (in the follow-up/status PR). A deleted claim = lane complete;
   its evidence lives in `experiments/` and the results doc.

## Staleness

Claims are cheap to inspect: `started-at` plus the branch name tells you if a
claim is live. A claim older than ~2 days with no open PR on its branch is
presumed abandoned — a new session may delete it and re-claim (note the
takeover in the new claim file).

## Naming

`<family>__<instrument-set>__<timeframe>.md` — lowercase, `__` separators;
`all8` = the full universe in `trading_lab.config.UNIVERSE`.
