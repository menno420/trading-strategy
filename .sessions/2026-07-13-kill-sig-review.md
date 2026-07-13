# 2026-07-13 — KILL-SIG verdict-class proposal (PR #91 card 💡): independent review + disposition

> **Status:** `in-progress` — coordinator-assigned review of the KILL-SIG
> verdict-class proposal left as the 💡 on the PR #91 session card
> (`.sessions/2026-07-13-r3-meanrev-new-tickers.md`). Deliverable is the
> review verdict + disposition recorded here; everything was read at
> origin/main HEAD `320a1e3`.

📊 Model: Claude Fable · kill-sig-review lane (worker session) · start 2026-07-13T13:55Z

💡 **Session idea (deduped against .sessions/ and docs/ideas/):** the
program now runs THREE disjoint verdict grammars — the promotion gate
(`PROMOTED-TO-FINDING`/`RULE-PASS`/`KILLED`,
`src/trading_lab/promotion.py::grade_promotion`), the sweep lane
(`KEEP`/`KILL`/`KILL-SIG` + report-level `UNGRADEABLE`,
`promotion.classify_verdict` + `scripts/run_r4_killsig_regrade.py`), and
the paper lane (`BEAT`/`MISS`/`FLAT`, `docs/paper-lane-protocol.md` §7,
which BANS t-stats at small n) — but no single page maps them, and the
definitions live in a code docstring, a plan section, and a protocol doc
respectively. The gap has a measured cost: this very session's tasking
assumed the sweep verdict classes lived in `docs/paper-lane-protocol.md`
/ `scripts/grade_paper.py`, and disambiguating took a multi-file
archaeology pass. Proposal: `docs/verdict-grammars.md` (badge
`reference`) — one table per lane: vocabulary, assignment rule, defining
file/anchor, and an explicit "these never mix" note (sweep KILL-SIG
REQUIRES a recorded t-stat; paper §7 FORBIDS one — importing either
class into the other lane is a protocol violation, not a refactor).
Distinct from the standing sweep-verdicts index (that indexes verdict
*records*; this documents the *taxonomies*) and from the tally-
reconciliation idea (that checks prose *numbers*; this pins prose
*vocabulary*).

## Why this session exists

The PR #91 session card (`.sessions/2026-07-13-r3-meanrev-new-tickers.md`,
lines 19–41 at `320a1e3`) left a 💡 proposing a third sweep verdict —
KEEP / KILL / **KILL-SIG**, where KILL-SIG iff `tstat ≤ −min_tstat` from
the already-recorded `promotion_grade` — motivated by TSLA
`rsi_mean_reversion` grading t = −3.01 against the ±2.64 bar while being
recorded as just another KILL. The coordinator asked for a genuine
independent review: does the class pay for its complexity, judged on
(a) the round-4 evidence and (b) protocol simplicity? Verdict + reasons
below; ACCEPT / ACCEPT-WITH-CHANGES / REJECT were all open outcomes.

## Review (the deliverable)

**Everything below was read at origin/main HEAD
`320a1e3fe38e18b8d0b22d011a3e722093ed4d73`** (verified equal to
`git ls-remote origin main` at session start).

### Finding 0 — the proposal is already adopted and merged

The review's first material fact: this proposal is not pending. It was
pre-registered as Round-4 slice R4-A (`docs/research-round-4-plan.md`
§ "R4-A — KILL-SIG verdict class (retroactive, non-destructive)", merged
before any Round-4 outcome existed) and implemented in **PR #100**
(merged 2026-07-13, card `.sessions/2026-07-13-r4-killsig.md`):

- `src/trading_lab/promotion.py::classify_verdict` (lines 145–170 at
  `320a1e3`) + `SWEEP_KEEP`/`SWEEP_KILL`/`SWEEP_KILL_SIG` constants —
  exactly the proposed rule (mirrored Bonferroni bar, zero new
  arithmetic), plus one hardening the proposal didn't spell out:
  missing/NaN/non-numeric t-stats degrade to plain KILL, so the function
  never invents a significance claim.
