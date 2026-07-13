# Fleet cleanup audit — 2026-07-13 (EAP final night)

> **Status:** `audit`
>
> Complementary read-only audit pass, run alongside the owner's live
> "ORDER 045 / dispatch instructions" fleet sweep. Scope: verify the
> STALE-heartbeat + 0-open-PR claims in the worklist doc, check CI/doc
> health, and report — no feature work, no control-bus edits. Written by
> an auditor subagent, not the trading-strategy coordinator seat; it does
> not carry the seat's own heartbeat authority and does not overwrite
> `control/status.md`, `control/inbox.md`, or `control/outbox.md`.

## What this repo is

`trading-lab` (`menno420/trading-strategy`) is an autonomous, research-only
quant lab. It backtests known and derived technical-indicator strategies
across daily/hourly tech-stock, gold/silver, and BTC-USD bars, under a
walk-forward + realistic-cost + anti-overfitting discipline (locked 18-month
holdout, Bonferroni-style significance bars scaled to configs tried,
pre-registration before every sweep). It never connects to a broker, never
executes trades, and never touches real money — confirmed by grep: no
broker/exchange/order-execution imports anywhere in `src/`, and the paper
trading lane (`src/trading_lab/paper.py`) only maintains a ledger, never
places orders. Source: `README.md`, `docs/founding-plan.md`.

## Structure

- `src/trading_lab/` — data loading (cached OHLCV, holdout-gated), backtest
  engine, ~20 strategy modules, promotion/verdict classification, the new
  `selection_gate.py` (D-0002), paper-lane grading. 6,527 lines.
- `tests/` — 6,217 lines, 646 tests (verified locally, see below).
- `experiments/sweeps/` — one directory per research round/slice (P1 through
  R6), each holding per-lane JSON + a `summary.json` rollup. `experiments/paper/`
  is the separate live-forward paper ledger.
- `data/` — cached daily/hourly bars (3.1 MB), `data/p5holdout/` (sealed,
  spent one-shot holdout), `data/p2ext/` (extended universe cache).
- `control/` — the fleet coordination bus: `inbox.md` (manager-written
  ORDERs, append-only), `status.md` (coordinator heartbeat, one-writer),
  `outbox.md` (manager-addressed reports, append-only), `claims/` (one file
  per in-flight work claim).
- `docs/` — 41 top-level docs plus `research/`, `retro/`, `proposals/`,
  `succession/`, `operations/`, `ideas/`. Runs on `substrate-kit` (vendored
  as `bootstrap.py`, 17,855 lines generated, currently v1.15.0).
- `.sessions/` — one session-card file per PR (born-red → complete
  convention), 19+ files for 2026-07-13 alone.

## CI setup and health

Three workflows: `tests.yml` (pytest on `pull_request` + push to `main`),
`substrate-gate.yml` (kit hygiene/session-card/claims/inbox-append-only gate,
same triggers, with a "control-only diff" fast lane), `auto-merge-enabler.yml`
(arms native squash auto-merge on non-draft `claude/*` PRs).

**Verified locally at HEAD `d6e3cf9`** (Python 3.11.15, fresh venv,
`pip install -r requirements.txt`):
- `python -m pytest -q` → **646 passed**, 7.04s. Matches PR #116's claimed
  "646 passed (607 baseline + 39 new)."
- `python bootstrap.py check --strict` → **all checks passed**.

**Verified live via GitHub Actions API** (`list_workflow_runs`): every PR
merged in the last hour (`#113`–`#116`) has green `tests` and `substrate-gate`
runs at its final `pull_request` head SHA before merge (e.g. #116 head
`fa12fcf` → both green at 22:50:48Z; #115 head `102a2a1` → both green at
22:54:30Z, after an earlier `substrate-gate` failure at head `965ae18` was
fixed forward within the same PR).

