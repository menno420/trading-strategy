# trading-lab — routines (RETIRED for this repo)

> **Status:** `reference`
>
> **This repo arms no routines.** The self-persistence / wake-chain / dead-man-cron
> doctrine that used to live here was EAP-era autonomy scaffolding, and it is
> **retired** (fresh-start cleanup, 2026-07-17). It described a persistent
> autonomous seat re-arming its own recurring triggers every turn — a model that
> (a) no longer applies now the project is an **owner-live seat** (EAP read-only
> cutoff 2026-07-21), and (b) drove agents straight into the ~2026-07-15
> permission classifier's `[Unauthorized Persistence]` refusals every session.

## What is true now

trading-lab is a **plain offline Python research library**. There is no live
service, no wake chain, and no agent-armed scheduled trigger.

- **Grading runs in-session or host-owned.** The weekly paper-lane grading pass
  runs either **in a live session** (`python3 scripts/grade_paper.py`, no args —
  idempotent, no persistence) or via a **host-owned GitHub Actions cron** — the
  designed-but-PARKED `.github/workflows/weekly-grading.yml`, which needs one
  explicit owner "per-seat go" to install (see [NEXT-TASKS.md](NEXT-TASKS.md)).
  Impact of a missed pass is ~zero: `grade_paper.py` is a graded-ledger no-op
  until the first evaluable window ~early August 2026.
- **Agents do not arm recurring triggers here.** No `create_trigger` /
  `send_later` wake chains, no failsafe/pacemaker crons. If a scheduled executor
  is ever wanted, it is a **host-owned GitHub Actions workflow the owner installs**,
  not an agent-armed Routine.

Capability walls around trigger tooling (should they ever become relevant) belong
in `docs/CAPABILITIES.md`, appended per its discovery rule.
