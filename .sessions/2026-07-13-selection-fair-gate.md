# 2026-07-13 — Selection-fair replay standing gate (round 6+ dev verdicts)

> **Status:** `complete` — the R5-D selection-fair fixed-config replay is
> now a STANDING GATE for round-6+ dev-lane KEEP verdicts (PR #111):
> `src/trading_lab/selection_gate.py` (replay semantics lifted from
> `scripts/run_r5d_selection_fair.py`, PR #110, byte-untouched), binding
> doc `docs/selection-fair-gate.md` with the 7 recorded semantic choices
> (each the stricter option), decision-ledger entry [D-0002], and 24
> tests including a read-only 1e-12 reproduction pin of the committed
> R5-D BTC-USD artifact. Effective research round 6, strictly
> forward-looking: no retroactive re-grading, every historical verdict
> byte-identical. This card was born red and flips `complete` in this
> final commit; the claim file is deleted in this same commit.

📊 Model: fable-5 · selection-fair-gate lane (worker session) · start 2026-07-13T15:20Z

⚑ Self-initiated: coordinator-sanctioned slice — executes the round-5
card's 💡 (make R5-D's selection-fair replay a standing gate) with the
coordinator's stricter semantic choices decided up front.

💡 **Session idea (deduped against recent cards — distinct from the
round-5 card's standing-gate idea, which THIS session executed; from the
r4-regime card's cardinality-matched control arm; and from the
kill-sig-review card's verdict-grammar unification):** the gate now
demotes on UNGRADEABLE (missing windows, fidelity failure, cache drift)
exactly like it demotes on a genuine rule failure — correct for verdict
strictness, but a round rollup that only counts KILLs cannot tell infra
rot from alpha decay. Add a machine-readable `reason_class` field to the
gate result (`rule-fail` vs the ungradeable subtypes:
`missing-windows` / `fidelity` / `drift` / `nan`) and have round-6+
rollups count them separately: any nonzero ungradeable share in a round
is an INFRASTRUCTURE alarm (irreproducible lanes) that should page the
coordinator, never be read as evidence about the strategies. Anchors:
`run_selection_gate`'s `_fail()` in `src/trading_lab/selection_gate.py`
(every call site already carries a distinct verbatim reason string —
classifying is one keyword per site); test target: a
`reason_class`-partition fixture in `tests/test_selection_gate.py`.

## Why this session exists

Round 5's R5-D slice (PR #110, `docs/research-round-5-results.md`
§ R5-D) replayed the program's five best KEEP-dev lanes selection-free
and found `selection_gap > 0` on only 3/5 — two lanes' searched
walk-forwards LOST to their own story-pinned fixed config (SLV −0.313,
META hourly −0.396). The round-5 card's 💡 asked for exactly this
follow-up: make the selection-fair fixed-config replay a standing gate
of future KEEP-dev grading, so a KEEP whose stitched edge exists only
under in-window re-selection is flagged the day it is minted instead of
rounds later. This session lands that gate — effective research round 6,
strictly forward-looking — plus its binding doc and tests.

## Work log

- 2026-07-13T15:20Z — branch `claude/selection-fair-gate` cut from
  origin/main HEAD `47d3cbc`. Collision check: `control/claims/` at HEAD
  contains only the READMEs — no overlap. Born-red FIRST commit
  `b05e3ff`: this card (`in-progress`) + claim
  `control/claims/selection-fair-gate.md`, per the claim-before-build
  convention. PR #111 opened READY immediately after push.
- 2026-07-13T15:35Z — read `scripts/run_r5d_selection_fair.py` end to
  end and inspected a real committed lane
  (`experiments/sweeps/r3-btc-coverage/bollinger_breakout__BTC-USD.json`):
  its `walk_forward.per_split` windows ARE contiguous (each start ==
  previous end, `[1008,1260],[1260,1512],…`), confirming R5-D's
  slice-span benchmark `windows[0][0]:windows[-1][1]` equals the
  stitched OOS coverage — so the gate hard-checks contiguity and treats
  non-contiguity as UNGRADEABLE → FAIL.
- 2026-07-13T15:45Z — implementation commit `33318c1`:
  `src/trading_lab/selection_gate.py` (stitched_replay lifted with costs
  parametrized; pure `gate_decision`; `run_selection_gate` with bounds +
  contiguity checks and the 1e-8 fidelity guard; `apply_gate`), the
  single constant `promotion.VERDICT_KEEP_DEV` (per-script literal
  defined once — no existing script edited), binding doc
  `docs/selection-fair-gate.md` + [D-0002] in `docs/decisions.md`,
  `tests/test_selection_gate.py` (24 tests). The integration pin
  reproduces the committed R5-D BTC-USD fixed/bench/searched Sharpes to
  1e-12 from the local cached data — read-only, no network, no artifact
  touched.
- 2026-07-13T15:50Z — verify: `python3 -m pytest -q` → **607 passed**
  (583 baseline + 24 new; no existing test touched);
  `python3 bootstrap.py check --strict` → red ONLY on this card's
  designed born-red hold pre-flip. Close-out commit: card flipped
  `complete`, claim deleted.

## Previous-session review

⟲ Most recent prior card (`.sessions/2026-07-13-round-5-research.md`,
Status `complete`, PR #110, merged as `47d3cbc` — the exact commit this
branch is cut from, so its claims were directly inspectable at branch
time). Its payload matches its promise: plan-before-outcome ordering is
visible in the branch history (`b6b8708` precedes every run commit), all
four registered slices landed with 1e-8 fidelity guards and 0 SKIPPED
lanes, and the results doc leads with the nulls and the one demotion
(META hourly `stochastic_reversion`, R5-B) rather than burying them. Its
💡 is the direct seed of this session, with concrete anchors
(`scripts/run_r5d_selection_fair.py`, the gap-sign test target) that
made this slice cheap to start. One honest gap it also named itself:
all four R5 runners re-copied the fidelity-guarded replay block instead
of sharing it — this session's module extraction is the first paydown of
that debt. No defect found in its work.

## Close-out

**Done:** on branch `claude/selection-fair-gate` (PR #111), three
commits `b05e3ff` (claim + born-red card) → `33318c1` (implementation)
→ this one (close-out) —

1. `src/trading_lab/selection_gate.py`: the standing home of R5-D's
   replay machinery. Gate = selection-free replay of the committed top
   variant over the committed contiguous test windows at the lane's
   costs vs same-window B&H; pass rule `fixed > bench AND fixed > 0`,
   both non-NaN (the `> 0` conjunct is the recorded strictness increase
   over R5-D); every UNGRADEABLE condition FAILs, never skips;
   `selection_gap` stays informational; fidelity guard at 1e-8.
2. `promotion.py`: one new constant `VERDICT_KEEP_DEV` — the
   "KEEP (dev-candidate only)" literal defined once for round-6+ code;
   zero existing scripts edited, zero historical artifacts touched.
3. `docs/selection-fair-gate.md` (badge `binding`) with all 7 recorded
   semantic choices and the runner call sketch; reachable via the dated
   [D-0002] entry appended to `docs/decisions.md`.
4. `tests/test_selection_gate.py`: 24 tests — pass-rule boundaries
   (tie fails, barely-above passes, NaN/None fail), all ungradeable
   paths (missing per_split, non-contiguous windows, out-of-bounds
   windows, NaN Sharpe, fidelity mismatch), `apply_gate` demotion
   matrix, `selection_gap` sign, and the committed-artifact
   reproduction pin.

**Verify:** `python3 -m pytest -q` → 607 passed.
`python3 bootstrap.py check --strict` → green with this card complete
(pre-flip its only red was the designed born-red hold). Integrity at
close: diff vs main touches only the new module, the one promotion.py
constant, the new doc + decisions.md entry, the new test file, and
`.sessions/` + the claim lifecycle. Every `experiments/**` file
byte-untouched; `data/p5holdout/` never read, `unlock_holdout` never
passed; `control/inbox.md`/`outbox.md`/`status.md` byte-untouched; no
existing `scripts/run_*.py` or round plan/results doc edited; no
broker/order/exchange code; no triggers; NO merge action by this
session — the auto-merge enabler is the landing path for PR #111.

**Next (guard recipe):** none owed for correctness. Follow-ups:
(1) this card's 💡 — `reason_class` taxonomy on gate FAILs (anchor:
`selection_gate._fail`, test target named above); (2) the first
round-6 runner must actually CALL the gate (the doc's call sketch is
the contract; a runner that mints KEEP-dev without a `selection_gate`
result block in its lane JSON is violating [D-0002]); (3) the R5
runners' duplicated replay blocks could later delegate to
`selection_gate.stitched_replay` — but only in NEW scripts; historical
runners stay byte-identical.

Session end: badge flipped `complete` in this final content commit
before push.