**Finding — push-triggered CI on `main` appears stalled since PR #97.**
`list_workflow_runs(branch=main, event=push)` shows the newest push-triggered
run is `08969bb` at **2026-07-13T09:12:19Z** (PR #97). Since then, roughly 20
more PRs have merged to `main` (`#98`–`#116`, confirmed via `list_pull_requests`
and the git log), but no further push-triggered `tests`/`substrate-gate` run
appears in the Actions history — all runs since then are `pull_request`-event
runs on `claude/*` branches. Both workflow files declare `push: branches:
[main]`, and the `tests` workflow's `state` is `active` (verified via
`actions_get get_workflow`), so this isn't a disabled workflow. Every merge is
independently pre-verified by the PR-level `pull_request` run, so this is not
a "broken CI" finding — the substantive gate still holds — but the **post-merge
verification of the final squashed commit on `main` has not run in over 13
hours** despite continuous merge activity. Possible cause (not confirmed):
the repo's native/GitHub-side auto-merge may be performing the squash-merge
in a way that doesn't emit a `push` webhook the workflow's trigger sees, or
some other change in the merge path around `08969bb`. Worth a coordinator
follow-up (see suggestions).

## Doc quality

Generally strong and unusually well cross-referenced for an autonomous repo:
`docs/current-state.md` (living ledger), `docs/decisions.md` (append-only
decision log, D-0001/D-0002), `docs/AGENT_ORIENTATION.md` (task router),
`control/README.md` + `control/claims/README.md` (protocol docs with
measured rationale, e.g. the claim-layout conflict-rate simulation). Every
research round has a pre-registered plan doc merged *before* any outcome
exists, and results docs are honest about null results (explicit K-adjusted
significance bars, "0 PROMOTED" headlines reported as first-class findings
rather than buried).

Two concrete drift items found:

1. **`docs/review-queue.md` line for #37 is stale by ~3 days of activity.**
   The file's only commit (`27d13a2`, 2026-07-10T17:00:39Z, verified via
   `list_commits(path=docs/review-queue.md)`) added: `#37 · P5 one-shot
   holdout evaluation + final report · classifier denied agent merge —
   owner click needed; re-check §Holdout verdicts against protocol §5`. But
   `docs/final-report.md` (lines 3–7) now states "§Holdout FILLED... executed
   exactly per the pre-registered p5-holdout-protocol.md... The holdout is
   now sealed," and `control/status.md`/`docs/current-state.md` have said
   "holdout SPENT" throughout the 2026-07-13 research rounds. The review-queue
   file's own convention ("Remove a line when the review is done" —
   `docs/review-queue.md` preamble) was never followed for this entry. Not
   fixed by this audit (out of scope for a report-only PR; flagged for the
   coordinator or a follow-up session).

