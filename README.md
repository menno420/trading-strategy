# trading-lab (menno420/trading-strategy)

> **📦 ARCHIVED 2026-08-23 — the research concluded; unmaintained, read-only.**
> 11 rounds, 5,940 configurations, **0 promoted**, holdout SPENT. The null
> result *is* the deliverable, and archiving preserves it readable while ending
> the impression that a session might pick this up.
> Archiving blocks **writes**, never reads — this repository stays public and
> clonable, every existing link and read path keeps working, and the archive is
> **reversible**. Disposition and the reason for this row:
> [`fleet-manager` § 2 of the 2026-08-22 repo dispositions](https://github.com/menno420/fleet-manager/blob/main/docs/planning/2026-08-22-repo-dispositions.md).

An autonomous research lab that systematically discovers and validates trading strategies
across timeframes — daily and hourly first — on tech stocks and gold/silver. The lab runs
extensive parallel backtesting of known indicators, indicator combinations, and novel
data-derived indicators, producing an evidence ledger of every experiment and a ranked,
honestly-validated strategy report.

**RESEARCH ONLY.** This project never connects to brokers, never executes trades, never
touches real money or credentials. Anything money-adjacent goes to ⚑ needs-owner.

## Where to start

- **[docs/founding-plan.md](docs/founding-plan.md)** — mission, binding methodology
  (anti-overfitting is the core discipline), data policy, experiment ledger, roadmap.
- **[control/README.md](control/README.md)** — fleet coordination protocol: how orders
  arrive (`control/inbox.md`) and how this Project reports back (`control/status.md`).
- **[claims/README.md](claims/README.md)** — lane-claim protocol for parallel sessions:
  one claim file per lane (strategy-family × instrument-set × timeframe).
- **[docs/p1-trend-following-results.md](docs/p1-trend-following-results.md)** — first
  P1 sweep results (trend-following × 8 tickers × daily).
- **[docs/p1-mean-reversion-results.md](docs/p1-mean-reversion-results.md)** — second
  P1 sweep results (mean-reversion × 8 tickers × daily).
- **[docs/p1-trend-hourly-results.md](docs/p1-trend-hourly-results.md)** — third
  P1 sweep results (trend-following × 8 tickers × hourly).
- **[docs/sniper-bucket.md](docs/sniper-bucket.md)** — paper-only design: capped,
  pre-registered opportunistic rule-based entries (no real money, ever).
- **[docs/hybrid-allocator.md](docs/hybrid-allocator.md)** — paper-only design:
  70/20/10 B&H-core / rule-sleeve / cash allocation with mechanical grading.
