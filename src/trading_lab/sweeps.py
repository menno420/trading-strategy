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


# ---------------------------------------------------------------------------
# Round 3: stochastic + Williams %R reversion (lane: r3-stoch-willr × all-8
# × daily — ORDER 012 night-run, post-holdout DEV-ONLY, promotion closed)
# ---------------------------------------------------------------------------
# Two classic oversold-oscillator reversion families, declared here BEFORE
# the sweep ran. Axes bracket the published defaults (14-bar window, 20/80
# stochastic bands, -80/-20 Williams bands) with slower windows and both a
# deep and a shallow oversold line. Williams %R is the unsmoothed complement
# of the stochastic (%R = %K - 100 at d_period=1); the stochastic arm is
# smoothed (d_period=3, frozen, NOT swept), so the pair probes smoothed vs
# raw oscillator reversion. Kept bounded on purpose: every extra variant
# raises the multiple-testing burden on any winner.

_R3_STOCH_WILLR_AXES: dict[str, dict[str, list]] = {
    "stochastic_reversion": {"k_period": [14, 21, 28],
                             "buy_below": [10, 20],
                             "sell_above": [70, 80]},
    "williams_r_reversion": {"period": [14, 21, 28],
                             "buy_below": [-90, -80],
                             "sell_above": [-30, -20]},
}

_R3_STOCH_WILLR_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "stochastic_reversion": lambda p: p["buy_below"] < p["sell_above"],
    "williams_r_reversion": lambda p: p["buy_below"] < p["sell_above"],
}

R3_STOCH_WILLR_FAMILIES = tuple(_R3_STOCH_WILLR_AXES)

# The full 8-ticker universe (config.UNIVERSE order), daily bars.
R3_STOCH_WILLR_INSTRUMENTS = ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                              "META", "GLD", "SLV")


