"""Parameter grids for the P1 known-indicator sweeps.

Grids are defined ONCE here so the sweep scripts, the ledger records and the
tests all count the same variants — the multiple-testing discipline in
docs/founding-plan.md requires the number of variants tried to be reported
alongside any result, so the count must be reproducible.

Each family's grid is bounded (roughly 40-80 variants per family) and
constraint-filtered: combinations the strategy itself would reject
(``fast >= slow``, ``exit > entry``) are excluded up front, so
:func:`variants` yields exactly the configurations that actually run.
"""

from __future__ import annotations

from itertools import product
from typing import Callable

# ---------------------------------------------------------------------------
# P1 trend-following family (lane: trend-following × all-8 × daily)
# ---------------------------------------------------------------------------
# Axes deliberately span fast/slow lookbacks used in the classic literature
# (golden cross 50/200, MACD 12/26/9, turtle Donchian 20/10 and 55/20) plus a
# sensible spread around them. Kept bounded on purpose: every extra variant
# raises the multiple-testing burden on any winner.

_TREND_AXES: dict[str, dict[str, list]] = {
    "sma_crossover": {"fast": [5, 10, 15, 20, 25, 30, 40, 50],
                      "slow": [30, 50, 75, 100, 150, 200]},
    "ema_crossover": {"fast": [5, 10, 15, 20, 25, 30, 40, 50],
                      "slow": [30, 50, 75, 100, 150, 200]},
    "macd": {"fast": [5, 8, 12, 16], "slow": [21, 26, 35, 50],
             "signal": [5, 9, 13]},
    "donchian": {"entry": [10, 15, 20, 30, 40, 55, 80, 100],
                 "exit": [5, 10, 15, 20, 30, 40, 55]},
}

_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "sma_crossover": lambda p: p["fast"] < p["slow"],
    "ema_crossover": lambda p: p["fast"] < p["slow"],
    "macd": lambda p: p["fast"] < p["slow"],
    "donchian": lambda p: p["exit"] <= p["entry"],
}

TREND_FOLLOWING_FAMILIES = tuple(_TREND_AXES)


