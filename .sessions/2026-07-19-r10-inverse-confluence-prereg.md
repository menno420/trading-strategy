# 2026-07-19 — Round 10 pre-registration (inverse-confluence EXIT vote, go-flat when ≥K agree)

> **Status:** `complete` — Round 10 pre-registered (PLAN + CODE
> INFRASTRUCTURE, ZERO results) — `docs/research-round-10-plan.md` (binding):
> the INVERSE of the owner's confluence idea — hold long by DEFAULT and use a
> cross-thesis-class ≥K-of-N majority VOTE to decide when to STEP ASIDE (go
> flat), a risk-OFF de-risking overlay on buy-and-hold. This PR lands the plan +
> the `ensemble.exit_confluence_positions` gate (the De Morgan dual of the R9
> entry vote) + the pinned 60-config R10 grid (`sweeps._R10_*`,
> `r10_total_configs()` = 60) with tests; the sweep RUNNER + graded results are a
> separate future RUN PR with its own card. POST-HOLDOUT, DEV-ONLY: holdout
> SPENT, promotion CLOSED, `min_tstat` bar never lowered. This pre-registration
> is a complete, landable deliverable on its own — the card flips `complete` as
> the final commit.

📊 Model: opus-4.8 · medium · idea/planning

## Why this session exists

