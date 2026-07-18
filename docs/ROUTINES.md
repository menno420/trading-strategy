# trading-lab — routines

> **Status:** `reference`
>
> **Agents CAN arm routines here** — `create_trigger` / `send_later` work
> agent-side (proven fleet-wide 2026-07-11; this repo itself armed a weekly
> grading cron historically). Arming a routine is normal agent work, not a
> capability wall. What this repo does NOT do is *rely* on self-armed
> persistence: that is a deliberate **design choice** for a reproducible
> offline research lab, not a platform limit. The old EAP-era
> "self-persistence / dead-man-cron re-arm every turn" scaffolding is retired
> (fresh-start cleanup, 2026-07-17) because that pattern is unnecessary here —
> not because agents are refused triggers.

## What is true now

trading-lab is a **plain offline Python research library**. There is no live
service and no wake chain it depends on to make progress.

- **Grading runs in-session or host-owned — by design.** The weekly paper-lane
  grading pass runs either **in a live session** (`python3
  scripts/grade_paper.py`, no args — idempotent, no persistence) or via a
  **host-owned GitHub Actions cron** — the designed-but-PARKED
  `.github/workflows/weekly-grading.yml`, which needs one explicit owner
  "per-seat go" to install (see [NEXT-TASKS.md](NEXT-TASKS.md)). Impact of a
  missed pass is ~zero: `grade_paper.py` is a graded-ledger no-op until the
  first evaluable window ~early August 2026.
- **A scheduled executor here is preferably host-owned.** Because the point is
  a durable, owner-visible cron independent of any one session, the preferred
  executor is a **host-owned GitHub Actions workflow**. An agent-armed Routine
  (`create_trigger`) is available and not walled — it is simply not the chosen
  persistence model for this lab.

Capability walls around trigger tooling (should any ever be discovered) belong
in `docs/CAPABILITIES.md`, appended per its discovery rule — but note the
current verified fact there is that routine creation is **not** walled.
