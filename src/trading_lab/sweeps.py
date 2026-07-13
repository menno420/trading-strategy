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


# ---------------------------------------------------------------------------
# Round 3 slice 7: cross-sectional lane on the EXPANDED universe (lane:
# r3-xsec-expanded × 14-instrument basket × daily — ORDER 012 night-run,
# post-holdout DEV-ONLY, promotion closed)
# ---------------------------------------------------------------------------
# The lab's second PORTFOLIO-level lane, declared here BEFORE the sweep ran.
# Two families over ONE basket: the EXISTING xsec_momentum (Round-2 R3 grid
# axes reused verbatim: L ∈ {63, 126, 252} × k ∈ {2, 3}, 21-bar rebalance
# frozen — no strategy code change, the universe was already a parameter)
# and the NEW xsec_reversal mirror thesis (short-term reversal: long
# equal-weight the k WORST trailing-N-bar performers; N ∈ {5, 10, 21} spans
# week/fortnight/month, the classic short-horizon reversal windows; k
# ∈ {2, 3} mirrors the momentum axis; WEEKLY 5-bar rebalance frozen — a
# monthly cadence would time-average away the short-horizon signal). The
# basket is the 14 daily EQUITY/ETF instruments the lab has caches for:
# the frozen 8-ticker universe minus BTC-USD, plus the six slice-3
# instruments (SPY, QQQ, TSLA, JPM, XOM, TLT). BTC-USD is deliberately
# excluded: an all-equity/ETF basket keeps the aligned common index on
# exchange trading days (the Round-2 lane dropped BTC weekend bars for the
# same reason). config.UNIVERSE stays frozen; the slice-3 instruments
# remain lane-local, reusing the committed caches. Portfolio lane: configs
# are grid points, NOT × instruments (Round-2 R3 accounting). Kept bounded
# on purpose: every extra variant raises the multiple-testing burden.

_R3_XSEC_EXPANDED_AXES: dict[str, dict[str, list]] = {
    "xsec_momentum": {"L": [63, 126, 252], "k": [2, 3]},
    "xsec_reversal": {"N": [5, 10, 21], "k": [2, 3]},
}

_R3_XSEC_EXPANDED_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "xsec_momentum": lambda p: True,
    "xsec_reversal": lambda p: True,
}

R3_XSEC_EXPANDED_FAMILIES = tuple(_R3_XSEC_EXPANDED_AXES)

# The 14-instrument expanded basket (XSEC-14), alphabetical — the column
# order of the aligned panel and the deterministic ranking tie-break order
# in both portfolio strategies.
R3_XSEC_EXPANDED_INSTRUMENTS = ("AAPL", "AMZN", "GLD", "GOOGL", "JPM",
                                "META", "MSFT", "NVDA", "QQQ", "SLV",
                                "SPY", "TLT", "TSLA", "XOM")

# Rebalance cadences, frozen per family and NOT swept: xsec_momentum keeps
# the Round-2 21-bar (monthly) cadence; xsec_reversal is 5-bar (weekly) —
# short-horizon reversal decays too fast for a monthly cadence.
R3_XSEC_EXPANDED_REBALANCE_EVERY = {"xsec_momentum": 21, "xsec_reversal": 5}