def r3_stoch_willr_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_STOCH_WILLR_AXES[family]
    except KeyError:
        raise ValueError(f"unknown R3 stoch-willr family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_STOCH_WILLR_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_stoch_willr_variants_per_family() -> dict[str, int]:
    """Round-3 variant counts by family (multiple-testing bookkeeping)."""
    return {fam: len(r3_stoch_willr_variants(fam))
            for fam in R3_STOCH_WILLR_FAMILIES}


def r3_stoch_willr_total_configs() -> int:
    """Total registered Round-3 configs: variants × instruments (each
    instrument × grid point counts as one config, as in Round 2 R1/R2)."""
    return (sum(r3_stoch_willr_variants_per_family().values())
            * len(R3_STOCH_WILLR_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 2: ROC momentum + ADX-filtered SMA (lane: r3-roc-adx × all-8
# × daily — ORDER 012 night-run, post-holdout DEV-ONLY, promotion closed)
# ---------------------------------------------------------------------------
# Two classic trend/momentum families, declared here BEFORE the sweep ran.
# roc_momentum axes bracket the canonical time-series-momentum lookbacks
# (quarter/half-year/year: 63, 126, 252 bars) with a simple 0/±5% hysteresis
# band around the classic zero-threshold rule (entry == exit == 0 IS the
# classic rule and is in the grid). adx_filtered_sma reuses the Round-2 R1
# SMA axes (fast {10, 20} × slow {50, 100, 200}) with the two most-cited ADX
# trend thresholds (20, 25); the ADX period is frozen at the Wilder default
# 14 and NOT swept (mirroring the frozen stochastic d_period in the
# r3-stoch-willr lane). Kept bounded on purpose: every extra variant raises
# the multiple-testing burden on any winner.

_R3_ROC_ADX_AXES: dict[str, dict[str, list]] = {
    "roc_momentum": {"lookback": [63, 126, 252],
                     "entry": [0.0, 0.05],
                     "exit": [-0.05, 0.0]},
    "adx_filtered_sma": {"fast": [10, 20],
                         "slow": [50, 100, 200],
                         "adx_min": [20.0, 25.0]},
}

_R3_ROC_ADX_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "roc_momentum": lambda p: p["exit"] <= p["entry"],
    "adx_filtered_sma": lambda p: p["fast"] < p["slow"],
}

R3_ROC_ADX_FAMILIES = tuple(_R3_ROC_ADX_AXES)

# The full 8-ticker universe (config.UNIVERSE order), daily bars.
R3_ROC_ADX_INSTRUMENTS = ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                          "META", "GLD", "SLV")


def r3_roc_adx_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-2 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_ROC_ADX_AXES[family]
    except KeyError:
        raise ValueError(f"unknown R3 roc-adx family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_ROC_ADX_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_roc_adx_variants_per_family() -> dict[str, int]:
    """Round-3 slice-2 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_roc_adx_variants(fam))
            for fam in R3_ROC_ADX_FAMILIES}


def r3_roc_adx_total_configs() -> int:
    """Total registered Round-3 slice-2 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the r3-stoch-willr lane)."""
    return (sum(r3_roc_adx_variants_per_family().values())
            * len(R3_ROC_ADX_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 3: NEW TICKERS (lane: r3-new-tickers × 6 new instruments
# × daily — ORDER 012 night-run, post-holdout DEV-ONLY, promotion closed)
# ---------------------------------------------------------------------------
# This slice expands the INSTRUMENT surface, not the strategy library: three
# existing, already-tested families with small pre-declared sub-grids of
# their published axes, run over six instruments the lab has never touched —
# SPY (broad market), QQQ (large-cap growth), TSLA (mega-cap not in the
# universe), JPM (financials), XOM (energy), TLT (long-duration rates) —
# chosen to diversify the tech-heavy 8-ticker universe. The instruments are
# deliberately NOT added to config.UNIVERSE (frozen; other sweeps depend on
# it) — they are lane-local here. Caches were fetched via the sanctioned
# trading_lab.data.fetch_ohlcv path only. Grids declared here BEFORE the
# sweep ran; each is a subset of the family's existing published axes
# (donchian: turtle 20/55 anchor; sma_crossover: the Round-2 R1 axes;
# rsi_mean_reversion: Wilder 14 / Connors short-horizon anchors). Kept
# bounded on purpose: every extra variant raises the multiple-testing
# burden on any winner.

_R3_NEW_TICKERS_AXES: dict[str, dict[str, list]] = {
    "donchian": {"entry": [20, 40, 55], "exit": [10, 20]},
    "sma_crossover": {"fast": [10, 20], "slow": [50, 100, 200]},
    "rsi_mean_reversion": {"period": [2, 5, 14],
                           "oversold": [30],
                           "overbought": [60, 70]},
}

_R3_NEW_TICKERS_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "donchian": lambda p: p["exit"] <= p["entry"],
    "sma_crossover": lambda p: p["fast"] < p["slow"],
    "rsi_mean_reversion": lambda p: p["oversold"] < p["overbought"],
}

R3_NEW_TICKERS_FAMILIES = tuple(_R3_NEW_TICKERS_AXES)

# The six NEW instruments (all fetch probes succeeded 2026-07-13; zero
# data-unavailable rows). Deliberately disjoint from config.UNIVERSE.
R3_NEW_TICKERS_INSTRUMENTS = ("SPY", "QQQ", "TSLA", "JPM", "XOM", "TLT")


def r3_new_tickers_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-3 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_NEW_TICKERS_AXES[family]
    except KeyError:
        raise ValueError(f"unknown R3 new-tickers family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_NEW_TICKERS_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_new_tickers_variants_per_family() -> dict[str, int]:
    """Round-3 slice-3 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_new_tickers_variants(fam))
            for fam in R3_NEW_TICKERS_FAMILIES}


