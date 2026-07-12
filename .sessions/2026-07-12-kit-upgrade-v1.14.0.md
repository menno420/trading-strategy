# Session 2026-07-12 — substrate-kit upgrade v1.13.0 → v1.14.0

> **Status:** `complete`

Intent: upgrade the vendored substrate-kit from v1.13.0 to v1.14.0 via the release-asset path, sha256 three-way verified (asset = release.json = kit dist, `47c1b8b9…e581`, 779,399 bytes). Distribution only — no lane domain work.

- **📊 Model:** Fable 5

## What shipped

- Vendored `bootstrap.py` v1.13.0 → v1.14.0; sha256 three-way verified (asset = release.json field = kit dist, `47c1b8b954be2f587d88f7ed5923870883deab88a8fa7fbf2bb755decc2ee581`, 779,399 bytes).
- Previous dist banked to `.substrate/backup/bootstrap-1.13.0.py` (bank verified in-tree).
- `upgrade --apply-docs` applied 4 template-improved docs: `CONSTITUTION.md`, `docs/question-router.md`, `docs/CAPABILITIES.md`, `docs/SKILLS.md`.
- Capability-seed: `docs/CAPABILITIES.md` consumer-untouched — whole file refreshed via `--apply-docs`; no fence-only hand-adopt needed.
- Diverged (both template and doc moved — lane-owed manual merges, template deltas recorded verbatim in the PR body and `.substrate/upgrade-report.md`): `docs/collaboration-model.md` (owner-assist output standard paragraph), `control/README.md` (owner-assist output standard section + `RISK:` field in OWNER-ACTION block).
- Carve-out scans: `substrate-gate.yml` 0 found; `auto-merge-enabler.yml` 0 found — both kept, already current.
- Verify: `python3 -m pytest -q` 229 passed; `python3 bootstrap.py check --strict` green except this card's own designed born-red hold. One never-exit-affecting advisory: `claims-legacy-location` (this repo's claims live in `claims/` per its own `claims/README.md`; kit convention is now `control/claims/`).
- Outstanding actions: the two diverged-doc manual merges above are lane-owed (owner-assist output standard); nothing else outstanding.

## Session enders

- 💡 **Session idea:** the `claims-legacy-location` advisory fires on every check while this repo's own `claims/README.md` still documents `claims/` as the canonical location — the two sources now disagree. A tiny lane task: either pin `claims_dir` in `substrate.config.json` (deliberate legacy) or migrate `claims/` → `control/claims/` and update the README, so the advisory stops nagging every session with no decision attached.
- ⟲ **Previous-session review:** the v1.13.0 upgrade session (card `2026-07-12-kit-v1130-upgrade.md`) asked for reports to end with an explicit "outstanding actions: none / list" line — this session adopted that (see above), which proves the review loop compounds. One miss it left: it hand-merged the diverged `docs/AGENT_ORIENTATION.md` in-session but didn't note the decision rule for when distribution sessions merge diverged docs vs. leave them lane-owed; this session followed the playbook's "lane-owed, record verbatim" rule, and the discrepancy between the two sessions' handling would be worth one line in the upgrade-distribution skill.