def r3_xsec_expanded_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-7 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_XSEC_EXPANDED_AXES[family]
    except KeyError:
        raise ValueError(
            f"unknown R3 xsec-expanded family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_XSEC_EXPANDED_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_xsec_expanded_variants_per_family() -> dict[str, int]:
    """Round-3 slice-7 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_xsec_expanded_variants(fam))
            for fam in R3_XSEC_EXPANDED_FAMILIES}


def r3_xsec_expanded_total_configs() -> int:
    """Total registered Round-3 slice-7 configs. Portfolio lane: ONE config
    per grid point over the whole 14-instrument basket (Round-2 R3
    accounting) — unlike the single-instrument lanes, instruments do NOT
    multiply the count."""
    return sum(r3_xsec_expanded_variants_per_family().values())


# ---------------------------------------------------------------------------
# Round 3 slice 8: TRIX momentum + Ichimoku cloud trend (lane:
# r3-trix-ichimoku × 12-ticker mixed set × daily — ORDER 012 night-run,
# post-holdout DEV-ONLY, promotion closed)
# ---------------------------------------------------------------------------
# Two classic-indicator families, declared here BEFORE the sweep ran.
# trix_momentum axes bracket the published TRIX windows (Hutson's 15 plus
# the faster 9/12 and slower 21 in common charting defaults) crossed with
# the signal-line smoothing {5, 9} (9 is the MACD-signal convention) AND
# the zero-line arm: signal_period == 0 replaces the signal line with the
# constant 0, recovering the classic TRIX zero-line rule — the
# within-family control arm committed in the grid per the slice-2/4 card
# convention (derived-trigger grids must include their neutral arm).
# ichimoku_trend axes bracket the standard Hosoda 9/26/52 (committed in
# the grid verbatim) with the faster 7/22/44 halves common in shorter-cycle
# charting, constrained tenkan < kijun < senkou_b; the forward displacement
# of the senkou spans is frozen at the standard 26 and NOT swept (mirroring
# the frozen stochastic d_period / ADX period conventions). Kept bounded
# on purpose: every extra variant raises the multiple-testing burden on
# any winner.

_R3_TRIX_ICHIMOKU_AXES: dict[str, dict[str, list]] = {
    "trix_momentum": {"period": [9, 12, 15, 21],
                      "signal_period": [0, 5, 9]},
    "ichimoku_trend": {"tenkan": [7, 9, 12],
                       "kijun": [22, 26],
                       "senkou_b": [44, 52]},
}

_R3_TRIX_ICHIMOKU_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "trix_momentum": lambda p: True,
    "ichimoku_trend": lambda p: p["tenkan"] < p["kijun"] < p["senkou_b"],
}

R3_TRIX_ICHIMOKU_FAMILIES = tuple(_R3_TRIX_ICHIMOKU_AXES)

# The 12-ticker mixed set of the slice-4/6 lanes, reused verbatim: the full
# frozen 8-ticker universe (config.UNIVERSE order) PLUS four of the slice-3
# new instruments (SPY, QQQ, TSLA, TLT). config.UNIVERSE stays frozen; the
# new instruments remain lane-local, reusing the slice-3 caches.
R3_TRIX_ICHIMOKU_INSTRUMENTS = ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                                "META", "GLD", "SLV",
                                "SPY", "QQQ", "TSLA", "TLT")


def r3_trix_ichimoku_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-8 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_TRIX_ICHIMOKU_AXES[family]
    except KeyError:
        raise ValueError(
            f"unknown R3 trix-ichimoku family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_TRIX_ICHIMOKU_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_trix_ichimoku_variants_per_family() -> dict[str, int]:
    """Round-3 slice-8 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_trix_ichimoku_variants(fam))
            for fam in R3_TRIX_ICHIMOKU_FAMILIES}