def r3_new_tickers_total_configs() -> int:
    """Total registered Round-3 slice-3 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes). The per-instrument buy-and-hold
    baseline is the benchmark, not a searched configuration, and is not
    counted."""
    return (sum(r3_new_tickers_variants_per_family().values())
            * len(R3_NEW_TICKERS_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 4: Aroon trend + CCI reversion (lane: r3-aroon-cci ×
# 12-ticker mixed set × daily — ORDER 012 night-run, post-holdout DEV-ONLY,
# promotion closed)
# ---------------------------------------------------------------------------
# Two classic-indicator families, declared here BEFORE the sweep ran.
# aroon_trend axes bracket the published Aroon windows (Chande's 25 plus a
# faster 14 and a slower 50) with a simple 0/±50 hysteresis band around the
# classic zero-threshold rule — entry == exit == 0 IS the classic
# Aroon-Up/Aroon-Down cross and is committed in the grid as the
# within-family control arm (adopting the slice-2 card's convention:
# banded/gated grids must include their neutral arm). cci_reversion axes
# bracket Lambert's default 20-bar window (14/20/28) with a deep and a
# shallow oversold line (−150/−100) and both canonical exits (back to the
# mean, 0; or overbought, +100). Kept bounded on purpose: every extra
# variant raises the multiple-testing burden on any winner.

_R3_AROON_CCI_AXES: dict[str, dict[str, list]] = {
    "aroon_trend": {"period": [14, 25, 50],
                    "entry": [0.0, 50.0],
                    "exit": [-50.0, 0.0]},
    "cci_reversion": {"period": [14, 20, 28],
                      "buy_below": [-150, -100],
                      "sell_above": [0, 100]},
}

_R3_AROON_CCI_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "aroon_trend": lambda p: p["exit"] <= p["entry"],
    "cci_reversion": lambda p: p["buy_below"] < p["sell_above"],
}

R3_AROON_CCI_FAMILIES = tuple(_R3_AROON_CCI_AXES)

# The 12-ticker mixed set: the full frozen 8-ticker universe
# (config.UNIVERSE order) PLUS four of the slice-3 new instruments
# (SPY, QQQ, TSLA, TLT — broad market, large-cap growth, mega-cap outside
# the universe, long-duration rates). config.UNIVERSE stays frozen; the
# new instruments remain lane-local, reusing the slice-3 caches.
R3_AROON_CCI_INSTRUMENTS = ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                            "META", "GLD", "SLV",
                            "SPY", "QQQ", "TSLA", "TLT")


def r3_aroon_cci_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-4 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_AROON_CCI_AXES[family]
    except KeyError:
        raise ValueError(f"unknown R3 aroon-cci family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_AROON_CCI_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_aroon_cci_variants_per_family() -> dict[str, int]:
    """Round-3 slice-4 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_aroon_cci_variants(fam))
            for fam in R3_AROON_CCI_FAMILIES}


def r3_aroon_cci_total_configs() -> int:
    """Total registered Round-3 slice-4 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes)."""
    return (sum(r3_aroon_cci_variants_per_family().values())
            * len(R3_AROON_CCI_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 5: mean-reversion families × HOURLY bars (lane:
# r3-meanrev-hourly × all-8 × hourly — ORDER 012 night-run, post-holdout
# DEV-ONLY, promotion closed)
# ---------------------------------------------------------------------------
# TIMEFRAME expansion, not a strategy expansion: NO new strategy code — the
# four existing mean-reversion families are re-swept on hourly bars over the
# frozen 8-ticker universe (committed hourly caches, dev rail 2023-08-10 →
# 2025-01-08). Parameter-scaling convention follows the one prior hourly
# lane (p1-trend-hourly, docs/p1-trend-hourly-results.md): grids stay
# BAR-denominated — on hourly bars the same lookback numbers mean
# hours-to-days instead of days-to-weeks (RSI(14) is ~2 sessions, Bollinger
# lookback 30 is ~4.6 sessions), which is the natural horizon for intraday
# mean reversion. Each grid here is a 12-variant SUBSET of the family's
# existing published daily axes (declared BEFORE the sweep ran): no new
# parameter values are introduced, so every hourly variant has a daily
# twin already in the burden ledger. The stochastic d_period smoothing (3)
# stays frozen at the strategy default and is NOT swept, as in the
# r3-stoch-willr lane. Kept bounded on purpose: every extra variant raises
# the multiple-testing burden on any winner.

_R3_MEANREV_HOURLY_AXES: dict[str, dict[str, list]] = {
    "rsi_mean_reversion": {"period": [2, 5, 14],
                           "oversold": [20, 30],
                           "overbought": [60, 70]},
    "bollinger_reversion": {"lookback": [10, 20, 30],
                            "z_entry": [1.5, 2.0],
                            "z_exit": [0.0, 0.5]},
    "stochastic_reversion": {"k_period": [14, 21, 28],
                             "buy_below": [10, 20],
                             "sell_above": [70, 80]},
    "williams_r_reversion": {"period": [14, 21, 28],
                             "buy_below": [-90, -80],
                             "sell_above": [-30, -20]},
}

_R3_MEANREV_HOURLY_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "rsi_mean_reversion": lambda p: p["oversold"] < p["overbought"],
    "bollinger_reversion": lambda p: p["z_exit"] > -p["z_entry"],
    "stochastic_reversion": lambda p: p["buy_below"] < p["sell_above"],
    "williams_r_reversion": lambda p: p["buy_below"] < p["sell_above"],
}

R3_MEANREV_HOURLY_FAMILIES = tuple(_R3_MEANREV_HOURLY_AXES)

# The full 8-ticker universe (config.UNIVERSE order) — hourly caches are
# committed for all 8 (data/hourly/).
R3_MEANREV_HOURLY_INSTRUMENTS = ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                                 "META", "GLD", "SLV")


def r3_meanrev_hourly_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-5 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_MEANREV_HOURLY_AXES[family]
    except KeyError:
        raise ValueError(
            f"unknown R3 meanrev-hourly family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_MEANREV_HOURLY_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_meanrev_hourly_variants_per_family() -> dict[str, int]:
    """Round-3 slice-5 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_meanrev_hourly_variants(fam))
            for fam in R3_MEANREV_HOURLY_FAMILIES}


