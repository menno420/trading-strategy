# 2026-07-10 — substrate-kit upgrade v1.1.0 → v1.7.0

> **Status:** `in-progress`

## What is about to happen

Distribution-wave kit upgrade (kit-lab v1.7.0 wave, Q-0261.3 scope): replace the
vendored `bootstrap.py` (v1.1.0 → v1.7.0, release asset sha256-verified), run
`bootstrap.py.new upgrade` (+ `--apply-docs` for consumer-untouched planted docs),
refresh the live `.github/workflows/substrate-gate.yml` from the regenerated staged
copy, verify `check --strict` green, ship as one PR. Scope fence: kit-owned files
only — no lane-owned content (control/, claims of other lanes, existing session
cards, domain code) is touched.
