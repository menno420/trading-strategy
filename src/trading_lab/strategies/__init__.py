"""Strategy library (P0 baselines + P1 trend-following family + video lane
+ P1 mean-reversion family).

Common interface: ``generate(ohlcv, **params) -> pd.Series`` of target
positions indexed like ``ohlcv``. ``positions[t]`` uses data only through
bar ``t`` (the engine delays execution to bar ``t+1``'s open). Values are
0/1 (long/flat) for all strategies here.

Families:

* baselines (P0): buy_and_hold, sma_crossover, rsi_mean_reversion
* trend-following (P1): sma_crossover, ema_crossover, macd, donchian
* video-strategy (P1, lane video-strategy__btcusd__multi): supertrend_flip,
  macd_supertrend (+ ema_crossover reused as the dual-EMA control) —
  competing interpretations of the DaviddTech video's under-specified rules
  (docs/research/video-source-2026-07-09.md).
* mean-reversion (P1, lane mean-reversion__all8__daily): rsi_mean_reversion
  (the P0 baseline, reused with a sweep grid), bollinger_reversion
  (z-score/band reversion), pullback (short-horizon dip-buying with an
  optional long-term trend filter).
* Round 2 (post-holdout dev-only, docs/research-round-2.md):
  vol_filtered_trend (slice R1 — SMA crossover gated by a realized-vol
  calm-regime filter; the filter-off arm is the within-family baseline);
  keltner_breakout (slice R2 — long on close > EMA(n) + m*ATR(n), exit on
  close < EMA(n)); xsec_momentum (slice R3 — cross-sectional momentum
  PORTFOLIO over the 9-instrument basket; different interface, see below).
* Round 3 (post-holdout dev-only, ORDER 012 night-run, lane
  r3-stoch-willr × all-8 × daily): stochastic_reversion (slow stochastic
  %K oversold cross-up entry), williams_r_reversion (Williams %R oversold
  cross-up entry — the unsmoothed complement of the stochastic; the two
  families probe smoothed vs raw oscillator reversion); slice 2 (lane
  r3-roc-adx × all-8 × daily): roc_momentum (time-series rate-of-change
  momentum with an entry/exit hysteresis band), adx_filtered_sma (SMA
  crossover gated by a Wilder ADX trending-regime filter — the lab's first
  ADX indicator; the mirror image of vol_filtered_trend's calm-regime gate);
  slice 4 (lane r3-aroon-cci × 12-ticker mixed set × daily): aroon_trend
  (Aroon oscillator trend-following with an entry/exit hysteresis band —
  the zero-band arm, i.e. the classic Aroon-Up/Aroon-Down cross, is the
  committed within-family control), cci_reversion (Lambert CCI
  mean-reversion, oversold cross-up entry — the lab's first CCI indicator);
  slice 5 (lane r3-meanrev-hourly × all-8 × hourly): NO new strategies —
  the four existing mean-reversion families (rsi_mean_reversion,
  bollinger_reversion, stochastic_reversion, williams_r_reversion)
  re-swept on hourly bars (timeframe expansion); slice 6 (lane
  r3-breakout × 12-ticker mixed set × daily): bollinger_breakout (long on
  close crossing ABOVE the upper Bollinger band, exit below the middle
  band — the trend/breakout INVERSE of bollinger_reversion's thesis, and
  the SMA+k·std sibling of keltner_breakout), atr_trailing
  (chandelier-style ATR trailing stop: N-day-high breakout entry, exit
  when close falls below highest-close-since-entry − k×ATR — the lab's
  first stateful trailing-stop exit); slice 7 (lane r3-xsec-expanded ×
  14-instrument basket × daily): xsec_reversal (short-term cross-sectional
  REVERSAL portfolio — long equal-weight the k WORST trailing-N-bar
  performers, weekly rebalance; the mirror thesis of xsec_momentum, same
  panel interface, see below) plus the EXISTING xsec_momentum re-run on
  the expanded 14-instrument basket (no strategy code change — the
  universe was already a parameter of the panel interface); slice 8 (lane
  r3-trix-ichimoku × 12-ticker mixed set × daily): trix_momentum (TRIX
  triple-smoothed EMA rate-of-change, long while TRIX is above its signal
  line — signal_period == 0 recovers the classic zero-line rule and is the
  committed within-family control arm), ichimoku_trend (Ichimoku cloud
  trend: long when close is above the cloud AND tenkan > kijun, flat on a
  full cloud break below OR tenkan < kijun, hysteresis in between; spans
  displaced forward the standard 26 bars using only past data — the lab's
  first multi-component indicator system).
* Round 4 (post-holdout dev-only, docs/research-round-4-plan.md § R4-F,
  lane r4-seasonality × 15 daily tickers): weekday_long (pure calendar
  rule — long only on bars signalled on one chosen weekday, the lab's
  first seasonality family; K counted honestly at 5 weekdays × 15
  tickers = 75, bar min_tstat(75) ≈ 3.21); slice R4-D (lane r4-regime ×
  the six slice-3 tickers × daily): regime_switch (trend-strength
  tercile regime switch — trend component in the strong-trend bucket,
  flat/reversion component in the weak bucket, middle tercile holds;
  metric ADX or |200d SMA slope|; ``regime_condition=False`` is the
  MANDATORY unconditional control arm — the same components, no gate —
  per the plan's control-arm discipline, motivated by PR #92's 6/6
  control-beats-gate result); slice R4-E (lane r4-crossasset ×
  {SPY, QQQ} × daily): crossasset_gate (the program's first CROSS-ASSET
  strategy — the frozen ema_crossover 20/100 equity component gated on
  the momentum sign of a DIFFERENT instrument's close series, TLT/XOM/GLD,
  aligned onto the equity index lookahead-free; ``gated=False`` is the
  MANDATORY ungated control arm — the same component, no gate).
* Round 6 (post-holdout dev-only, docs/research-round-6-plan.md, ORDER 014
  items 1+3 — first round under the selection-fair standing gate [D-0002]),
  slice R6-A (lane r6-volume × 15 daily tickers): obv_trend (long while
  on-balance volume is above its own trailing SMA — the lab's first
  VOLUME-based family; ``price_confirm=False`` is the pure-OBV
  within-family control arm), mfi_reversion (Money Flow Index oversold
  cross-up reversion — the volume-weighted sibling of the RSI /
  stochastic / Williams %R / CCI oscillator families); slice R6-B (lane
  r6-gap × 12-ticker mixed equity/ETF set, BTC-USD deliberately excluded —
  a 24/7 market has no overnight gap): overnight_gap (the lab's first
  family whose SIGNAL reads the open column — trailing-ATR-normalized
  overnight gap, ``mode="fade"`` / ``mode="follow"`` are the two committed
  mirror theses); slice R6-C (lane r6-volume-hourly × all-8 × hourly): NO
  new strategies — the two R6-A volume families re-swept on hourly bars
  (timeframe expansion, the slice-5/14/15 precedent).

Portfolio strategies (``PORTFOLIO_STRATEGIES``) take a panel of aligned
closes (one column per instrument) and return a target-weight DataFrame
for ``trading_lab.portfolio.run_portfolio_backtest`` — they do NOT fit the
single-instrument ``generate(ohlcv, **params) -> pd.Series`` interface and
are deliberately kept out of ``STRATEGIES``.
"""

