# 2026-07-11 — ORDER 009: model-attribution ground truth + P1-drops annotation

> **Status:** `complete` — full session, single PR: session card (this file,
> first commit, carrying the lane's first real family-level Model line),
> card-convention docs updated (null convention "withheld" replaced with
> real-family-name rule in `.sessions/README.md` + `docs/collaboration-model.md`),
> one-line P1-drops annotation in `docs/p1-trend-following-results.md`,
> `control/status.md` acked+done 009. P3 hygiene only: zero `data/**` reads,
> zero backtests, zero bars loaded, holdout untouched (stays SPENT at 13
> reads), paper lane untouched, no research work.

📊 Model: fable-5 · order-009 lane (fired worker session) · start 2026-07-11T04:07:33Z

💡 **Session idea:** execute ORDER 009 (control/inbox.md,
2026-07-11T03:25:25Z, fm ORDER 010 relay) exactly: (1) the session-card
convention carries a `📊 Model:` line — confirmed present (needle enforced
by the kit; convention docs now spell it out); (2) every fired session
records the model family its own harness reports on that line — this
session's harness reports **fable-5**, recorded above (family-level name
only, never a full model-id string; the Routines screen is NOT a reliable
attribution surface); (3) the "withheld per session policy" null convention
is replaced with the real family name in the convention docs — old cards
left byte-untouched as historical record. Plus trading#21 residue: one-line
annotation in docs/p1-trend-following-results.md on the two unexplained P1
drops (AAPL-SMA 1.04*, AAPL-MACD 1.04*) — historical record only,
non-load-bearing.

## Previous-session review

⟲ Previous-session review: the 2026-07-11 kit-upgrade-v1.8.0 session (#51)
hash-logged its banked backup and left an explicit follow-ups list owed to
this repo's lane (diverged `control/README.md` template merge, `kit:`
heartbeat line already correct at v1.8.0, CAPABILITIES landing-constraints
note) — the list format made it trivial to confirm none of those follow-ups
fall inside this order's P3 hygiene scope (they remain owed, untouched
here). What it could have added: the exact upgrade-report section anchor for
the diverged-doc delta, so the future merging session needs zero search.

## Work log

- 2026-07-11T04:07:33Z — landed on origin/main HEAD 39a5646 (ORDER 009 relay
  commit, PR #52); confirmed 39a5646 is the tip. Read control/inbox.md +
  control/status.md; inbox ORDER 009 matches the fired instructions in
  substance — proceed. Branch `order-009-model-attribution`; session card
  first commit. No lane claim: this is a doc-hygiene order, not sweep work —
  no strategy-family × instrument × timeframe lane to claim, and the whole
  order is one squash-merged PR (a claim would net to zero).
- Template/convention survey: no standalone session-card template file
  exists in the repo. The convention lives in `.sessions/README.md`
  (required markers, incl. "Model line") and `docs/collaboration-model.md`
  §Session lifecycle ("Model line reads \"withheld per session policy\"" —
  the null convention ORDER 009 retires); the `📊 Model:` needle itself is
  enforced kit-side (vendored `bootstrap.py`, `MODEL_LINE_NEEDLE`, not
  repo-editable). Both convention docs updated: the Model line records the
  family-level model name the session's own harness reports (e.g.
  `fable-5`), never a full model-id string, never "withheld". Old cards NOT
  edited — their "withheld" lines are the historical record.
- This card's Model line: `fable-5` — the family my own harness/environment
  reports for this fired session. Family-level form only, per the fleet
  standing rule (Q-0262).
- P1-drops annotation: one bullet appended to the Honest-read section of
  `docs/p1-trend-following-results.md`, directly under the Survivors bullet
  — AAPL sma (1.04*) and AAPL macd (1.04*) starred as B&H-beats in the
  headline table yet absent from the Survivors-for-P2 list, no stated drop
  rule; historical-record annotation only, non-load-bearing (program
  complete, holdout spent, P2 selection never re-read). No numbers, tables,
  or P2 selection text altered.
- `control/status.md`: orders line → acked=001–009, done=001–009; updated
  stamp + last-PR line; PAPER LANE OPERATIONAL block, research-round-2
  close-out state, holdout SPENT block, routine state, ⚑ items and
  next-update-by all preserved intact.

## Close-out

**Done:** ORDER 009 in full, single PR —

1. `📊 Model:` line confirmed in the card convention; convention docs
   (`.sessions/README.md`, `docs/collaboration-model.md`) now state it
   explicitly and carry the real-family-name rule.
2. This fired session's committed card (this file) records the harness-
   reported family: **fable-5**.
3. "withheld" null convention replaced in the convention docs; prior cards
   untouched.
4. `docs/p1-trend-following-results.md` carries the one-line P1-drops
   annotation (trading#21 residue, historical record only).
5. `control/status.md` acks 009 done.

**Verify:** `python3 -m pytest -q` → see status health line (recorded
verbatim at commit time: 223 passed). Integrity audit: zero `data/**` reads,
zero market-data access, no ledger rows added, `holdout_unlocked` count
unchanged at 13, `control/inbox.md` byte-untouched, paper-lane files
byte-untouched.

**Next (guard recipe):** none owed by this order. Standing follow-ups from
the v1.8.0 upgrade session remain owed to the lane (see that card's
close-out); first paper-lane grading pass due by 2026-07-17 per protocol §6.

Session end: recorded in the final status commit. Badge stays `complete`.
