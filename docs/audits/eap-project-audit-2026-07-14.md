# EAP project audit 2026-07-14 — pointer to the seat-level audit

> **Status:** `audit`
>
> THIN POINTER (ORDER 015(a)(1)). The definitive end-of-EAP audit of this
> seat — measured usage and scale, tooling verdicts, platform walls,
> landing/scheduling friction, self-engineered fixes, remaining pains, and
> a wishlist for BOTH of the seat's repos (`menno420/venture-lab` and this
> repo) — lives in the venture-lab repo, where the coordinator seat is
> homed. This repo never received a dedicated audit ORDER (inbox topped at
> 014 when the audit ran); this pointer gives the audit a stable read-path
> home here and quotes this repo's headline numbers verbatim.

## The audit itself

**[Venture Lab seat — EAP project audit, 2026-07-14](https://github.com/menno420/venture-lab/blob/37e3c0500f0b194da1fa715bdf6bbf5cc09b0106/docs/audits/eap-project-audit-2026-07-14.md)**
(`menno420/venture-lab` → `docs/audits/eap-project-audit-2026-07-14.md`,
pinned at commit `37e3c0500f0b194da1fa715bdf6bbf5cc09b0106`, blob
`eb38b523366af41911a9609944b2972d16b02c6c`; verified live via GitHub MCP
`get_file_contents` and read in full, 2026-07-14T09:58Z).

Its method line: "Measured 2026-07-14 (~08:35–08:50Z) by three measurement
passes: local git forensics on venture-lab at origin/main `17b0499` and on
a read-only clone of trading-strategy at origin/main `01aa0ce`, plus
full-population GitHub MCP metrics". Note the pin: this repo was measured
at `01aa0ce`; main has since moved (first delta: `0ea6950`, the ORDER 015
inbox append).

## This repo's headline numbers (quoted verbatim from audit §1)

From the §1 "Measured" table ("PR totals exact: `search_pull_requests`
total_counts match `list_pull_requests state=all` item counts, numbers
… 1..121 with no gaps"), trading-strategy column:

| measure | trading-strategy |
|---|---|
| session cards (`.sessions/*.md`, README excluded) | 71 |
| commits on main (`git rev-list --count origin/main`) | 130 |
| PRs opened | 121 |
| PRs merged | 120 |
| PRs closed-unmerged | 1 (#64) |
| PRs open at audit | 0 |

Active window, verbatim (§1): "`f65d4773` 2026-07-09T14:34:03+02:00 →
`01aa0cec` 2026-07-14T09:15:42+02:00 — **~5 days**." Research outcome,
verbatim (§1): "Research outcome is already told in
`docs/research-program-retrospective.md@d857e50` ('5,055 registered
configurations → 0 promoted', verified two ways there) — not restated
here." (Local depth: [../research-program-retrospective.md](../research-program-retrospective.md).)

## Walls + CI state (quoted verbatim, this repo's slice)

- Walls (§3): "trading `docs/CAPABILITIES.md@67f5554` (**7 seed-fence
  walls + 1 append entry, which is a capability, not a wall** — the
  enabler-supersedes-REST-merge note)". Living ledger:
  [../CAPABILITIES.md](../CAPABILITIES.md).
- CI (§6): "trading-strategy 640 runs, substrate-gate **68 failures**
  (26% of 265), tests **0/265**, enabler 0. **All CI red on both repos —
  182 runs — is the designed born-red gate**; no test has ever failed."
- Landing (§4): "trading-strategy **median 1m52s** (n=120)" time-to-land.
- Branch debt (§3): "**131 stale `claude/*` branches in venture-lab + 56
  in trading-strategy**" behind the branch-delete 403 wall.

## What this pointer is NOT

Not a second audit: every §2–§11 verdict, wall verbatim, paste-ready
Anthropic ask, and wishlist item stays in the venture-lab original — read
it there. This repo's own complementary audit artifacts remain
[2026-07-13-fleet-cleanup-audit.md](2026-07-13-fleet-cleanup-audit.md)
(fleet cleanup pass, EAP final night) and the EAP close-out walkthrough
[../eap-closeout-walkthrough-2026-07-14.md](../eap-closeout-walkthrough-2026-07-14.md).
