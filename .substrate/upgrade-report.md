# substrate-kit upgrade report — v1.1.0 → v1.7.0

> Generated 2026-07-10 by `bootstrap.py upgrade`. Rollback: `python3 bootstrap.py upgrade --rollback`.

**Docs:** consumer-edited: 3 · diverged: 5 · template-improved: 10 · unchanged: 1

| planted doc | class | note |
|---|---|---|
| CONSTITUTION.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/decisions.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/architecture.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/ownership.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/runtime_contracts.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/repo-navigation-map.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/helper-policy.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/collaboration-model.md | diverged | both the template and the doc moved — manual merge |
| docs/ai-project-workflow.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/owner-profile.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/AGENT_ORIENTATION.md | diverged | both the template and the doc moved — manual merge |
| docs/current-state.md | consumer-edited | template unchanged — consumer-owned, nothing to apply |
| docs/question-router.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| docs/CAPABILITIES.md | unchanged | template identical across versions |
| docs/ideas/README.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| .session-journal.md | template-improved | consumer-untouched + template improved — safe to apply with `upgrade --apply-docs` |
| control/README.md | diverged | no recorded hash or old templates unavailable (pre-1.0 install) — manual review |
| control/inbox.md | diverged | no recorded hash or old templates unavailable (pre-1.0 install) — manual review |
| control/status.md | diverged | no recorded hash or old templates unavailable (pre-1.0 install) — manual review |

## Applied (--apply-docs)

- applied: CONSTITUTION.md (template@new, hash re-recorded)
- applied: docs/decisions.md (template@new, hash re-recorded)
- applied: docs/architecture.md (template@new, hash re-recorded)
- applied: docs/runtime_contracts.md (template@new, hash re-recorded)
- applied: docs/helper-policy.md (template@new, hash re-recorded)
- applied: docs/ai-project-workflow.md (template@new, hash re-recorded)
- applied: docs/owner-profile.md (template@new, hash re-recorded)
- applied: docs/question-router.md (template@new, hash re-recorded)
- applied: docs/ideas/README.md (template@new, hash re-recorded)
- applied: .session-journal.md (template@new, hash re-recorded)

## Template deltas for diverged docs

### docs/collaboration-model.md

```diff
--- docs/collaboration-model.md (template@old, current slots)
+++ docs/collaboration-model.md (template@new, current slots)
@@ -23,6 +23,17 @@
 - **Ask** when the change is irreversible (data loss / external publish),
   large and cross-cutting (architectural), or the goal itself is genuinely
   ambiguous.
+
+## Routing work to the owner
+
+The owner is the scarcest resource in the program. An ask reaches the owner
+only when the agent has **attempted the action itself** or can name the
+**exact wall** (error text, permission denial) proving only the owner can do
+it — assumption-based asks are banned. Every ask uses the OWNER-ACTION
+format — WHAT / WHERE / HOW / WHY-IT-MATTERS / UNBLOCKS / VERIFIED-NEEDED
+(canonical: `control/README.md`) — phrased so a non-technical owner can act
+directly: one plain sentence, an exact click path, paste-ready text.
+Withdraw asks that have gone stale; fewer, clearer asks beat complete lists.
 
 ## Friction → guard
 
```

### docs/AGENT_ORIENTATION.md

```diff
--- docs/AGENT_ORIENTATION.md (template@old, current slots)
+++ docs/AGENT_ORIENTATION.md (template@new, current slots)
@@ -9,7 +9,9 @@
 
 1. `.claude/CLAUDE.md` — the working agreement.
 2. `docs/current-state.md` — the living status ledger.
-3. This file — task-specific reading routes.
+3. `docs/CAPABILITIES.md` — verified session capabilities & walls (the
+   discovery rule lives there; append what you learn).
+4. This file — task-specific reading routes.
 
 ## Binding contracts
 
@@ -26,7 +28,7 @@
 `docs/collaboration-model.md` · `docs/helper-policy.md` ·
 `docs/repo-navigation-map.md` · `docs/ai-project-workflow.md` ·
 `docs/owner-profile.md` · `docs/current-state.md` · `docs/decisions.md` ·
-`docs/question-router.md` · `docs/ideas/README.md` — plus the root
+`docs/question-router.md` · `docs/CAPABILITIES.md` · `docs/ideas/README.md` — plus the root
 `CONSTITUTION.md` (the working agreement) and `.session-journal.md`.
 
 ## Verifying any change
```

