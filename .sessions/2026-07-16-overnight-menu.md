# 2026-07-16 — Overnight planning menu: land the veto-ready RESEARCH-ONLY menu

> **Status:** complete

Born-red HOLD: this card ships in-progress on purpose so the substrate-gate
holds this PR red until the deliverable is fully in place. It flips to
`complete` in the LAST commit of this session, which releases the gate.

- **📊 Model:** Opus 4.8 · medium · idea/planning

💡 **Session idea:** the overnight menu is a large veto-ballot (25
RESEARCH-ONLY proposals sized S/M/L). A recurring friction is that a
veto-ballot and the claim/session grammar drift apart — the menu names real
surfaces (`R7_INSTRUMENTS`, `selection_gate`, `promotion.min_tstat`) but a
future reader can't mechanically tell which proposals are already claimed or
in flight. A durable fix: give each menu item a stable slug so a later
`bootstrap claim <slug>` and this menu share one token, making "is this one
already picked up?" answerable by grep instead of prose.

**Previous-session review:** the most recent complete cards are the R3/R4/R6
research lanes and the main-cron-verify CI card (PR #134, HEAD `6a4d3ab`).
Those close-outs establish the standing rails this menu inherits verbatim —
the selection-fair gate ([D-0002]), the R5-D fixed-config row, the
`reason_class` UNGRADEABLE rollup, and the untouched promotion bar
(`min_tstat` ~2.638 at K=12, promotion CLOSED). This session adds no code and
runs no lane; it only lands planning docs, so it does not touch those rails.

## Six-field summary

- **WHAT:** land the overnight planning menu on main.
- **WHERE:** `planning/2026-07-17-overnight-menu.md` (+ this card, +
  `control/claims/2026-07-16-overnight-menu.md`, + `planning/README.md` index).
- **HOW:** authored under the owner's live overnight order, planning docs
  ONLY — no M/L builds, no lane runs, no holdout spend, no broker/API touch.
- **WHY:** a veto-ready menu deliverable the owner can skim and strike in the
  morning (vote-by-veto over 25 S/M/L RESEARCH-ONLY proposals).
- **UNBLOCKS:** owner morning skim / veto pass over the menu.
- **VERIFY:** `python3 bootstrap.py check --strict` green (only this card's
  designed born-red HOLD outstanding until the flip); menu renders and its
  Status badge sits within the first 12 lines.

## Landing discipline

Born-red HOLD by design: the FIRST commit ships this card in-progress so the
gate stays red and the PR cannot merge prematurely. The card flips to
`complete` in the LAST commit — that release is the only thing that lets the
auto-merge enabler carry the PR in.
