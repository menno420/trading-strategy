# 2026-07-10 — kit upgrade: substrate-kit v1.7.0 → v1.7.1

> **Status:** `complete`

📊 Model: withheld per session policy · kit-distribution seat (owner directive Q-0261.3) · start 2026-07-10T22:04:01Z

💡 **Session idea:** The v1.7.1 adopter checklist asks each repo to update its `kit:` heartbeat line in `control/status.md` in the same session as the upgrade — but the distribution seat's hard scope forbids touching `control/`. Kit idea worth routing upstream: let `bootstrap upgrade` emit the exact ready-to-paste heartbeat line (`kit: v1.7.1 · check: green · engaged: yes`) into the upgrade report, so the repo's own next session (which IS allowed to write `control/status.md`) applies it mechanically instead of re-deriving it.

## What happened

Vendored-kit upgrade v1.7.0 → v1.7.1 via the canonical release-asset path
(sha256-verified `bootstrap.py` asset `2aa4fedd…` + `release.json`, staged as
`bootstrap.py.new`, `python3 bootstrap.py.new upgrade`, staging files
self-cleaned).

## Work log

- Pre-upgrade tree at v1.7.0: `bootstrap.py` header + `KIT_VERSION = "1.7.0"`, `substrate.config.json` `kit_version: "1.7.0"`; vendored dist sha256 `00f4f4cd…`.
- Pre-existing `.substrate/backup/bootstrap-1.7.0.py` (committed by PR #38 — the known v1.7.0 spurious-new-dist-bank bug, cited in the v1.7.1 release notes). Byte-equal to the pre-upgrade vendored dist (`00f4f4cd…`), so the fixed v1.7.1 upgrade recognized it: `archived: .substrate/backup/bootstrap-1.7.0.py (already banked)`. Exactly one banked dist for this upgrade; no spurious `bootstrap-1.7.1.py`.
- `.github/workflows/substrate-gate.yml` regenerated kit-owned, byte-equal to staged `.substrate/ci/substrate-gate.yml`, now carrying the inbox append-only gate (`--inbox-base`, line 78).
- Carve-out detector: zero carve-outs (no ⚠️ section in `.substrate/upgrade-report.md`, no `substrate-gate.pre-regen-*.yml` banked) — the live gate was pristine kit-generated from #38.
- `python3 bootstrap.py check --strict` → exit 0.
- Local CI mirror: `python3 -m pytest -q` (Python 3.11, same as tests.yml) → 154 passed.
- Changed files: all kit-owned (`bootstrap.py`, `substrate.config.json`, `.github/workflows/substrate-gate.yml`, `.substrate/**`) + this session card. `control/` untouched.

## Previous-session review

The 2026-07-10 kit-upgrade-v1.7.0 session (#38) landed a clean 1.1.0→1.7.0 hop and its card documented the merge path well; what it could not have avoided was banking the spurious `bootstrap-1.7.0.py` copy — that was the kit's own upgrade bug, since fixed in exactly this release. Workflow improvement it surfaces: an upgrade session should hash-log the banked backup(s) in its card (as this one now does), so the next upgrade can distinguish "already banked, byte-equal" from real drift in seconds.

## Close-out

- ⚑ Owner/next-session item (out of this seat's scope): update the `kit:` line in `control/status.md` to `kit: v1.7.1 · check: green · engaged: yes` (adopter checklist step 4); the repo-level "Allow auto-merge" toggle remains OFF (standing ⚑ item — not touched).
- Landing per `docs/collaboration-model.md`: REST squash on green, this PR (#44).
