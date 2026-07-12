# Auto-merge enabler — owner actions & guards

> **Status:** `owner-guidance` — two one-time repo settings the owner must
> flip before the installed auto-merge enabler can arm.

The substrate-kit auto-merge enabler is installed as
`.github/workflows/auto-merge-enabler.yml` (KIT-OWNED, wired byte-identical
from `.substrate/ci/auto-merge-enabler.yml`). It arms GitHub-native
auto-merge (squash) on agent PRs at open, so a green `claude/*` PR merges
itself the moment the required check goes green — no manual merge click.

The enabler is **INERT until two one-time repo settings exist**. It is
deliberately conservative: its refuse-to-arm guard counts required
status-check *contexts* on the base branch and **refuses to arm on zero**,
so arming can never merge a PR with nothing to wait for. Head-branch filter:
it arms **only `claude/*`** head branches from this repo (not forks, not
drafts), and never arms a PR carrying the `do-not-automerge` label
(re-checked fresh against the API to defeat the stale-payload race).

Until action 1 is done, PRs park **READY + green** with auto-merge simply
never armed — a safe no-op, not a failure. This is the current expected
state.

## ⚑ Open owner actions (six-field form: what / why / exact click / where / blocking? / fallback)

### Owner action 1 — ALLOW AUTO-MERGE TOGGLE (existing status ⚑ (c))

- **what:** tick "Allow auto-merge" for the repository.
- **why:** GitHub-native auto-merge cannot be armed on any PR while the repo
  toggle is off; with it off, every merge needs an agent to poll-and-merge.
  This is the same item already flagged as ⚑ (c) in `control/status.md` and
  `docs/retro/archive-ready-2026-07-11.md`.
- **exact click:** Settings → General → Pull Requests → "Allow auto-merge"
  → ON.
- **where:** GitHub → menno420/trading-strategy → Settings → General.
- **blocking?:** no — PRs still land via REST/MCP squash-merge on green
  (the path every merge to date has used); this only removes the manual
  merge step.
- **fallback:** continue merging green PRs manually / via the existing
  merge-on-green path until the toggle is on.

### Owner action 2 — REQUIRE THE `substrate-gate` CHECK ON `main`

- **what:** create or confirm a ruleset on the `main` branch that REQUIRES
  the `substrate-gate` status check as a required status context.
- **why:** the enabler's guard refuses to arm when the base branch requires
  **zero** status-check contexts — with no required check, arming would
  merge a PR instantly. Requiring `substrate-gate` is what makes an armed
  PR wait for CI to pass before it self-lands, so this is the setting that
  makes auto-merge safe rather than instant.
- **exact click:** Settings → Rules → Rulesets → New branch ruleset (or
  edit the existing `main` ruleset) → target `main` → enable "Require
  status checks to pass" → add `substrate-gate` → save.
- **where:** GitHub → menno420/trading-strategy → Settings → Rules →
  Rulesets.
- **blocking?:** no — with action 1 off the enabler stays inert anyway; but
  this must be in place *before* action 1 for arming to be safe.
- **fallback:** leave `main` without a required check and keep auto-merge
  off (action 1 off); the enabler stays inert and refuses to arm.

## What it unblocks

Once BOTH settings are on, green `claude/*` PRs self-land with no merge
click — e.g. the weekly paper-lane grading PRs due from 2026-07-17
(protocol §6–§7) need no manual merge, closing the succession gap where a
green PR could otherwise sit unmerged with no executor to click merge.

## VERIFIED-WHEN

The mechanism is verified working when the **next green `claude/*` PR merges
itself** — armed automatically at open, then squash-merged by GitHub the
moment `substrate-gate` reports green, with no human or agent merge action.

## Secrets (NAMES only — never values)

The enabler uses at most one optional repo secret:

- `ROUTINE_PAT` (OPTIONAL) — a fine-grained PAT with **Pull requests: write**
  and **Contents: write**. If present, the eventual merge attributes to a
  real user; if absent, the workflow falls back to the built-in
  `GITHUB_TOKEN`. No secret VALUES belong in this repo or any doc — env var
  NAMES only.