- `scripts/run_r4_killsig_regrade.py` — the retroactive, NON-destructive
  re-grade: every `experiments/sweeps/r3-*/` JSON byte-untouched, one
  separate report artifact
  (`experiments/sweeps/r4-killsig-regrade/summary.json`).
- All five later Round-4 runners (`run_r4_cost_sensitivity.py`,
  `run_r4_seasonality_sweep.py`, `run_r4_ensemble_sweep.py`,
  `run_r4_regime_sweep.py`, `run_r4_crossasset_sweep.py`) call
  `classify_verdict` natively at grade time.

This review therefore doubles as a post-adoption audit: was adopting it
right, and did the adoption hold up in use? Both answers are yes, with
one interpretive caveat (below).

### (a) Evidence — significantly-negative results DO carry different information than plain KILL

1. **The class separates a real, small tail — it does not relabel the
   KILL mass.** R4-A re-graded all 302 committed r3 per-lane summaries:
   **58 KEEP / 238 KILL / 4 KILL-SIG / 2 UNGRADEABLE**
   (`docs/research-round-4-results.md` § R4-A at `320a1e3`). 4/300
   graded lanes ≈ 1.3%. A verdict class that fires this rarely at
   comparable exposure is informative by construction; had it swallowed
   half the KILLs it would have been noise-splitting.
2. **Boundary behaviour has discriminating power.** The motivating lane
   (TSLA rsi_mean_reversion, t = −3.011) is KILL-SIG; the predicted
   near-miss (SPY donchian, t = −2.417 vs bar 2.638) correctly stays
   plain KILL. The hypothesis was pre-registered as "1–3 lanes" and the
   observed 4 was reported as a near-miss of a real prediction — the
   class was born inside the repo's own commitment discipline, not
   fitted after the fact.
3. **The "study the loser" value is captured the right way round.** The
   coordinator's review brief asks whether a significantly negative
   signal is worth studying as an inverted hypothesis. The repo's answer
   — stated in the plan, the results doc, and the script docstring — is
   the correct one: a KILL-SIG is evidence AGAINST the lane and
   explicitly NOT an inversion signal (inverting a loser selected on the
   very data that graded it is selection-on-outcome). What the class DOES
   buy is exactly the proposal's payoff (c): any future inversion
   temptation now meets a pre-registered record of which losers were
   significant, and exclusion lists become evidence-graded. As a
   pipeline-bias tripwire it also proved useful: the four KILL-SIG lanes
   cluster in two reversion families on strong-benchmark daily lanes — a
   pattern a flat KILL bucket would have hidden.
4. **Verified, not trusted, at this session's HEAD:** re-ran
   `scripts/run_r4_killsig_regrade.py` at `320a1e3` — output
   `re-graded 302 r3 lanes`, counts
   `{'KEEP': 58, 'KILL': 238, 'KILL-SIG': 4, 'UNGRADEABLE': 2}`, same
   four lanes (AAPL/NVDA cci_reversion −2.84/−2.93, TSLA
   rsi_mean_reversion −3.01, GOOGL adx_filtered_sma −3.10); the
   regenerated report differed from the committed artifact ONLY in the
   two provenance fields (`created_utc`, `git_sha`), then was restored
   byte-identical (`git status` clean). `python3 -m pytest
   tests/test_promotion.py -q` → **32 passed**.
5. **The caveat that bounds interpretation (the one genuine weakness).**
   R4-F minted **30/75** KILL-SIGs on the seasonality slice, and the
   results doc itself reads them honestly as a *benchmark-exposure
   artifact*: a rule holding ~20% market exposure graded against
   fully-invested B&H over a rising window goes "significantly harmful"
   by under-investment, not by harmful timing
   (`docs/research-round-4-results.md` § R4-F and § closing tally,
   point (1)). So KILL-SIG means "significantly worse than THIS
   benchmark", and its evidential force is conditional on comparable
   exposure. The round-5 synthesis already queues the right amendment
   (exposure-ratio column, item 5) — reporting-side, not a grading
   change; no bar or class change is warranted.

### (b) Simplicity — the class costs almost nothing where it lives

