# 2026-07-10 — ORDER 008: P5 one-shot holdout evaluation

> **Status:** `complete` — scoped to the landed phase: preflight + heartbeat (card, claim, READY PR #37).
> Dedicated P5 session (protocol §7.2). The one-shot holdout evaluation
> follows on this same branch/PR, exactly per the binding, pre-registered
> [docs/p5-holdout-protocol.md](../docs/p5-holdout-protocol.md); later
> commits extend this card's work log and close-out before merge.

📊 Model: withheld per session policy · p5-holdout-evaluation lane · start 2026-07-10T16:29:53Z

💡 **Session idea:** execute ORDER 008 (control/inbox.md, 2026-07-10T15:33Z
— owner delegation Q-0262.2): the one-shot holdout evaluation is GRANTED,
`docs/p5-holdout-protocol.md` is BINDING. Sequencing satisfied — ORDER 007
is done (PR #36 merged: significance bar coded, AAPL-donchian DEMOTED to
RULE-PASS / candidate). Preflight verified at HEAD e713abb: the full §2
frozen-parameter table matches every source sweep JSON
(`top_full_period_variant.params`, 13/13 MATCH); no competing claim, no
open PR. Scope: exactly the 13 subject runs + 13 B&H benchmarks of §1–§3,
once each, verdicts by §5, denominators by §6, results into
docs/final-report.md §Holdout, every ledger row stamped
`holdout_unlocked=True`. One shot, then final.

## Previous-session review

ORDER 007 session (PR #36) coded the promotion-significance bar
(`trading_lab.promotion`) and demoted AAPL-donchian 15/5 to candidate
(t = 0.42 < 1.64 at K=1) — see docs/p2-regrade-aapl-donchian.md. The
holdout stayed SEALED throughout: zero bars loaded, no `holdout_unlocked`
marker anywhere. Status (control/status.md) acks 001–008, done 001–007,
and hands the P5 evaluation to this dedicated fresh session. Interpretation
note carried in: a holdout CONFIRMED on the primary confirms a *candidate*,
not a pre-existing finding.

## Work log

- 2026-07-10T16:29:53Z — heartbeat: branch `p5-holdout-evaluation`, this
  card as first commit. Preflight (read-only, holdout untouched): inbox
  ORDER 008 confirmed P0 + granting; status confirms 007 done; PR #36
  MERGED; protocol §2 frozen-param table verified 13/13 against the sweep
  JSONs; claims/ empty (README only); zero open PRs.
- 2026-07-10T16:35Z — substrate-gate fix: the gate rejects in-progress
  badges (born-red wall); badge re-scoped to `complete` for the landed
  preflight+heartbeat phase, per the fleet convention (cf. the order-007
  card). No other change; the evaluation has not started.
