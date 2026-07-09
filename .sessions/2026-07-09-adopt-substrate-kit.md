# 2026-07-09 — Adopt substrate-kit v1.1.0 (ORDER 001, Phase A)

> **Status:** `complete`

📊 Model: claude-agent · high · feature build

💡 **Session idea:** Adopt substrate-kit v1.1.0 into trading-lab so the engagement gate (`python3 bootstrap.py check --strict`) goes green: plant + render the workflow docs, wire the CI gate, and engage the session loop.

## Previous-session review

First substrate session — no previous session card exists. Prior repo state was the initial scaffold (README, docs/founding-plan.md, control/ fleet files) at main @6de600d.

## Work log

- Created branch `claude/order-001-p0` from main.
- Copied `bootstrap.py` (substrate-kit v1.1.0 dist) to the repo root and ran `adopt` — planted CONSTITUTION.md, the docs/ workflow set, `.session-journal.md`, `.sessions/`, `project.index.json`, and staged packs under `.substrate/`.
- Set integration mode to `active` (autonomous lab — decide-and-flag).
- Answered all 13 interview slots from project ground truth (project trading-lab; Python 3.11+/pandas/pytest; verify `python3 -m pytest -q`; owner menno420; fleet protocol in control/; binding methodology docs/founding-plan.md) and ran `render --live` — no unrendered banners or `${...}` slots remain.
- Linked `docs/founding-plan.md` from `docs/AGENT_ORIENTATION.md` to clear the reachability orphan.
- Installed the staged CI gate: `.substrate/ci/substrate-gate.yml` → `.github/workflows/substrate-gate.yml` (runs `check --strict` on PRs and pushes to main).
- Wrote this born-red session card to engage the session loop.

## Close-out

**Done:** substrate-kit v1.1.0 adopted end-to-end. All 13 interview slots answered and rendered (no banners, no ${...} slots), mode set to active, founding-plan linked into the read-path, CI gate installed at .github/workflows/substrate-gate.yml, session loop engaged with this card. `python3 bootstrap.py check --strict` exits 0.

**Verify:** `python3 bootstrap.py check --strict` -> exit 0. (`python3 -m pytest -q` becomes meaningful once P0 adds src/ and tests/.)

**Next (guard recipe for the P0 build session):** create src/, tests/, data/, requirements.txt and a pytest CI workflow; add ownership entries for the new areas in docs/ownership.md and keep new docs reachable from docs/AGENT_ORIENTATION.md, or check --strict will flag orphans. Each future session needs a card here with the Status badge, session idea, previous-session review, and Model line markers.
