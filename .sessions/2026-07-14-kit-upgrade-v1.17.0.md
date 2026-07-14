# 2026-07-14 — kit upgrade v1.16.0 → v1.17.0

> **Status:** `in-progress`

- **📊 Model:** fable-5 · medium · mechanical refactor

## Scope

Distribution-wave upgrade of the vendored substrate-kit from v1.16.0 to
v1.17.0: stage the verified release asset as `bootstrap.py.new` +
`release.json`, run the mandatory two-command upgrade (`upgrade` then
`upgrade --apply-docs`), pass `check --strict`, land via the live
auto-merge enabler on green.

Rails (Q-0261.3): only bootstrap.py, `.substrate/**`, --apply-docs-applied
docs, and kit-owned workflows move. control/**, hooks, settings, product
code untouched. Heartbeat `kit:` bump stays lane-owed. The new v1.17.0
branch-sweep workflow stays STAGED-only (`.substrate/ci/branch-sweep.yml`)
— not hand-installed live.

## Close-out

(pending — flipped complete in the final commit)

💡 Session idea: the v1.17.0 branch-sweep workflow ships staged-only, so
the fleet's branch-litter cure (this repo still carries four spent
claude/kit-upgrade-v1.13–16 remote branches) stays dormant until a lane
runs `adopt --wire-enforcement`; the kit could emit a one-line
"staged-but-unwired enforcement" advisory in `check` so wiring debt is
visible in the heartbeat instead of only in the release notes.

⟲ Previous-session review: the v1.16.0 upgrade session here (#125) landed
clean via the enabler and correctly filled the three reading-path slots
in-wave, but its card's lane-owed list repeats the same diverged-doc
manual merges the v1.15.0 card listed — the lane never picks them up
between waves; graduating the standing diverged-doc merges into a
fleet-manager inbox ORDER would close that recurring class.