def r3_trix_ichimoku_total_configs() -> int:
    """Total registered Round-3 slice-8 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes)."""
    return (sum(r3_trix_ichimoku_variants_per_family().values())
            * len(R3_TRIX_ICHIMOKU_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 10: FULL TREND FAMILIES × NEW TICKERS (lane:
# r3-trend-new-tickers × the six slice-3 instruments × daily — ORDER 012
# night-run, post-holdout DEV-ONLY, promotion closed; lands AFTER the
# Round-3 synthesis of slices 1-8, extending the round)
# ---------------------------------------------------------------------------
# Slice 3 (r3-new-tickers, PR #83) added the six instrument caches but
# probed them with only 6-variant grids of three families. This slice
# completes the TREND-family coverage: the four existing trend families
# with 12-variant sub-grids, declared here BEFORE the sweep ran. NO new
# strategy code and NO new parameter territory — every grid point is a
# point of the family's existing published grid (donchian/ema_crossover/
# macd: the P1 trend axes; supertrend_flip: the P1 video-lane grid), and
# the subset relation is pinned by tests. The donchian sub-grid is
# deliberately DISJOINT from the slice-3 donchian probe grid (entry
# {20,40,55} × exit {10,20}) so no config is registered twice on the same
# instruments. supertrend_flip honesty note: the family has only ever been
# run on BTC-USD (the P1 video lane); this is its first run on
# equities/ETFs, with the MACD triple frozen at the classic 12/26/9 (one
# of the two video-lane triples) and NOT swept. The instruments reuse the
# committed slice-3 caches; config.UNIVERSE stays frozen. Kept bounded on
# purpose: every extra variant raises the multiple-testing burden on any
# winner.

_R3_TREND_NEW_TICKERS_AXES: dict[str, dict[str, list]] = {
    "donchian": {"entry": [10, 15, 30, 80, 100], "exit": [5, 15, 30]},
    "ema_crossover": {"fast": [10, 20, 30], "slow": [50, 100, 150, 200]},
    "macd": {"fast": [8, 12], "slow": [21, 26, 35], "signal": [5, 9]},
    "supertrend_flip": {"st_period": [10, 14], "st_mult": [2.0, 3.0, 4.0],
                        "ema_len": [100, 200],
                        "macd_fast": [12], "macd_slow": [26],
                        "macd_signal": [9]},
}

_R3_TREND_NEW_TICKERS_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "donchian": lambda p: p["exit"] <= p["entry"],
    "ema_crossover": lambda p: p["fast"] < p["slow"],
    "macd": lambda p: p["fast"] < p["slow"],
    "supertrend_flip": lambda p: p["macd_fast"] < p["macd_slow"],
}

R3_TREND_NEW_TICKERS_FAMILIES = tuple(_R3_TREND_NEW_TICKERS_AXES)

# The six slice-3 instruments, reused verbatim (same tuple object — the
# identity is the point: this slice completes coverage of THAT surface).
R3_TREND_NEW_TICKERS_INSTRUMENTS = R3_NEW_TICKERS_INSTRUMENTS


def r3_trend_new_tickers_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-10 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_TREND_NEW_TICKERS_AXES[family]
    except KeyError:
        raise ValueError(
            f"unknown R3 trend-new-tickers family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_TREND_NEW_TICKERS_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_trend_new_tickers_variants_per_family() -> dict[str, int]:
    """Round-3 slice-10 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_trend_new_tickers_variants(fam))
            for fam in R3_TREND_NEW_TICKERS_FAMILIES}


def r3_trend_new_tickers_total_configs() -> int:
    """Total registered Round-3 slice-10 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes). The per-instrument buy-and-hold
    baselines already sit on the ledger from slice 3 and are not searched
    configurations."""
    return (sum(r3_trend_new_tickers_variants_per_family().values())
            * len(R3_TREND_NEW_TICKERS_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 11: MEAN-REVERSION FAMILIES × NEW TICKERS (lane:
# r3-meanrev-new-tickers × the six slice-3 instruments × daily — ORDER 012
# night-run, post-holdout DEV-ONLY, promotion closed; lands AFTER the
# Round-3 synthesis of slices 1-8, extending the round)
# ---------------------------------------------------------------------------
# The mean-reversion counterpart of slice 10 (r3-trend-new-tickers): slice 3
# (r3-new-tickers, PR #83) added the six instrument caches but probed them
# with only 6-variant grids of three families, and slice 10 completed the
# TREND-family coverage. This slice completes the MEAN-REVERSION coverage:
# the five existing mean-reversion families with 12-variant sub-grids,
# declared here BEFORE the sweep ran. NO new strategy code and NO new
# parameter territory — every grid point is a point of the family's
# existing published grid (rsi_mean_reversion/bollinger_reversion/pullback:
# the P1 mean-reversion axes; stochastic_reversion/williams_r_reversion:
# the r3-stoch-willr axes, whose full grids are already exactly 12 and are
# reused VERBATIM), and the subset relations are pinned by tests. Overlap
# honesty: slice 3 already probed rsi_mean_reversion on these instruments
# (period {2,5,14} × oversold {30} × overbought {60,70}); this slice's rsi
# sub-grid keeps the same periods and overboughts but takes oversold from
# {10, 20} — deliberately DISJOINT from the slice-3 probe so no config is
# registered twice on the same instruments (slice 10's donchian precedent;
# disjointness pinned by a test). The bollinger sub-grid is the
# r3-meanrev-hourly daily-twin subset reused verbatim (every point already
# in the burden ledger on both timeframes for the frozen universe); the
# pullback sub-grid commits the trend_len=0 unfiltered control arm per the
# slice-2/4 convention (gated grids must include their neutral arm); the
# stochastic d_period smoothing (3) stays frozen at the strategy default
# and is NOT swept, as in the r3-stoch-willr lane. The instruments reuse
# the committed slice-3 caches; config.UNIVERSE stays frozen. Kept bounded
# on purpose: every extra variant raises the multiple-testing burden on
# any winner.

_R3_MEANREV_NEW_TICKERS_AXES: dict[str, dict[str, list]] = {
    "rsi_mean_reversion": {"period": [2, 5, 14],
                           "oversold": [10, 20],
                           "overbought": [60, 70]},
    "bollinger_reversion": {"lookback": [10, 20, 30],
                            "z_entry": [1.5, 2.0],
                            "z_exit": [0.0, 0.5]},
    "pullback": {"entry_lookback": [3, 5],
                 "exit_len": [5, 10],
                 "trend_len": [0, 100, 200]},
    "stochastic_reversion": {"k_period": [14, 21, 28],
                             "buy_below": [10, 20],
                             "sell_above": [70, 80]},
    "williams_r_reversion": {"period": [14, 21, 28],
                             "buy_below": [-90, -80],
                             "sell_above": [-30, -20]},
}

_R3_MEANREV_NEW_TICKERS_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "rsi_mean_reversion": lambda p: p["oversold"] < p["overbought"],
    "bollinger_reversion": lambda p: p["z_exit"] > -p["z_entry"],
    "pullback": lambda p: True,
    "stochastic_reversion": lambda p: p["buy_below"] < p["sell_above"],
    "williams_r_reversion": lambda p: p["buy_below"] < p["sell_above"],
}

R3_MEANREV_NEW_TICKERS_FAMILIES = tuple(_R3_MEANREV_NEW_TICKERS_AXES)

# The six slice-3 instruments, reused verbatim (same tuple object — the
# identity is the point: this slice completes coverage of THAT surface).
R3_MEANREV_NEW_TICKERS_INSTRUMENTS = R3_NEW_TICKERS_INSTRUMENTS


def r3_meanrev_new_tickers_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-11 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_MEANREV_NEW_TICKERS_AXES[family]
    except KeyError:
        raise ValueError(
            f"unknown R3 meanrev-new-tickers family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_MEANREV_NEW_TICKERS_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_meanrev_new_tickers_variants_per_family() -> dict[str, int]:
    """Round-3 slice-11 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_meanrev_new_tickers_variants(fam))
            for fam in R3_MEANREV_NEW_TICKERS_FAMILIES}


