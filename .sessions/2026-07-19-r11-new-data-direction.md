# 2026-07-19 — Research-direction sketch: what a "new data source" round would look like

> **Status:** `in-progress`

📊 Model: opus-4.8 · medium · idea/planning

## Why this session exists

Ten rounds and **5,913 registered configs of price/volume-derived indicators
plus their combinations have promoted 0** ([current-state.md](../docs/current-state.md);
[research-program-dashboard.md](../docs/research-program-dashboard.md)). Rounds 9
and 10 closed the confluence family as a proven De Morgan pair: combining
near-independent price-derived signals (0/15 instruments trip the >0.5
correlation flag) cannot manufacture an edge the members individually lack —
the vote is not one signal counted twice, but neither is it a new source of
edge. The honest cross-round conclusion is that the binding constraint is the
**absence of a single source of post-cost edge in price/volume history**, so
the frontier is a genuinely NEW data type, not another combination of the same
inputs (the R10 run card's own "next" note: *"Any further confluence work needs
new OWNER-GATED data, not more dev-surface votes."*).

This session **sketches the candidate new-data-source directions** — a
forward-looking scoping memo, PLAN-ONLY. It writes ONE direction doc
([docs/research-direction-new-data-sources.md](../docs/research-direction-new-data-sources.md))
and adds its reachability pointer to `current-state.md`. It pre-registers NO
round, ingests NO data, adds NO code, adds NO dependency, and runs NOTHING.
Execution of any direction awaits an explicit owner turn (some directions need
owner-provisioned data access). Authorized by the venture-lab coordinator on a
live owner turn (2026-07-19).

POST-HOLDOUT, DEV-ONLY, RESEARCH-ONLY: the holdout stays SPENT, promotion stays
CLOSED, the 5,913/0 tally is unchanged, and the `min_tstat(K)` Bonferroni bar
is UNCHANGED and never lowered.

## Work log

- branch `claude/r11-new-data-direction` cut from origin/main HEAD `2aafa96`
  (#156, the R10 run; program cumulative 5,913 registered configs / 0
  promoted). Born-red FIRST commit: this card.
- `docs/research-direction-new-data-sources.md` (badge `plan`) — the
  direction sketch: why-now, candidate data types (cross-asset/macro,
  fundamentals, flows/positioning) each with thesis + example signals + honest
  access-cost split (self-serve within `requirements.txt` rails vs
  owner-gated), the recommended first step (cross-asset/macro, self-serve), the
  unchanged pre-registration shape + promotion bar, the RESEARCH-ONLY
  guardrails for new data, and the owner-decision list. Plus its reachability
  pointer in `docs/current-state.md`.

💡 **Session idea:** the program now has THREE living "what a future round would
need" menus — the cross-round meta-analysis §"What an owner-gated future round
would need", the retrospective §f–g, and (now) this new-data-source direction
doc — that overlap heavily but are cited independently. A one-screen
`docs/owner-decision-queue.md` index (one row per open owner-gated decision:
the R5-C BTC OOS check, new-ticker/extended-history fetch, point-in-time
fundamentals provisioning, flows/options-feed provisioning — each with its
UNBLOCKS + cost class) would give the owner a single place to say go/no-go
instead of reconstructing the choice from three prose menus. Anchor: the
meta-analysis "What an owner-gated future round would need" list (L242–272) and
this doc's §"Owner decision needed".

## Previous-session review

⟲ PR #156 (`r10-exit-confluence-run`, merged as main `2aafa96`) — executed the
pre-registered inverse-confluence EXIT vote (go-flat when ≥K distinct
thesis-class members agree OUT), the De Morgan DUAL of R9's entry vote:
**11 KEEP-dev / 40 KILL / 9 KILL-SIG of 60 lanes, 0 promoted**, best
informational t **1.04** (BTC-USD SET-3/K=2, the SAME lane/value as R9). The
pre-registered correlation check confirmed the Pearson identity
`corr(1-x,1-y)=corr(x,y)` to 1.3e-15 — the exit-signal correlations EQUAL R9's
position correlations, 0 of 15 trip >0.5, members near-independent. **How this
directly motivates THIS session:** #156 (with R9 before it) fully characterizes
the confluence-over-price-signals family as null from both directions and
records — on its own close-out card — that *"any further confluence work needs
new OWNER-GATED data, not more dev-surface votes"*, and the meta-analysis
states across three round closings that the dev surface is mined out and
"anything further on this surface needs either new data (OWNER-GATED) or a
genuinely different idea class." This session takes the FIRST of those two
permitted moves seriously and scopes what "new data" would actually mean — as
a plan, not a run, because the higher-potential data types need owner-provisioned
access.

## Close-out

**Done** (3 commits):
- (born-red FIRST commit) — this session card (`in-progress` hold).
- (direction-doc commit) — `docs/research-direction-new-data-sources.md`
  (badge `plan`, PLAN-ONLY) + its reachability pointer in
  `docs/current-state.md`. NO code, NO grid, NO runner, NO dependency, NO data
  ingestion, NO round pre-registered.
- (this commit) — close-out flip: badge `in-progress` → `complete`, close-out
  slots resolved.

**Verify:**
- `python3 -m pytest -q` → [[fill: passed count]].
- `python3 bootstrap.py check --strict` → EXIT 0 at flip (the born-red
  in-progress hold clears when the badge flips to `complete`).
- Integrity: the branch diff touches only
  `docs/research-direction-new-data-sources.md` +
  the `docs/current-state.md` pointer + this session card. PLAN ONLY — no
  code / grid / run / verdict / holdout / paper / dependency / trigger changes;
  the holdout was never read, no fetch, `experiments/paper/**` untouched, the
  `min_tstat` bar unchanged, the 5,913/0 tally unchanged, promotion CLOSED / 0
  promoted, no round CLOSED or flipped.

**Next (owner turn):** the owner decides (a) go/no-go on the cross-asset/macro
first step (self-serve, no new data access needed — pre-registerable under the
existing rails on an owner turn), and (b) whether to provision point-in-time
fundamentals or flows/options data for the higher-potential owner-gated
directions (cost/access = owner call). Framed as owner-queue items in the
direction doc's §"Owner decision needed"; nothing is scheduled or run until an
owner turn selects a direction.
