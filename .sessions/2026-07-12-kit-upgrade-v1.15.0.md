# Session 2026-07-12 — substrate-kit upgrade v1.14.0 → v1.15.0

> **Status:** `complete`

Intent: upgrade the vendored substrate-kit from v1.14.0 to v1.15.0 via the release-asset path, sha256 three-way verified (asset = release.json = kit dist @ eaf4f23, `25d22af9…650e`, 828,825 bytes). Distribution only — no lane domain work.

- **📊 Model:** fable-5

## What shipped

- Vendored `bootstrap.py` v1.14.0 → v1.15.0; sha256 three-way verified (asset = release.json field = `git show eaf4f23:dist/bootstrap.py`, `25d22af9d9d81b2a7dc6d8d500234b6aa0f3f1c6a0400284ce2381baaeac650e`, 828,825 bytes).
- Previous dist banked to `.substrate/backup/bootstrap-1.14.0.py` — byte-identical to origin/main's `bootstrap.py`; pre-existing banks untouched.
- `upgrade --apply-docs` applied 2 template-improved docs: `CONSTITUTION.md`, `docs/SKILLS.md`.
- Newly planted: `docs/ROUTINES.md` and `docs/seat-digest.md` (seat-digest refresh reported "already current — nothing to refresh"; the file itself was newly created by the upgrade).
- Capability-seed: `docs/CAPABILITIES.md` unchanged (template identical across versions) — no refresh this release.
- Diverged (lane-owed manual merges, template deltas verbatim in the PR body + `.substrate/upgrade-report.md`): `docs/AGENT_ORIENTATION.md` (preflight hard-reset section — only the minimal ROUTINES.md wiring hunk was hand-merged here, clearing the `[reachable]` orphan red, same class as v1.13.0), `control/README.md` (plain-`kit:`-token grammar + version-truth sections), `control/status.md` (plain-token parse warning + self-report note; distribution never touches it).
- Carve-out scans: `substrate-gate.yml` 0 found; `auto-merge-enabler.yml` 0 found — both kept, already current.
- Verify: `python3 -m pytest -q` 229 passed; `python3 bootstrap.py check --strict` green except this card's own designed born-red hold. Pre-existing never-exit-affecting advisory: `claims-legacy-location` (known since v1.14.0; lane task already ideated).
- Outstanding actions (all lane-owed): heartbeat `kit:` bump in `control/status.md`; the three diverged-doc manual merges above; the claims-dir decision (pin vs migrate).

## Session enders

- 💡 **Session idea:** the seat-digest refresh printed "already current — nothing to refresh" while simultaneously *creating* `docs/seat-digest.md` for the first time in this repo — the message conflates "no delta vs template" with "file already existed". A tiny kit patch making the plant-vs-refresh distinction explicit in the log line ("planted new" vs "already current") would spare every future distribution session the double-take and the extra verification step; worth a line in the kit repo's intake.
- ⟲ **Previous-session review:** the v1.14.0 upgrade session's card was a strong template (this session reused its structure) and its explicit "outstanding actions" line carried forward cleanly. Its one gap: it flagged the AGENT_ORIENTATION merge-decision discrepancy between v1.13.0 and v1.14.0 handling but routed it nowhere durable — this session benefited only because the playbook itself now encodes the rule ("hand-merge only the minimal wiring hunk, rest lane-owed"). Improvement: when a review remark identifies a decision-rule gap, route it into the upgrade-distribution skill/playbook the same session instead of leaving it as card prose.