from __future__ import annotations

from . import (adx_filtered_sma, aroon_trend, atr_trailing,
               bollinger_breakout, bollinger_reversion, buy_and_hold,
               cci_reversion, crossasset_gate, donchian, drawdown_reversion,
               ema_crossover, high_proximity, ichimoku_trend,
               keltner_breakout, macd, macd_supertrend,
               mfi_reversion, obv_trend, overnight_gap, pullback,
               regime_switch, roc_momentum, rsi_mean_reversion,
               sma_crossover, stochastic_reversion, supertrend_flip,
               trix_momentum, vol_filtered_trend, washout_recovery,
               weekday_long, williams_r_reversion, xsec_drawdown,
               xsec_momentum, xsec_reversal)

STRATEGIES = {
    "buy_and_hold": buy_and_hold.generate,
    "sma_crossover": sma_crossover.generate,
    "rsi_mean_reversion": rsi_mean_reversion.generate,
    "ema_crossover": ema_crossover.generate,
    "macd": macd.generate,
    "donchian": donchian.generate,
    "supertrend_flip": supertrend_flip.generate,
    "macd_supertrend": macd_supertrend.generate,
    "bollinger_reversion": bollinger_reversion.generate,
    "pullback": pullback.generate,
    "vol_filtered_trend": vol_filtered_trend.generate,
    "keltner_breakout": keltner_breakout.generate,
    "stochastic_reversion": stochastic_reversion.generate,
    "williams_r_reversion": williams_r_reversion.generate,
    "roc_momentum": roc_momentum.generate,
    "adx_filtered_sma": adx_filtered_sma.generate,
    "aroon_trend": aroon_trend.generate,
    "cci_reversion": cci_reversion.generate,
    "bollinger_breakout": bollinger_breakout.generate,
    "atr_trailing": atr_trailing.generate,
    "trix_momentum": trix_momentum.generate,
    "ichimoku_trend": ichimoku_trend.generate,
    "weekday_long": weekday_long.generate,
    "regime_switch": regime_switch.generate,
    "crossasset_gate": crossasset_gate.generate,
    "obv_trend": obv_trend.generate,
    "mfi_reversion": mfi_reversion.generate,
    "overnight_gap": overnight_gap.generate,
    "drawdown_reversion": drawdown_reversion.generate,
    "high_proximity": high_proximity.generate,
    "washout_recovery": washout_recovery.generate,
}

