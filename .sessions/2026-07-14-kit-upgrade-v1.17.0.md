# 2026-07-14 — kit upgrade v1.16.0 → v1.17.0

> **Status:** `complete`

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

- Asset sha256 `0d08b8aa9efc30178cf8e8befcfa28dd2b65e02106cc9ba6d520133017955521`
  (995,446 B) three-way verified (expected == downloaded == release.json /
  release-API digest).
- Two-command upgrade run. The `--apply-docs` pass was a legitimate no-op
  this release — verbatim: `upgrade: apply-docs: no template-improved docs
  to apply — every planted doc is already current or consumer-owned.`
  (every v1.17.0 planted-doc template is byte-identical to v1.16.0, so the
  report carries no `## Applied (--apply-docs)` section).
- Carve-out scan: ran, 0 found on both live kit-owned workflows; all three
  live `.github/workflows/*` byte-identical before/after (sha256-verified).
- Banked exactly one new `.substrate/backup/bootstrap-1.16.0.py` (sha256
  `bba34e21…` = the v1.16.0 asset); pre-existing banks untouched.
- New staged-only plant: `.substrate/ci/branch-sweep.yml` + `branch_sweep`
  config knob (patterns claude/* · codex/* · bot/*, cron `17 3 * * *`) —
  NOT wired live per wave doctrine.
- Verify: `python3 -m pytest -q` = 668 passed; `check --strict` green except
  the designed born-red hold this flip clears (sibling-card model-line
  advisories pre-existing, lane-owed).
- Claim `control/claims/2026-07-14-kit-upgrade-v1.17.0.md` deleted in this
  flip commit. Landing via the live auto-merge enabler on green (PR #126);
  no manual merge by this session.

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
