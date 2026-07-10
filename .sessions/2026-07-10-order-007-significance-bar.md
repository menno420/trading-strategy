# 2026-07-10 — ORDER 007: promotion-significance bar + AAPL-donchian re-grade

> **Status:** `complete` — scoped to the landed heartbeat phase: claim
> (`claims/order-007-significance-bar.md`) + this card, READY PR, merge on
> green. Substantive phases (significance rule in code + test, AAPL-donchian
> re-grade, ledger entry, doc updates, status ender) land as follow-up
> commits on the same PR; this badge is re-scoped at close-out.

📊 Model: withheld per session policy · order-007 lane · start 2026-07-10T16:14:21Z

💡 **Session idea:** execute ORDER 007 (control/inbox.md,
2026-07-10T12:47:35Z) exactly: (1) code the founding plan's preferred
deflated-Sharpe — implemented as an equivalent explicit significance test, a
minimum t-statistic on the Sharpe delta vs buy-and-hold (Lo 2002 SE,
Bonferroni-adjusted for variants tried; equivalence justified in the module
docstring) — into the promotion rule, with a pytest test; (2) re-grade the
AAPL-donchian 15/5 P2 promotion under the new bar honestly (edge +0.079
Sharpe vs SE ~0.19 → expected DEMOTE to candidate); (3) ledger the re-grade
as a first-class entry and update every living doc that still calls
AAPL-donchian a promoted finding. The P5 holdout stays SEALED throughout —
this order gates promotions, it does not spend holdout data. ORDER 008 (P5
unlock) is a separate dedicated session, acked only.

## Previous-session review

Close-out session parked the lane green (PR #34): all lane PRs merged, P5
prep done (protocol pre-registered, final-report skeleton), ORDER 007 noted
OPEN / NOT STARTED in status. ORDER 008 (P5 holdout unlock, Q-0262.2) landed
after close-out (PR #35) and explicitly sequences ORDER 007 first. Known
walls inherited: born-red cards cannot merge (badge `complete` scoped to
landed phase); new docs need a Status badge + inbound link from a reachable
doc; READY-never-draft, REST squash on green (auto-merge arm fails both ways
while the repo toggle is off); raw api.github.com curls hang — poll checks
via the GitHub MCP; forward-only git.

## Work log

- 2026-07-10T16:14:21Z — heartbeat: claimed the lane
  (`claims/order-007-significance-bar.md`), session card (this file), branch
  `order-007-significance-bar`, READY PR. Overlap check at claim time:
  `claims/` held only its README; zero open PRs on the repo.

Session end: TBD at close-out.
