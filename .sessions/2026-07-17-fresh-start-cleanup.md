# 2026-07-17 — fresh-start cleanup (claims · docs · next-tasks · scaffolding)

> **Status:** `complete` — owner-authorized fresh-start cleanup ahead of the
> EAP read-only cutoff (2026-07-21) and the project re-creation as an owner-live
> seat. One ready PR. All changes are docs / control scaffolding only — no
> `src/trading_lab/`, no tests, no verdict touched; holdout SPENT and untouched.
> End 2026-07-17.

- **📊 Model:** opus-4.8 · medium · docs-only

💡 **Session idea:** Treat "wind-down + re-create" as a first-class doc state:
a repo handed to a fresh **owner-live** seat should read clean from
`CONSTITUTION.md` + `current-state.md` + `NEXT-TASKS.md` alone, with every
EAP-era autonomy surface (self-persistence doctrine, auto-merge/"silence =
consent" landing, the `control/` fleet bus) either corrected in place or
banner-deprecated — never silently left to misorient the next agent.

## Previous-session review

The prior session (PR #138, Friday 2026-07-17 in-session grading pass) did the
honest thing well: it ran `grade_paper.py` in-session, recorded the true no-op
(ledger untouched, `paper-0001` still WATCH), and did not fake a graded window.
What it (and the EAP chain generally) left behind was **doc drift + retired
scaffolding**: `current-state.md` lagged `control/status.md` by a day and still
framed the 2026-07-17 grading pass as a future event with a re-arm plan; the
`CONSTITUTION.md` merge doctrine ("open READY → arm auto-merge → it lands
itself") and `ROUTINES.md` wake-chain invariant ("zero armed wakes is a
seat-killing bug") were exactly the instructions the ~2026-07-15 permission
classifier now refuses. **System improvement:** on any autonomy wind-down,
the merge/persistence doctrine and the divergent-ledger pattern are the two
highest-value things to correct first — they actively drive a fresh seat into
denied calls and stale reads.

## Work log

- Deleted 3 stale claim files (`control/claims/2026-07-16-main-cron-verify.md`,
  `2026-07-16-overnight-menu.md`, `friday-grading.md`); `control/claims/README.md`
  kept.
- `docs/current-state.md`: added a "Fresh-start snapshot" (EAP cutoff 2026-07-21,
  autonomy wind-down, re-creation, honest 0-promoted headline, grading no-op
  until ~August); replaced the stale trigger-laden "In flight" block; rewrote
  "Review rhythm" to the owner-live model; marked it the single living ledger.
- `CONSTITUTION.md`: removed the auto-merge / "silence = consent" / "lands
  itself" merge doctrine (reframed to owner-live: owner merges on green CI);
  replaced the unrendered adopt-time template residue in the disagree bullet
  with the intended "source wins, fix drift same session" rule; filled the empty
  "Rails specific to trading-lab" section with the 5 real hard rails.
- `docs/ROUTINES.md`: gutted the self-persistence / wake-chain / dead-man-cron
  doctrine to a deprecation banner + the correct "grading is in-session or
  host-owned, agents arm nothing" guidance.
- Created `docs/NEXT-TASKS.md`: curated the 25-item overnight menu into top next
  steps (Round 7, S-sized guards, one new research direction, onboarding docs)
  + the parked `weekly-grading.yml` executor as a flagged owner decision.
- Deprecation banners on the EAP fleet scaffolding: `control/README.md`,
  `control/status.md`, `docs/succession/NEXT-BOOT.md`. Workflow files left
  intact (not deleted); `control/inbox.md` untouched (CI append-only gate).
- Local verify: `python3 bootstrap.py check --strict` exit 0; full pytest green.
