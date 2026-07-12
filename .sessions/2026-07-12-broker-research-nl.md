# 2026-07-12 — broker-research: NL-legal small-account custom-bot landscape

> **Status:** `complete` — RESEARCH-ONLY lane. Merged five desk-research files
> (four broker clusters + NL crypto-legality) into one cited landscape doc for a
> small-account (€100–200) custom-bot owner:
> `docs/research/broker-bot-options-nl-2026-07-12.md` (indexed from
> `docs/research/README.md`). Born-red first commit → flipped complete as the
> deliberate last step. NO accounts created, NO trades, NO backtests, zero
> `data/**` reads, holdout untouched, `control/inbox.md` + `control/status.md`
> byte-untouched.

📊 Model: opus · broker-research-nl lane (fired worker session, Money-seat coordinator direction) · start 2026-07-12T11:05:45Z

💡 **Session idea:** land ONE evidence-based, ranked broker/exchange landscape
for the owner's exact use case — NL resident, €100–200 start, custom bot, one
open trade at a time — at `docs/research/broker-bot-options-nl-2026-07-12.md`.
Preserve every source URL + "accessed 2026-07-12" citation and every UNVERIFIED
flag from the source files. Headline finding: at this account size the
per-order MINIMUM commission (IBKR family, Saxo) is the killer, so the lowest-
friction path is **Bitvavo** (NL-domiciled MiCA CASP, ~0.50% round-trip, no
per-order minimum), runner-up **MEXEM** for regulated real equities (~2.0%).
Research-only: this doc identifies the cheapest place to run a bot, NOT evidence
that a profitable bot exists — our own program found 0 of 13 strategies beat
buy-and-hold with significance on the one-shot holdout. Owner-action rows are
FLAG-ONLY; going live needs an explicit owner order lifting the RESEARCH-ONLY
rail.

## Previous-session review

⟲ Previous-session review: the 2026-07-12 ORDER 011 ack session (#67) did
clean record-keeping — born-red card first commit, surgical `control/status.md`
edit last, independent GitHub verification of terminal PR states (Q-0120:
record reality, not the order's stale premise), zero data reads. Its discipline
worth carrying here: cite the primary source for every non-obvious claim and
flag discrepancies rather than smoothing them over. What it could not help with:
this is a fresh research-synthesis lane (no prior broker doc exists), so there
is no earlier card anchor to reuse — the source files are the ground truth.

## Work log

- 2026-07-12T11:05:45Z — landed on origin/main HEAD `3ba081c`; `bootstrap.py
  check --strict` green on the clean tree. Branch `claude/broker-research-nl`;
  this card first commit (born-red). Read `control/inbox.md` read-only (never
  edited). Merged doc → `docs/research/broker-bot-options-nl-2026-07-12.md`.

## Close-out

**Done:** merged NL-broker landscape doc landed —

1. `docs/research/broker-bot-options-nl-2026-07-12.md` — ranked landscape
   (Bitvavo #1, MEXEM runner-up), fee-reality section, honest-expectations
   caveat, FLAG-ONLY owner-action rows, all citations + UNVERIFIED flags
   carried forward.
2. `.sessions/2026-07-12-broker-research-nl.md` — this card (born-red first
   commit → flipped complete last).

**Verify:** `python3 bootstrap.py check --strict` → green after this card flips
complete. Integrity audit: zero `data/**` reads, zero market-data access, no
backtests, no accounts created, no trades, holdout untouched, `control/inbox.md`
+ `control/status.md` byte-untouched.

**Next (guard recipe):** none owed. Going live requires a separate explicit
owner order lifting this lane's RESEARCH-ONLY rail — no agent self-activates it.

Session end: badge flips `complete` in the final content commit.
