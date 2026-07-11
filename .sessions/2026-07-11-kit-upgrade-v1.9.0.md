# 2026-07-11 — kit upgrade: substrate-kit v1.8.0 → v1.9.0

> **Status:** `complete`

📊 Model: fable-5 · kit-distribution seat (owner directive Q-0261.3) · start 2026-07-11

💡 **Session idea:** The upgrade emitted no `required_context` validation advisory anywhere (upgrade output, report, `check`), so a distribution seat can't tell "validated clean" from "validation never ran". Kit idea: have `upgrade` print an explicit one-liner either way (`required_context: validated, 0 findings` / `required_context: not applicable`) — absence-of-signal is ambiguous evidence, and every seat in this wave was asked to record it.

## What happened

Vendored-kit upgrade v1.8.0 → v1.9.0 via the canonical release-asset path:
sha256-verified `bootstrap.py` asset
(`55181082c796657c8e5e14750d248cea2df9e69a9aa896dd8a8c7f1adfb9cc90`) +
`release.json`, staged as `bootstrap.py.new`, `python3 bootstrap.py.new
upgrade` (staging inputs self-cleaned). Kit upgrade ONLY — no domain work;
`control/inbox.md` / `control/status.md` untouched.

## Work log

- Pre-upgrade tree at v1.8.0 (vendored dist sha256 `28c5dcb6…`, matching the expected v1.8.0 dist).
- Backups: exactly ONE new bank, `.substrate/backup/bootstrap-1.8.0.py` (`28c5dcb64b713dde8d64a513a9a1aa860b4a07bf17d832686f0009932dc89b9b`, byte-equal to the pre-upgrade vendored dist). Pre-existing banks byte-untouched before/after: `bootstrap-1.1.0.py` `c12a2f55…`, `bootstrap-1.7.0.py` `00f4f4cd…`, `bootstrap-1.7.1.py` `2aa4fedd…`.
- Plants (v1.9.0 additions): root `.ignore` + `.gitattributes` planted fresh (neither pre-existed; append-only path not exercised). CLAUDE.md search-hygiene note is **staged-only** (`.substrate/claude/CLAUDE.md` § "Kit machinery — search hygiene"; no live `.claude/CLAUDE.md` in this repo). `.sessions/README.md` host file **kept** — it already carries the model-attribution doctrine (ORDER 009, PR #53). SessionStart handoff-push confirmed: `bootstrap.py hook sessionstart` renders "## Handoff — the previous session's trail (pushed; read before re-deriving)" pointing at the newest card.
- Gate regenerated kit-owned, byte-equal to staged `.substrate/ci/substrate-gate.yml`; carries the `check --strict … --added-card` grammar lint on the born-red advisory lane.
- Carve-out scan: `- carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found` (explicit section at zero).
- `control/README.md` reclassified from v1.8.0's `diverged` to `consumer-edited` — "template unchanged — consumer-owned, nothing to apply"; the v1.8.0 owed manual merge is no longer flagged by the kit.
- `required_context` validation advisory: NOT emitted (not in upgrade output, report, or `check` output).
- `control/inbox.md` + `control/status.md` untouched: `git diff control/` clean apart from this session's claim file.
- `python3 bootstrap.py check --strict` with card in-progress → exit 1, verbatim "check: HOLD (by design): session card … declares an in-progress Status — the born-red session gate holds the merge red until the card flips complete. This red is the designed hold, not a defect; nothing to investigate." Nothing else red.
- CI first-exercise data point (v1.9.0 gate): on the in-progress card the gate took the **locked-door** lane (card ADDED + PR touches the gate workflow), printed the HOLD-by-design line, and fired the `::notice` annotation ("Designed hold — not a CI failure to investigate"). Gate run 29141244043.
- Local CI mirror: `python3 -m pytest -q` (Python 3.11, same as tests.yml) → 223 passed.

## Previous-session review

⟲ Previous-session review: the 2026-07-11 kit-upgrade-v1.8.0 session did exactly what it promised in its own review — it recorded the repo's landing constraints (auto-merge toggle OFF, branch deletion 403s) in the card, which let this session skip rediscovery entirely and go straight to REST squash-merge. What it could have done better: its close-out flagged the diverged `control/README.md` manual merge as lane-owed, but v1.9.0 now classifies that doc `consumer-edited` (template unchanged), so the flag aged out without a pointer to re-check — a lane-owed item should name the condition under which it expires. Workflow improvement: lane-owed lists deserve "verify still owed at next kit upgrade" as a standing line, since template reclassification can retire them silently.

## Close-out

- Follow-ups owed to the repo's own lane (NOT done here, per distribution-seat hard scope): (1) update the `kit:` heartbeat line in `control/status.md` to v1.9.0; (2) decide whether to adopt the staged CLAUDE.md search-hygiene note live; (3) the v1.8.0-owed `control/README.md` manual merge appears retired by the v1.9.0 reclassification (`consumer-edited`) — repo lane should confirm and drop it from its owed list; (4) still no `docs/CAPABILITIES.md` entry for the merge/cleanup constraints (owed since the v1.8.0 card).
- Branch left in place after merge (branch deletion 403s in this repo — known, attempt once, don't fight it).
