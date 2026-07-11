# 2026-07-11 — kit upgrade: substrate-kit v1.9.0 → v1.10.0

> **Status:** `complete`

📊 Model: fable-5 · kit-distribution seat (owner directive Q-0261.3) · start 2026-07-11

💡 **Session idea:** The gate's locked-door log prints the in-run
`simulate-added-card` verdict *before* the HOLD banner, with no blank line or
`---` between them — in a red CI log the advisory "would HOLD" line reads like
part of the failure. Kit idea: prefix the simulation block with an explicit
`(advisory — not this run's verdict)` header line so a human scanning a red
log can't mistake the simulation for the finding. Cheap, print-only, and the
confusion is real: this session had to read the source to confirm which line
was load-bearing (gate run 29144119497).

## What happened

Vendored-kit upgrade v1.9.0 → v1.10.0 via the canonical release-asset path:
sha256-verified `bootstrap.py` asset
(`ba69fc5cf21619cc85e4c733ebe3d9eda8803e678f810fcc39b94d60c2f3b5a4`, tag
v1.10.0 @ `1b5db16`, release run 29142780212) + `release.json`, staged as
`bootstrap.py.new`, `python3 bootstrap.py.new upgrade` (staging inputs
self-cleaned). Kit upgrade ONLY — no domain work; `control/inbox.md` /
`control/status.md` untouched. Last repo of the v1.10.0 wave (fleet-manager
#69 and superbot-games #42 already merged).

## Work log

- Pre-upgrade tree at v1.9.0 (vendored dist sha256 `55181082…`, matching the expected v1.9.0 dist).
- Backups: exactly ONE new bank, `.substrate/backup/bootstrap-1.9.0.py` (`55181082c796657c8e5e14750d248cea2df9e69a9aa896dd8a8c7f1adfb9cc90`, byte-equal to the pre-upgrade vendored dist). Pre-existing banks byte-untouched before/after: `bootstrap-1.1.0.py` `c12a2f55…`, `bootstrap-1.7.0.py` `00f4f4cd…`, `bootstrap-1.7.1.py` `2aa4fedd…`, `bootstrap-1.8.0.py` `28c5dcb6…`.
- v1.10.0 loophole fix live in the regenerated gate: `session-card-hold` — an ADDED in-progress card HOLDs even on card-only diffs; gate-touching PRs run the in-run `--simulate-added-card` on the locked-door lane.
- Retroactive model-attribution doctrine APPENDED to the pre-existing `.sessions/README.md` — old file verified as a byte-exact prefix of the new (1566 → 2047 bytes, +481, provenance-marked ORDER 012 block). Second live exercise of the v1.10.0 append path (first: superbot-games #42).
- Carve-out scan: `- carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found` (explicit section intact in `.substrate/upgrade-report.md`).
- `tests.yml` byte-untouched; zero pytest refs in the regenerated gate. Local CI mirror: `python3 -m pytest -q` (Python 3.11, same as tests.yml) → 223 passed.
- `check --strict` pre-flip → exit 1, verbatim "check: HOLD (by design): session card … declares an in-progress Status — the born-red session gate holds the merge red until the card flips complete. This red is the designed hold, not a defect; nothing to investigate." Nothing else red.
- `check --simulate-added-card <this card>` → exit 0, verbatim "check: simulate-added-card … — the added-card lane would HOLD (born-red: the card declares an in-progress/drafted Status; the gate would stay red until it flips complete)." + "check: simulation is advisory-only — it never affects this run's exit code."
- CI live-fire: card-only first commit `21e1a77` rode the OLD (v1.9.0) gate green one last time (run 29144064721) — loophole demonstrated pre-fix; payload commit `c6ae73e` held RED by the NEW gate on the locked-door lane with the in-run "would HOLD" simulation verdict + HOLD banner + `##[notice]` annotation (run 29144119497).
- `control/inbox.md` + `control/status.md` untouched: `git diff control/` clean apart from this session's claim file. Claims-format advisory taught me the bullet needs a backticked branch token — fixed in-session.

## Previous-session review

⟲ Previous-session review: the 2026-07-11 kit-upgrade-v1.9.0 session's card was the single most useful input to this one — its verbatim HOLD line, backup-hash table, and landing-constraint notes (auto-merge OFF, REST squash) made this session near-mechanical. One miss: it recorded "branch deletion 403s in this repo — known" as a standing constraint, but GitHub auto-deleted head branches on merge that same wave (the folklore was already stale when written). Workflow improvement: constraint notes in session cards should carry a verified-on date the way backup hashes do — a dated constraint invites re-verification; an undated one reads as permanent truth.

## Close-out

- Follow-ups owed to the repo's own lane (NOT done here, per distribution-seat hard scope): (1) update the `kit:` heartbeat line in `control/status.md` to v1.10.0; (2) decide whether to adopt the staged CLAUDE.md search-hygiene note live (still no live `.claude/CLAUDE.md`); (3) `docs/CAPABILITIES.md` landing-constraints entry still owed (auto-merge toggle OFF, REST squash path, branch auto-delete now ON — verified again this wave).
- Merge path: repo auto-merge toggle OFF → REST `merge_pull_request` squash on green, matching #51/#54 precedent.