2. **`docs/current-state.md` "In flight" bullet for Round 6 undercounts its
   own landedness.** The bullet (added by PR #116 itself, commit `c0e6459`,
   diff confirmed via `git diff d929972 c0e6459`) describes the plan as
   "Research Round 6 (branch `claude/round-6-plan`, ORDER 014 items 1+3)"
   with no PR citation — but that is the very branch this commit merges;
   by the time it lands on `main` the plan is no longer "on a branch," it's
   merged (PR #116). Compare the Round 5 bullet immediately below it, which
   at least cites its PR number (`PR #110`). Minor — the only genuinely
   in-flight thing is item 2 (the separately claimed `claude/round-6-run`
   slice, confirmed active via `control/claims/2026-07-13-round-6-run.md`)
   — but the phrasing invites a reader to think the plan itself is still
   unmerged.

3. **`project.index.json` is an unfilled substrate-kit stub.** Its single
   `areas` entry is still the literal placeholder `"name": "example-area"`
   with every field empty. Grep confirms nothing in this repo's own code
   reads it (only `bootstrap.py`'s generic kit machinery references the
   filename); it looks like adoption never got round to authoring real
   areas (e.g. `research`, `control`, `data`) the way `docs/AGENT_ORIENTATION.md`
   already does by hand. Cosmetic — the orientation doc already carries this
   information — but it's dead scaffold that could confuse a future agent
   into thinking area-level context packs exist.

No secrets/credentials found (`grep -riE 'api[_-]?key|secret|password|token'`
across `src/`, `scripts/` — the one hit, `paper.py`'s `status_token()`, is a
ledger status-code accessor, not a credential).

## Open PRs — verified, and what happened during the audit

**The worklist's "0 open PRs" claim is correct at every point I checked.**
`list_pull_requests(state=open)` returned an empty list both at the start of
this audit (repo at commit `c9297a7`, 2026-07-13T22:55:07Z) and again after
resyncing to the new HEAD (`d6e3cf9`, three merges later). There was nothing
to merge, close, or leave open — no PR action was taken or needed.

**The "STALE heartbeat ~5h04m old" claim was accurate at the time it was
generated, and has since self-corrected.** At audit start, `control/status.md`
read `updated: 2026-07-13T16:26:35Z` (PR #112) — against the fleet-context
verification time of ~21:30–22:00Z that is almost exactly 5h04m, matching the
worklist precisely. **But the repo is not dark tonight — it is actively being
worked by a live coordinator session** executing ORDER 014 (the very worklist
this audit was asked to verify): while this audit was running, PRs `#113`
(22:16:46Z), `#114` (22:37:17Z), `#116` (22:51:12Z), and `#115` (22:54:40Z)
all merged to `main`, the last one only ~27 seconds before this audit's first
`list_pull_requests` call. `control/status.md` was refreshed to
`updated: 2026-07-13T22:46:50Z` as part of that work (PR #114/#115), so the
heartbeat is no longer stale by the time of this report. **Activity tonight:
ACTIVE**, not dark — per the global safety rules, nothing here was touched
beyond reading.

## Suggestions

1. **Investigate the main-branch push-CI gap** (see CI section) — confirm
   whether `08969bb` (2026-07-13T09:12:19Z) really is the last push-triggered
   `tests`/`substrate-gate` run on `main`, and if so, why (auto-merge actor
   identity? workflow trigger regression?). Low urgency since PR-level
   `pull_request` runs are still gating every merge, but a repo that believes
   it has post-merge CI and doesn't has a blind spot for anything that could
   only surface after a squash (e.g. a bad merge conflict resolution).
2. **Fold the review-queue "remove when done" discipline into the substrate
   gate**, the way `control/inbox.md`'s append-only-ness and
   `control/claims/`'s 72h staleness are already checker-enforced
   (`check_claims` per `control/claims/README.md`). A single stale
   review-queue line survived 3 days and ~40 PRs untouched — exactly the
   "friction → guard" pattern (checker > hook > manual habit) this fleet's
   sibling repos already apply. Centralizing this at the kit level
   (`substrate-kit`) would fix it fleet-wide, not just here.
3. **Consider a `project.index.json` pass** (or drop the file from
   adoption if it's genuinely unused) — an unfilled `example-area` stub
   sitting next to a hand-maintained, much richer `AGENT_ORIENTATION.md`
   is the kind of half-adopted scaffold that's easy to mistake for live
   config. Low priority; cosmetic only.
4. **Fleet-wide: the "PR merged N seconds before you checked" experience in
   this audit is a good argument for the fleet-manager's own dashboards to
   timestamp their `list_pull_requests`/heartbeat checks explicitly** (this
   report does, per the rule above) — several `control/status.md` entries in
   this repo already do this well (e.g. "Verified 2026-07-13T09:19Z via
   GitHub MCP"); worth holding every repo's audits to the same bar so a
   downstream fleet-wide roll-up can distinguish "confirmed dark" from
   "confirmed active 30 seconds ago."

## Notes on method

- All PR/commit/workflow-run facts in this report were checked live via the
  GitHub MCP tools (`list_pull_requests`, `list_commits`,
  `actions_list/list_workflow_runs`, `actions_get/get_workflow`) against
  `menno420/trading-strategy`, not read from any local doc as ground truth.
- The local clone was fast-forwarded from `c9297a7` to `d6e3cf9` mid-audit
  (`git fetch && git merge --ff-only`) once it became clear main had moved;
  all test/check runs in this report are against the post-fast-forward HEAD.
- No file outside this new report was modified. `control/status.md`,
  `control/inbox.md`, and `control/outbox.md` were read but not written —
  those are the coordinator seat's own instruments, not this audit's.