def r3_meanrev_hourly_total_configs() -> int:
    """Total registered Round-3 slice-5 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes)."""
    return (sum(r3_meanrev_hourly_variants_per_family().values())
            * len(R3_MEANREV_HOURLY_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 6: Bollinger breakout + ATR trailing stop (lane: r3-breakout
# × 12-ticker mixed set × daily — ORDER 012 night-run, post-holdout
# DEV-ONLY, promotion closed)
# ---------------------------------------------------------------------------
# Two breakout/trailing-stop TREND families, declared here BEFORE the sweep
# ran — the trend counterparts of the existing band families:
# bollinger_breakout is the inverse thesis of the merged bollinger_reversion
# (long on close crossing ABOVE the upper band; exit below the MIDDLE band,
# the committed exit semantic — the SMA+k·std sibling of keltner_breakout's
# EMA+m·ATR channel); atr_trailing is a chandelier-style trailing stop
# (N-day-high breakout entry, exit below highest-close-since-entry − k×ATR).
# bollinger_breakout axes reuse the reversion family's published band axes
# (period {10, 20, 50} spans the reversion lookbacks plus the Keltner slow
# 50; num_std {1.0, 1.5, 2.0, 2.5} is the reversion z_entry axis verbatim,
# so every band width already sits in the burden ledger). atr_trailing axes
# anchor the classics: turtle entry channels {20, 55}, Wilder/chandelier ATR
# windows {14, 22}, and the published chandelier multipliers {2.0, 3.0}
# bracketed by a loose 4.0. The slice-2/4 committed-control-arm convention
# (banded/gated grids must include their neutral arm) is NOT applicable
# here: neither grid has a hysteresis band or an on/off gate — both are
# pure threshold families, like the reversion grids slice 5 noted the same
# for. Kept bounded on purpose: every extra variant raises the
# multiple-testing burden on any winner.

_R3_BREAKOUT_AXES: dict[str, dict[str, list]] = {
    "bollinger_breakout": {"period": [10, 20, 50],
                           "num_std": [1.0, 1.5, 2.0, 2.5]},
    "atr_trailing": {"entry_lookback": [20, 55],
                     "atr_period": [14, 22],
                     "k": [2.0, 3.0, 4.0]},
}

_R3_BREAKOUT_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "bollinger_breakout": lambda p: True,
    "atr_trailing": lambda p: True,
}

R3_BREAKOUT_FAMILIES = tuple(_R3_BREAKOUT_AXES)

# The 12-ticker mixed set of the slice-4 lane, reused verbatim: the full
# frozen 8-ticker universe (config.UNIVERSE order) PLUS four of the slice-3
# new instruments (SPY, QQQ, TSLA, TLT). config.UNIVERSE stays frozen; the
# new instruments remain lane-local, reusing the slice-3 caches.
R3_BREAKOUT_INSTRUMENTS = ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                           "META", "GLD", "SLV",
                           "SPY", "QQQ", "TSLA", "TLT")


def r3_breakout_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-6 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_BREAKOUT_AXES[family]
    except KeyError:
        raise ValueError(f"unknown R3 breakout family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_BREAKOUT_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_breakout_variants_per_family() -> dict[str, int]:
    """Round-3 slice-6 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_breakout_variants(fam))
            for fam in R3_BREAKOUT_FAMILIES}


def r3_breakout_total_configs() -> int:
    """Total registered Round-3 slice-6 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes)."""
    return (sum(r3_breakout_variants_per_family().values())
            * len(R3_BREAKOUT_INSTRUMENTS))
