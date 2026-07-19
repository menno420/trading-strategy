# 2026-07-19 — Round 9 pre-registration (signal-confluence vote, cross-class ≥K-of-N)

> **Status:** `complete` — Round 9 pre-registered (PLAN + CODE INFRASTRUCTURE,
> ZERO results) — `docs/research-round-9-plan.md` (binding): a
> cross-thesis-class ≥K-of-N majority VOTE that enters only when ≥2 (and
> separately ≥3) DISTINCT strategies agree, the owner's live signal-confluence
> idea. This PR lands the plan + the `ensemble.confluence_positions` vote gate
> + the pinned 60-config R9 grid (`sweeps._R9_*`, `r9_total_configs()` = 60)
> with tests; the sweep RUNNER + graded results are a separate future RUN PR
> with its own card. POST-HOLDOUT, DEV-ONLY: holdout SPENT, promotion CLOSED,
> `min_tstat` bar never lowered. This pre-registration is a complete, landable
> deliverable on its own — the card flips `complete` as the final commit.

📊 Model: opus-4.8 · medium · idea/planning

## Why this session exists

Live owner turn 2026-07-19 (verbatim: *"any more progress on the trading
strategies, what I was thinking about, isn't it a good idea to find multiple
strategies and wait untill at least 2 or 3 give the same signals, what do you
think about that?"*), relayed via the venture-lab coordinator. The owner's idea
is signal CONFLUENCE: enter only when several DISTINCT strategies agree. Round 9
pre-registers exactly that as a binary cross-thesis-class ≥K-of-N majority vote
— long only on bars where at least K of N distinct-class members are
simultaneously long — and grades it under the standard corrections
(plan-before-outcome, selection-fair gate, `min_tstat` bar never lowered,
holdout SPENT, promotion CLOSED).

This is the untested corner between two burned neighbors: R4-C
(`ensemble.committee_positions`, `docs/research-round-4-results.md` §R4-C)
AVERAGED member positions into a fractional ~OR-weighted size (5 KEEP-dev / 7
KILL, best new-config t 1.09, 0 promoted); R7-C `washout_recovery`
(`docs/research-round-7c-results.md`) AND-gated two windows WITHIN ONE
thesis-class (180 configs, 1 KEEP-dev / 11 KILL / 3 KILL-SIG, best t 0.22,
KILL-SIG on AMZN/MSFT/QQQ — actively value-destroying). R9 is the case neither
ran: a BINARY ≥K vote ACROSS distinct thesis-classes. Honest registered prior:
distinct-class signals (momentum vs mean-reversion) are often anti-correlated,
rarely co-agree, so AND-gating collapses trade count and statistical power — a
NEGATIVE result is the expected and publishable outcome.

Per the header protocol, this pre-registration PR lands PLAN + CODE
INFRASTRUCTURE only (the compositor + the pinned grid + tests), ZERO
results/outcomes; the sweep runner + graded `docs/research-round-9-results.md`
are a separate future RUN PR. Held BORN-RED: the card stays `in-progress`.

## Work log

- branch `claude/r9-confluence-prereg` cut from origin/main HEAD `d907d01`
  (#152, cross-round meta-analysis; program cumulative 5,793 registered
  configs / 0 promoted). Born-red FIRST commit: this card.
- ORDER 019 appended to `control/inbox.md` (decide-and-flag provenance note,
  mirroring the ORDER 018 precedent — `control/` is RETIRED at HEAD but the
  live owner turn is landed here under that flag).
- `ensemble.confluence_positions(members, k)` — the binary ≥k vote gate
  (AND/vote, distinct from `committee_positions`' AVERAGE) + unit tests.
- the R9 grid pinned in `sweeps.py` (`_R9_MEMBER_SET_3`, `_R9_MEMBER_SET_5`,
  `_R9_VOTE_CONFIGS`, `_R9_INSTRUMENTS = R7_INSTRUMENTS`, `r9_total_configs()`
  = 15 × 4 = 60) + pins in `tests/test_sweeps.py`.
- `docs/research-round-9-plan.md` (badge `binding`) + a PLAN-ONLY reachability
  bullet in `docs/current-state.md`'s rounds list (NOT the health heartbeat /
  NOT a CLOSED flip — that is the RUN PR's job at flip time).

💡 **Session idea:** the confluence idea has a pre-registered correlation check
(mean pairwise member position-correlation per instrument) precisely because
"confluence between correlated members is one signal counted twice." A reusable
`scripts/member_overlap.py` — read-only over `data.load_ohlcv`, emitting per
instrument the pairwise position-correlation / Jaccard signal-overlap / return
correlation matrices for any member panel at default params — would mechanize
that check for R9 AND retro-fit it to the R4-C committees (whose AVERAGE also
silently double-counts correlated members). Anchor: the "PRE-REGISTERED
correlation check" section of this R9 plan + `ensemble.confluence_positions` /
`ensemble.committee_positions`; test target: assert the tool reproduces a
hand-computed Jaccard on a 2-member toy panel and flags the ~0.5 threshold.

## Previous-session review

⟲ PR #152 (`cross-round-meta-analysis`, merged) — landed
`docs/cross-round-meta-analysis.md`, the honest P1 → Round 8 synthesis (**5,793
registered configs / 0 promoted**; program best t anywhere 1.66 at R5, far
under the 2.638 bar) plus the read-only `scripts/aggregate_effect_sizes.py`
(pytest-pinned). Its closing question — "what an owner-gated future round would
need" — is answered by THIS round: the owner GATED it with a live turn, and R9
enters under the SAME corrections #152 tallied (selection-fair gate, `min_tstat`
never lowered, holdout SPENT, promotion CLOSED). The direct methodological
inheritance: #152 foregrounds that every prior round's strongest dev arm sat
FAR below its Bonferroni bar and that fewer effective trades inflate the SE
(`SE ∝ sqrt((1+SR²/2)/N)`) — which is exactly why R9's pre-registered
trade-count / power-impact section is first-class, not a footnote: a ≥K vote
across anti-correlated distinct-class members can only SHRINK N, RAISE the SE,
and make the unchanged bar HARDER to clear. #152 is a synthesis doc; no
correctness defect to inherit, but its effect-size honesty is the frame R9
grades under. No sweep re-run, holdout untouched — confirmed clean at HEAD.

## Close-out

**Done** (6 commits on `claude/r9-confluence-prereg`, cut from origin/main HEAD
`d907d01`):
- `84724bb` — born-red FIRST commit: this session card (`in-progress` hold).
- `427429b` — `control/inbox.md` ORDER 019 (signal-confluence research) under a
  decide-and-flag provenance note (the ORDER 018 precedent; `control/` RETIRED
  at HEAD).
- `e445a15` — `ensemble.confluence_positions(members, k)`: the binary ≥k-of-N
  vote gate (AND/vote, distinct from `committee_positions`' AVERAGE) + 12 unit
  tests.
- `a91a938` — the R9 grid pinned in `sweeps.py` (`_R9_MEMBER_SET_3`,
  `_R9_MEMBER_SET_5`, `_R9_VOTE_CONFIGS`, `_R9_INSTRUMENTS = R7_INSTRUMENTS`,
  `r9_vote_configs()`, `r9_total_configs()` = 15 × 4 = 60) + 10 pins in
  `tests/test_sweeps.py`.
- `e5e96b3` — the BINDING plan `docs/research-round-9-plan.md` (badge `binding`)
  + a PLAN-ONLY reachability bullet in `docs/current-state.md`'s rounds list
  (NOT the health heartbeat / NOT a CLOSED flip — that is the RUN PR's job).
- (this commit) — close-out flip: badge `in-progress` → `complete`, close-out
  written. The pre-registration is a complete, landable deliverable on its own.

**Verify:**
- `python3 -m pytest -q` → **786 passed** (762 prior + 12 ensemble + 10 sweeps +
  the confluence end-to-end pins).
- `python3 bootstrap.py check --strict` → EXIT 0 at flip (the born-red
  in-progress HOLD was the only red; it clears when the badge flips to
  `complete`). Advisories only: seat-digest + pre-existing model-line payload
  nits on OLDER cards (never exit-affecting); this card's Model line carries the
  taught three-field form (`opus-4.8 · medium · idea/planning`) and adds no new
  advisory.
- No member substitutions were required — all five R9 members
  (`ema_crossover`, `rsi_mean_reversion`, `donchian`, `drawdown_reversion`,
  `obv_trend`) resolve to registry families with sane defaults emitting clean
  0/1 daily positions; `obv_trend` reads volume, present on every one of the 15
  daily cache tickers (verified).

**Integrity — PLAN + INFRASTRUCTURE, ZERO results:** the branch diff touches
only the plan doc, the `confluence_positions` gate + its tests, the pinned R9
grid + its tests, the ORDER 019 inbox append, the current-state reachability
bullet, and this card. NO sweep run, NO backtest, NO runner, NO verdict; the
holdout was never read, no fetch, `experiments/paper/**` untouched,
`control/status.md` untouched, no triggers, no broker code. Promotion stays
CLOSED / 0 promoted, holdout stays SPENT, the `min_tstat` bar is unchanged. NO
manual merge — the landing workflow merges on green.

**Next (the R9 RUN slice, a future separately-claimed session + card):** clone a
gate-carrying daily runner into `scripts/run_r9_confluence_sweep.py` (compose
each (instrument × vote config) via `confluence_positions`, grade under the
Round-2 rule + selection-fair gate on every lane), compute the pre-registered
correlation/overlap check (§ 6) and the trade-count / SE-inflation impact (§ 7)
as first-class report sections, and land `docs/research-round-9-results.md`
(5,793 → 5,853), flipping the round to CLOSED in `docs/current-state.md`.
