# 2026-07-16 — Main CI triggers: schedule + workflow_dispatch on both workflows

> **Status:** `in-progress`

- **📊 Model:** Fable · medium effort · CI-plumbing task-class

⚑ Scope (claimed, `control/claims/2026-07-16-main-ci-triggers.md`, branch
`claude/main-ci-triggers`): close the GITHUB_TOKEN-merge → no-push-CI gap.
Main has had NO push-triggered CI run since `7d6aa67` (2026-07-14) because
the auto-merge enabler merges with `GITHUB_TOKEN`, whose pushes never fire
`on: push` workflows — every later main SHA is only green-by-proxy via its
PR-head checks. Fix: add `schedule:` (cron `23 */6 * * *`, every 6h at an
off-minute) AND `workflow_dispatch:` to the `on:` blocks of BOTH
`.github/workflows/tests.yml` and `.github/workflows/substrate-gate.yml`.
Minimal diff — only the `on:` blocks change; existing triggers preserved
byte-identical. Provenance: coordinator dispatch per the 2026-07-16
post-reboot-restamp session card's 💡 fix proposal. Rails: pure CI
plumbing — no strategy/executor/broker code, no secrets/PATs, no trigger
create/delete/fire, `control/inbox.md` byte-untouched.

## Plan

1. Claim + this born-red card as first commit; push; open READY PR.
2. Read both workflow files fully; add the two triggers to each `on:`
   block; check event-context assumptions (pull_request-gated steps) and
   the substrate-gate born-red HOLD behavior on schedule runs against main
   (all cards on main are flipped `complete`, so it should pass).
3. Validate YAML (`yaml.safe_load` both files); actionlint if available.
4. Carve-out check: read the auto-merge enabler workflow at main HEAD and
   determine whether PRs touching `.github/workflows/**` are excluded from
   auto-merge; cite file@SHA + lines.
5. Flip this card `complete` with evidence; drive PR to terminal state.

## Close-out

[[fill: what shipped — files, PR#, SHAs]]
[[fill: verification evidence — YAML validation output, CI run links]]
[[fill: previous-session review]]
[[fill: session idea]]
