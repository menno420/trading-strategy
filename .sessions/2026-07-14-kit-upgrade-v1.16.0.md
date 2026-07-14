# 2026-07-14 — kit upgrade v1.15.0 → v1.16.0

> **Status:** `in-progress`

📊 Model: fable-5 (distribution-wave worker seat)

## Scope

Distribution-wave upgrade of the vendored substrate-kit from v1.15.0 to
v1.16.0: stage the verified release asset as `bootstrap.py.new` +
`release.json`, run the mandatory two-command upgrade (`upgrade` then
`upgrade --apply-docs`), pass `check --strict`, run the repo verify line
(`python3 -m pytest -q`), and land via the live auto-merge enabler on green.

Rails (Q-0261.3): only bootstrap.py, `.substrate/**`, --apply-docs-applied
docs, the staged/live gate, and the kit pin move. control/**, hooks,
settings, product code untouched. Heartbeat `kit:` bump stays lane-owed.

## Close-out

_(pending)_
