# 2026-07-10 — kit upgrade: substrate-kit v1.7.0 → v1.7.1

> **Status:** `in-progress`

📊 Model: withheld per session policy · kit-distribution seat (owner directive Q-0261.3) · start 2026-07-10T22:04:01Z

## What is about to happen

Vendored-kit upgrade v1.7.0 → v1.7.1 via the canonical release-asset path:
download `bootstrap.py` + `release.json` from the substrate-kit v1.7.1 release,
sha256-verify the asset, stage as `bootstrap.py.new`, run
`python3 bootstrap.py.new upgrade`, verify (`bootstrap.py check --strict`,
kit-owned gate regeneration, backup banking, carve-out report), then land this
PR per the repo's documented REST-squash-on-green path
(`docs/collaboration-model.md` § "Arm auto-merge at creation; REST squash is
the path that fires"). Kit-owned files only; `control/` untouched.

## Work log

- (filled at close-out)
