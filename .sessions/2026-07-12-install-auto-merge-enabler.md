# 2026-07-12 — install substrate-kit auto-merge enabler (CI + owner-action doc)

> **Status:** `in-progress` — CI/docs-only slice. Heartbeat first (this card,
> born-red, first commit), then wire the kit's auto-merge enabler workflow
> byte-identically into `.github/workflows/` and add the six-field
> OWNER-ACTION doc that records the two one-time repo settings the enabler
> needs before it can arm. NO merge action taken by this session (no arm, no
> auto-merge toggle, no merge). RESEARCH-ONLY RAIL held: zero `data/**`
> reads, zero backtests, zero bars loaded, holdout untouched, paper lane
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

<!-- filled as the deliberate LAST step; badge flips to complete then -->