DEFAULT_PARAMS = {
    "buy_and_hold": {},
    "sma_crossover": {"fast": 20, "slow": 50},
    "rsi_mean_reversion": {"period": 14, "oversold": 30, "overbought": 70},
    "ema_crossover": {"fast": 20, "slow": 50},
    "macd": {"fast": 12, "slow": 26, "signal": 9},
    "donchian": {"entry": 20, "exit": 10},
    "supertrend_flip": {"st_period": 10, "st_mult": 3.0, "ema_len": 200,
                        "macd_fast": 12, "macd_slow": 26, "macd_signal": 9},
    "macd_supertrend": {"macd_fast": 12, "macd_slow": 26, "macd_signal": 9,
                        "st_period": 10, "st_mult": 3.0, "ema_len": 200},
    "bollinger_reversion": {"lookback": 20, "z_entry": 2.0, "z_exit": 0.0},
    "pullback": {"entry_lookback": 5, "exit_len": 5, "trend_len": 200},
    "vol_filtered_trend": {"fast": 20, "slow": 50, "vol_filter": True},
    "keltner_breakout": {"n": 20, "m": 2.0},
    "stochastic_reversion": {"k_period": 14, "d_period": 3,
                             "buy_below": 20, "sell_above": 80},
    "williams_r_reversion": {"period": 14, "buy_below": -80,
                             "sell_above": -20},
    "roc_momentum": {"lookback": 126, "entry": 0.0, "exit": 0.0},
    "adx_filtered_sma": {"fast": 20, "slow": 50, "adx_period": 14,
                         "adx_min": 20.0},
    "aroon_trend": {"period": 25, "entry": 0.0, "exit": 0.0},
    "cci_reversion": {"period": 20, "buy_below": -100, "sell_above": 100},
    "bollinger_breakout": {"period": 20, "num_std": 2.0},
    "atr_trailing": {"entry_lookback": 20, "atr_period": 14, "k": 3.0},
    "trix_momentum": {"period": 15, "signal_period": 9},
    "ichimoku_trend": {"tenkan": 9, "kijun": 26, "senkou_b": 52,
                       "displacement": 26},
    "weekday_long": {"weekday": 0},
    "regime_switch": {"metric": "adx", "rank_window": 252,
                      "weak_family": "reversion", "regime_condition": True,
                      "trend_fast": 20, "trend_slow": 100,
                      "rsi_period": 2, "rsi_oversold": 20,
                      "rsi_overbought": 60},
    "crossasset_gate": {"gate_asset": "TLT", "gate_lookback": 126,
                        "gated": True, "trend_fast": 20, "trend_slow": 100},
    "obv_trend": {"window": 50, "price_confirm": False},
    "mfi_reversion": {"period": 14, "buy_below": 20, "sell_above": 80},
    "overnight_gap": {"gap_atr": 1.0, "hold": 3, "mode": "fade",
                      "atr_period": 14},
    "drawdown_reversion": {"lookback": 126, "entry_dd": 0.10,
                           "exit_frac": 1.0},
    "high_proximity": {"N": 126, "p": 0.95},
    "washout_recovery": {"W_dd": 252, "entry_dd": 0.10, "W_prox": 63,
                         "p": 0.95},
}