- **Zero new arithmetic**, as proposed: both inputs (`tstat`,
  `min_tstat`) were already in every sweep summary JSON; the rule is one
  comparison against the mirrored, already-Bonferroni'd bar. No new
  statistics, no new K accounting, the bar itself untouched.
- **One pure total function** with a safe degrade path, pinned by tests
  (18 added at adoption; the module's suite is 32 as of `320a1e3`).
  Report-level `UNGRADEABLE` handles the two verdict-less XSEC
  bookkeeping summaries by counting, never recomputing.
- **Future-grader burden proved low in practice:** five subsequent R4
  runners applied it natively with no friction, including at raised bars
  (K=13 → 2.665, K=14 → 2.690, K=75 → 3.209).
- **Non-destructive retroactivity:** the historical record stayed
  byte-identical; the re-grade is a separate report artifact. Verified
  at `320a1e3` (item 4 above).

### Verdict: **ACCEPT** (ratifying already-merged adoption; zero further diff)

The class pays for its complexity: the evidence side shows a rare,
pre-registered, boundary-respecting distinction with real action content
(evidence-graded exclusion, anti-inversion tripwire), and the cost side
is one pure function on fields that already existed. The R4-F exposure
caveat is real but is an interpretation bound, already flagged with a
queued reporting fix — it does not overturn the class.

**Disposition — what this ACCEPT does NOT license:**

1. **No implementation work remains.** "KILL-SIG exists and is assigned
   per the proposal" is already true at HEAD in the correct place
   (`src/trading_lab/promotion.py::classify_verdict`; runners call it at
   grade time). This branch deliberately carries no code diff.
2. **`docs/paper-lane-protocol.md` is NOT amended and must not be.** It
   never contained the KEEP/KILL sweep classes: its §7 verdict grammar
   is per-window `BEAT`/`MISS`/`FLAT` and it explicitly bans t-stats,
   p-values and the word "significant" at the lane's single-digit n.
   That document is `binding` and pre-registered before any paper
   outcome was observable; grafting a significance class onto it
   mid-lane would be precisely the "grading rule chosen after watching
   the first trade" failure its own preamble forbids. The proposal was
   about the sweep lane and was adopted there; lane grammars never mix.
3. **No retroactive re-labelling, still.** Historical
   ledgers/results/sweep JSONs stay byte-identical (verified); the class
   applies to committed history only via the separate R4-A report
   artifact, and to everything else from grade time forward.

### Files read @ `320a1e3` (all at that SHA)

- `.sessions/2026-07-13-r3-meanrev-new-tickers.md` (the proposal, lines
  19–41; verdict table context)
- `docs/research-round-4-plan.md` § R4-A (pre-registration)
- `.sessions/2026-07-13-r4-killsig.md` (adoption record, PR #100)
- `docs/research-round-4-results.md` (R4-A counts + four-lane table;
  R4-B/C/D/E/F native use; R4-F exposure caveat; closing tally)
- `src/trading_lab/promotion.py` (verdict constants; `grade_promotion`;
  `classify_verdict` lines 145–170)
- `scripts/run_r4_killsig_regrade.py` (rule + non-destructive report)
- `docs/paper-lane-protocol.md` (esp. §7 grading grammar, §8) and
  `scripts/grade_paper.py` (delegates to `trading_lab.paper`;
  BEAT/MISS/FLAT lane — no KEEP/KILL classes live there)
- `docs/research-round-2-results.md` § pre-reg KEEP/KILL rule (grep,
  lines 52/126 context)
- `.sessions/README.md`, `control/claims/README.md` (conventions)

## Coordinator-bundled check — `control/status.md` pointer (no change made)

Asked to verify the alleged `docs/retros/` → `docs/retro/` typo on the
`pointer_venture_retro:` line. Finding at `320a1e3`: this repo has
`docs/retro/` only (no `docs/retros/`), **but** the pointer line reads
`docs/retros/2026-07-13-coordinator-session.md (venture-lab repo)` — it
explicitly targets the **venture-lab repo**, which this seat cannot
read, and the referenced file exists in NEITHER `docs/retro/` nor
`docs/retros/` of THIS repo (this repo's `docs/retro/` holds no
`2026-07-13-coordinator-session.md`). Rewriting a cross-repo pointer in
the coordinator-owned heartbeat based on the wrong repo's directory
listing would be a guess, not a fix — the verification the task
prescribed cannot reach the pointer's actual target. **No change made;
finding recorded here** for the coordinator (who can verify venture-lab
directly).

## Work log

- 2026-07-13T13:55Z — fresh clone; `git ls-remote origin main` =
  `320a1e3` (expected value; descendant chain intact). Read PR #91 via
  GitHub MCP → card `.sessions/2026-07-13-r3-meanrev-new-tickers.md`;
  full reading list above. Collision check: `control/claims/` at HEAD
  holds only `README.md` — no overlap.
- 2026-07-13T13:58Z — independent verification at HEAD: regrade re-run
  reproduces 58/238/4/2 (provenance fields only diff; restored
  byte-identical); `pytest tests/test_promotion.py -q` → 32 passed.
- 2026-07-13T14:0xZ — branch `claude/kill-sig-review-2026-07-13`;
  born-red FIRST commit = this card (`in-progress`) + claim
  `control/claims/2026-07-13-kill-sig-review.md`, pushed before anything
  else.

## Previous-session review

⟲ Reviewed PR #108 (boot-refresh, merged 2026-07-13T13:48Z, card
`.sessions/2026-07-13-boot-refresh.md`): a clean coordinator heartbeat —
`control/status.md` rewritten with the verified trigger cutover (four
old trigger ids confirmed deleted, four coordinator-seat replacements
listed), `docs/current-state.md` unstaled, ORDER 011 verification +
the foreign duplicate grading one-shot flagged to the manager via an
append-only outbox entry; born-red card discipline followed, no merge
action taken. One genuine nit, found by this session's own task: its
status.md rewrite carries the cross-repo pointer
`pointer_venture_retro: docs/retros/... (venture-lab repo)` that is
unverifiable from inside this repo (and whose path this session was
asked to typo-check) — cross-repo pointers in a heartbeat should be
verified in the *named* repo at write time, since no downstream session
in THIS repo can check them.

## Close-out

**Done:** on branch `claude/kill-sig-review-2026-07-13` —

1. Independent review of the PR #91-card KILL-SIG proposal: verdict
   **ACCEPT**, ratifying the already-merged R4-A adoption (PR #100);
   zero further code/doc diff required, and the two changes an
   over-literal ACCEPT could have made (amending the binding
   `docs/paper-lane-protocol.md`; any retroactive re-labelling) are
   explicitly declined with reasons above.
2. Verification evidence at `320a1e3`: regrade reproduction (58 KEEP /
   238 KILL / 4 KILL-SIG / 2 UNGRADEABLE, byte-identical artifact after
   restore) + `tests/test_promotion.py` 32 passed.
3. `control/status.md` pointer check: **no change** — the alleged typo
   targets the venture-lab repo (out of this seat's read scope) and the
   pointed file exists in neither candidate directory of this repo;
   finding recorded above.
4. This card (born-red first commit → flipped `complete` last) — claim
   file deleted in this same commit.

**Verify:** `python3 -m pytest tests/test_promotion.py -q` → 32 passed
(no code changed by this session; full-suite run not owed).
`python3 bootstrap.py check --strict` → green before the final push
(pre-flip, the only red was the designed born-red gate). Integrity at
close: no code touched, no sweep run, no data loaded, holdout (SPENT)
untouched, paper-lane files byte-untouched, `control/inbox.md` /
`control/outbox.md` / `control/status.md` byte-untouched, historical
ledgers and every `experiments/**` file byte-untouched, no triggers
created or modified, no broker/order/exchange code, NO merge action
taken by this session.

**Next (guard recipe):** none owed for correctness. Follow-up
candidates: the verdict-grammars map (this card's 💡 — anchors named
there); the exposure-ratio column (round-5 item 5) as the R4-F
interpretation guard; coordinator to verify the venture-lab retro
pointer in the venture-lab repo itself.

Session end: badge flips `complete` in the final content commit before
push.
