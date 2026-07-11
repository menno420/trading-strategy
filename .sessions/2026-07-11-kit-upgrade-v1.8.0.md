# 2026-07-11 — kit upgrade: substrate-kit v1.7.1 → v1.8.0

> **Status:** `complete`

📊 Model: withheld per session policy · kit-distribution seat (owner directive Q-0261.3) · start 2026-07-11

💡 **Session idea:** The v1.8.0 upgrade report classifies `control/README.md` as `diverged` ("both the template and the doc moved — manual merge") and embeds the template delta, but the distribution seat can't act on it and a later repo session has to rediscover it inside a long report. Kit idea: emit diverged-doc deltas as a one-line checklist item in the report header (e.g. `⚠ 1 diverged doc awaiting manual merge: control/README.md`) so the repo's own next session sees the owed merge at a glance.

## What happened

Vendored-kit upgrade v1.7.1 → v1.8.0 via the canonical release-asset path:
sha256-verified `bootstrap.py` asset (`28c5dcb64b713dde8d64a513a9a1aa860b4a07bf17d832686f0009932dc89b9b`,
625,066 bytes, release tag 63c6b39, release run 29133041799) + `release.json`,
staged as `bootstrap.py.new`, `python3 bootstrap.py.new upgrade` (staging inputs self-cleaned).

## Work log

- Pre-upgrade tree at v1.7.1 (`KIT_VERSION = "1.7.1"`, `.substrate/state.json` `kit_version: "1.7.1"`); vendored dist sha256 `2aa4fedd…`.
- Backups: exactly ONE new bank, `.substrate/backup/bootstrap-1.7.1.py` (`2aa4fedd…`, byte-equal to the pre-upgrade vendored dist). Pre-existing banks byte-untouched: `bootstrap-1.1.0.py` `c12a2f55…`, `bootstrap-1.7.0.py` `00f4f4cd…` (hashes identical before/after). No collision-banking (sha8 names) needed — no name collision occurred.
- Carve-out scan (kit #156a): explicit section even at zero — `## Carve-out scan` → `carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found`.
- Gate regenerated kit-owned, byte-equal to staged `.substrate/ci/substrate-gate.yml`, now carrying the hold-tightening (#156c): a PR-ADDED card gets the FULL locked door when the same PR touches the gate workflow (venture-lab #14 fix) — exactly this PR's shape, so it sat red until this card flipped `complete`.
- Plants: `control/claims/README.md` (unified claims convention) and `scripts/env-setup.sh` (setup-script contract) — neither pre-existed, so skip-if-exists was not exercised; both planted fresh.
- Auto-merge enabler: staged under `.substrate/ci/auto-merge-enabler.yml` ONLY — this repo's enabler is not live (`.github/workflows/` still has just `substrate-gate.yml` + `tests.yml`), matching the "live only where already live" rule. Repo auto-merge toggle remains OFF (standing owner item).
- `control/inbox.md` + `control/status.md` untouched: sha256 identical before/after (`72715aaa…` / `03c81248…`), `git diff control/` clean apart from the planted `control/claims/`.
- `python3 bootstrap.py check --strict` → exit 0 (with this card complete).
- Local CI mirror: `python3 -m pytest -q` (Python 3.11, same as tests.yml) → 223 passed.

## Previous-session review

⟲ Previous-session review: the 2026-07-10 kit-upgrade-v1.7.1 session (#44) hash-logged its banked backup in the card — exactly the practice that let this session verify "pre-existing banks byte-untouched" in seconds instead of re-deriving provenance; it also correctly predicted the already-banked path. What it could have added: a one-line note that the repo's auto-merge toggle is OFF and branch deletion 403s, so each upgrade session stops rediscovering the merge/cleanup constraints. This card records both. Workflow improvement: repo-specific landing constraints (merge path, branch-deletion policy) deserve a durable home in `docs/CAPABILITIES.md` rather than session-card folklore — owed to the repo's own lane.

## Close-out

- Follow-ups owed to the repo's own lane (NOT done here, per distribution-seat hard scope): (1) manual merge of the diverged `control/README.md` template delta (see `.substrate/upgrade-report.md` § Template deltas); (2) update the `kit:` heartbeat line in `control/status.md` to v1.8.0; (3) record the merge/cleanup constraints in `docs/CAPABILITIES.md`.
- Branch left in place after merge (branch deletion 403s in this repo — known, not fought).