# P1 trend-following family: the four strategies swept in the
# trend-following × all-8-tickers × daily lane.
TREND_FOLLOWING_FAMILY = ["sma_crossover", "ema_crossover", "macd", "donchian"]

# Video-strategy lane: competing interpretations of the video's rules.
# ema_crossover doubles as the dual-EMA control (video Strategy A region).
VIDEO_STRATEGY_FAMILY = ["supertrend_flip", "macd_supertrend", "ema_crossover"]

# P1 mean-reversion family: the three strategies swept in the
# mean-reversion × all-8-tickers × daily lane (QUEUE item 2).
MEAN_REVERSION_FAMILY = ["rsi_mean_reversion", "bollinger_reversion",
                         "pullback"]

# Round 2 slice R1 (docs/research-round-2.md §3a): the single family swept
# in the r2-vol_filtered_trend × {AAPL, MSFT, NVDA, GLD} × daily lane.
R2_VOL_TREND_FAMILY = ["vol_filtered_trend"]

# Round 2 slice R2 (docs/research-round-2.md §3b): the single family swept
# in the r2-keltner_breakout × {BTC-USD, META, AMZN, SLV} × daily lane.
R2_KELTNER_FAMILY = ["keltner_breakout"]

# Round 2 slice R3 (docs/research-round-2.md §3c): the single PORTFOLIO
# family swept in the r2-xsec_momentum × 9-instrument-basket × daily lane.
# Portfolio interface (weights over a panel), so it lives in
# PORTFOLIO_STRATEGIES, not STRATEGIES.
R2_XSEC_FAMILY = ["xsec_momentum"]

# Round 3 (ORDER 012 night-run, post-holdout dev-only): the two oscillator
# reversion families swept in the r3-stoch-willr × all-8-tickers × daily lane.
R3_STOCH_WILLR_FAMILY = ["stochastic_reversion", "williams_r_reversion"]

# Round 3 slice 2 (ORDER 012 night-run, post-holdout dev-only): the two
# trend/momentum families swept in the r3-roc-adx × all-8-tickers × daily
# lane.
R3_ROC_ADX_FAMILY = ["roc_momentum", "adx_filtered_sma"]

# Round 3 slice 4 (ORDER 012 night-run, post-holdout dev-only): the Aroon
# trend + CCI reversion families swept in the r3-aroon-cci × 12-ticker
# mixed set (frozen 8-ticker universe + SPY/QQQ/TSLA/TLT) × daily lane.
R3_AROON_CCI_FAMILY = ["aroon_trend", "cci_reversion"]

# Round 3 slice 5 (ORDER 012 night-run, post-holdout dev-only): the four
# EXISTING mean-reversion families re-swept on HOURLY bars in the
# r3-meanrev-hourly × all-8-tickers × hourly lane (timeframe expansion —
# no new strategy code).
R3_MEANREV_HOURLY_FAMILY = ["rsi_mean_reversion", "bollinger_reversion",
                            "stochastic_reversion", "williams_r_reversion"]

