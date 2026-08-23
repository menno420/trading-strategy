# 2026-08-23 — the pre-archive README notice, written while this repo can still be written to

> **Status:** `complete` — branch `claude/pre-archive-readme-notice`, opened against `main` in this
> repository. Flipped after `python3 bootstrap.py check --strict` returned a
> real exit 0 on this tree, read directly and never after a pipe.

- **📊 Model:** opus-5 · high · docs-only

## 💡 Session idea

This repository is **archive-bound** under the estate's 2026-08-22 disposition
pass ([`fleet-manager` § 2](https://github.com/menno420/fleet-manager/blob/main/docs/planning/2026-08-22-repo-dispositions.md)),
and the owner's go-ahead for the nine ungated rows is recorded there. An
archived repository is **read-only**, and GitHub's own archiving guidance
recommends updating the README and description *before* archiving — so anything
this repo still needs said has to be said now.

What this repo still needed said is that the research **concluded** — 11 rounds,
5,940 configurations, 0 promoted, holdout spent. The README below reads as an
active lab soliciting work. The null result is the deliverable, and the notice
says so at the top rather than three documents in.

Scope: the README notice only. No code, no behaviour, no dependency changes.
The archive itself is performed from the hub in the same pass.

## previous-session review

The previous card (`2026-07-21-final-closeout.md`) closed this repository out at
the end of the autonomous-Projects program, with the holdout spent and nothing
promoted. Nothing it recorded is contradicted here; this notice simply moves
that conclusion to where a reader meets it first.

## What landed

One notice at the top of `README.md`, stating plainly that the repository is
archived, unmaintained and read-only — and, because the asymmetry is the whole
reason one line of owner approval was enough, that **archiving blocks writes and
never reads**: the repo stays public and clonable, every existing link keeps
resolving, and the archive is reversible. The GitHub description is updated to
match, so the state is visible without opening the repo.

## What was checked, not assumed

- **The README was read before it was written to.** The notice is placed after
  the existing H1 so the file still opens with its own title.
- **The archive's read-safety is sourced, not inferred.** GitHub's archiving
  documentation states an archived repository's contents become read-only while
  it stays publicly visible and forkable, and that archived repositories can be
  unarchived. What is *not* stated there — and so is not claimed here — is
  anything about `git+https://…` installs or scheduled Actions; those are
  measured separately from the hub in this same pass.

## Verify

`python3 bootstrap.py check --strict` → **exit 0**, read directly, never after a
pipe.
