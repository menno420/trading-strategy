# Strategy-family catalog

> **Status:** `reference`
>
> Generated 2026-07-17 (UTC) from the strategies tree
> (`src/trading_lab/strategies/__init__.py`) and the cited results docs. This
> is an ADJACENCY REFERENCE, not a source of truth: the code and the merged
> results docs win on any conflict. Docs only — this file changes no verdict,
> schedules nothing, reads no holdout, and implies no promotion.

The lab carries **32 strategy families** in `src/trading_lab/strategies/`
(`STRATEGIES` = 30 single-instrument families + `PORTFOLIO_STRATEGIES` = 2
panel families). Every family was tested **post-holdout, dev-only**: the
holdout is SPENT and promotion is CLOSED, so **0 families are promoted** and
every `KEEP-dev` below is a **dev-candidate only** — never a finding, never an
out-of-sample or live claim. The multiple-testing bar
(`trading_lab.promotion.min_tstat`, ~2.638 at K=12) only ever rises, and no
family's best standing t comes near it. This table exists so a round plan or
proposal can cite a family's class, thesis, round, and standing verdict
directly instead of re-deriving adjacency from seven results docs.

## The families

| Family | Class | Thesis (one line) | Round tested | Standing verdict | Source |
|---|---|---|---|---|---|
| `buy_and_hold` | single-name | Long 1 unit for the whole period — the benchmark every lane is scored against. | P0/P1 baseline | benchmark (B&H) | `strategies/buy_and_hold.py`; `p1-*-results.md` |
| `sma_crossover` | trend | Long while the fast SMA is above the slow SMA, else flat. | P1 trend / re-tested Round 3 | KEEP-dev | `research-round-3-results.md` (XOM, TLT daily) |
| `rsi_mean_reversion` | mean-rev | Long below RSI oversold, exit above overbought (Wilder smoothing). | P0/P1 mean-rev / Round 3 hourly | KEEP-dev | `research-round-3-results.md` (JPM daily; AAPL/GOOGL/AMZN hourly) |
| `ema_crossover` | trend | Long while the fast EMA is above the slow EMA, else flat. | P1 trend / video control / Round 3+5 | KEEP-dev | `research-round-5-results.md` (TLT daily, survived all four R5 slices) |
| `macd` | trend | Long while the MACD line is above its signal line. | P1 trend | KILL | `p1-trend-following-results.md`; `research-program-retrospective.md` |
| `donchian` | breakout | Long on close breaking the prior N-bar high, exit on the M-bar low (turtle). | P1 trend / P5 holdout / Round 3 | KEEP-dev | `research-round-3-results.md` (XOM, TLT daily); P5 holdout t≈0.02 (retrospective) |
| `supertrend_flip` | trend | SuperTrend-flip entry with EMA + MACD filters (video interpretation i). | P1 video | KILL | `p1-video-strategy-results.md` (BTC-only, "none is a finding") |
| `macd_supertrend` | trend | MACD-cross entry with SuperTrend + EMA filters (video interpretation ii). | P1 video | KILL | `p1-video-strategy-results.md` (BTC-only, "none is a finding") |
| `bollinger_reversion` | mean-rev | Long when the close z-score drops below −z_entry, exit as it recovers. | P1 mean-rev (0/8 daily) / Round 3 hourly | KEEP-dev | `research-round-3-results.md` (MSFT/AMZN/META hourly); `p1-mean-reversion-results.md` (0/8 daily) |
| `pullback` | mean-rev | Buy a fresh short-horizon low (optionally in an uptrend), sell the recovery. | P1 mean-rev | KILL | `p1-mean-reversion-results.md` |
| `vol_filtered_trend` | trend | SMA crossover gated to calm realized-vol regimes (filter-off arm is the control). | Round 2 (slice R1) | KILL | `research-round-2-results.md` (0 KEEP / 4 KILL; the filter added nothing) |
| `keltner_breakout` | breakout | Long on close > EMA(n) + m·ATR(n), exit on close < EMA(n). | Round 2 (slice R2) | KEEP-dev | `research-round-2-results.md` (2 KEEP / 2 KILL) |
| `stochastic_reversion` | mean-rev | Long on slow-stochastic %K crossing up out of oversold, exit above sell_above. | Round 3 / Round 5 | KEEP-dev | `research-round-3-results.md` (AAPL/GOOGL hourly); META hourly demoted to KILL in `research-round-5-results.md` |
| `williams_r_reversion` | mean-rev | Long on Williams %R crossing up out of oversold, exit above sell_above. | Round 3 / Round 5 | KEEP-dev | `research-round-3-results.md` (SLV daily); survived all four R5 slices (`research-round-5-results.md`) |
| `roc_momentum` | trend | Long when N-day rate-of-change rises above entry, exit below exit (hysteresis). | Round 3 | KEEP-dev | `research-round-3-results.md` (META daily) |
| `adx_filtered_sma` | trend | SMA crossover gated to Wilder-ADX trending regimes (mirror of `vol_filtered_trend`). | Round 3 | KEEP-dev | `research-round-3-results.md` (META daily) |
| `aroon_trend` | trend | Long on Aroon-oscillator trend with an entry/exit hysteresis band. | Round 3 | KEEP-dev | `research-round-3-results.md` (AAPL/META/TLT daily) |
| `cci_reversion` | mean-rev | Long on Lambert CCI crossing up out of oversold, exit above sell_above. | Round 3 | KEEP-dev | `research-round-3-results.md` (SLV daily) |
| `bollinger_breakout` | breakout | Long on close crossing above the upper Bollinger band, exit below the middle (inverse of `bollinger_reversion`). | Round 3 / Round 5 | KEEP-dev | `research-round-3-results.md` (AAPL/TSLA daily); BTC-USD survived R5 (`research-round-5-results.md`) |
| `atr_trailing` | breakout | N-high breakout entry, chandelier ATR trailing-stop exit (first stateful exit). | Round 3 | KEEP-dev | `research-round-3-results.md` (META daily) |
| `trix_momentum` | trend | Long while TRIX (triple-smoothed EMA rate-of-change) is above its signal line. | Round 3 | KEEP-dev | `research-round-3-results.md` (AAPL/META/SLV/TLT daily) |
| `ichimoku_trend` | trend | Long above the Ichimoku cloud with tenkan > kijun; flat on a full break below. | Round 3 / Round 5 | KEEP-dev | `research-round-3-results.md` (META/TLT daily); META survived R5 (`research-round-5-results.md`) |
| `weekday_long` | state | Long only on bars falling on one chosen weekday, flat otherwise (calendar rule). | Round 4 (slice R4-F) | burned-class | `research-round-4-results.md` §R4-F (0/75 combos, 30 KILL-SIG; `research-round-7-plan.md` "burned the class") |
| `regime_switch` | state | Trend component in the strong-trend tercile, flat/reversion in the weak (control = no gate). | Round 4 (slice R4-D) | burned-class | `research-round-4-results.md` §R4-D (0 KEEP / 6 KILL; the ungated control beat the gate) |
| `crossasset_gate` | state | Frozen EMA-cross equity component gated on another instrument's momentum sign (control = ungated). | Round 4 (slice R4-E) | burned-class | `research-round-4-results.md` §R4-E (0 KEEP / 2 KILL; the ungated control beat the gate) |
| `obv_trend` | volume | Long while on-balance volume sits above its own trailing SMA (first volume family). | Round 6 (slice R6-A) | KEEP-dev | `research-round-6-results.md` §R6-A (BTC-USD/META daily; both KEEPs are `obv_trend`) |
| `mfi_reversion` | volume | Long on Money Flow Index crossing up out of oversold (volume-weighted oscillator). | Round 6 (R6-A daily + R6-C hourly) | KEEP-dev | `research-round-6-results.md` §R6-C (AMZN hourly only; 0/15 daily, MSFT daily KILL-SIG) |
| `overnight_gap` | gap | Trade the ATR-normalized overnight gap (fade/follow mirror theses; first signal to read the open). | Round 6 (slice R6-B) | burned-class | `research-round-6-results.md` §R6-B (0 KEEP / 12 KILL / 7 KILL-SIG; harmful in both theses) |
| `drawdown_reversion` | state | Long-only reversion on drawdown depth from a trailing-window peak, hysteresis exit. | Round 7 (slice R7-A) | KEEP-dev | `research-round-7-results.md` §R7-A (SLV/TLT/XOM daily; 3 KEEP-dev / 12 KILL) |
| `high_proximity` | state | Long while the close sits within fraction p of its trailing N-bar close-maximum (52-week-high as a state band). | Round 7 (slice R7-B) | KEEP-dev | `research-round-7-results.md` §R7-B (BTC-USD/TSLA daily; 2 KEEP-dev / 13 KILL) |
| `xsec_momentum` | portfolio | Hold the top-k trailing-return names equal-weight, periodic rebalance (first portfolio family). | Round 2 / Round 3 (XSEC-14) | KEEP-dev | `research-round-2-results.md` (3 KEEP / 3 KILL); `research-round-3-results.md` (6/6 XSEC-14) |
| `xsec_reversal` | portfolio | Hold the k worst trailing-return names equal-weight, weekly rebalance (mirror of `xsec_momentum`). | Round 3 (slice 7) | KILL | `research-round-3-results.md` (0 KEEP / 6; all 6 XSEC-14 KEEPs were `xsec_momentum`) |

