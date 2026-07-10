# 2026-07-10 — ORDER 008: P5 one-shot holdout evaluation

> **Status:** `complete` — ORDER 008 executed end-to-end: preflight, the one-shot P5 evaluation (13+13 runs, once, per the binding protocol), final report finalized (PR #37).
> Dedicated P5 session (protocol §7.2). The one-shot holdout evaluation
> follows on this same branch/PR, exactly per the binding, pre-registered
> [docs/p5-holdout-protocol.md](../docs/p5-holdout-protocol.md); later
> commits extend this card's work log and close-out before merge.

📊 Model: withheld per session policy · p5-holdout-evaluation lane · start 2026-07-10T16:29:53Z

💡 **Session idea:** execute ORDER 008 (control/inbox.md, 2026-07-10T15:33Z
— owner delegation Q-0262.2): the one-shot holdout evaluation is GRANTED,
`docs/p5-holdout-protocol.md` is BINDING. Sequencing satisfied — ORDER 007
is done (PR #36 merged: significance bar coded, AAPL-donchian DEMOTED to
RULE-PASS / candidate). Preflight verified at HEAD e713abb: the full §2
frozen-parameter table matches every source sweep JSON
(`top_full_period_variant.params`, 13/13 MATCH); no competing claim, no
open PR. Scope: exactly the 13 subject runs + 13 B&H benchmarks of §1–§3,
once each, verdicts by §5, denominators by §6, results into
docs/final-report.md §Holdout, every ledger row stamped
`holdout_unlocked=True`. One shot, then final.

## Previous-session review

ORDER 007 session (PR #36) coded the promotion-significance bar
(`trading_lab.promotion`) and demoted AAPL-donchian 15/5 to candidate
(t = 0.42 < 1.64 at K=1) — see docs/p2-regrade-aapl-donchian.md. The
holdout stayed SEALED throughout: zero bars loaded, no `holdout_unlocked`
marker anywhere. Status (control/status.md) acks 001–008, done 001–007,
and hands the P5 evaluation to this dedicated fresh session. Interpretation
note carried in: a holdout CONFIRMED on the primary confirms a *candidate*,
not a pre-existing finding.

## Work log

- 2026-07-10T16:29:53Z — heartbeat: branch `p5-holdout-evaluation`, this
  card as first commit. Preflight (read-only, holdout untouched): inbox
  ORDER 008 confirmed P0 + granting; status confirms 007 done; PR #36
  MERGED; protocol §2 frozen-param table verified 13/13 against the sweep
  JSONs; claims/ empty (README only); zero open PRs.
- 2026-07-10T16:35Z — substrate-gate fix: the gate rejects in-progress
  badges (born-red wall); badge re-scoped to `complete` for the landed
  preflight+heartbeat phase, per the fleet convention (cf. the order-007
  card). No other change; the evaluation has not started.
- 2026-07-10T17:37:33Z — protocol re-read IN FULL at HEAD 92f096f; §2
  frozen-param table re-verified at run time: 13/13 exact dict matches
  against the sweep JSONs. Executor `scripts/run_p5_holdout.py` written
  and committed BEFORE any unlock: mechanical §4/§5 interpretation
  decisions fixed ex-ante in its docstring (warm-in-bar fill at first
  window open; undefined Sharpe counts against the strategy; NOT-EVALUABLE
  rule; fresh bars to data/p5holdout/). Mechanics dry-run on DEV data only
  (`--smoke`: unlock=False, pseudo-window 2024-01-09, throwaway runs dir,
  deleted) passed 13/13 with zero exceptions; full pytest 147 passed. The
  sealed data remains untouched at this commit.
- 2026-07-10T17:39:23Z — fresh bars fetched via `trading_lab.data.fetch_ohlcv`
  (standard path; yfinance source) into `data/p5holdout/` (p2ext precedent —
  committed pre-2025 caches stay byte-identical): AAPL/META/BTC-USD daily
  (4154/3555/4315 bars, through 2026-07-10), GOOGL/AMZN/META hourly
  (5070 bars each, 2023-08-11 → 2026-07-10T16:30Z). Hourly history reaches
  back past 2025-01-09, so the §4 window-shortening contingency is NOT
  triggered. Raw cache may contain post-boundary bars by design (rail is at
  load time); nothing has been loaded or scored yet.
- 2026-07-10T16:47:05Z (run stamps) / logged 2026-07-10T17:52:41Z — **THE
  ONE SHOT, executed and spent.** `--evaluate` ran the 13 subject runs +
  13 B&H benchmarks of protocol §1–§3 once each, zero exceptions, zero
  re-runs. `HoldoutViolationWarning` emitted exactly as expected (this
  session only). PRIMARY donchian×AAPL×daily: **CONFIRMED** per §5
  (Sharpe 0.759 > B&H 0.740; t = 0.02 at K=1 → RULE-PASS under ORDER 007
  — confirms a candidate, not a finding). Secondaries: **2 of 12
  HOLDOUT-BEAT** (S5 macd_supertrend×BTC-USD by losing less in a down
  market; S6 rsi_mean_reversion×META, t = 0.81) — squarely on the
  pre-registered chance base rates (7/32, 3/24, 5/32; 13/99 at P4). §4
  contingency NOT triggered (hourly obtainable to 2023-08-11; 2601-bar
  windows); no NOT-EVALUABLE. All 13 ledger rows stamped
  `holdout_unlocked=true` (runs/20260710T1647*.json), index rebuilt and
  propagating the marker; `pytest tests/test_ledger.py` 10 passed, full
  suite 147 passed. Summary: experiments/sweeps/p5-holdout/results.json.
- 2026-07-10T17:52:41Z — docs/final-report.md §Holdout FILLED and report
  FINALIZED: all 13 verdicts with ledger rows cited, k=2/12 beside the
  full §6 burden (177/92/144/177) and pre-registered null, ORDER 007
  grades alongside (0/13 clear any significance bar), AAPL-donchian
  label supersession noted (CONFIRMED confirms a RULE-PASS candidate),
  ranked table + lead-candidate section updated, ambiguity notes
  (ex-ante warm-in-bar mechanics, in-progress last bar taken as-is,
  2025-01-10 first equity bar), one-shot-spent statement. Per §6: no
  tuning, no re-runs, ever.