# Round 3 slice 6 (ORDER 012 night-run, post-holdout dev-only): the two
# breakout/trailing-stop trend families swept in the r3-breakout ×
# 12-ticker mixed set (frozen 8-ticker universe + SPY/QQQ/TSLA/TLT) ×
# daily lane — the trend counterparts of the existing band families.
R3_BREAKOUT_FAMILY = ["bollinger_breakout", "atr_trailing"]

# Round 3 slice 7 (ORDER 012 night-run, post-holdout dev-only): the two
# PORTFOLIO families swept in the r3-xsec-expanded × 14-instrument basket
# (XSEC-14: frozen 8-ticker universe minus BTC-USD, plus the six slice-3
# instruments SPY/QQQ/TSLA/JPM/XOM/TLT) × daily lane — the existing
# xsec_momentum on the expanded basket plus its NEW mirror thesis,
# short-term cross-sectional reversal. Panel interface (weights over
# aligned closes), so both live in PORTFOLIO_STRATEGIES, not STRATEGIES.
R3_XSEC_EXPANDED_FAMILY = ["xsec_momentum", "xsec_reversal"]

# Round 3 slice 8 (ORDER 012 night-run, post-holdout dev-only): the TRIX
# momentum + Ichimoku cloud trend families swept in the r3-trix-ichimoku ×
# 12-ticker mixed set (frozen 8-ticker universe + SPY/QQQ/TSLA/TLT) ×
# daily lane.
R3_TRIX_ICHIMOKU_FAMILY = ["trix_momentum", "ichimoku_trend"]

# Round 3 slice 14 (ORDER 012 night-run, post-holdout dev-only): the four
# EXISTING Round-3 trend/momentum families re-swept on HOURLY bars in the
# r3-trend-hourly × all-8-tickers × hourly lane (timeframe expansion — no
# new strategy code; the trend-side mirror of slice 5).
R3_TREND_HOURLY_FAMILY = ["roc_momentum", "adx_filtered_sma",
                          "aroon_trend", "trix_momentum"]

# Round 3 slice 15 (ORDER 012 night-run, post-holdout dev-only): the four
# remaining EXISTING Round-3 single-instrument families re-swept on HOURLY
# bars in the r3-hourly-completion × all-8-tickers × hourly lane
# (timeframe expansion — no new strategy code; completes the Round-3
# hourly matrix started by slices 5 and 14).
R3_HOURLY_COMPLETION_FAMILY = ["cci_reversion", "bollinger_breakout",
                               "atr_trailing", "ichimoku_trend"]

# Round 4 slice R4-F (docs/research-round-4-plan.md § R4-F, ORDER 012,
# post-holdout dev-only): the single calendar family swept in the
# r4-seasonality × 15-daily-ticker × daily lane. K = 75 (5 weekdays × 15
# tickers), bar min_tstat(75) ≈ 3.21 — never lowered.
R4_SEASONALITY_FAMILY = ["weekday_long"]

# Round 4 slice R4-D (docs/research-round-4-plan.md § R4-D, ORDER 012,
# post-holdout dev-only): the single trend-strength regime-switch family
# swept in the r4-regime × six-slice-3-tickers × daily lane, WITH its
# mandatory unconditional control arm (regime_condition=False) committed
# in the same grid.
R4_REGIME_FAMILY = ["regime_switch"]

# Round 4 slice R4-E (docs/research-round-4-plan.md § R4-E, ORDER 012,
# post-holdout dev-only): the single cross-asset gate family swept in the
# r4-crossasset × {SPY, QQQ} × daily lane, WITH its mandatory ungated
# control arm (gated=False) committed in the same grid.
R4_CROSSASSET_FAMILY = ["crossasset_gate"]

