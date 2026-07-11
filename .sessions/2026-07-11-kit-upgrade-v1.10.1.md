# 2026-07-11 — kit upgrade: substrate-kit v1.10.0 → v1.10.1

> **Status:** `complete`

📊 Model: fable-5 · kit-distribution seat (owner directive Q-0261.3) · start 2026-07-11

💡 **Session idea:** The locked-door gate lane re-runs `check --strict
--require-session-log --simulate-added-card` per card, and each local
`check` run appends 2–3 near-identical `session-log` findings to
`.substrate/guard-fires.jsonl` — the file is now dominated by duplicate
born-red heartbeat noise (same card, same message, seconds apart). Kit
idea: dedupe consecutive guard-fires entries with identical
(guard, path, message) within a short window, or mark designed-hold
findings with a distinct `kind`, so the fires log stays a signal ledger
instead of a heartbeat echo chamber.

## What happened

Vendored-kit upgrade v1.10.0 → v1.10.1 via the canonical release-asset path:
sha256-verified `bootstrap.py` asset
(`fbe83ce35d1fb3b544ac58fc60ee2609eaa6c69c13d77883e9fdc5da6bbad158`) +
`release.json`, staged as `bootstrap.py.new`, `python3 bootstrap.py.new
upgrade` (staging inputs self-cleaned). Payload: gate tail-1 multi-card
shadowing fix (every card in the diff graded; added in-progress cards HOLD;
modified-sibling advisory) + emphasis-blind `_MODEL_DOCTRINE_PHRASE`. Kit
upgrade ONLY — no domain work; `control/inbox.md` / `control/status.md` /
`tests.yml` untouched. Same-day wave as fleet-manager #70 (merge `3150f0e2`)
and superbot-games #43 (merge `eeb9f854`).

## Work log

- Pre-upgrade tree at v1.10.0 (vendored dist sha256 `ba69fc5c…`, matching the v1.10.0 release asset); zero open PRs touching bootstrap.py / .substrate / substrate-gate.yml.
- Backups: exactly ONE new bank, `.substrate/backup/bootstrap-1.10.0.py` (`ba69fc5cf21619cc85e4c733ebe3d9eda8803e678f810fcc39b94d60c2f3b5a4`, byte-equal to the pre-upgrade vendored dist). Pre-existing banks byte-untouched before/after: `bootstrap-1.1.0.py` `c12a2f55…`, `bootstrap-1.7.0.py` `00f4f4cd…`, `bootstrap-1.7.1.py` `2aa4fedd…`, `bootstrap-1.8.0.py` `28c5dcb6…`, `bootstrap-1.9.0.py` `55181082…`.
- `.substrate/backup/last-upgrade.json`: from 1.10.0 → to 1.10.1, archived_dist `bootstrap-1.10.0.py`.
- Regenerated gate: the old tail-1 card picker is GONE — per-card `while IFS= read -r card` loops grade EVERY card in the diff (added-card lane + locked-door lane + modified/close-out lane); "modified sibling card (advisory — logged, never grade-affecting)" printed alongside adds; the only remaining `tail -1` picks the substrate-gate.yml diff path, not a card. Zero pytest refs in the gate; `tests.yml` byte-untouched.
- Carve-out scan: `- carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found` (`.substrate/upgrade-report.md`).
- Doctrine idempotence: `.sessions/README.md` byte-identical before/after (`b1be3a49…` both sides) — no duplicate ORDER 009/012 append.
- `check --strict` pre-flip → exit 1, only red the designed hold: "check: HOLD (by design): session card .sessions/2026-07-11-kit-upgrade-v1.10.1.md declares an in-progress Status — the born-red session gate holds the merge red until the card flips complete. This red is the designed hold, not a defect; nothing to investigate."
- `check --simulate-added-card <this card>` → exit 0: "the added-card lane would HOLD (born-red: the card declares an in-progress/drafted Status; the gate would stay red until it flips complete)." + "simulation is advisory-only — it never affects this run's exit code."
- CI live-fire on payload head `7458277`: substrate-gate run 29147514534 held RED on the locked-door lane ("card … is ADDED but this PR also touches the gate workflow itself — locked-door gate") with the in-run "would HOLD" simulation verdict, the HOLD banner, and the `##[notice]` designed-hold annotation. `tests.yml` pytest run 29147514540 GREEN.
- `control/inbox.md` + `control/status.md` untouched; claim file deleted IN this flip commit (the #56 lesson — no post-merge micro-PR).

## Previous-session review

⟲ Previous-session review: the 2026-07-11 kit-upgrade-v1.10.0 session (#55/#56) left exactly the artifacts this session needed — verbatim HOLD/simulation lines, the full backup-hash table, and the landing constraints (auto-merge OFF, MCP squash, branch auto-delete ON) made this run near-mechanical. Its one miss became this session's guardrail: forgetting the claim-file deletion in the flip commit cost it a post-merge micro-PR (#56); this session folded the deletion into the flip commit. Workflow improvement: the flip-commit checklist ("Status → complete + delete claim file, ONE commit") should live in the claims README so it's read at claim time, not rediscovered from PR archaeology.

## Close-out

- Follow-ups owed to the repo's own lane (NOT done here, per distribution-seat hard scope): (1) `control/status.md` kit heartbeat line still stale (predates this wave) — update to v1.10.1; (2) still no live `.claude/CLAUDE.md` (staged copy at `.substrate/claude/CLAUDE.md`); (3) `docs/CAPABILITIES.md` landing-constraints entry still owed (auto-merge toggle OFF, MCP squash path, branch auto-delete ON — re-verified this wave).
- Merge path: repo auto-merge toggle OFF → GitHub MCP `merge_pull_request` SQUASH on green, matching #51/#54/#55 precedent.
