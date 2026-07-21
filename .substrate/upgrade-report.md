# substrate-kit upgrade report — v1.20.1 → v1.20.2

> Generated 2026-07-21 by `bootstrap.py upgrade`. Rollback: `python3 bootstrap.py upgrade --rollback`.

**Docs:** consumer-edited: 12 · diverged: 1 · unchanged: 11

| planted doc | class | note |
|---|---|---|
| CONSTITUTION.md | diverged | both the template and the doc moved — manual merge |
| docs/decisions.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
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
| docs/CAPABILITIES.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/SKILLS.md | unchanged | template identical across versions |
| docs/ROUTINES.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/reading-path.md | unchanged | template identical across versions |
| docs/ideas/README.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| .session-journal.md | unchanged | template identical across versions |
| control/README.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/inbox.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/status.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| control/claims/README.md | unchanged | template identical across versions |
| scripts/env-setup.sh | unchanged | template identical across versions |

## Carve-out scan

- carve-out scan: .github/workflows/substrate-gate.yml — ran, 0 found
- carve-out scan: .github/workflows/auto-merge-enabler.yml — ran, 0 found

## Capability-ledger seed refresh

- capability-seed: NOT refreshed — the fenced seed block in docs/CAPABILITIES.md differs from the kit-form fence (edited inside the fence, or the old templates are unavailable). The fence is kit-owned: move your own findings BELOW the fence into the append log, restore the block between the BEGIN/END markers to kit form (copy it from the new template render), and the next upgrade refreshes it automatically.

This upgrade ships the venue-scoped capability ledger (grounded-skills §4.2): entries carry a venue token (owner-live · autonomous-project · routine-fired · subagent · any) and the ledger's kit-owned seed block carries the posture decision rule. If this repo carries a local prose copy of the boot-triad/venue-posture rule (superbot Q-0270), that copy is now superseded by docs/CAPABILITIES.md's posture rule — collapse the local copy into a pointer.

## Seat-digest refresh

- seat-digest: docs/seat-digest.md already current — nothing to refresh.

## Template deltas for diverged docs

### CONSTITUTION.md

```diff
--- CONSTITUTION.md (template@old, current slots)
+++ CONSTITUTION.md (template@new, current slots)
@@ -88,9 +88,9 @@
   **land your own work** — flip to ready, arm auto-merge, or merge it
   yourself (MCP/REST, or let a merge-on-green workflow land it) the moment
   CI is green. Landing a green PR, your own or a sibling's, is a **normal
-  agent action, not an owner action** — there is **no standing
-  "classifier-denied" merge wall; do not invent one, and never route a
-  mergeable green PR to the owner.** If the branch falls behind, update it
+  agent action, not an owner action** — there is
+  **no standing "classifier-denied" merge wall; do not invent one, and never
+  route a mergeable green PR to the owner.** If the branch falls behind, update it
   (merge, never force). Only if a *specific* merge/arm call returns a
   real, verbatim permission refusal *this session* do you park that one
   call (attempt-once rule), queue ONE owner item for the systemic cause,
```

