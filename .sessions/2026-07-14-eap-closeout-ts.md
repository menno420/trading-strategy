# 2026-07-14 — EAP close-out (ORDER 015): walkthrough + audit pointer + round-7 plan

> **Status:** `in-progress`

📊 Model: fable-5 · eap-closeout-ts lane (coordinator-dispatched worker, ORDER 015) · start 2026-07-14T10:01Z

⚑ Scope (claimed, `control/claims/2026-07-14-eap-closeout-ts.md`): ORDER 015
(`control/inbox.md` @ `0ea6950`) — EAP final-day close-out. Deliverables:
(a1) audit pointer doc `docs/audits/eap-project-audit-2026-07-14.md` linking
the seat-level EAP audit in menno420/venture-lab; (a2) heartbeat re-stamp
with ORDER 015 close-out ack lines (stale since 01:13:55Z per the file
itself at `0ea6950`; the fm recon in ORDER 015 cites 02:03:24Z — either way
~8h stale at execution); (a3) the round-7 pre-registered plan
`docs/research-round-7-plan.md` (PLAN ONLY — no sweep, no backtest, no grid
code this session); (b) the walkthrough
`docs/eap-closeout-walkthrough-2026-07-14.md` (sections A–E) + a ≤40-line
outbox close-out carrying the OWNER ACTIONS checklist. Parked items are
cited, never scheduled: R5-C BTC OOS (owner-gated, ~2026-09-09 earliest,
`docs/proposals/r5c-btc-bollinger-breakout-oos-proposal.md`), MTF-Bollinger
prereg (FROZEN, `docs/proposals/bollinger-mtf-preregistration-draft.md`),
wake-resilience rebind (owner console click, ORDER 014 blocked list @
`0ea6950` L214), Friday grading (time-gated 2026-07-17T09:05Z).

💡 **Session idea (deduped against prior cards — distinct from the
night-research-infra card's grading-pass liveness watchdog, the
rounds-retrospective card's machine-generated funnel table, the
night-grading-preverify card's review index (executed), the
selection-fair-gate card's reason_class taxonomy (executed), the
round-6-plan card's burden ledger, the round-6-run card's shared
lane-pipeline entry point, the kill-sig-review card's verdict-grammar
unification, and the 2026-07-13-ender card's fixed-shape `rebind_N:`
keys):** pending OWNER decisions have no single machine-readable home in
this repo — assembling ORDER 015's OWNER ACTIONS checklist required
hand-scanning `control/inbox.md` parked lists, `control/outbox.md` flag
entries, `docs/review-queue.md`, two `docs/proposals/*.md` badges, and
`docs/CAPABILITIES.md` walls; every close-out re-pays that derivation, and
a decision recorded in only one of those surfaces can silently drop out of
the next roll-up. Fix the class, not the instance: adopt the sibling seat's
derived-generator pattern (venture-lab `scripts/derive_owner_queue.py`,
cited in the EAP audit §2 as **reliable**) — a small script that derives
`docs/owner-actions.md` from fixed-grammar markers (review-queue bullets,
proposal badges carrying `OWNER-GATED`, outbox lines tagged `⚑ owner`),
with an advisory checker comparing its count against the heartbeat's
`⚑ needs-owner` line. Anchors: `docs/review-queue.md` (one-line grammar
already stable), badge lines in `docs/proposals/*.md`, outbox flag entries
(e.g. the foreign-trigger flag, `control/outbox.md` GRADING PRE-VERIFY
entry); test target: a fixture repo-scan in a new
`tests/test_owner_actions.py` pinning the marker grammar.

## Why this session exists