# Round 6 slice R6-A (docs/research-round-6-plan.md § R6-A, ORDER 014,
# post-holdout dev-only, selection-fair gate [D-0002] applies): the two
# NEW volume-based families swept in the r6-volume × 15-daily-ticker ×
# daily lane.
R6_VOLUME_FAMILY = ["obv_trend", "mfi_reversion"]

# Round 6 slice R6-B (docs/research-round-6-plan.md § R6-B): the single
# NEW overnight-gap family swept in the r6-gap × 12-ticker mixed
# equity/ETF set (BTC-USD excluded — no overnight session) × daily lane.
R6_GAP_FAMILY = ["overnight_gap"]

# Round 6 slice R6-C (docs/research-round-6-plan.md § R6-C): the two R6-A
# volume families re-swept on HOURLY bars in the r6-volume-hourly ×
# all-8-tickers × hourly lane (timeframe expansion — no new strategy
# code; the Round-3 slice-5/14/15 precedent).
R6_VOLUME_HOURLY_FAMILY = ["obv_trend", "mfi_reversion"]

# Round 7D slice R7-D (docs/research-round-7d-plan.md § R7-D, owner GO
# 2026-07-18, post-holdout dev-only, promotion CLOSED): the single NEW
# cross-sectional PORTFOLIO family swept in the r7d-xsec-drawdown × XSEC-14
# basket × daily lane — ranks the basket on DRAWDOWN DEPTH (depth from a
# trailing L-bar close peak), structurally distinct from its return-ranked
# neighbours xsec_momentum / xsec_reversal. Panel interface (weights over
# aligned closes), so it lives in PORTFOLIO_STRATEGIES, not STRATEGIES.
R7D_XSEC_DRAWDOWN_FAMILY = "xsec_drawdown"

PORTFOLIO_STRATEGIES = {
    "xsec_momentum": xsec_momentum.generate_weights,
    "xsec_reversal": xsec_reversal.generate_weights,
    "xsec_drawdown": xsec_drawdown.generate_weights,
}

__all__ = ["STRATEGIES", "DEFAULT_PARAMS", "PORTFOLIO_STRATEGIES",
           "TREND_FOLLOWING_FAMILY",
           "VIDEO_STRATEGY_FAMILY", "MEAN_REVERSION_FAMILY",
           "R2_VOL_TREND_FAMILY", "R2_KELTNER_FAMILY", "R2_XSEC_FAMILY",
           "R3_STOCH_WILLR_FAMILY", "R3_ROC_ADX_FAMILY",
           "R3_AROON_CCI_FAMILY", "R3_MEANREV_HOURLY_FAMILY",
           "R3_BREAKOUT_FAMILY", "R3_XSEC_EXPANDED_FAMILY",
           "R3_TRIX_ICHIMOKU_FAMILY", "R3_TREND_HOURLY_FAMILY",
           "R3_HOURLY_COMPLETION_FAMILY", "R4_SEASONALITY_FAMILY",
           "R4_REGIME_FAMILY", "R4_CROSSASSET_FAMILY",
           "R6_VOLUME_FAMILY", "R6_GAP_FAMILY", "R6_VOLUME_HOURLY_FAMILY",
           "R7D_XSEC_DRAWDOWN_FAMILY",
           "buy_and_hold", "sma_crossover", "rsi_mean_reversion",
           "ema_crossover", "macd", "donchian", "supertrend_flip",
           "macd_supertrend", "bollinger_reversion", "pullback",
           "vol_filtered_trend", "keltner_breakout", "stochastic_reversion",
           "williams_r_reversion", "roc_momentum", "adx_filtered_sma",
           "aroon_trend", "cci_reversion", "bollinger_breakout",
           "atr_trailing", "trix_momentum", "ichimoku_trend",
           "weekday_long", "regime_switch", "crossasset_gate",
           "obv_trend", "mfi_reversion", "overnight_gap",
           "drawdown_reversion", "high_proximity", "washout_recovery",
           "xsec_drawdown", "xsec_momentum", "xsec_reversal"]
