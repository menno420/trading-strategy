---
state: routed
origin: lab
shipped_pr: null
shipped_repo: null
merged_date: null
outcome: open
---

# In-repo trigger registry (`control/triggers.md`)

> **Status:** `ideas`

## The idea

Triggers/Routines are load-bearing infrastructure that lives entirely
outside the repo: a routine bound to a chat session dies silently when
that chat is archived, and nothing committed anywhere shows the loss. This
lane hit exactly that at archive prep 2026-07-11 — two live triggers (the
2h failsafe cron and the 2026-07-17 weekly-grading wake) were bound to the
coordinator session and known only in chat; capturing them required a
dedicated close-out pass (see
[../retro/archive-ready-2026-07-11.md](../retro/archive-ready-2026-07-11.md) ⚑ (g)).

Proposal: a one-file registry, `control/triggers.md` — one line per live
trigger: trigger id, cron/one-shot spec, bound session, purpose, and the
re-arm recipe. Convention (cheapest enforcing form: written rule first, a
kit checker later): any session that creates, updates, or deletes a
trigger updates the registry in the same PR. Succession risk then becomes
a `git grep` instead of coordinator chat memory.

## MAP

- Owning area: `control/` (fleet coordination files) — plausibly a
  substrate-kit convention rather than lane-local, so also a candidate to
  route upstream to the kit repo.
- Size: small (one doc + one written rule; optional kit checker later).
- Risk: low — pure documentation; worst case is a stale registry, which is
  still strictly better than no registry.

## ROUTE

Routed: **discuss-first** → fleet manager / kit seat, since the failure
mode is fleet-wide (every lane with a coordinator-bound routine has this
exact silent-death risk), and the kit is where the convention would be
enforced. Next destination: surface to the fleet manager via the next
manager sweep of this lane's status/retro files.
