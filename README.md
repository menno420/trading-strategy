# trading-lab (menno420/trading-strategy)

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
