# Project Closeout — Trading Strategy Research Program

> **Status:** `reference` — final closeout snapshot at HEAD `f2330b6` (2026-07-21). Written for a cold reader: the owner, and any fresh future session that boots this repo knowing nothing of the sessions that produced it. The single living ledger remains [`docs/current-state.md`](./current-state.md); this document is the stable summary that outlives the sessions.

## 1. What this project is, and what it accomplished

This repository is an **honest, offline quantitative-research program**. It asks one question: can any price-derived trading strategy, tuned on historical daily bars, reliably beat buy-and-hold after realistic costs? It answers with a pre-registered, holdout-guarded protocol built so it cannot fool itself.

After eleven rounds, the answer is **no**.

- **Scale:** Rounds 1 through 11 registered and graded **5,940 distinct strategy configurations** across **32 strategy families** (see [`strategy-catalog.md`](./strategy-catalog.md)).
- **Result:** **0 configurations were promoted.** None cleared the pre-registered promotion bar (`promotion.min_tstat` ≈ **2.638** at K=12 independent tests). The single strongest *informational* t-statistic across the whole program was **1.66** (Round 5, a silver `williams_r_reversion` grid neighbor) — well short of the bar, and informational only. The per-round scoreboard reconciles exactly to 5,940 / 0 in [`research-program-dashboard.md`](./research-program-dashboard.md).
- **The finding is the negative result.** "Nothing price-derived beat buy-and-hold after costs" is a real, defensible conclusion — the cross-round synthesis is in [`cross-round-meta-analysis.md`](./cross-round-meta-analysis.md).

**The confluence question (Rounds 9 & 10).** A natural hope: combine weak signals — require several indicators to *agree* before acting. Round 9 tested **confluence entry** (only enter when ≥K signals agree); Round 10 tested its **mathematical dual, an inverse-confluence exit** (go flat when ≥K signals agree). Both are null, and the program documents *why*: gating on agreement mostly reduces exposure without improving per-trade edge, so after costs it tracks or lags buy-and-hold. See the Round 9 and Round 10 results docs.

**Cross-asset regime conditioning (Round 11).** The last round asked whether *external* information helps where price alone did not: it conditioned a risk leg's exposure continuously on a **causal** cross-asset regime score (rolling-percentile-rank, built only from the existing daily cache, no look-ahead). 27 configs, **0 promoted** — null, with mechanism documented ([`research-round-11-plan.md`](./research-round-11-plan.md) + results). See run PRs #158–#159.

**Where to go next (scoped, not executed).** [`research-direction-new-data-sources.md`](./research-direction-new-data-sources.md) is a plan-only memo: the remaining unexplored lever is *genuinely new data*, not more price transforms — cross-asset / macro-regime data (self-serve from existing caches) versus **fundamentals and flows/positioning** (owner-gated, needs provisioning). No round is pre-registered; execution awaits an explicit owner turn.

**The paper lane.** Separately from the offline research, the repo runs a **research-only paper-trading lane**: one open position record, `paper-0001` (a `donchian_AAPL_daily` config on AAPL daily), currently **WATCH / FLAT / $0 deployed**, graded weekly. It has produced **0 verdicts** so far — the first evaluable window lands **~early August 2026**. No real money is or was deployed; the repo has no exchange-write capability.

## 2. Current true state (verified live at HEAD `f2330b6`, 2026-07-21)

| Fact | Value | Source of truth |
|---|---|---|
| Test suite | **849 passed** | `python3 -m pytest -q` (the CI `tests` check) |
| Repo self-check | **exit 0 — all checks passed** | `python3 bootstrap.py check --strict` |
| Rounds / configs / promoted | **11 / 5,940 / 0** | `research-program-dashboard.md` |
| Strategy families | **32**, all dev-only | `strategy-catalog.md` |
| Promotion | **CLOSED** | `current-state.md`, dashboard |
| Holdout | **SPENT** (13 one-shot reads, ORDER 008) | dashboard, `research-round-2.md`, `holdout-enforcement.md` |
| Paper ledger | `paper-0001` **WATCH**, 0 verdicts | `experiments/paper/ledger.md` |
| Live trading capability | **none** — RESEARCH-ONLY | `CONSTITUTION.md` |

The holdout window is spent and stays spent: it was a one-shot budget (`HOLDOUT_START = 2025-01-09`, enforced in `trading_lab.data.load_ohlcv`). Promotion is closed. Neither can be reopened to "try again" without invalidating the result.

## 3. Continuation — what a future session or the owner does next

Priority order, with exact resume steps.

**(a) Weekly paper-lane grading — the one recurring task.**
The paper lane is graded every Friday. Until now a scheduled cron fired a session to run it; **that cron dies when the program closes (2026-07-21).** From **Friday 2026-07-24** onward, grading must be run **manually**:

```
cd trading-strategy
git fetch origin && git reset --hard origin/main
python3 scripts/grade_paper.py        # no args — that IS the contract
git status                            # commit + PR only if the ledger changed
```