def variants(family: str) -> list[dict]:
    """All valid parameter dicts for ``family``, constraint-filtered, in a
    deterministic order."""
    try:
        axes = _TREND_AXES[family]
    except KeyError:
        raise ValueError(f"unknown sweep family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def variants_per_family() -> dict[str, int]:
    """Variant counts by family (multiple-testing bookkeeping)."""
    return {fam: len(variants(fam)) for fam in TREND_FOLLOWING_FAMILIES}


def total_variants() -> int:
    """Total distinct configurations in the trend-following sweep."""
    return sum(variants_per_family().values())


# ---------------------------------------------------------------------------
# P1 video-strategy lane (lane: video-strategy × BTC-USD × daily)
# ---------------------------------------------------------------------------
# Competing interpretations of the DaviddTech video's under-specified rules
# (docs/research/video-source-2026-07-09.md). The video never states the
# SuperTrend/EMA/MACD parameters, so the SuperTrend/MACD axes bracket common
# published defaults (period 7/10/14, multiplier 2/3/4; MACD 12-26-9 and the
# faster 8-21-5; EMA trend filter 100/200). The dual-EMA control's axes are
# the video's OWN stated sweep bounds coarsened (slow 110→400, fast 10→100)
# and include the video's stated winner slow=400 / fast=45. Kept bounded on
# purpose: every extra variant raises the multiple-testing burden.

_VIDEO_MACD_TRIPLES = [
    {"macd_fast": 12, "macd_slow": 26, "macd_signal": 9},
    {"macd_fast": 8, "macd_slow": 21, "macd_signal": 5},
]
_VIDEO_ST_PERIODS = [7, 10, 14]
_VIDEO_ST_MULTS = [2.0, 3.0, 4.0]
_VIDEO_EMA_LENS = [100, 200]
_VIDEO_CONTROL_SLOW = [110, 200, 300, 400]
_VIDEO_CONTROL_FAST = [10, 25, 45, 70, 100]

VIDEO_STRATEGY_FAMILIES = ("supertrend_flip", "macd_supertrend",
                           "ema_crossover")


def _video_supertrend_grid() -> list[dict]:
    """Shared grid for both SuperTrend/EMA/MACD interpretations: the MACD
    triple varies as a paired unit (not a full product) to stay bounded."""
    return [
        {"st_period": p, "st_mult": m, "ema_len": e, **triple}
        for p in _VIDEO_ST_PERIODS
        for m in _VIDEO_ST_MULTS
        for e in _VIDEO_EMA_LENS
        for triple in _VIDEO_MACD_TRIPLES
    ]


def video_variants(family: str) -> list[dict]:
    """All parameter dicts for a video-lane ``family``, deterministic order."""
    if family in ("supertrend_flip", "macd_supertrend"):
        return _video_supertrend_grid()
    if family == "ema_crossover":
        return [{"fast": f, "slow": s}
                for s in _VIDEO_CONTROL_SLOW for f in _VIDEO_CONTROL_FAST
                if f < s]
    raise ValueError(f"unknown video-lane family {family!r}")


def video_variants_per_family() -> dict[str, int]:
    """Video-lane variant counts by family (multiple-testing bookkeeping)."""
    return {fam: len(video_variants(fam)) for fam in VIDEO_STRATEGY_FAMILIES}


def video_total_variants() -> int:
    """Total distinct configurations in the video-strategy sweep."""
    return sum(video_variants_per_family().values())

# ---------------------------------------------------------------------------
# P1 mean-reversion family (lane: mean-reversion × all-8 × daily)
# ---------------------------------------------------------------------------
# Three sub-families: RSI-threshold reversion (the P0 baseline strategy,
# reused — periods bracket the classic Wilder 14 and the short-horizon 2/3
# of the Connors literature), Bollinger/z-score band reversion, and
# short-horizon pullback entries with and without a long-term trend filter
# (trend_len=0 disables the filter). Kept bounded on purpose: every extra
# variant raises the multiple-testing burden on any winner. Mean-reversion
# trades often — the grids deliberately include slower exits so the sweep can
# see whether turnover/costs are the binding constraint.

_MEAN_REVERSION_AXES: dict[str, dict[str, list]] = {
    "rsi_mean_reversion": {"period": [2, 3, 5, 14],
                           "oversold": [10, 20, 25, 30],
                           "overbought": [50, 60, 70]},
    "bollinger_reversion": {"lookback": [10, 15, 20, 30],
                            "z_entry": [1.0, 1.5, 2.0, 2.5],
                            "z_exit": [0.0, 0.5, 1.0]},
    "pullback": {"entry_lookback": [3, 5, 7, 10],
                 "exit_len": [3, 5, 7, 10],
                 "trend_len": [0, 100, 200]},
}

_MEAN_REVERSION_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "rsi_mean_reversion": lambda p: p["oversold"] < p["overbought"],
    "bollinger_reversion": lambda p: p["z_exit"] > -p["z_entry"],
    "pullback": lambda p: True,
}

MEAN_REVERSION_FAMILIES = tuple(_MEAN_REVERSION_AXES)


def mean_reversion_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a mean-reversion ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _MEAN_REVERSION_AXES[family]
    except KeyError:
        raise ValueError(f"unknown mean-reversion family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _MEAN_REVERSION_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def mean_reversion_variants_per_family() -> dict[str, int]:
    """Mean-reversion variant counts by family (multiple-testing bookkeeping)."""
    return {fam: len(mean_reversion_variants(fam))
            for fam in MEAN_REVERSION_FAMILIES}


def mean_reversion_total_variants() -> int:
    """Total distinct configurations in the mean-reversion sweep."""
    return sum(mean_reversion_variants_per_family().values())


# ---------------------------------------------------------------------------
# Round 2 slice R1: vol_filtered_trend (lane: r2-vol_filtered_trend × 4 × daily)
# ---------------------------------------------------------------------------
# Grid frozen by the pre-registration (docs/research-round-2.md §3a) — any
# change requires a committed amendment to that doc BEFORE running:
# fast ∈ {10, 20}, slow ∈ {50, 100, 200} with fast < slow, filter ∈ {on, off}
# → 12 variants/instrument × 4 instruments = 48 registered configs. The
# vol-filter windows (20-bar realized vol vs its trailing 252-bar median)
# are frozen in the strategy's defaults and are NOT swept.

_R2_VOL_TREND_AXES: dict[str, dict[str, list]] = {
    "vol_filtered_trend": {"fast": [10, 20],
                           "slow": [50, 100, 200],
                           "vol_filter": [True, False]},
}

_R2_VOL_TREND_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "vol_filtered_trend": lambda p: p["fast"] < p["slow"],
}

R2_VOL_TREND_FAMILIES = tuple(_R2_VOL_TREND_AXES)

# Instruments frozen by the pre-registration (§3a).
R2_VOL_TREND_INSTRUMENTS = ("AAPL", "MSFT", "NVDA", "GLD")