R9 just landed (PR #154, `docs/research-round-9-results.md`): the owner's live
signal-confluence idea — enter only when ≥2 (and separately ≥3) DISTINCT
strategies agree — graded to **60 configs, 11 KEEP-dev / 44 KILL / 5 KILL-SIG,
0 promoted, best informational t 1.04**, with the pre-registered correlation
check finding the members near-INDEPENDENT (0 of 15 instruments tripped the >0.5
flag). The entry-confluence vote sat flat through the market's drift and was
KILL-SIG on trending names — waiting for agreement to ENTER left it in cash
through the rise.

Round 10 tests the DIRECT COMPLEMENT the coordinator authorized on the same live
2026-07-19 owner turn: if requiring agreement to ENTER made it sit in cash
through the drift, does requiring agreement to EXIT (a de-risking overlay on
buy-and-hold) do any better? R10 holds long by DEFAULT and uses the SAME ≥K
cross-class vote to decide when to STEP ASIDE — the risk-OFF dual of R9. The vote
gate is `ensemble.exit_confluence_positions`, the De Morgan dual of the R9 entry
vote: R9 position = 1 iff ≥K long; R10 position = 0 iff ≥K flat.

Per the header protocol, this pre-registration PR lands PLAN + CODE
INFRASTRUCTURE only (the compositor + the pinned grid + tests), ZERO
results/outcomes; the sweep runner + graded `docs/research-round-10-results.md`
are a separate future RUN PR. Held BORN-RED: the card stays `in-progress`.

## Work log

- branch `claude/r10-inverse-confluence-prereg` cut from origin/main HEAD
  `b1564f2` (#154, R9 results; program cumulative 5,853 registered configs / 0
  promoted). Born-red FIRST commit: this card.
- ORDER 020 appended to `control/inbox.md` (decide-and-flag provenance note,
  mirroring the ORDER 019 precedent — `control/` is RETIRED at HEAD but the live
  owner turn is landed here under that flag).
- `ensemble.exit_confluence_positions(members, k)` — the risk-OFF ≥k exit vote
  (hold long by default, go flat when ≥k members want out), implemented as the De
  Morgan dual `1 - confluence_positions([1-m for m in members], k)` + unit tests.
- the R10 grid pinned in `sweeps.py` (`_R10_MEMBER_SET_3`, `_R10_MEMBER_SET_5`
  aliasing the R9 sets, `_R10_VOTE_CONFIGS`, `_R10_INSTRUMENTS = R7_INSTRUMENTS`,
  `r10_total_configs()` = 15 × 4 = 60) + pins in `tests/test_sweeps.py`.
- `docs/research-round-10-plan.md` (badge `binding`) + a PLAN-ONLY reachability
  bullet in `docs/current-state.md`'s rounds list (NOT the health heartbeat / NOT
  a CLOSED flip — that is the RUN PR's job at flip time).

💡 **Session idea:** R9 and R10 are a De Morgan pair over the SAME member panel —
R9's `confluence_positions` (≥K long → in) and R10's `exit_confluence_positions`
(≥K flat → out) — and the Pearson identity `corr(1-x, 1-y) = corr(x, y)` means
R10's exit-signal correlations EQUAL R9's already-computed position correlations
(0/15 tripped >0.5). A tiny read-only `scripts/dual_signal_report.py` over
`data.load_ohlcv` that emits, per instrument, both the entry-confluence and
exit-confluence lanes side by side (co-agreement bar counts + the shared
correlation block) would let the R10 RUN reuse R9's correlation matrices verbatim
rather than recompute them. Anchor: the "PRE-REGISTERED correlation check"
section of the R10 plan + `ensemble.confluence_positions` /
`ensemble.exit_confluence_positions`; test target: assert
`exit_confluence_positions(m, k) == 1 - confluence_positions([1-x for x in m], k)`
on a toy panel and that the reported exit-corr block equals the entry-corr block.

## Previous-session review

⟲ PR #154 (`r9-confluence-run`, merged) — landed
`docs/research-round-9-results.md`, grading the owner's entry-confluence vote:
60 configs, **11 KEEP-dev / 44 KILL / 5 KILL-SIG, 0 promoted, best informational
t 1.04** (BTC-USD SET-3/K=2) vs the K=4 bar 2.24 and program K=60 bar 3.14. Two
findings drive R10 directly: (a) the pre-registered correlation check found the
members near-INDEPENDENT — 0 of 15 instruments tripped the >0.5 flag — so the
vote was NOT one signal counted twice; and (b) the entry vote sat flat through
the drift and was KILL-SIG on trending names (waiting to agree before entering
cost the rise). R10 answers the complement the coordinator authorized on the same
owner turn: hold by default, use the same ≥K agreement to decide when to EXIT.
The near-independence finding sets R10's honest prior: because ≥K agreement is
rare either way, a strict K=3 exit barely deviates from buy-and-hold (t near 0)
while a loose K=2 exit steps aside often and likely misses the drift a hold rides
— a null (0 promoted) is the expected, publishable outcome. No sweep re-run,
holdout untouched — confirmed clean at HEAD (`b1564f2`).

## Close-out

**Done** (6 commits on `claude/r10-inverse-confluence-prereg`, cut from
origin/main HEAD `b1564f2`):
- `2551472` — born-red FIRST commit: this session card (`in-progress` hold).
- `2289a1d` — `control/inbox.md` ORDER 020 (inverse-confluence exit-vote
  research) under a decide-and-flag provenance note (the ORDER 019 precedent;
  `control/` RETIRED at HEAD).
- `7d60530` — `ensemble.exit_confluence_positions(members, k)`: the risk-OFF ≥k
  exit vote (long by default, go flat when ≥k members are flat), the De Morgan
  dual `1 - confluence_positions([1-m for m in members], k)` + 11 unit tests
  incl. the identity.
- `feff384` — the R10 grid pinned in `sweeps.py` (`_R10_MEMBER_SET_3` /
  `_R10_MEMBER_SET_5` aliasing the R9 panels, `_R10_VOTE_CONFIGS`,
  `_R10_INSTRUMENTS = R7_INSTRUMENTS`, `r10_vote_configs()`,
  `r10_total_configs()` = 15 × 4 = 60) + 12 pins in `tests/test_sweeps.py`.
- `da31935` — the BINDING plan `docs/research-round-10-plan.md` (badge `binding`)
  + a PLAN-ONLY reachability bullet in `docs/current-state.md`'s rounds list
  (NOT the health heartbeat / NOT a CLOSED flip — that is the RUN PR's job) +
  the guard-fires telemetry delta.
- (this commit) — close-out flip: badge `in-progress` → `complete`, close-out
  written. The pre-registration is a complete, landable deliverable on its own.

**Verify:**
- `python3 -m pytest -q` → **809 passed** (786 prior + 11 exit-vote ensemble + 12
  R10 sweeps pins).
- `python3 bootstrap.py check --strict` → EXIT 0 at flip (the born-red
  in-progress HOLD was the only red; it clears when the badge flips to
  `complete`). Advisories only: seat-digest + pre-existing model-line payload
  nits on OLDER cards (never exit-affecting); this card's Model line carries the
  taught three-field form (`opus-4.8 · medium · idea/planning`) and adds no new
  advisory.
- No member substitutions were required — the R10 panels are the R9 panels
  reused VERBATIM (aliased, not duplicated): `ema_crossover`,
  `rsi_mean_reversion`, `donchian` (SET-3) + `drawdown_reversion`, `obv_trend`
  (SET-5), all resolving to registry families emitting clean 0/1 daily positions.

**Integrity — PLAN + INFRASTRUCTURE, ZERO results:** the branch diff touches
only the plan doc, the `exit_confluence_positions` gate + its tests, the pinned
R10 grid + its tests, the ORDER 020 inbox append, the current-state reachability
bullet, the guard-fires telemetry delta, and this card. NO sweep run, NO
backtest, NO runner, NO verdict; the holdout was never read, no fetch,
`experiments/paper/**` untouched, `control/status.md` untouched, no triggers, no
broker code. Promotion stays CLOSED / 0 promoted, holdout stays SPENT, the
`min_tstat` bar is unchanged. NO manual merge — the landing workflow merges on
green.

**Next (the R10 RUN slice, a future separately-claimed session + card):** clone a
gate-carrying daily runner into `scripts/run_r10_exit_confluence_sweep.py`
(compose each (instrument × exit-vote config) via `exit_confluence_positions`,
benchmark vs buy-and-hold, grade under the Round-2 rule + selection-fair gate on
every lane), compute the pre-registered exit-signal correlation/overlap check
(§ 6, confirming the `corr(1-x,1-y)=corr(x,y)` identity vs R9) and the exit-count
/ trade-count-vs-B&H / SE-inflation impact (§ 7) with the degenerate ~0-exit
flag, and land `docs/research-round-10-results.md` (5,853 → 5,913), flipping the
round to CLOSED in `docs/current-state.md`.
