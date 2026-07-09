# Proposed gen-2 Custom Instructions — trading-lab lane

> **Status:** `reference` — gen-1's rewrite from lived experience. Honest caveat: the exact gen-1 Custom Instructions text is not visible from the repo; keep/drop judgments below reconstruct from lived behavior, orders, and the platform defaults we fought.
>
> **Blueprint alignment** (fleet-manager `docs/gen2-blueprint.md`, status `binding`, read at wind-down):
> - ADD-1/ADD-2 match blueprint §2 deltas 1–2 (READY + arm-auto-merge-at-creation; explicit merge-authority grant) — adopt the blueprint's stronger "arm auto-merge at creation" phrasing.
> - ADD-3/ADD-4 match §1 seed items (heartbeat-before-work; walking skeleton through the FULL merge path ≤20 min); the blueprint tightens spawn-liveness to 5–10 min — take the tighter bound.
> - ADD-5/ADD-6/ADD-8 match §1/§2a (PLATFORM-LIMITS walls with exact error text at day 0; Model+time from card #1; `date -u` timestamps — §2a rule 4).
> - ADD-7 (self-terminal briefs) has no direct blueprint counterpart; the blueprint attacks the same liveness problem from the other side with §2a routine wake cadence. Both are needed: routines wake lanes, self-terminal briefs survive steering-channel loss.
> - The blueprint adds two things this rewrite missed — order-lease + re-read-inbox-at-HEAD before acting (§2 delta 5) and a boot-time capability audit (§2 delta 6). Adopt both as ADD-9/ADD-10 in the final paste.
> - Differs on environment: this proposal originally shipped a simpler setup script; superseded — `environments/setup-universal.sh` is now synced with the fleet canonical template (materially better: set +e, env-setup.sh escape hatch, .git-based detection).

## KEEP (worked, with why)
- Inbox-first / status-last ritual + one-writer-per-file (zero conflicts all day).
- do/why/done-when order format (crisp acceptance tests; better than most human tickets).
- Decide-and-flag with mandatory one-line why (zero waiting, zero reversals in gen-1).
- Binding methodology by pointer (founding-plan) instead of inline rules (one source of truth).
- Research-only rail, stated absolutely (never ambiguous in practice).

## DROP (hurt, with why)
- The platform's draft-PR default, and any instruction inherited from it ("create the pull request as a draft") — it directly contradicted a merged done-when and parked finished work for ~2.8 h. Replace per ADD-1.
- Implicit merge authority — gen-1 never knew who merges until the owner did it by hand. Replace per ADD-2.
- Any assumption that spawned sessions start alive (two provision deaths say otherwise). Replace per ADD-3.

## ADD (each with why)
1. "Open every PR READY with auto-merge armed or merge on green yourself. Drafts are forbidden; 'not mergeable' means a failing check or a ⚑ flag." (Why: finished-but-invisible work was gen-1's second-biggest loss.)
2. "Merge authority is YOURS on green CI. No human approval is part of the loop unless branch protection blocks you — then ⚑ the exact click." (Why: explicit authority is the difference between 2 minutes and 2.8 hours.)
3. "Heartbeat before work: your FIRST action is confirming a clean provision in your reply channel and status file; any session YOU spawn must heartbeat within 10 minutes or you respawn it." (Why: silent DOA cost gen-1 an afternoon.)
4. "Walking skeleton before real work: prove branch→PR→CI→merge in your first 20 minutes." (Why: gen-1 discovered the gate's rules by failing them mid-deliverable.)
5. "Known walls are listed in docs/succession/NEXT-BOOT.md; consult before probing any wall, append new ones with exact error text." (Why: walls were re-discovered twice in gen-1.)
6. "Every session card carries Model + start/end time." (Why: the audit needed platform-log forensics for what a one-line convention could have recorded.)
7. "Brief every spawned session self-terminal — it must be able to land its work with zero follow-up messages." (Why: the steering channel vanished mid-day: `send_message: tool is not enabled for this organization`.)
8. "Timestamps from `date -u` only; no invented times." (Why: scripts/agents cannot call clock functions in some harness contexts; committed times must be real.)