def r2_vol_trend_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-2 R1 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R2_VOL_TREND_AXES[family]
    except KeyError:
        raise ValueError(f"unknown R1 family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R2_VOL_TREND_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r2_vol_trend_variants_per_family() -> dict[str, int]:
    """R1 variant counts by family (multiple-testing bookkeeping)."""
    return {fam: len(r2_vol_trend_variants(fam))
            for fam in R2_VOL_TREND_FAMILIES}


def r2_vol_trend_total_configs() -> int:
    """Total registered R1 configs: variants × instruments (Round-2
    accounting counts each instrument × grid point as one config — the
    pre-registration's 48)."""
    return (sum(r2_vol_trend_variants_per_family().values())
            * len(R2_VOL_TREND_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 2 slice R2: keltner_breakout (lane: r2-keltner_breakout × 4 × daily)
# ---------------------------------------------------------------------------
# Grid frozen by the pre-registration (docs/research-round-2.md §3b) — any
# change requires a committed amendment to that doc BEFORE running:
# n ∈ {20, 50}, m ∈ {1.5, 2.0, 2.5} → 6 variants/instrument × 4 instruments
# = 24 registered configs.

_R2_KELTNER_AXES: dict[str, dict[str, list]] = {
    "keltner_breakout": {"n": [20, 50], "m": [1.5, 2.0, 2.5]},
}

_R2_KELTNER_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "keltner_breakout": lambda p: True,
}

R2_KELTNER_FAMILIES = tuple(_R2_KELTNER_AXES)

# Instruments frozen by the pre-registration (§3b).
R2_KELTNER_INSTRUMENTS = ("BTC-USD", "META", "AMZN", "SLV")


def r2_keltner_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-2 R2 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R2_KELTNER_AXES[family]
    except KeyError:
        raise ValueError(f"unknown R2 family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R2_KELTNER_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r2_keltner_variants_per_family() -> dict[str, int]:
    """R2 variant counts by family (multiple-testing bookkeeping)."""
    return {fam: len(r2_keltner_variants(fam))
            for fam in R2_KELTNER_FAMILIES}


def r2_keltner_total_configs() -> int:
    """Total registered R2 configs: variants × instruments (Round-2
    accounting counts each instrument × grid point as one config — the
    pre-registration's 24)."""
    return (sum(r2_keltner_variants_per_family().values())
            * len(R2_KELTNER_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 2 slice R3: xsec_momentum (lane: r2-xsec_momentum × 9-basket × daily)
# ---------------------------------------------------------------------------
# Grid frozen by the pre-registration (docs/research-round-2.md §3c) — any
# change requires a committed amendment to that doc BEFORE running:
# L ∈ {63, 126, 252}, k ∈ {2, 3} → 6 registered configs. First
# PORTFOLIO-level lane: each config is ONE portfolio rule over all 9 cached
# daily instruments, so configs = grid points (NOT × instruments). The
# 21-bar rebalance interval is frozen in the pre-registration and NOT swept.

_R2_XSEC_AXES: dict[str, dict[str, list]] = {
    "xsec_momentum": {"L": [63, 126, 252], "k": [2, 3]},
}

_R2_XSEC_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "xsec_momentum": lambda p: True,
}

R2_XSEC_FAMILIES = tuple(_R2_XSEC_AXES)

# All 9 cached daily instruments (pre-reg §1, §3c), alphabetical — the
# column order of the aligned panel (also the deterministic ranking
# tie-break order in strategies/xsec_momentum.py).
R2_XSEC_INSTRUMENTS = ("AAPL", "AMZN", "BTC-USD", "GLD", "GOOGL", "META",
                       "MSFT", "NVDA", "SLV")

# Frozen by the pre-registration (§3c): rebalance every 21 bars. Not swept.
R2_XSEC_REBALANCE_EVERY = 21


def r2_xsec_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-2 R3 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R2_XSEC_AXES[family]
    except KeyError:
        raise ValueError(f"unknown R3 family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R2_XSEC_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r2_xsec_variants_per_family() -> dict[str, int]:
    """R3 variant counts by family (multiple-testing bookkeeping)."""
    return {fam: len(r2_xsec_variants(fam))
            for fam in R2_XSEC_FAMILIES}


def r2_xsec_total_configs() -> int:
    """Total registered R3 configs. Portfolio lane: ONE config per grid
    point over the whole 9-instrument basket (the pre-registration's 6) —
    unlike R1/R2, instruments do NOT multiply the count."""
    return sum(r2_xsec_variants_per_family().values())
