# EAP close-out walkthrough — trading-strategy, 2026-07-14

> **Status:** `reference`
>
> ORDER 015(b) deliverable — the owner's review walkthrough for this seat
> at the end of the EAP. Written 2026-07-14 against origin/main `0ea6950`
> (cited below as `@0ea6950` where a pin matters). Five sections: A. what
> this seat did · B. current state + how to run/verify · C. OWNER ACTIONS
> checklist · D. a 5-minute verify-it-yourself tour · E. handoff notes.
> This document changes no verdict, schedules nothing, reads no holdout
> data, and implies no promotion. Research-only lane: no real money, no
> broker, no orders — ever.

## A. What this seat did during the EAP

~5 active days (2026-07-09 → 2026-07-14), 121 PRs opened / 120 merged —
headline numbers quoted verbatim with citations in the audit pointer,
[audits/eap-project-audit-2026-07-14.md](audits/eap-project-audit-2026-07-14.md).
Compact, PR-cited arc:

- **Built the lab** ([#1](https://github.com/menno420/trading-strategy/pull/1)):
  data rail with a locked 18-month holdout, walk-forward engine with
  t+1-open fills and realistic costs, baseline strategies, experiment
  ledger, tests + CI — under the binding
  [founding-plan.md](founding-plan.md) anti-overfitting discipline.
- **Ran the P1→P5 validation chain** (P1 sweeps; P2 re-validation; P4
  transfer 13/13 FAILED; P5 pre-registered one-shot holdout read under
  ORDER 008 — landing chain includes
  [#37](https://github.com/menno420/trading-strategy/pull/37); holdout
  SPENT since). ORDER 007 added the Bonferroni significance bar and
  demoted the program's only promotion
  ([p2-regrade-aapl-donchian.md](p2-regrade-aapl-donchian.md)).
- **Six research rounds, honestly null**: R2
  ([#46](https://github.com/menno420/trading-strategy/pull/46)–[#49](https://github.com/menno420/trading-strategy/pull/49)),
  R3 surface expansion
  ([#81](https://github.com/menno420/trading-strategy/pull/81)–[#95](https://github.com/menno420/trading-strategy/pull/95)),
  R4 idea classes ([#98](https://github.com/menno420/trading-strategy/pull/98)–[#107](https://github.com/menno420/trading-strategy/pull/107)),
  R5 robustness ([#110](https://github.com/menno420/trading-strategy/pull/110)),
  the selection-fair standing gate
  ([#111](https://github.com/menno420/trading-strategy/pull/111), decision
  D-0002), R6 volume/gap families
  ([#116](https://github.com/menno420/trading-strategy/pull/116) plan,
  [#118](https://github.com/menno420/trading-strategy/pull/118) run).
  Funnel: **5,055 registered configurations → 0 promoted**; nothing in six
  rounds came within ~1 t of its bar. The full story, every number
  adversarially re-verified at source:
  [research-program-retrospective.md](research-program-retrospective.md)
  ([#120](https://github.com/menno420/trading-strategy/pull/120)).
- **Stood up the forward paper lane** (protocol
  [paper-lane-protocol.md](paper-lane-protocol.md); rail + ledger
  [#42](https://github.com/menno420/trading-strategy/pull/42); grader
  [#43](https://github.com/menno420/trading-strategy/pull/43); pre-verify
  + dry-run [#115](https://github.com/menno420/trading-strategy/pull/115);
  review index [#121](https://github.com/menno420/trading-strategy/pull/121))
  — one RULE-PASS candidate, zero money, first weekly grading pass
  time-gated to 2026-07-17T09:05Z.
- **Self-engineered its landing/ops path**: auto-merge enabler
  ([#65](https://github.com/menno420/trading-strategy/pull/65), the
  standing landing path), claims convention, born-red session cards,
  trigger doctrine ([ROUTINES.md](ROUTINES.md)), owner-idea vets
  ([#69](https://github.com/menno420/trading-strategy/pull/69) position
  sizing, [#71](https://github.com/menno420/trading-strategy/pull/71) MTF
  Bollinger — both honest NULLs).

Depth: the audit pointer above (platform walls, friction, wishlist) and
the retrospective (the research story).

## B. Current state + how to run/verify

State at `0ea6950`: research rounds 1–6 CLOSED (0 promoted, promotion
CLOSED, holdout SPENT); paper lane FLAT/WATCH (sole record `paper-0001`);
0 open PRs; 0 live claims; all 15 inbox ORDERs consumed or in service
(this doc serves 015). Living ledger: [current-state.md](current-state.md).

Exact commands (repo root, Python 3.11, `pip install -r requirements.txt`):

- **Test suite — the exact line CI runs**
  (`.github/workflows/tests.yml`):

  ```
  python3 -m pytest -q
  ```

  Expected: `668 passed` (count at `0ea6950`).

- **Substrate gate — the exact strict check CI's substrate-gate runs**:

  ```
  python3 bootstrap.py check --strict
  ```

  Expected tail: `check: all checks passed.` (exit 0).

- **Paper-lane grader dry-run — the PR #115 pattern** (throwaway tree
  copy so the real ledger cannot be written even in principle; the script
  has no dry-run flag, none needed — a FLAT pass writes nothing):

  ```
  cp -r . /tmp/ts-dryrun && cd /tmp/ts-dryrun && python3 scripts/grade_paper.py
  ```

  Expected (verbatim §7 FLAT/warm-up shape, exit 0):

  ```
  paper-0001: WATCH — not gradeable, left untouched
  FLAT — no window closed and no position open this pass (§7)
  this pass: 0 BEAT of 0 newly graded windows; 0 closed windows total in ledger (1 WATCH, 0 open)
  ```

- **Selection-fair gate** — a library API, not a CLI
  (`src/trading_lab/selection_gate.py`; binding rule doc
  [selection-fair-gate.md](selection-fair-gate.md)): round-6+ runners
  (e.g. `scripts/run_r6_volume_sweep.py`) call
  `trading_lab.selection_gate.run_selection_gate(ohlcv=…, strategy=…,
  per_split=…, top_variant=…, …)` on every lane and fold the result
  through `apply_gate(verdict, gate_result)` BEFORE writing any verdict;
  every result carries a machine-readable `reason_class` (8 classes;
  `UNGRADEABLE_*` = infrastructure alarm). Behavior is pinned by
  `tests/test_selection_gate.py` (runs inside the pytest line above).

## C. OWNER ACTIONS checklist

Every pending owner decision found at HEAD `0ea6950` (scanned:
control/inbox.md, control/status.md, control/outbox.md,
docs/review-queue.md, docs/proposals/, docs/CAPABILITIES.md). No agent
action is possible on any of these — each is an owner decision or click.

1. **R5-C BTC-USD out-of-sample check — letter decision A/B/C.** The
   pre-registered, owner-gated proposal
   [proposals/r5c-btc-bollinger-breakout-oos-proposal.md](proposals/r5c-btc-bollinger-breakout-oos-proposal.md)
   ([deep link](https://github.com/menno420/trading-strategy/blob/0ea6950/docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md))
   needs one of: **A** — approve: issue an owner ORDER fixing a
   contiguous post-2026 window of ≥252 BTC-USD daily bars (execution
   impossible before **~2026-09-09**, so approval now means execution
   then); **B** — decline ("Doing nothing is a perfectly acceptable owner
   choice", proposal §6); **C** — defer the letter until ~2026-09-09.
   **Recommendation: A — approve now with execution owner-ORDERed at the
   earliest valid window (~2026-09-09):** it is the only evidence-bearing
   OOS option the program produced, it is cheap (one fetch, one
   selection-free replay, no new code), p-hack-proof by construction, and
   the unfavorable prior ("a 1.4-t dev edge … usually regresses", §6) is
   exactly why a pre-registered answer is worth having. VERIFY: your
   ORDER appears in `control/inbox.md`; nothing runs before the window
   you fixed; on execution, results cite the proposal's frozen config
   verbatim (`period=10, num_std=1.0`, K per §4).
2. **Wake-resilience rebind — owner console click.** Parked in ORDERs
   014/015 as "wake-resilience rebind (owner click)"
   ([inbox @0ea6950](https://github.com/menno420/trading-strategy/blob/0ea6950/control/inbox.md)).
   Substance: every trigger is bound to its creating session and dies at
   archive ([ROUTINES.md](ROUTINES.md) "A self-bound trigger dies with
   its session"; the 2026-07-13 cutover already re-bound this seat's
   chain once, `control/outbox.md` BOOT REPORT 13:45:05Z), and
   fresh-session cron delivery is UNVERIFIED-BROKEN (0-for-2 observed),
   so lasting wake resilience needs the console-side action only the
   owner has (environment/routine console per
   [CAPABILITIES.md](CAPABILITIES.md) walls).
   **Recommendation: at the next seat archive/cutover, click the rebind
   in the console the same day** — an archived seat's triggers fire into
   nothing and the failure is silent. VERIFY: after any cutover,
   `list_triggers` (or the console Routines screen) shows the grading
   cron bound to the LIVE seat with a future `next_run_at`.
3. **Foreign duplicate grading trigger — disposition before Friday.**
   `trig_01YXNmgqYeYQ1LuepsLmbNCG` (a `send_later` firing
   2026-07-17T09:00Z, "WEEKLY GRADING PASS", bound to non-seat
   `session_01NwvvbgUVSdQvY8eYwtuEoo`) could race the seat's 09:05Z
   grading cron and double-write the graded ledger once past warm-up —
   flagged twice, not ours to delete
   ([outbox GRADING PRE-VERIFY entry](https://github.com/menno420/trading-strategy/blob/0ea6950/control/outbox.md)).
   **Recommendation: delete the foreign trigger (or confirm its target
   session dead) before 2026-07-17.** Risk is low THIS week (FLAT
   warm-up writes nothing) but structural for every graded week after.
   VERIFY: the trigger no longer appears in the registry, or its target
   session is confirmed archived.
4. **Review-queue #37 — the one standing second-eyes item.**
   [review-queue.md](review-queue.md)
   ([deep link](https://github.com/menno420/trading-strategy/blob/0ea6950/docs/review-queue.md))
   still carries: "#37 · P5 one-shot holdout evaluation + final report ·
   classifier denied agent merge — owner click needed; re-check §Holdout
   verdicts against protocol §5". PR #37 has long merged; what remains is
   the owner (or an owner-sanctioned session) doing the §Holdout-vs-§5
   re-check and removing the line (its own convention: "Remove a line
   when the review is done"). **Recommendation: do the 10-minute re-check
   of [final-report.md](final-report.md) §Holdout against
   [p5-holdout-protocol.md](p5-holdout-protocol.md) §5, then delete the
   line.** VERIFY: `docs/review-queue.md` no longer lists #37.
5. **Repo setting: "Automatically delete head branches".** 56 stale
   `claude/*` branches in this repo (audit §3, measured 2026-07-14);
   branch deletion is 403-walled agent-side
   ([CAPABILITIES.md](CAPABILITIES.md) walls). **Recommendation: enable
   Settings → General → "Automatically delete head branches" on both
   seat repos, then hand-prune the existing 56** (note audit §6: prune
   AFTER confirming no wanted telemetry commits sit only on those
   branches). VERIFY: the next enabler-merged PR's branch disappears on
   merge.
6. **MTF-Bollinger preregistration draft — keep FROZEN or close.** The
   owner-gated draft
   [proposals/bollinger-mtf-preregistration-draft.md](proposals/bollinger-mtf-preregistration-draft.md)
   sits FROZEN behind a clean dev NULL (all 12 configs KILLED,
   [research/bollinger-mtf-dev-2026-07-12.md](research/bollinger-mtf-dev-2026-07-12.md)).
   **Recommendation: close it (decline)** — the dev evidence is null and
   the R5-C proposal is the better-evidenced OOS candidate; keeping two
   open OOS asks dilutes the decision queue. VERIFY: the draft's badge
   line records the owner disposition (one-line edit), or an inbox ORDER
   states it.

## D. 5-minute verify-it-yourself tour

Copy-paste, from a fresh clone (`git clone
https://github.com/menno420/trading-strategy && cd trading-strategy &&
pip install -r requirements.txt`):

```
# 1) The whole suite, exactly as CI runs it (~10 s)
python3 -m pytest -q
# expect tail:            668 passed in ~6s

# 2) The substrate gate, exactly as CI runs it
python3 bootstrap.py check --strict
# expect tail:            check: all checks passed.

# 3) The program funnel headline, from the committed artifact (no run)
python3 -c "import json; print(json.load(open('experiments/sweeps/r6-volume-hourly/summary.json'))['program_variants_tried'])"
# expect:                 5055

# 4) Research-only + holdout rails, by inspection
grep -rln "unlock_holdout=True" --include=*.py scripts/
# expect exactly:         scripts/run_p5_holdout.py   (the SPENT one-shot; no other script can unlock)
ls data/p5holdout/                                # sealed holdout caches (daily/ hourly/) — SPENT, never re-read
grep -rniE "import (ccxt|ib_insync|alpaca|binance)" --include=*.py src/ scripts/ | wc -l
# expect:                 0 — no broker/exchange libraries anywhere

# 5) Paper-lane grader dry-run (throwaway copy; writes nothing on FLAT)
cp -r . /tmp/ts-tour && (cd /tmp/ts-tour && python3 scripts/grade_paper.py; git status --porcelain | wc -l)
# expect: the 3-line FLAT output from §B, then 0 (no file changed)
```

Expected outputs are pinned at `0ea6950`; the test count grows as work
lands — `passed` with zero failures is the invariant.

## E. Handoff notes

- **Friday grading baton (time-gated — do NOT run early).** First weekly
  paper-lane grading pass fires 2026-07-17T09:05Z. Executor LIVE:
  `trig_01UsNU4JRps4b7jiAMdEfXNi`, cron `0 9 * * 5`, bound to the
  coordinator seat — independently confirmed via a read-only
  `list_triggers` call 2026-07-13T22:48Z
  (`.sessions/2026-07-13-night-grading-preverify.md`, PR #115;
  `control/status.md` `grading_executor:` line @`0ea6950` matches).
  Dry-run CLEAN: exit 0, exact protocol §7 FLAT/warm-up shape, zero
  writes (same card). Expected Friday result: FLAT (warm-up; first
  evaluable entry signal ~early August 2026 per
  [paper-lane-protocol.md](paper-lane-protocol.md) §3). The executor
  should re-verify the trigger live at fire time per
  [ROUTINES.md](ROUTINES.md) ("a record is a claim; the live registry is
  the proof") and watch for the foreign 09:00Z duplicate (item C-3).
- **Round-7 plan: PRE-REGISTERED, NOT RUN.**
  [research-round-7-plan.md](research-round-7-plan.md) (this close-out's
  own PR) pre-registers two new idea families on committed caches under
  the standing selection-fair gate, the R5-D fixed-config row, and the
  new reason_class rollup requirement. **Running it is a future
  session's slice** — plan-before-outcome: grids + tests go into
  `trading_lab.sweeps` before any run, per the plan's own sequencing.
- **KEEP-dev survivors (dev-data artifacts, NOT findings — promotion
  CLOSED).** Four round-5 survivors: BTC-USD daily `bollinger_breakout`
  (the strongest, t 1.38; source of the R5-C proposal), SLV daily
  `williams_r_reversion`, META daily `ichimoku_trend`, TLT daily
  `ema_crossover` — plus three weak round-6 KEEPs: BTC-USD `obv_trend`
  (t 0.60), META `obv_trend` (t 0.18), AMZN `mfi_reversion` hourly
  (t 0.29). Fragility notes per lane:
  [research-program-retrospective.md](research-program-retrospective.md)
  §(d). Known gap, stated there: **no document merges the 4+3 into one
  standing list** — the combined post-r6 surface is not measured (cheap
  future docs slice).
- **PARKED (cited, never schedule agent-side):** R5-C BTC OOS —
  owner-gated, execution impossible before ~2026-09-09
  ([proposal](proposals/r5c-btc-bollinger-breakout-oos-proposal.md)) ·
  MTF-Bollinger prereg — FROZEN, dev NULL
  ([draft](proposals/bollinger-mtf-preregistration-draft.md)) ·
  wake-resilience rebind — owner console click (item C-2) · Friday
  grading — time-gated 2026-07-17T09:05Z (baton above).
- **What the next phase needs**: the §C decisions, then either the
  round-7 run slice (agent-executable) or steady-state (paper lane on
  cron, retrospective §(g) option 4 — also a legitimate choice).
