# substrate-kit upgrade report — v1.10.1 → v1.11.0

> Generated 2026-07-11 by `bootstrap.py upgrade`. Rollback: `python3 bootstrap.py upgrade --rollback`.

**Docs:** consumer-edited: 8 · unchanged: 13

| planted doc | class | note |
|---|---|---|
| CONSTITUTION.md | unchanged | template identical across versions |
| docs/decisions.md | unchanged | template identical across versions |
| docs/architecture.md | unchanged | template identical across versions |
| docs/ownership.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/runtime_contracts.md | unchanged | template identical across versions |
| docs/repo-navigation-map.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/helper-policy.md | unchanged | template identical across versions |
| docs/collaboration-model.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/ai-project-workflow.md | unchanged | template identical across versions |
| docs/owner-profile.md | unchanged | template identical across versions |
| docs/AGENT_ORIENTATION.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/current-state.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/question-router.md | unchanged | template identical across versions |
| docs/CAPABILITIES.md | unchanged | template identical across versions |
| docs/ideas/README.md | unchanged | template identical across versions |
| .session-journal.md | unchanged | template identical across versions |
| control/README.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/inbox.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/status.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/claims/README.md | unchanged | template identical across versions |
| scripts/env-setup.sh | unchanged | template identical across versions |

## ⚠️ Gate carve-outs (host additions the kit-owned regen could not keep)

- carve-out: .github/workflows/substrate-gate.yml — host-added step 'uses: actions/checkout@v4' in job 'substrate-gate'
- carve-out: .github/workflows/substrate-gate.yml — host-added step 'uses: actions/setup-python@v5' in job 'substrate-gate'
- carve-out: full pre-regen gate banked at .substrate/backup/substrate-gate.pre-regen-4f50eb4d.yml — host additions were NOT carried into the regenerated kit-owned gate; move them into a separate workflow file (e.g. .github/workflows/host-ci.yml) and commit that before shipping this upgrade/adopt PR.

## Carve-out scan

- carve-out scan: 3 carve-out line(s) reported above (see the ⚠️ section).
