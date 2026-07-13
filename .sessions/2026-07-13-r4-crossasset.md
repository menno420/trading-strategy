# 2026-07-13 — R4-E: cross-asset exposure gate

> **Status:** `in-progress`

📊 Model: fable-5 · trading-research (worker session) · start 2026-07-13T11:03:14Z

💡 **Session idea:** (to be filled at close-out — must be a genuine idea
earned by this session's work, not a placeholder.)

## Why this session exists

Round 4 slice R4-E (`docs/research-round-4-plan.md` @ main, pre-registered
and merged before this session started) — the LAST open Round-4 run slice:
the round-3 universe expansion committed TLT, XOM and GLD caches (PRs
#90–#92) but used them only as standalone lanes; cross-asset information
(bond/commodity momentum as an equity risk gate) is an untested idea
class, and the round's two conditioning results so far (PR #92's vol-gate
control winning 6/6; PR #104's trend-strength control splitting 3/3 with
conditioning still producing zero candidates) make the prior informed.
R4-E gates the exposure of existing SPY/QQQ trend-family variants on the
momentum sign of a DIFFERENT instrument (TLT, plus XOM and GLD as
pre-declared alternates), with the **ungated control arm** committed in
the same grid and a machine-readable `control_arm_delta` per lane.
Pre-registered kill criterion (same control-arm rule as R4-D): KILL iff
gated stitched OOS Sharpe ≤ the ungated control's; a KEEP additionally
requires beating B&H. Pre-registered hypothesis: **null expected**.
Engine/rail note: this is the program's first strategy that consumes a
SECOND instrument's OHLCV — gate-series alignment onto the equity's index
must be lookahead-free (gate signal at bar t uses gate-asset data ≤ t,
applied to the equity fill at t+1 per house convention), pinned by tests.
Owner mandate: ORDER 012 generative rung; holdout SPENT; promotion CLOSED
— any KEEP is a dev-candidate only, never a finding. This session also
closes out Round 4 in the results doc (all six slices now landed).

## Work log

- 2026-07-13T11:03Z — branch `claude/r4-crossasset` cut from origin/main
  HEAD (`7778ddb`, the merged R4-D slice). Born-red FIRST commit: this
  card `in-progress` + claim `control/claims/2026-07-13-r4-crossasset.md`,
  pushed before any implementation; PR opened READY immediately after.

## Previous-session review

(to be completed at close-out — review of `.sessions/2026-07-13-r4-regime.md`.)

## Close-out

(to be completed at close-out.)
