# 2026-07-12 — install substrate-kit auto-merge enabler (CI + owner-action doc)

> **Status:** `complete` — CI/docs-only slice, one PR (#65): the kit's
> auto-merge enabler wired BYTE-IDENTICAL into
> `.github/workflows/auto-merge-enabler.yml` (sha256 `64f9db41…c84`), a
> six-field OWNER-ACTION doc at `docs/operations/auto-merge-guards.md`, and a
> one-bullet reachability link from `docs/current-state.md`. NO merge action
> taken (no arm, no auto-merge toggle, no merge); PR opened READY and parks
> READY+green until the owner flips "Allow auto-merge". RESEARCH-ONLY RAIL
> held: zero `data/**` reads, zero backtests, zero bars loaded, holdout
> untouched, paper lane untouched; PR #64 / its branch / `control/status.md`
> untouched.

📊 Model: opus-4.8 · install-auto-merge-enabler lane (fired worker session) · start 2026-07-12T00:00:27Z

💡 **Session idea:** install the substrate-kit auto-merge enabler so that
green `claude/*` agent PRs self-land once the owner flips two repo settings.
Two artifacts: (1) copy `.substrate/ci/auto-merge-enabler.yml` →
`.github/workflows/auto-merge-enabler.yml` BYTE-IDENTICAL (manual `cp`, not
`bootstrap.py adopt --wire-enforcement`, which has overreached elsewhere and
had to be reverted); the enabler arms native auto-merge only on `claude/*`
head branches and carries a refuse-to-arm guard that counts required
status-check CONTEXTS and refuses on zero (so arming can never merge a PR
with nothing to wait for). (2) A six-field OWNER-ACTION doc
(`docs/operations/auto-merge-guards.md`, the path the enabler itself points
at) recording the two one-time owner settings — "Allow auto-merge" ON and a
`main` ruleset REQUIRING the `substrate-gate` check — plus what it unblocks,
the verified-when, and secret NAMES only. The PR opens READY; with the
"Allow auto-merge" toggle OFF it will park READY+green, which is EXPECTED —
this slice installs the enabler, it does not flip the owner settings.

## Previous-session review

⟲ Previous-session review: the ORDER 009 model-attribution session (PR #52,
fable-5) landed the lane's first real family-level `📊 Model:` line and
retired the "withheld" null convention in the card-convention docs — this
card follows that convention with a real family name (`opus-4.8`). The
2026-07-11 archive-prep close-out (`docs/retro/archive-ready-2026-07-11.md`)
recorded the standing six-field ⚑ owner-action form and, as ⚑ (c), the
"Allow auto-merge" toggle being OFF — the exact setting this enabler needs.
This slice turns that flagged toggle into an installed, guarded mechanism
plus a durable OWNER-ACTION doc, without spending or touching any research
or paper-lane state. What it could have added: a single home for the
auto-merge landing guards — this session creates it at
`docs/operations/auto-merge-guards.md`.

## Work log

- 2026-07-12T00:00:27Z — heartbeat: fresh clone hard-synced to origin/main
  HEAD `ea22323` (verified against `git ls-remote origin main`). Branch
  `claude/install-auto-merge-enabler`; this card as first commit (born-red).
  Read `control/inbox.md` (read-only, never edited): newest order is 010, no
  order newer than 010. RESEARCH-ONLY RAIL: no `data/**` reads, no
  backtests, no paper-lane changes; PR #64 / its branch / `control/status.md`
  left untouched.

## Close-out

**Done:** ORDER-scope slice in full, one PR (#65,
`claude/install-auto-merge-enabler`) —

1. `.github/workflows/auto-merge-enabler.yml` wired **byte-identical** from
   `.substrate/ci/auto-merge-enabler.yml` via manual `cp` (not
   `bootstrap.py adopt --wire-enforcement`) — `sha256sum` on both files
   matched: `64f9db4122c69631ab01d097a4f46ff49eac5d5d42728429e27543c45fc64c84`.
   Confirmed the enabler arms native auto-merge only on `claude/*` head
   branches (job `if`, `startsWith(github.head_ref, 'claude/')`) and refuses
   to arm when the base branch requires zero status-check contexts (the
   `rules` step counts contexts; every arming step gates on
   `required != '0'`).
2. `docs/operations/auto-merge-guards.md` — six-field OWNER-ACTION doc
   (what / why / exact click / where / blocking? / fallback) covering owner
   action 1 ("Allow auto-merge" ON — existing status ⚑ (c)) and owner
   action 2 (a `main` ruleset REQUIRING `substrate-gate`), plus
   what-it-unblocks (weekly grading PRs from 2026-07-17 self-land),
   VERIFIED-WHEN (next green `claude/*` PR merges itself), and secret NAMES
   only (`ROUTINE_PAT`, optional — no values anywhere).
3. `docs/current-state.md` — one "In flight" bullet linking the new doc
   (satisfies the kit reachability check).

**Verify:** `python3 bootstrap.py check --strict` — all non-session-card
findings clean after adding the `owner-guidance` badge + the reachability
link; the sole remaining finding while the card was born-red was the
by-design HOLD on this card, which this final commit clears. PR #65 opened
READY (not draft); with "Allow auto-merge" OFF it parks READY+green —
EXPECTED, stated in the PR body. No merge action taken by this session.

**Integrity audit:** zero `data/**` reads, zero market-data access, no
ledger rows, holdout untouched, `control/inbox.md` + `control/status.md`
byte-untouched, PR #64 / its branch untouched. Timestamps from `date -u`.

**Next (guard recipe):** none owed by this slice. Landing depends on the two
one-time owner settings in `docs/operations/auto-merge-guards.md`; until
"Allow auto-merge" is ON the enabler is inert and PRs merge via the existing
merge-on-green path.

Session end: badge flips to `complete` in this final commit.