`grade_paper.py` grades every closed, ungraded window in `experiments/paper/ledger.md`, appends verdict fields, and flips only those rows to GRADED (idempotent — it never re-touches a verdict or mutates a WATCH/ENTRY row; it reads market data only via `trading_lab.data.load_paper_ohlcv`, which cannot see the holdout). **Expected result every week until ~early August 2026: a true no-op** (`paper-0001` stays WATCH, no verdict appended, exit 0). The first real grade lands around the 16th paper-lane bar, ~early August 2026. If it ever appends a row, commit it on a `claude/*` branch and land via the normal path.

**(b) The owner-gated data-provisioning decision — the one standing choice.**
The price-derived space is exhausted; the next lever is new data, and it forks:
- *Self-serve:* more cross-asset / macro-regime features from existing caches (a session can pre-register and run this with no owner action).
- *Owner-gated:* **fundamentals** (earnings, valuation) and **flows/positioning** — these need the owner to provision a data source/credentials. See [`research-direction-new-data-sources.md`](./research-direction-new-data-sources.md). Nothing is pre-registered; this is a decision, not pending work.

**(c) The RESEARCH-ONLY rail — a standing constraint.**
This repo grades paper strategies and researches offline. It has **no exchange-write capability**, and adding one (live API config, broker/exchange promotion) ships **only on an explicit owner turn**. A spent holdout stays spent; the promotion bar is never lowered. See `CONSTITUTION.md`.

**Open PR at closeout.** PR [#160](https://github.com/menno420/trading-strategy/pull/160) (a substrate-kit vendored-dist upgrade) is **PARKED, not abandoned.** It reds `substrate-gate` on lines that are deliberate owner-live governance decisions (not checker false positives), so it is not auto-mergeable. Resume: an owner/resident either adopts the flagged governance lines or closes the PR — do not force-merge it.

## 4. Owner walkthrough (plain language)

**What this repo proves.** Eleven rounds of honest research asked whether a computer can find a price-chart trading rule that beats simply buying and holding, after real trading costs. It can't — not among 5,940 configurations across 32 strategy families. **That result protects your money:** it is direct evidence not to trust a "backtested edge" just because it looks good. This program built thousands of good-looking edges under a protocol designed to catch the ones that only *look* good — and none survived.

**Where to read it** (no code needed):
- The scoreboard: [`research-program-dashboard.md`](./research-program-dashboard.md) — every round, every count, 5,940 / 0.
- The "why": [`cross-round-meta-analysis.md`](./cross-round-meta-analysis.md).
- Any single round, e.g. the last: [`research-round-11-plan.md`](./research-round-11-plan.md).

**What the paper lane is.** A single make-believe position (`paper-0001`) tracked on paper with **no real money**, so a strategy can be watched in the open without risking anything. It's flat today and graded weekly; it starts producing pass/fail marks around early August.

**The one decision that's yours.** Everything price-based has been tried. To learn something new, the program needs **new kinds of data** — company fundamentals, or market flow/positioning data — and buying and wiring those up is a call only you can make (see [the data-direction memo](./research-direction-new-data-sources.md)). The honest default: **it is fine to let this rest.** The negative result stands on its own.

## 5. Working this repo with a fresh session

- **Boot route:** read `CONSTITUTION.md`, then **`current-state.md` — that is THE living ledger.** The `control/` tree, `docs/succession/`, and `docs/ROUTINES.md` are **retired** (each carries a deprecation banner) — ignore them. This closeout is the stable summary; `current-state.md` is the live one.
- **Verify commands:** `python3 -m pytest -q` (expect 849 passed) and `python3 bootstrap.py check --strict` (expect exit 0).
- **Landing path:** work on a `claude/<slug>` branch; main moves by PR only. Open a **born-red session-log card** (`.sessions/YYYY-MM-DD-<slug>.md`, `> **Status:** `in-progress``) as the FIRST commit to hold the PR red, mark the PR READY immediately, and flip the card to `complete` as the deliberate LAST step. Required checks: **`substrate-gate`** (docs / session-log gate; the born-red card holds it red until flipped) + **`tests`** (`pytest`). The `auto-merge-enabler` workflow squash-merges green `claude/*` PRs.
- **Gotchas that will bite you if you skip them:**
  - **Pre-registration before running.** A round's plan (thesis, grid, promotion rule) is committed *before* its results — plan-before-outcome is enforced by convention; results without a prior registered plan don't count.
  - **The promotion bar is never lowered**, and the **holdout is spent** — you cannot reopen either to chase a result.
  - **Never invent trades or verdicts.** The paper ledger is append-only and committed before outcomes; `grade_paper.py` is the only thing that writes verdicts.

---

*This is a closeout snapshot. The repository continues to live at its `main` branch; `current-state.md` remains authoritative for anything that changes after 2026-07-21.*