## How to read this table

- **Class** is the single best-fit label from the allowed set (single-name /
  portfolio / trend / mean-rev / volume / gap / breakout / state); several
  families straddle two ideas (e.g. `adx_filtered_sma` is a `state`-gated
  `trend` rule) and the parenthetical thesis names the second idea.
- **`KEEP-dev` = dev-candidate only, never a finding.** It means the family
  holds at least one lane that beat same-window B&H under the Round-2 rule,
  dev-side; it is NOT out-of-sample, NOT promoted, and NOT a live claim. The
  Source column names the specific KEEP-dev lane(s).
- **`KILL`** = every lane tested was killed (no standing dev-candidate).
- **`KILL-SIG`** = a lane graded significantly HARMFUL (t ≤ −2.638 at K=12);
  noted inline in the Source column where it applies (`mfi_reversion` MSFT
  daily) but not the family's headline standing where the family also holds a
  KEEP-dev.
- **`burned-class`** = the whole idea class was nulled (0 KEEP across the
  family, often with KILL-SIG mass) — a decisive dead end recorded as a
  first-class result, not merely an unproductive search. The Round-4
  conditioning families (`regime_switch`, `crossasset_gate`), the calendar
  family (`weekday_long`), and the overnight-gap family (`overnight_gap`) are
  the four burned classes.
- **`benchmark (B&H)`** = `buy_and_hold` is the control every other lane is
  scored against, not a candidate.
- **All verdicts are dev-only.** The holdout is SPENT and promotion is CLOSED;
  no row carries any OOS or live implication.

## Provenance

Generated 2026-07-17 from the strategies tree
(`src/trading_lab/strategies/__init__.py` `STRATEGIES` + `PORTFOLIO_STRATEGIES`,
each `strategies/<name>.py` module docstring) and the cited results docs
(`p1-trend-following-results.md`, `p1-mean-reversion-results.md`,
`p1-video-strategy-results.md`, `research-round-2-results.md`,
`research-round-3-results.md`, `research-round-4-results.md`,
`research-round-5-results.md`, `research-round-6-results.md`,
`research-round-7-results.md`, `research-program-retrospective.md`). On any
conflict the code and the merged results docs win over this reference.
