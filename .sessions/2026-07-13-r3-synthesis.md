# 2026-07-13 — R3 slice 9: Round-3 synthesis doc (no new experiments)

> **Status:** `complete` — the single honest Round-3 findings document
> (`docs/research-round-3-results.md`) written from the merged sweep
> summary JSONs and linked from `docs/current-state.md`: 8 slices
> (PRs #81–#88), 1,752 registered configs, **0 PROMOTED / 41 KEEP
> (dev-candidate only) / 125 KILL of 166 graded lanes**, all 41 KEEPs
> tabled against the ORDER 007 Bonferroni bar (max t 1.04 vs 2.64/2.39 —
> nothing is a finding). No new experiments, no `src/` changes. This card
> was born red (`in-progress`) and flipped `complete` as the deliberate
> last content change before push; the claim file is deleted in this same
> commit.

📊 Model: fable-5 · r3-synthesis lane (worker session) · start 2026-07-13T03:00Z

💡 **Session idea:** the sweep-summary schema has silently FORKED between
lane kinds, and this session paid for it: single-instrument summaries put
`verdict` + `promotion_grade` at the top level, but the portfolio
summaries (`r3-xsec-expanded/*.json`, following the R2 xsec shape) nest
them per config under `walk_forward.per_config[]` with no top-level
verdict at all — this session's first cross-sweep aggregator crashed on
`KeyError: 'verdict'` and every future consumer (the Friday grading, the
slice-4 verdicts-index idea, any morning-tally script) will need the same
two hand-written parsers. Before the verdicts index lands, normalize the
record: define the canonical graded-unit row (sweep, family, lane/params,
oos_sharpe, bench_sharpe, tstat, min_tstat, verdict, timeframe, data_end)
and bump summaries to `schema_version: 2` where portfolio lanes ALSO emit
one graded-unit record per config at a shared path (anchor: the summary
dict built in `scripts/run_r3_xsec_expanded.py` vs
`scripts/run_r3_stoch_willr_sweep.py`; natural home: the slice-1
sweep-runner extraction emits the canonical row for both kinds). Test
target: an aggregation test that parses EVERY committed
`experiments/sweeps/*/*.json` with one code path and asserts the round's
verdict totals (41/125/166 for r3-*) — which doubles as a regression pin
on tonight's scoreboard. Recent cards' ideas (sweep-runner extraction,
verdicts index, control arms, provenance sidecar, cost-drag line, OOS
activity line, benchmark-drift arm, walk-forward warm-history fix) don't
cover this: the verdicts index assumes a parseable verdict; this makes
the verdict parseable in one way everywhere.

## Why this session exists

ORDER 012 (control/inbox.md, owner night-run direct order, 2026-07-13)
instructs this seat: "TRADING RESEARCH: expand the backtest surface — new
strategies, new stocks/tickers, new indicators — every result recorded
honestly." Slices 1-8 (PRs #81-#88) are merged. This slice runs NO new
experiments: it writes the single honest Round-3 findings document —
scoreboard with denominators, every KEEP's t-stat against the Bonferroni
bar, verified cross-cutting patterns, and the explicit statement of what
the round does NOT establish — so the night's 1,752 configs are readable
in one place for the Friday grading and the morning tally.

## Work log

- 2026-07-13T03:00Z — clone hard-synced to origin/main HEAD `7f7ca07`
  (verified byte-identical to `git ls-remote origin main`).
  `control/inbox.md` read at HEAD (read-only): newest order is **ORDER 012 ·
  2026-07-13T00:46:37Z · status: new** (owner night-run direct order) — this
  session executes its research lane (slice 9, synthesis). Collision check:
  `control/claims/` at HEAD contains only `README.md` +
  `2026-07-13-order-night-run.md` — no overlap with this scope. Branch
  `claude/r3-synthesis`; this card + the claim
  `control/claims/2026-07-13-r3-synthesis.md` are the born-red FIRST
  commit (`286d800`), pushed before any writing work.
- 2026-07-13T03:01Z — ground-truth pass BEFORE writing: all 166 graded
  units re-aggregated directly from the merged summary JSONs under
  `experiments/sweeps/r3-*/` (not from card prose) — verdict totals
  0 PROMOTED / 41 KEEP / 125 KILL, per-slice splits 2/16, 2/16, 5/18,
  4/24, 13/32, 3/24, 6/12, 6/24, lane-variant sums 1,752 with program
  cumulative 2,432, every KEEP's OOS/bench Sharpe + t-stat + Bonferroni
  bar, and per-instrument benchmark Sharpes for the pattern claims (NVDA
  0 KEEP in 14 lanes; MSFT daily 0/10; SPY 0/9; QQQ 0/9; GLD hourly 0/4;
  META 9 KEEP / 5 KILL across 14 lanes; AAPL hourly noted as the honest
  counterexample to the strong-benchmark pattern). All eight slice cards
  read and reconciled; no discrepancy found between cards and JSONs.
- 2026-07-13T03:02Z — commit `f817373`: `docs/research-round-3-results.md`
  (Status `reference`, round-2-results structure mirrored: headline,
  budget ledger, scoreboard with denominators, full 41-row KEEP-vs-bar
  table, verified cross-cutting patterns, "what this round does NOT say"
  caveats, per-script reproducibility list) + one linking bullet at the
  top of `docs/current-state.md` § Recently shipped (the round-2
  convention; current-state is a docs-gate reachability root). No other
  current-state edits — the live-state sections are the coordinator's.
- 2026-07-13T03:03Z — verify: `python3 -m pytest -q` → 383 passed
  (unchanged from main — docs-only diff); `bootstrap.py check --strict
  --require-session-log` → the only red pre-flip is the designed born-red
  gate (docs-gate badge + reachability clean for the new doc). PR **#89**
  opened READY (non-draft) with the doc's headline numbers; no merge
  action by this session (auto-merge-enabler is the landing path).
- 2026-07-13T03:05Z — flip + claim-delete folded into this final commit.

## Previous-session review

⟲ The most recent prior card (`.sessions/2026-07-13-r3-trix-ichimoku.md`,
Status `complete`) landed PR #88 clean — born-red first commit, grids
declared before the run, the round's most safety-critical strategy work
(three explicit ichimoku no-lookahead tests for the forward-displaced
spans, exactly the classic trap), flip+claim-delete folded into one final
commit — correct discipline throughout, and its verify block reproduces
at this session's start: 383 passed on main matches its claimed count,
and its 24 `r3-trix-ichimoku` sweep JSONs are on main
(`variants_tried=12`, `data_end=2025-01-08`, program cumulative 2,432)
exactly as claimed — this synthesis re-derived every one of its lane
numbers from the JSONs and found zero drift from its card prose. Its
honest-pattern language ("five of six KEEPs at t ≤ 0.14 — coin-flip
territory"; "a low bar cleared, not an edge") set the register this
synthesis doc adopts round-wide. Its 💡 (walk-forward train-side
cold-start vs warm-test asymmetry) is sound, still unimplemented, and its
closing observation — that `walkforward.py` is now the fleet's
most-cited unpaid-instrumentation site — is strengthened by this
session's schema-fork finding: the round's follow-up debt clusters in
exactly two files (walkforward.py, and the copy-pasted sweep-script
family). One nit: its card calls the 12-ticker set "slice-4/6" mixed set
while slice 4's card credits itself — harmless, but the synthesis doc
names the set once and cites both.

## Close-out

**Done:** on branch `claude/r3-synthesis` (PR #89) —

1. `docs/research-round-3-results.md` — the Round-3 synthesis (Status
   `reference`): 1,752 configs / 166 lanes / 0 PROMOTED / 41 KEEP-dev /
   125 KILL, full KEEP-vs-bar table (max t 1.04), verified patterns,
   explicit non-claims, reproducibility list. Every number from the
   merged sweep JSONs; PRs and file paths cited per claim.
2. One linking bullet in `docs/current-state.md` § Recently shipped
   (reachability per convention; no live-state edits).
3. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:**
`python3 -m pytest -q` → 383 passed (unchanged from main).
`python3 bootstrap.py check --strict --require-session-log --session-log .sessions/2026-07-13-r3-synthesis.md`
→ exit 0 after this flip (pre-flip the only red was the designed born-red
gate). Integrity at close: NO new backtests run, no `src/` or `scripts/`
changes, holdout (SPENT) untouched, `unlock_holdout` never passed,
`data/p5holdout/` untouched, paper-lane files byte-untouched,
`experiments/` byte-untouched, `control/inbox.md` + `control/status.md` +
`control/outbox.md` byte-untouched, no triggers created or modified, no
promotion/finding language beyond the recorded KILL/KEEP-dev verdicts,
NO merge action taken by this session.

**Next (guard recipe):** none owed for correctness. Follow-up candidates:
the graded-unit schema normalization (this card's 💡 — anchors and test
target named there; it unblocks slice 4's verdicts index), then the
standing stack (sweep-runner extraction, walk-forward warm-history fix,
OOS activity line, cost-drag line, benchmark-drift arm, provenance
sidecar). The 41 KEEPs are dev-candidates only; any OOS test of them is
OWNER-GATED behind a new pre-registered protocol on post-2026 data, per
docs/research-round-2-results.md and the new
docs/research-round-3-results.md.

Session end: badge flipped `complete` in this final content commit before
push.