def r3_meanrev_new_tickers_total_configs() -> int:
    """Total registered Round-3 slice-11 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes). The per-instrument buy-and-hold
    baselines already sit on the ledger from slice 3 and are not searched
    configurations."""
    return (sum(r3_meanrev_new_tickers_variants_per_family().values())
            * len(R3_MEANREV_NEW_TICKERS_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 12: R2/GATED FAMILIES × NEW TICKERS (lane:
# r3-gated-new-tickers × the six slice-3 instruments × daily — ORDER 012
# night-run, post-holdout DEV-ONLY, promotion closed; lands AFTER the
# Round-3 synthesis of slices 1-8, extending the round)
# ---------------------------------------------------------------------------
# The R2/gated counterpart of slices 10-11: slice 3 (r3-new-tickers, PR #83)
# added the six instrument caches, slice 10 completed the TREND coverage and
# slice 11 the MEAN-REVERSION coverage. This slice completes the remaining
# single-instrument coverage with the three R2/gated families — ALL of them
# previously narrow-universe (the honesty note that motivates the slice):
# vol_filtered_trend has only ever run on the Round-2 §3a four (AAPL, MSFT,
# NVDA, GLD); keltner_breakout only on the Round-2 §3b four (BTC-USD, META,
# AMZN, SLV); macd_supertrend only on BTC-USD (the P1 video lane) — its
# first run on equities/ETFs. Grids declared here BEFORE the sweep ran; NO
# new strategy code and NO new parameter territory — every grid point is a
# point of the family's existing published grid, subset relations pinned by
# tests: vol_filtered_trend reuses its full 12-variant R2 grid VERBATIM
# (fast {10,20} × slow {50,100,200} × vol_filter {on,off}; the
# vol_filter=False control arm is committed per the slice-2/4 convention —
# gated grids include their neutral arm; the vol windows 20/252 stay frozen
# at the strategy defaults and are NOT swept, as in R2); keltner_breakout
# reuses its full R2 grid VERBATIM (n {20,50} × m {1.5,2.0,2.5}) — that
# published grid is only 6 variants, and inventing new n/m values to reach
# ~12 would open new parameter territory, so this family honestly runs at
# 6, not 12; macd_supertrend takes a 12-variant sub-grid of the 36-variant
# P1 video grid (st_period {10,14} × st_mult {2.0,3.0,4.0} × ema_len
# {100,200}) with the MACD triple frozen at the classic 12/26/9 (one of
# the two video-lane triples) and NOT swept — slice 10's supertrend_flip
# precedent, verbatim axes. The instruments reuse the committed slice-3
# caches; config.UNIVERSE stays frozen. Kept bounded on purpose: every
# extra variant raises the multiple-testing burden on any winner.

_R3_GATED_NEW_TICKERS_AXES: dict[str, dict[str, list]] = {
    "keltner_breakout": {"n": [20, 50], "m": [1.5, 2.0, 2.5]},
    "vol_filtered_trend": {"fast": [10, 20],
                           "slow": [50, 100, 200],
                           "vol_filter": [True, False]},
    "macd_supertrend": {"st_period": [10, 14], "st_mult": [2.0, 3.0, 4.0],
                        "ema_len": [100, 200],
                        "macd_fast": [12], "macd_slow": [26],
                        "macd_signal": [9]},
}

_R3_GATED_NEW_TICKERS_CONSTRAINTS: dict[str, Callable[[dict], bool]] = {
    "keltner_breakout": lambda p: True,
    "vol_filtered_trend": lambda p: p["fast"] < p["slow"],
    "macd_supertrend": lambda p: p["macd_fast"] < p["macd_slow"],
}

R3_GATED_NEW_TICKERS_FAMILIES = tuple(_R3_GATED_NEW_TICKERS_AXES)

# The six slice-3 instruments, reused verbatim (same tuple object — the
# identity is the point: this slice completes coverage of THAT surface).
R3_GATED_NEW_TICKERS_INSTRUMENTS = R3_NEW_TICKERS_INSTRUMENTS


def r3_gated_new_tickers_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-12 ``family``,
    constraint-filtered, in a deterministic order."""
    try:
        axes = _R3_GATED_NEW_TICKERS_AXES[family]
    except KeyError:
        raise ValueError(
            f"unknown R3 gated-new-tickers family {family!r}") from None
    keys = list(axes)
    combos = (dict(zip(keys, vals)) for vals in product(*(axes[k] for k in keys)))
    keep = _R3_GATED_NEW_TICKERS_CONSTRAINTS[family]
    return [c for c in combos if keep(c)]


def r3_gated_new_tickers_variants_per_family() -> dict[str, int]:
    """Round-3 slice-12 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_gated_new_tickers_variants(fam))
            for fam in R3_GATED_NEW_TICKERS_FAMILIES}


def r3_gated_new_tickers_total_configs() -> int:
    """Total registered Round-3 slice-12 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes). The per-instrument buy-and-hold
    baselines already sit on the ledger from slice 3 and are not searched
    configurations."""
    return (sum(r3_gated_new_tickers_variants_per_family().values())
            * len(R3_GATED_NEW_TICKERS_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 13: ROUND-3 FAMILIES × BTC-USD coverage (lane:
# r3-btc-coverage × BTC-USD × daily — ORDER 012 night-run, post-holdout
# DEV-ONLY, promotion closed; lands AFTER the Round-3 synthesis of slices
# 1-8, extending the round)
# ---------------------------------------------------------------------------
# The BTC-USD counterpart of slices 10-12: the committed BTC-USD daily
# cache (P1 video lane; dev rail ends 2025-01-08) has only ever been swept
# by the video-lane families (supertrend_flip, macd_supertrend, the
# dual-EMA control), the R2 §3b keltner_breakout arm and the P4 transfer
# spot checks — the TEN single-instrument families Round 3 added have
# NEVER run on it. This slice completes that coverage. NO new strategy
# code and NO new parameter territory: each family's declared Round-3
# 12-variant grid is reused VERBATIM by DELEGATING to the source lane's
# generator (byte-identical grids by construction; equality pinned by
# tests). The cross-sectional family (xsec_momentum) is out of scope —
# it is a basket strategy, not a single-instrument one, and its expanded
# lane (slice 9) deliberately EXCLUDES BTC-USD over the calendar-mixing
# problem (crypto trades 7 days/week; see R3_XSEC_EXPANDED notes).
# BTC-USD stays lane-local (config.UNIVERSE frozen); the committed cache
# is reused, nothing fetched. Annualization follows the P1 video-lane
# convention: PERIODS_PER_YEAR["daily"] = 252 although BTC trades ~365
# days/year, so annualized Sharpe/CAGR are UNDERSTATED by a constant
# factor for strategy and benchmark alike — same-window comparisons vs
# B&H are unaffected; flagged, not patched (the constant is lab-wide).

_R3_BTC_COVERAGE_SOURCES: dict[str, Callable[[str], list[dict]]] = {
    "stochastic_reversion": r3_stoch_willr_variants,
    "williams_r_reversion": r3_stoch_willr_variants,
    "roc_momentum": r3_roc_adx_variants,
    "adx_filtered_sma": r3_roc_adx_variants,
    "aroon_trend": r3_aroon_cci_variants,
    "cci_reversion": r3_aroon_cci_variants,
    "bollinger_breakout": r3_breakout_variants,
    "atr_trailing": r3_breakout_variants,
    "trix_momentum": r3_trix_ichimoku_variants,
    "ichimoku_trend": r3_trix_ichimoku_variants,
}

R3_BTC_COVERAGE_FAMILIES = tuple(_R3_BTC_COVERAGE_SOURCES)

# BTC-USD only — the point of the slice is coverage of THAT instrument.
R3_BTC_COVERAGE_INSTRUMENTS = ("BTC-USD",)


def r3_btc_coverage_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-13 ``family`` —
    the family's declared Round-3 grid, VERBATIM (delegated to the source
    lane's generator, so the grids cannot drift apart)."""
    try:
        source = _R3_BTC_COVERAGE_SOURCES[family]
    except KeyError:
        raise ValueError(
            f"unknown R3 btc-coverage family {family!r}") from None
    return source(family)


def r3_btc_coverage_variants_per_family() -> dict[str, int]:
    """Round-3 slice-13 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_btc_coverage_variants(fam))
            for fam in R3_BTC_COVERAGE_FAMILIES}


def r3_btc_coverage_total_configs() -> int:
    """Total registered Round-3 slice-13 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes). BTC-USD has no buy-and-hold
    ledger row yet (the video lane predates the slice-3 baseline
    convention), so the slice records exactly ONE — a benchmark, not a
    searched configuration."""
    return (sum(r3_btc_coverage_variants_per_family().values())
            * len(R3_BTC_COVERAGE_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 14: TREND/MOMENTUM FAMILIES × HOURLY bars (lane:
# r3-trend-hourly × all-8 × hourly — ORDER 012 night-run, post-holdout
# DEV-ONLY, promotion closed; lands AFTER the Round-3 synthesis of slices
# 1-8, extending the round)
# ---------------------------------------------------------------------------
# TIMEFRAME expansion, not a strategy expansion — the TREND-side mirror of
# slice 5 (r3-meanrev-hourly): NO new strategy code — the four Round-3
# trend/momentum single-instrument families (roc_momentum and
# adx_filtered_sma from slice 2, aroon_trend from slice 4, trix_momentum
# from slice 8) are re-swept on hourly bars over the frozen 8-ticker
# universe (committed hourly caches, dev rail 2023-08-10 → 2025-01-08).
# Parameter-scaling convention follows the two prior hourly lanes
# (p1-trend-hourly, r3-meanrev-hourly) exactly: grids stay BAR-denominated
# — the same lookback numbers mean hours-to-days instead of days-to-weeks
# (roc lookback 252 bars is ~38.8 hourly sessions ≈ 2 months instead of a
# year; adx slow 200 is ~31 sessions; trix period 15 is ~2.3 sessions) —
# and each family's declared Round-3 12-variant daily grid is reused
# VERBATIM by DELEGATING to the source lane's generator (the slice-13
# convention: byte-identical grids by construction, so the slice-5
# subset-of-the-published-daily-axes relation degenerates to equality;
# both pinned by tests). No new parameter values are introduced, so every
# hourly variant has a daily twin already in the burden ledger. The frozen
# non-swept parameters stay frozen (ADX period 14; TRIX zero-line control
# arm signal_period == 0 stays IN the grid — verbatim reuse inherits the
# slice-2/4/8 committed-control-arm decisions unchanged). The two Round-3
# breakout families (bollinger_breakout, atr_trailing) and ichimoku_trend
# are OUT of scope here: this slice mirrors slice 5's four-family × all-8
# shape (384 configs) for cross-lane comparability, and takes the four
# families slices 2/4/8 declared as the round's classic trend/momentum
# indicators; a breakout/ichimoku hourly lane would be its own declared
# slice. Kept bounded on purpose: every extra variant raises the
# multiple-testing burden on any winner.

_R3_TREND_HOURLY_SOURCES: dict[str, Callable[[str], list[dict]]] = {
    "roc_momentum": r3_roc_adx_variants,
    "adx_filtered_sma": r3_roc_adx_variants,
    "aroon_trend": r3_aroon_cci_variants,
    "trix_momentum": r3_trix_ichimoku_variants,
}

R3_TREND_HOURLY_FAMILIES = tuple(_R3_TREND_HOURLY_SOURCES)

# The full 8-ticker universe (config.UNIVERSE order) — hourly caches are
# committed for all 8 (data/hourly/), as in the p1-trend-hourly and
# r3-meanrev-hourly lanes.
R3_TREND_HOURLY_INSTRUMENTS = ("AAPL", "MSFT", "NVDA", "GOOGL", "AMZN",
                               "META", "GLD", "SLV")


def r3_trend_hourly_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-14 ``family`` —
    the family's declared Round-3 daily grid, VERBATIM (delegated to the
    source lane's generator, so the grids cannot drift apart; on hourly
    bars the same numbers are bar-denominated per the p1-trend-hourly
    convention)."""
    try:
        source = _R3_TREND_HOURLY_SOURCES[family]
    except KeyError:
        raise ValueError(
            f"unknown R3 trend-hourly family {family!r}") from None
    return source(family)


def r3_trend_hourly_variants_per_family() -> dict[str, int]:
    """Round-3 slice-14 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_trend_hourly_variants(fam))
            for fam in R3_TREND_HOURLY_FAMILIES}


def r3_trend_hourly_total_configs() -> int:
    """Total registered Round-3 slice-14 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes)."""
    return (sum(r3_trend_hourly_variants_per_family().values())
            * len(R3_TREND_HOURLY_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 3 slice 15: HOURLY-MATRIX COMPLETION — remaining four families ×
# HOURLY bars (lane: r3-hourly-completion × all-8 × hourly — ORDER 012
# night-run, post-holdout DEV-ONLY, promotion closed; lands AFTER the
# Round-3 synthesis of slices 1-8, extending the round)
# ---------------------------------------------------------------------------
# TIMEFRAME expansion, not a strategy expansion — the COMPLETION of the
# Round-3 hourly matrix started by slice 5 (r3-meanrev-hourly: the four
# mean-reversion families) and slice 14 (r3-trend-hourly: the four classic
# trend/momentum families): NO new strategy code — the four remaining
# Round-3 single-instrument families (cci_reversion from slice 4,
# bollinger_breakout and atr_trailing from slice 6, ichimoku_trend from
# slice 8) are re-swept on hourly bars over the frozen 8-ticker universe
# (committed hourly caches, dev rail 2023-08-10 → 2025-01-08). After this
# slice every Round-3 single-instrument family has both a daily and an
# hourly lane. Parameter-scaling convention follows the three prior hourly
# lanes (p1-trend-hourly, r3-meanrev-hourly, r3-trend-hourly) exactly:
# grids stay BAR-denominated — the same lookback numbers mean hours-to-days
# instead of days-to-weeks (cci period 20 is ~3 sessions; the atr_trailing
# turtle entry channel 55 is ~8.5 sessions; the Hosoda 9/26/52 spans
# ~1.4/4/8 sessions with the senkou displacement 26 staying frozen in
# BARS) — and each family's declared Round-3 12-variant daily grid is
# reused VERBATIM by DELEGATING to the source lane's generator (the
# slice-13/14 convention: byte-identical grids by construction, so the
# slice-5 subset-of-the-published-daily-axes relation degenerates to
# equality; both pinned by tests). No new parameter values are introduced,
# so every hourly variant has a daily twin already in the burden ledger.
# The frozen non-swept parameters stay frozen (ichimoku senkou
# displacement 26; bollinger_breakout's middle-band exit semantic;
# atr_trailing's chandelier exit form), and the slice-6 note carries over
# verbatim: bollinger_breakout and atr_trailing are pure threshold
# families with no hysteresis band or on/off gate, so the committed
# control-arm convention is not applicable; cci_reversion and
# ichimoku_trend inherit their slice-4/8 committed-grid decisions
# unchanged. Kept bounded on purpose: every extra variant raises the
# multiple-testing burden on any winner.

_R3_HOURLY_COMPLETION_SOURCES: dict[str, Callable[[str], list[dict]]] = {
    "cci_reversion": r3_aroon_cci_variants,
    "bollinger_breakout": r3_breakout_variants,
    "atr_trailing": r3_breakout_variants,
    "ichimoku_trend": r3_trix_ichimoku_variants,
}

R3_HOURLY_COMPLETION_FAMILIES = tuple(_R3_HOURLY_COMPLETION_SOURCES)

# The full 8-ticker universe (config.UNIVERSE order) — hourly caches are
# committed for all 8 (data/hourly/), as in the p1-trend-hourly,
# r3-meanrev-hourly and r3-trend-hourly lanes.
R3_HOURLY_COMPLETION_INSTRUMENTS = ("AAPL", "MSFT", "NVDA", "GOOGL",
                                    "AMZN", "META", "GLD", "SLV")


def r3_hourly_completion_variants(family: str) -> list[dict]:
    """All valid parameter dicts for a Round-3 slice-15 ``family`` —
    the family's declared Round-3 daily grid, VERBATIM (delegated to the
    source lane's generator, so the grids cannot drift apart; on hourly
    bars the same numbers are bar-denominated per the p1-trend-hourly
    convention)."""
    try:
        source = _R3_HOURLY_COMPLETION_SOURCES[family]
    except KeyError:
        raise ValueError(
            f"unknown R3 hourly-completion family {family!r}") from None
    return source(family)


def r3_hourly_completion_variants_per_family() -> dict[str, int]:
    """Round-3 slice-15 variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r3_hourly_completion_variants(fam))
            for fam in R3_HOURLY_COMPLETION_FAMILIES}


