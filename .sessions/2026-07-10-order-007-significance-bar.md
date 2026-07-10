# 2026-07-10 — ORDER 007: promotion-significance bar + AAPL-donchian re-grade

> **Status:** `complete` — full session: heartbeat (claim + card, PR #36),
> significance rule + test, AAPL-donchian re-grade + first-class ledger
> entry, label updates across the living docs, and this wrap-up (card
> close-out + claim released + status overwrite) — all in PR #36, merged on
> green. Lane closed; ORDER 007 done; holdout sealed throughout.

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
  `order-007-significance-bar`, READY PR #36. Overlap check at claim time:
  `claims/` held only its README; zero open PRs on the repo. Auto-merge arm
  failed with the known pending-side wall ("unstable status", repo toggle
  off) — REST squash on green is the fallback, not retried.
- 2026-07-10T16:2xZ — significance rule: new `src/trading_lab/promotion.py`
  (Lo 2002 SE of the annualized Sharpe; t-stat on the Sharpe delta vs B&H;
  Bonferroni-adjusted one-sided minimum t, alpha=0.05 — the founding plan's
  deflated-Sharpe preference as an explicit equivalent test, equivalence
  argued in the module docstring); `scripts/run_p2_validation.py` verdict
  path now routes through `promotion.grade_promotion` (PROMOTED-TO-FINDING /
  RULE-PASS / KILLED); `tests/test_promotion.py` (14 tests, incl. the exact
  AAPL re-grade arithmetic pinned). Local: 147 passed; `bootstrap.py check
  --strict --require-session-log` exit 0.
- AAPL-donchian 15/5 re-grade, from the ledgered P2 row only (no backtests
  re-run, zero bars loaded, holdout sealed): edge +0.078779 Sharpe,
  SE 0.185474 (N=7,331 daily bars), t = 0.4247 < 1.6449 (K=1; K=41/177 only
  raise the bar to 3.03/3.45) → **DEMOTED to RULE-PASS / candidate**.
  First-class ledger entry: `docs/p2-regrade-aapl-donchian.md` (old rule,
  new rule + formulas, computation, denominators, P5-protocol implications
  noted without editing the binding doc). Labels updated:
  docs/p2-validation-results.md, docs/final-report.md (headline, ranked
  table, lead-candidate section, methodology), docs/succession/QUEUE.md,
  docs/current-state.md, docs/p4-transfer-results.md.

## Close-out (full session)

**Done:** ORDER 007 in full, single PR (#36) —

1. Significance rule coded with tests: `src/trading_lab/promotion.py`,
   `tests/test_promotion.py` (14 tests), `scripts/run_p2_validation.py`
   verdict path amended. Promotion requires B&H beat net of costs AND
   t ≥ Φ⁻¹(1 − 0.05/K) on the Sharpe delta (Lo 2002 SE); below the bar =
   RULE-PASS / candidate.
2. AAPL-donchian 15/5 re-graded from the ledgered P2 numbers only:
   t = 0.4247 < 1.6449 → DEMOTED to candidate. Ledger entry:
   `docs/p2-regrade-aapl-donchian.md` (incl. P5-protocol implications noted
   without editing the binding doc). All living-doc labels updated.
3. Wrap-up: inbox re-read at origin/main HEAD fd5e9fe 2026-07-10T16:21:48Z
   (nothing newer than ORDER 008; 008 belongs to a dedicated P5 session and
   is acked-only here), claim `claims/order-007-significance-bar.md`
   deleted, `control/status.md` overwritten.

**Verify:** `python3 -m pytest -q` → 147 passed; `python3 bootstrap.py check
--strict --require-session-log --session-log
.sessions/2026-07-10-order-007-significance-bar.md` → exit 0. Holdout audit
unchanged: zero bars loaded, zero backtests run, no `holdout_unlocked`
marker anywhere, `docs/p5-holdout-protocol.md` and `control/inbox.md`
untouched.

**Next (guard recipe):** ORDER 008 — P5 one-shot holdout evaluation,
FRESH dedicated session (not this one, per protocol §7.2),
`docs/p5-holdout-protocol.md` binding; note for that session: the PRIMARY
subject's label is now candidate (RULE-PASS), see the re-grade entry.

Session end: 2026-07-10T16:21:48Z. Badge stays `complete`.