ORDER 015 (`control/inbox.md` @ `0ea6950`, appended by fm PR #122) — EAP
final day: every lane terminal-or-parked-cited plus a walkthrough for the
owner to review the seat. This session lands the audit-coverage pointer,
the walkthrough, the round-7 pre-registered plan (self-startable under
standing ORDER 012 item 4, round-6 self-start precedent per ORDER 014),
the outbox close-out with the OWNER ACTIONS checklist, and the heartbeat
re-stamp. Docs + control only: NO sweeps, NO backtests, NO fetches, NO
holdout reads (it is SPENT), NO verdict changes, NO code changes, NO
trigger writes, NO broker/order/exchange-write code.

## Premise re-verification (Q-0120 — leads, not facts)

- Seat-level EAP audit EXISTS and was read in full, live via GitHub MCP
  `get_file_contents`: `menno420/venture-lab` →
  `docs/audits/eap-project-audit-2026-07-14.md` at commit
  `37e3c0500f0b194da1fa715bdf6bbf5cc09b0106` (blob
  `eb38b523366af41911a9609944b2972d16b02c6c`), verified
  2026-07-14T09:58Z. Headline numbers for this repo, verbatim from its §1
  table: session cards **71** · commits on main **130** · PRs opened
  **121** · PRs merged **120** · PRs closed-unmerged **1 (#64)** · PRs
  open at audit **0** (measured at trading-strategy `01aa0ce`; HEAD has
  since moved one commit to `0ea6950`, the ORDER 015 append).
- Heartbeat staleness: `control/status.md` @ `0ea6950` reads
  `updated: 2026-07-14T01:13:55Z` — stale, confirmed (the recon's
  02:03:24Z matches the file's last content line stamp
  `night-2026-07-14: 2026-07-14T02:00:43Z`, commit d857e50 merged
  02:03:24Z; the `updated:` field itself is older still).
- No audit doc exists at HEAD in this repo covering the EAP program
  (docs/audits/ holds only `2026-07-13-fleet-cleanup-audit.md`, a
  different scope) — confirmed by `ls docs/audits/` at `0ea6950`.
- Grading executor LIVE + dry-run CLEAN: verified against repo state —
  `control/status.md` @ `0ea6950` `grading_executor:` line
  (trig_01UsNU4JRps4b7jiAMdEfXNi · cron `0 9 * * 5` · next fire
  2026-07-17T09:05Z · bound coordinator seat) and the PR #115 card
  (`.sessions/2026-07-13-night-grading-preverify.md`: `list_triggers`
  verbatim record 2026-07-13T22:48Z; dry-run exit 0, §7 FLAT shape).
  Repo-state citations, not a fresh trigger probe: this worker venue has
  the trigger MCP but ORDER 015 asks for close-out, not a re-probe; the
  most recent independent verification is <12h old and is cited as such
  in the walkthrough (docs/ROUTINES.md "probe, never record" is flagged
  there for the Friday executor to re-verify at fire time).
- Claim collision check at `0ea6950`: `control/claims/` holds only its
  README — no live claims, no open PRs (`git ls-remote` + MCP; the
  enabler left nothing in flight). No collision.

## Work log

- 2026-07-14T09:56Z — hard-synced to origin/main `0ea6950` (tree clean,
  no rescue branch needed). Read IN FULL at HEAD: control/inbox.md
  (ORDER 015 canonical text), control/README.md, control/status.md,
  control/outbox.md, control/claims/README.md, .sessions/README.md,
  docs/current-state.md, docs/CAPABILITIES.md, docs/AGENT_ORIENTATION.md,
  docs/research-program-retrospective.md (§g closely),
  docs/research-round-6-plan.md (structure mirrored by the round-7 plan),
  docs/selection-fair-gate.md, docs/paper-lane-protocol.md (§6–§7),
  docs/ROUTINES.md, docs/review-queue.md, both docs/proposals/*.md,
  .github/workflows/tests.yml (CI pytest line), plus the two most recent
  cards (night-research-infra, rounds-retrospective) and the PR #115
  card. Baseline verify at HEAD: `python3 -m pytest -q` → **668 passed**;
  `python3 bootstrap.py check --strict` → all checks passed.
- 2026-07-14T10:01Z — branch `claude/eap-closeout-ts` cut from `0ea6950`.
  This born-red card + claim are the FIRST commit (holds the substrate
  gate red until the deliberate final flip); PR opens READY after the
  content commits, never draft, never self-merged — the auto-merge
  enabler (`bf885f0`, PR #65) is the landing path.
- (work log continues below as commits land)

## Decisions taken (recorded per ORDER 015)

1. **Audit coverage: THIN POINTER DOC, not a fold into walkthrough §A.**
   Why: the repo already has a `docs/audits/` convention with its own
   badge token (`audit`, per `2026-07-13-fleet-cleanup-audit.md`) and an
   AGENT_ORIENTATION planted-doc entry pattern (commit `5d47091` linked
   the fleet audit there); a dedicated pointer keeps the walkthrough
   compact and gives the audit a stable citable path symmetric with the
   venture-lab original. §A links it.
2. **Round-7 direction: §(g) option 2 — genuinely new idea families on
   existing committed caches.** Why (recorded in the plan itself):
   options 1 and 3 are owner-gated (fetch decision / owner ORDER —
   agents cannot take them), option 4 registers no new evidence and
   needs no plan; option 2 is the §(g) menu's own "Cost: lowest — no
   owner action, committed caches only, compute in the round-6 range"
   entry, i.e. the cheapest option that still bears evidence.
3. Read-path: all three new docs linked from
   `docs/AGENT_ORIENTATION.md`'s planted-doc set (the router that
   "reaches every live doc"); the walkthrough additionally linked from
   `docs/current-state.md`.

## Previous-session review

⟲ Most recent prior card: `.sessions/2026-07-14-rounds-retrospective.md`
(PR #120, squash `d857e50` — merged after #121 at 02:03:24Z, so it is the
latest card-bearing landing; #117 and #122 that followed are control/audit
appends without cards, correctly per the fast-lane convention). Verified
against the tree rather than trusted: the retrospective doc exists at
`docs/research-program-retrospective.md` with badge `reference` at line 3
(inside the docs-gate's first-12-lines window), is reachable from
`docs/current-state.md` L30 exactly as the card claims, and its close-out
integrity statement holds — `git show d857e50 --stat` touches only the
retrospective doc, one current-state link line, one status heartbeat line,
the card, and the claim deletion, leaving `control/claims/` clean at HEAD.
Its adversarial-verify discipline (43 claim-groups re-derived, 2 anchor
fixes, 0 numeric errors) made THIS session cheap: §A/§E of the walkthrough
and the round-7 plan's premise lines cite the retrospective's already
re-verified numbers (5,055 → 0; the §(g) menu) instead of re-deriving
them — the card system paying rent twice in one day. One honest nit: the
card's close-out says "five commits" and lists four arrows plus the
close-out — accurate but easy to misread; no defect found in the work
itself.

## Close-out

(to be written at flip — see final section below)