def r3_hourly_completion_total_configs() -> int:
    """Total registered Round-3 slice-15 configs: variants × instruments
    (each instrument × grid point counts as one config, as in Round 2
    R1/R2 and the earlier Round-3 lanes)."""
    return (sum(r3_hourly_completion_variants_per_family().values())
            * len(R3_HOURLY_COMPLETION_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 4 slice R4-F: DAY-OF-WEEK SEASONALITY (lane: r4-seasonality ×
# 15 committed daily tickers × daily — docs/research-round-4-plan.md § R4-F,
# ORDER 012 night-run, post-holdout DEV-ONLY, promotion closed)
# ---------------------------------------------------------------------------
# The program's first *calendar* hypothesis and a classic multiple-testing
# trap — pre-registered as the stress test of the round's correction
# discipline. One family (weekday_long), one axis (which weekday, pandas
# dayofweek 0=Mon .. 4=Fri), NO parameter search inside a combo. K counts
# ALL day×ticker combos tested: 5 weekdays × 15 tickers = 75, so the
# Bonferroni bar RISES to min_tstat(75) ≈ 3.21 (vs 2.64 at K=12) — K is
# never counted down, the bar is never lowered. Any multi-day subsets, if
# ever swept, must be ADDED to K in a grid commit before running (none are
# registered here). Pre-registered hypothesis: null after correction.
# BTC-USD's committed daily cache contains weekend bars (dayofweek 5/6);
# those days are NOT part of the registered grid — the five registered
# variants simply stay flat on them and K stays 75.

_R4_SEASONALITY_AXES: dict[str, dict[str, list]] = {
    "weekday_long": {"weekday": [0, 1, 2, 3, 4]},
}

R4_SEASONALITY_FAMILIES = tuple(_R4_SEASONALITY_AXES)

# Every committed daily cache (the frozen 8-ticker universe + the six
# slice-3 instruments + BTC-USD) — the full committed daily surface, so
# no post-hoc instrument selection is possible.
R4_SEASONALITY_INSTRUMENTS = ("AAPL", "AMZN", "BTC-USD", "GLD", "GOOGL",
                              "JPM", "META", "MSFT", "NVDA", "QQQ", "SLV",
                              "SPY", "TLT", "TSLA", "XOM")

# The REGISTERED significance K for this slice: every day×ticker combo.
R4_SEASONALITY_K = 75


def r4_seasonality_variants(family: str = "weekday_long") -> list[dict]:
    """All parameter dicts for the Round-4 slice R4-F ``family`` (the five
    single-weekday variants), in deterministic order."""
    try:
        axes = _R4_SEASONALITY_AXES[family]
    except KeyError:
        raise ValueError(f"unknown R4 seasonality family {family!r}") from None
    keys = list(axes)
    return [dict(zip(keys, vals))
            for vals in product(*(axes[k] for k in keys))]


def r4_seasonality_variants_per_family() -> dict[str, int]:
    """Round-4 slice R4-F variant counts by family (multiple-testing
    bookkeeping)."""
    return {fam: len(r4_seasonality_variants(fam))
            for fam in R4_SEASONALITY_FAMILIES}


def r4_seasonality_total_configs() -> int:
    """Total registered Round-4 slice R4-F configs: variants × instruments
    = 5 × 15 = 75 — and for THIS slice the registered significance K is
    the same number (``R4_SEASONALITY_K``): every day×ticker combo counts
    toward the bar, per the pre-registered plan."""
    return (sum(r4_seasonality_variants_per_family().values())
            * len(R4_SEASONALITY_INSTRUMENTS))


# ---------------------------------------------------------------------------
# Round 4 slice R4-C: SURVIVOR COMMITTEE ENSEMBLES (lane: r4-ensemble —
# docs/research-round-4-plan.md § R4-C, ORDER 012 night-run, post-holdout
# DEV-ONLY, promotion closed)
# ---------------------------------------------------------------------------
# Round 3 never asked whether survivors *combine*. This slice forms, per
# instrument x timeframe group with >= R4_ENSEMBLE_MIN_MEMBERS KEEP-dev
# lanes, an equal-weight signal committee (position = mean of member
# positions; trading_lab.ensemble.committee_positions) of members FROZEN
# at their committed walk-forward choices — the committee is the ONLY new
# object, there is no search inside it (frozen-replay precedent: PR #101).
# The member universe is the committed, machine-readable KEEP surface of
# the R4-A re-grade (PR #100): the 58 new_verdict == "KEEP" rows of
# R4_ENSEMBLE_KEEP_UNIVERSE. Pre-registered rule: KEEP (dev-candidate
# only) iff the committee beats BOTH the best single member and the
# same-window same-cost B&H benchmark on stitched OOS Sharpe; otherwise
# KILL (KILL-SIG possible via promotion.classify_verdict). The t-stat is
# INFORMATIONAL ONLY, graded at the round-standard K = 12 (bar
# min_tstat(12) ≈ 2.638): each committee is a single pre-declared config,
# but the plan registers no smaller K for this slice and the bar is NEVER
# lowered — so the standard bar stands. Adopted conventions the plan is
# silent on (decided before any committee ran; see trading_lab.ensemble):
# grouping is instrument x timeframe (never across timeframes), and one
# member per family per committee (performance-blind lexicographic
# tiebreak for duplicate round-3 coverage; the best-member comparison
# uses ALL the group's KEEP lanes, which can only raise the bar).

# Minimum KEEP-dev lanes for an (instrument, timeframe) group to qualify.
R4_ENSEMBLE_MIN_MEMBERS = 2

# Registered significance K for the informational t — the round-standard
# bar, never lowered (min_tstat(12) ≈ 2.638).
R4_ENSEMBLE_K = 12

# The committed KEEP surface the members come from (R4-A, PR #100).
R4_ENSEMBLE_KEEP_UNIVERSE = ("experiments/sweeps/r4-killsig-regrade/"
                             "summary.json")
R4_ENSEMBLE_EXPECTED_KEEPS = 58

# Ledger strategy name for committee rows (one row per committee,
# variants_tried=1 — each committee is one pre-declared config).
R4_ENSEMBLE_STRATEGY_NAME = "committee_equal_weight"
