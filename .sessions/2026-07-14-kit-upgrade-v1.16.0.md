# 2026-07-14 — kit upgrade v1.15.0 → v1.16.0

> **Status:** `complete`

- **📊 Model:** fable-5 · medium · mechanical refactor

## Scope

Distribution-wave upgrade of the vendored substrate-kit from v1.15.0 to
v1.16.0: staged the verified release asset as `bootstrap.py.new` +
`release.json`, ran the mandatory two-command upgrade (`upgrade` then
`upgrade --apply-docs`), passed `check --strict`, ran the repo verify line
(`python3 -m pytest -q`), landed via the live auto-merge enabler on green.

Rails (Q-0261.3): only bootstrap.py, `.substrate/**`, --apply-docs-applied
docs, the kit-owned gate, and the kit pin moved. control/status.md, hooks,
settings, product code untouched. Heartbeat `kit:` bump stays lane-owed.

## Close-out

- Asset sha256 `bba34e2102cbaf09394f39992f0501ea5cfd542d90301ef67e31a0854ca59170`
  (980,026 B) three-way verified (download == release.json == vendored file).
- `--apply-docs` applied: CONSTITUTION.md, docs/SKILLS.md, docs/ROUTINES.md,
  control/claims/README.md. Report carries the `## Applied (--apply-docs)`
  section.
- New v1.16.0 plant `docs/reading-path.md`: filled the three fleet slots
  (`fleet_dark_repos`, `fleet_siblings`, `fleet_status_command`) via
  `bootstrap answer` + `render --live` with verified fleet facts, and
  hand-merged the minimal reading-path wiring hunk into the diverged
  `docs/AGENT_ORIENTATION.md` (standing minimal-hunk precedent; the rest of
  that template delta stays lane-owed).
- Banked exactly one new `.substrate/backup/bootstrap-1.15.0.py` (sha256
  `25d22af9…`); all pre-existing banks byte-identical. Carve-out scan: ran,
  0 found on both live kit-owned workflows.
- Lane-owed (untouched, deltas preserved in `.substrate/upgrade-report.md`):
  diverged manual merges for `docs/collaboration-model.md`,
  `docs/AGENT_ORIENTATION.md` (remainder), `docs/CAPABILITIES.md`; heartbeat
  `kit:` line bump in control/status.md; pre-existing model-line advisories
  on 2026-07-13/14 sibling cards (taught-form fix belongs to those lanes).
- Verify: `python3 -m pytest -q` = 668 passed; `check --strict` green except
  the designed born-red hold this flip clears.

💡 Session idea: the v1.16.0 reading-path plant reds `check --strict` on
every adopter until the three fleet slots are answered — the kit could ship
a fleet-level answers file (or inherit answers from the adopters registry)
so a distribution worker doesn't hand-derive the same sibling/dark-repo
facts on each of ~10 repos.

⟲ Previous-session review: the previous kit session here (#75, v1.15.0)
landed clean via the enabler with a 3-diverged carve-out report and left the
heartbeat bump lane-owed — correct per rails, but the bump is now several
waves stale; graduating the chronic heartbeat bump into a fleet-manager
inbox ORDER would close the recurring drift class better than wave-report
prose.
