#!/usr/bin/env python3
"""Synthetic Monte Carlo for the owner's position-sizing idea — DEV-ONLY / ILLUSTRATIVE.

Companion to docs/research/position-sizing-vet-2026-07-12.md.

RESEARCH-ONLY / DEV-ONLY. This script is a self-contained thought experiment on
SYNTHETIC per-trade returns. It imports NOTHING from the repo — no
``trading_lab`` package, no data loader, no market data, no holdout. It only
uses numpy + the standard library. It makes NO out-of-sample / FINDING /
PROMOTED claim of any kind. It illustrates how three position-sizing rules
behave over synthetic edge scenarios; it does not measure any real strategy's
edge and cannot, because sizing scales edge, it never creates it.

Model (per trade, i.i.d.):
  - r ~ Normal(mu, sigma) is a synthetic per-trade return NET of costs
    (mu already has round-trip costs subtracted; see the doc's cost section).
  - Fractional-f rule: account_{t+1} = account_t * (1 + f * r).
      * Ruin guard: if (1 + f*r) <= 0 the account is wiped to 0 and stays 0
        (a fractional bettor cannot go negative but can be effectively ruined).
  - Fixed-stake rule: account_{t+1} = account_t + stake * r, with stake a
    constant euro amount that never compounds. If the account would drop to
    0 or below it is floored at 0 and stays there (ruin absorbs).

Reported per (scenario, rule, horizon): median and 25/75 quartiles of final
equity from a EUR 100 start, ruin probability (equity < EUR 20 at the horizon),
and median time-to-ruin (first trade index at which equity < EUR 20; NaN if the
median path never ruins).

Deterministic: a fixed master seed makes the whole table reproduce byte-for-byte.

Usage:
  python3 scripts/position_sizing_mc.py            # prints the tables
  python3 scripts/position_sizing_mc.py --json out.json  # also dumps JSON
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, asdict

import numpy as np

# ---------------------------------------------------------------------------
# Parameters (all synthetic / illustrative).
# ---------------------------------------------------------------------------
START_EQUITY = 100.0          # EUR
RUIN_LEVEL = 20.0             # EUR — "effectively ruined" for a small account
FIXED_STAKE = 80.0           # EUR — constant stake for the fixed-stake rule
N_PATHS = 10_000
HORIZONS = (100, 200, 500)
BASE_SIGMA = 0.03            # 3% per-trade vol (base case)
MASTER_SEED = 20260712

# Net-of-cost per-trade edge scenarios (mu). Base case for THIS program is
# mu <= 0: our own holdout cleared 0/13 at the significance bar (t=0.02 on the
# sole rule-pass). See the doc. Positive mus are shown only to bracket the
# behaviour, not as a claim that any real strategy achieves them.
MU_SCENARIOS = {
    "mu=-0.20%": -0.002,
    "mu= 0.00%": 0.0,
    "mu=+0.20%": 0.002,
    "mu=+0.50%": 0.005,
}

# Sizing rules. Fractional rules carry a fraction f; the fixed rule carries None.
RULES = {
    "frac 80%": 0.80,
    "frac 40%": 0.40,
    "fixed EUR80": None,
}


@dataclass
class Cell:
    scenario: str
    rule: str
    horizon: int
    sigma: float
    median_final: float
    q25_final: float
    q75_final: float
    ruin_prob: float
    median_time_to_ruin: float  # NaN-as -1.0 in JSON when >50% never ruin


def _simulate(mu: float, sigma: float, rule_f, horizon: int, seed: int):
    """Return (final_equity[N], time_to_ruin[N]) arrays for one cell.

    ``rule_f`` is the fraction for a fractional rule, or ``None`` for the
    constant fixed-stake rule. ``time_to_ruin`` is the 1-based trade index at
    which equity first drops below RUIN_LEVEL, or ``horizon + 1`` (a sentinel
    meaning "did not ruin within the horizon").
    """
    rng = np.random.default_rng(seed)
    # draws shape (paths, horizon)
    draws = rng.normal(loc=mu, scale=sigma, size=(N_PATHS, horizon))

    equity = np.full(N_PATHS, START_EQUITY, dtype=np.float64)
    ruined = np.zeros(N_PATHS, dtype=bool)
    ttr = np.full(N_PATHS, horizon + 1, dtype=np.int64)  # sentinel = no ruin

    for t in range(horizon):
        r = draws[:, t]
        if rule_f is None:
            # Fixed constant euro stake; does not compound. Absorbed at 0.
            new_equity = equity + FIXED_STAKE * r
        else:
            factor = 1.0 + rule_f * r
            # A factor <= 0 wipes the fractional account this trade.
            factor = np.where(factor <= 0.0, 0.0, factor)
            new_equity = equity * factor
        # Once ruined, stay ruined (absorbing barrier at 0).
        new_equity = np.where(ruined, 0.0, new_equity)
        new_equity = np.maximum(new_equity, 0.0)
        equity = new_equity

        newly_ruined = (~ruined) & (equity < RUIN_LEVEL)
        ttr = np.where(newly_ruined, t + 1, ttr)
        ruined = ruined | (equity < RUIN_LEVEL)

    return equity, ttr


def run(sigma: float = BASE_SIGMA):
    """Run the full grid and return a list of Cell records."""
    cells: list[Cell] = []
    # Deterministic per-cell seeds derived from the master seed so each cell is
    # independent yet fully reproducible.
    ss = np.random.SeedSequence(MASTER_SEED)
    keys = list(MU_SCENARIOS.items())
    child_seeds = ss.spawn(len(keys) * len(RULES) * len(HORIZONS))
    idx = 0
    for scen_name, mu in keys:
        for rule_name, rule_f in RULES.items():
            for horizon in HORIZONS:
                seed = int(child_seeds[idx].generate_state(1)[0])
                idx += 1
                final, ttr = _simulate(mu, sigma, rule_f, horizon, seed)
                ruin_prob = float(np.mean(final < RUIN_LEVEL))
                # Median time-to-ruin over paths that ruined; if <50% ruin the
                # population median TTR is "never" — report -1.0 sentinel.
                ruined_mask = ttr <= horizon
                if ruin_prob >= 0.5:
                    med_ttr = float(np.median(ttr[ruined_mask]))
                else:
                    med_ttr = -1.0
                cells.append(
                    Cell(
                        scenario=scen_name,
                        rule=rule_name,
                        horizon=horizon,
                        sigma=sigma,
                        median_final=float(np.median(final)),
                        q25_final=float(np.percentile(final, 25)),
                        q75_final=float(np.percentile(final, 75)),
                        ruin_prob=ruin_prob,
                        median_time_to_ruin=med_ttr,
                    )
                )
    return cells


def _fmt_eur(x: float) -> str:
    return f"EUR{x:,.2f}"


def _fmt_ttr(x: float) -> str:
    return "never(<50%)" if x < 0 else f"{x:.0f}"


def print_tables(cells, sigma: float):
    print(f"\n=== Synthetic position-sizing Monte Carlo (DEV-ONLY / ILLUSTRATIVE) ===")
    print(
        f"start=EUR{START_EQUITY:.0f}  ruin<EUR{RUIN_LEVEL:.0f}  "
        f"fixed_stake=EUR{FIXED_STAKE:.0f}  sigma={sigma*100:.1f}%/trade  "
        f"paths={N_PATHS:,}  seed={MASTER_SEED}"
    )
    for horizon in HORIZONS:
        print(f"\n--- Horizon = {horizon} trades ---")
        header = (
            f"{'scenario':<11} {'rule':<12} {'median':>13} "
            f"{'q25':>12} {'q75':>13} {'ruinP':>7} {'medTTR':>12}"
        )
        print(header)
        print("-" * len(header))
        for c in cells:
            if c.horizon != horizon:
                continue
            print(
                f"{c.scenario:<11} {c.rule:<12} {_fmt_eur(c.median_final):>13} "
                f"{_fmt_eur(c.q25_final):>12} {_fmt_eur(c.q75_final):>13} "
                f"{c.ruin_prob*100:>6.1f}% {_fmt_ttr(c.median_time_to_ruin):>12}"
            )


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", metavar="PATH", help="also dump results as JSON")
    ap.add_argument(
        "--sigma-sensitivity",
        action="store_true",
        help="also run sigma=2%% and sigma=5%% for the mu=0 base case",
    )
    args = ap.parse_args()

    cells = run(BASE_SIGMA)
    print_tables(cells, BASE_SIGMA)

    extra = {}
    if args.sigma_sensitivity:
        for sig in (0.02, 0.05):
            sub = [c for c in run(sig) if c.scenario == "mu= 0.00%"]
            print(f"\n=== sigma sensitivity (mu=0 only), sigma={sig*100:.0f}% ===")
            for horizon in HORIZONS:
                for c in sub:
                    if c.horizon != horizon:
                        continue
                    print(
                        f"  h={horizon:<4} {c.rule:<12} median={_fmt_eur(c.median_final):>12} "
                        f"ruinP={c.ruin_prob*100:5.1f}%  medTTR={_fmt_ttr(c.median_time_to_ruin)}"
                    )
            extra[f"sigma_{int(sig*100)}pct_mu0"] = [asdict(c) for c in sub]

    if args.json:
        payload = {
            "meta": {
                "label": "DEV-ONLY / ILLUSTRATIVE synthetic Monte Carlo; no market data, no holdout, no OOS claim",
                "start_equity": START_EQUITY,
                "ruin_level": RUIN_LEVEL,
                "fixed_stake": FIXED_STAKE,
                "n_paths": N_PATHS,
                "base_sigma": BASE_SIGMA,
                "horizons": list(HORIZONS),
                "master_seed": MASTER_SEED,
            },
            "cells": [asdict(c) for c in cells],
            **extra,
        }
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"\nwrote {args.json}")


if __name__ == "__main__":
    main()
