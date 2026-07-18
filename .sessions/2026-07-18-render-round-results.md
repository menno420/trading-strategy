# 2026-07-18 — render_round_results.py: mechanize results-doc tables

> **Status:** `complete` — render_round_results.py landed — read-only
> generator that emits the standardized results-table block (slice-summary,
> per-lane table, counts, reason_class rollup with the UNGRADEABLE infra-alarm
> line, burden) from a slice's committed experiments/sweeps/<slice>/ JSONs;
> reproduces docs/research-round-8-results.md verbatim, 11-test numbers suite;
> single-name slices (portfolio a documented TBD); retires the per-round
> hand-transcription risk.

📊 Model: opus-4.8 · render-round-results lane (overnight worker, owner GO
2026-07-18T13:47Z / R7-run-card 💡 + menu #13-adjacent) · start
2026-07-18T16:25:32Z

## Why this session exists

Every run slice this session (R7-A/B, R7-C, R7-D, R8) hand-transcribed a
per-lane results table from the committed lane JSONs into
`docs/research-round-<N>-results.md` — the searched/bench/fixed/gap/t row, the
counts sub-tables, the reason_class rollup, the UNGRADEABLE infra-alarm line,
and the burden tally. Hand-transcription is a copy risk that GROWS every round
(more lanes, more families, more numbers to fat-finger), and this program has
repeatedly flagged transcription-risk as its recurring failure mode. This
session adds `scripts/render_round_results.py`: a pure read-only generator that
emits the standardized results-table markdown block for a single-name research
slice directly from its committed `experiments/sweeps/<slice>/` JSONs, so
future round results tables are mechanical + diffable instead of typed by hand.
NO strategy/backtest/verdict changes, NO sweep re-run — it only re-formats
numbers that already exist in committed artifacts.

## Work log

- branch `claude/render-round-results` cut from origin/main HEAD (incl. the R8
  run, #150). Born-red FIRST commit: this card.

💡 **Session idea:** the slice-summary row's human label —
`R8 \`r8-hourly\` (drawdown_reversion + high_proximity × 8 hourly)` — is the
one field the generator still has to SYNTHESIZE (round prefix parsed from the
slice name, families joined, ticker-count × timeframe) rather than read
verbatim from a JSON. A tiny `"slice_label"` string committed into each
`summary.json` at run time (the runner already knows all four facts) would let
the generator read the label instead of reconstructing it, removing the last
non-mechanical guess from the results block. Anchor: the label-synthesis helper
in `render_round_results.py`; test target: assert the rendered slice row equals
`summary["slice_label"]` once the runner emits it. (Distinct from the
round-8-run card's shared-hourly-runner idea — that dedupes the `run_*` runner
body; this adds one authored string to the summary schema.)

## Previous-session review

⟲ PR #150 (`round-8-run`, merged) — executed the pre-registered Round-8 hourly
companion sweep (`docs/research-round-8-plan.md`, #149): the two newest
single-instrument R7 families — `drawdown_reversion` (R7-A) and
`high_proximity` (R7-B) — re-swept VERBATIM on the committed 8-ticker hourly
cache, 16 lanes / 192 configs, gate on every lane (8 PASS / 8 FAIL), yielding 3
KEEP-dev / 13 KILL / 0 KILL-SIG, 0 promoted, best informational t 1.079 (MSFT
`drawdown_reversion`) under the unchanged ~2.638 bar; the registered null
(hourly amplifies KILLs) held cleanly for `high_proximity` (0 KEEP-dev) and
split-but-held for `drawdown_reversion` (its 3 dev-KEEPs rest entirely on the
single ~8.5-month 2024 regime). 1/16 lanes (GLD hourly) came back
`UNGRADEABLE_NAN` — the mandated infrastructure alarm, never strategy evidence.
**R8 is this generator's proof case:** the 11-test numbers suite asserts
`render_round_results.py` reproduces R8's hand-written
`docs/research-round-8-results.md` table block EXACTLY — the per-lane rows, the
counts sub-tables, the reason_class rollup, the burden tally, and critically
the UNGRADEABLE infra-alarm line — so the one round whose table was fully
hand-transcribed is the fixture that pins the mechanization to be byte-faithful.
**One honest nit:** #150's results doc is single-name only; the portfolio lane
shape it does not exercise is exactly the generator's documented TBD, so R8
proves the single-name path but leaves the portfolio row unproven by
construction. No correctness defect found in #150.

## Close-out

**Done** (4 commits):
- `f0898a6` — born-red FIRST commit: this session card (`in-progress` hold).
- `d178472` — `scripts/render_round_results.py` (read-only generator: emits the
  standardized results-table block — slice-summary, per-lane table, counts,
  reason_class rollup incl. the UNGRADEABLE infra-alarm line, burden — from a
  slice's committed `experiments/sweeps/<slice>/` JSONs) +
  `tests/test_render_round_results.py` (11-test numbers suite reproducing
  `docs/research-round-8-results.md` verbatim).
- `9ed80e0` — docs pointer: future round results docs point at
  `render_round_results.py`.
- (this commit) — close-out flip: badge `in-progress` → `complete`, headline +
  previous-session-review + close-out slots resolved.

**Verify:**
- `python3 -m pytest -q` → 756 passed (incl. the 11 new numbers tests).
- `python3 bootstrap.py check --strict` → EXIT 0 at flip (the born-red
  in-progress hold clears when the badge flips to `complete`).
- Integrity: the branch diff touches only
  `scripts/render_round_results.py` + `tests/test_render_round_results.py` +
  one docs pointer + this session card. Read-only tooling: NO
  strategy/backtest/verdict changes, NO sweep re-run, the holdout was never
  read, no fetch, `experiments/paper/**` untouched, `control/status.md`
  untouched, no triggers, no broker code. NO manual merge — the auto-merge
  enabler lands PR #151 on green.

**Next:** commit a `"slice_label"` string into each slice's `summary.json` at
run time (the runner already knows all four facts — round prefix, families,
ticker-count, timeframe) so the generator's slice-summary label is READ verbatim
rather than SYNTHESIZED — the last non-mechanical guess in the block (this
card's 💡; test target: assert the rendered slice row equals
`summary["slice_label"]`). Extend the generator to the portfolio lane shape
(currently a documented TBD — the single-name path is proven by the R8 fixture,
the portfolio row is not). A future round author runs
`python3 scripts/render_round_results.py <slice>` to emit the table block
instead of hand-transcribing it.
