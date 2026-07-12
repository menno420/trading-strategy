#!/usr/bin/env python3
"""PHASE 1 - MTF CONDITIONING STUDY (DEV-ONLY, research-only, promotion-closed).

The owner's core mechanism claim:
  1. (Test A) a lower-timeframe Bollinger band break becomes MORE likely when
     the higher timeframe is stretched beyond its own outer band.
  2. (Test B) GIVEN a lower-band touch, mean-reversion back to the mid-band is
     RELIABLE when the higher TF is in-range and FAILS when the higher TF is
     stretched.

This script measures those conditional probabilities directly, BEFORE any
strategy P&L. A null (probabilities do not separate) is a valid, publishable
result and would mean the strategy has no foundation.

RAILS: no holdout access (load_ohlcv only, dev bars < 2025-01-09), no network,
costs are irrelevant here (pure conditional probabilities). Strictly causal
alignment via trading_lab.mtf.align_higher_to_lower (one-coarse-bar lag).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from trading_lab.data import load_ohlcv  # noqa: E402
from trading_lab.mtf import (  # noqa: E402
    align_higher_to_lower, boll_z, resample_ohlcv,
)

LOOKBACK = 20
K = 2.0            # outer band multiple
STOP_Z = -3.5      # reversion failure barrier
HORIZON = LOOKBACK  # forward horizon in lower-TF bars

HOURLY_TICKERS = ["AAPL", "AMZN", "GLD", "GOOGL", "META", "MSFT", "NVDA", "SLV"]
DAILY_TICKERS = ["AAPL", "AMZN", "BTC-USD", "GLD", "GOOGL", "META", "MSFT",
                 "NVDA", "SLV"]

BUCKET_EDGES = [-np.inf, -2.0, -1.0, 0.0, 1.0, 2.0, np.inf]
BUCKET_LABELS = ["(-inf,-2]", "(-2,-1]", "(-1,0]", "(0,1]", "(1,2]", "(2,inf)"]

# (name, lower_kind, higher_kind). "kind" is either "native:<tf>" or
# "resample:<base_tf>:<rule>".
PAIRS = [
    ("1h/4h", "native:hourly", "resample:hourly:4h", HOURLY_TICKERS),
    ("1h/6h", "native:hourly", "resample:hourly:6h", HOURLY_TICKERS),
    ("2h/daily", "resample:hourly:2h", "native:daily", HOURLY_TICKERS),
    ("daily/weekly", "native:daily", "resample:daily:W", DAILY_TICKERS),
]


def _frame(kind: str, ticker: str) -> pd.DataFrame:
    tag, *rest = kind.split(":")
    if tag == "native":
        return load_ohlcv(ticker, rest[0])
    if tag == "resample":
        base, rule = rest
        return resample_ohlcv(load_ohlcv(ticker, base), rule)
    raise ValueError(kind)


def _bucket_of(z: float) -> int:
    if np.isnan(z):
        return -1
    return int(np.digitize([z], BUCKET_EDGES[1:-1])[0])  # 0..5


def _touch_events(z_l: pd.Series) -> np.ndarray:
    """Fresh lower-band touch entries: z crosses from > -K to <= -K."""
    below = z_l <= -K
    prev = below.shift(1, fill_value=False)
    return (below & ~prev).to_numpy()


def _reversion_outcome(z_l: np.ndarray, close: np.ndarray, t: int) -> tuple:
    """From a touch at index t, first-passage over the next HORIZON bars.

    success = z_l returns to >= 0 before z_l <= STOP_Z. Returns
    (success:bool, fwd_mean_ret:float over the path t+1..exit)."""
    n = len(z_l)
    end = min(t + HORIZON, n - 1)
    exit_i = end
    success = False
    for j in range(t + 1, end + 1):
        if z_l[j] <= STOP_Z:
            exit_i = j
            success = False
            break
        if z_l[j] >= 0.0:
            exit_i = j
            success = True
            break
    if exit_i <= t:
        return success, np.nan
    # mean per-bar close return over the held path t+1..exit_i
    seg = close[t:exit_i + 1]
    rets = seg[1:] / seg[:-1] - 1.0
    fwd = float(np.mean(rets)) if len(rets) else np.nan
    return success, fwd


def _spread(vals: list[float]) -> dict:
    a = [v for v in vals if v is not None and not (isinstance(v, float) and np.isnan(v))]
    if not a:
        return {"min": None, "median": None, "max": None, "n_tickers": 0}
    return {"min": float(np.min(a)), "median": float(np.median(a)),
            "max": float(np.max(a)), "n_tickers": len(a)}


def study_pair(name, lower_kind, higher_kind, tickers) -> dict:
    # pooled accumulators
    tA_bucket_touch = {b: [0, 0] for b in range(6)}  # bucket -> [touches, bars]
    tA_inrange = [0, 0]
    tA_stretched = [0, 0]
    # Test B pooled: cell -> {"succ":int,"n":int,"fwd":[...]}
    tB = {"in_range": {"succ": 0, "n": 0, "fwd": []},
          "stretched": {"succ": 0, "n": 0, "fwd": []}}
    tB_bucket = {b: {"succ": 0, "n": 0, "fwd": []} for b in range(6)}
    # per-ticker for spread
    perT_A_in, perT_A_st = [], []
    perT_B_in, perT_B_st = [], []
    per_ticker_detail = {}

    for tk in tickers:
        lo = _frame(lower_kind, tk)
        hi = _frame(higher_kind, tk)
        z_l = boll_z(lo["close"], LOOKBACK, ddof=0)
        z_h = boll_z(hi["close"], LOOKBACK, ddof=0)
        z_h_al = align_higher_to_lower(z_h, lo.index)
        valid = z_l.notna() & z_h_al.notna()

        zl_arr = z_l.to_numpy()
        close_arr = lo["close"].to_numpy()
        zh_arr = z_h_al.to_numpy()
        valid_arr = valid.to_numpy()

        # ---- Test A: state-based P(touch | bucket) over valid bars ----
        a_in = [0, 0]
        a_st = [0, 0]
        for i in range(len(lo)):
            if not valid_arr[i]:
                continue
            b = _bucket_of(zh_arr[i])
            touch = 1 if zl_arr[i] <= -K else 0
            tA_bucket_touch[b][0] += touch
            tA_bucket_touch[b][1] += 1
            stretched = abs(zh_arr[i]) >= K
            if stretched:
                tA_stretched[0] += touch; tA_stretched[1] += 1
                a_st[0] += touch; a_st[1] += 1
            else:
                tA_inrange[0] += touch; tA_inrange[1] += 1
                a_in[0] += touch; a_in[1] += 1
        perT_A_in.append(a_in[0] / a_in[1] if a_in[1] else np.nan)
        perT_A_st.append(a_st[0] / a_st[1] if a_st[1] else np.nan)

        # ---- Test B: reversion success | regime, on fresh touch events ----
        events = _touch_events(z_l)
        b_in = {"succ": 0, "n": 0}
        b_st = {"succ": 0, "n": 0}
        for i in range(len(lo)):
            if not events[i] or not valid_arr[i]:
                continue
            succ, fwd = _reversion_outcome(zl_arr, close_arr, i)
            bkt = _bucket_of(zh_arr[i])
            tB_bucket[bkt]["n"] += 1
            tB_bucket[bkt]["succ"] += int(succ)
            if not np.isnan(fwd):
                tB_bucket[bkt]["fwd"].append(fwd)
            if abs(zh_arr[i]) >= K:
                cell, per = tB["stretched"], b_st
            else:
                cell, per = tB["in_range"], b_in
            cell["n"] += 1; cell["succ"] += int(succ)
            per["n"] += 1; per["succ"] += int(succ)
            if not np.isnan(fwd):
                cell["fwd"].append(fwd)
        perT_B_in.append(b_in["succ"] / b_in["n"] if b_in["n"] else np.nan)
        perT_B_st.append(b_st["succ"] / b_st["n"] if b_st["n"] else np.nan)
        per_ticker_detail[tk] = {
            "n_lower_bars": int(len(lo)),
            "A_p_touch_in_range": perT_A_in[-1],
            "A_p_touch_stretched": perT_A_st[-1],
            "B_success_in_range": perT_B_in[-1], "B_n_in_range": b_in["n"],
            "B_success_stretched": perT_B_st[-1], "B_n_stretched": b_st["n"],
        }

    def rate(pair):
        return pair[0] / pair[1] if pair[1] else None

    def bcell(c):
        return {"success_rate": (c["succ"] / c["n"] if c["n"] else None),
                "n_events": c["n"],
                "fwd_mean_ret": (float(np.mean(c["fwd"])) if c["fwd"] else None)}

    sr_in = rate((tB["in_range"]["succ"], tB["in_range"]["n"]))
    sr_st = rate((tB["stretched"]["succ"], tB["stretched"]["n"]))
    return {
        "lower_kind": lower_kind, "higher_kind": higher_kind,
        "n_tickers": len(tickers), "tickers": tickers,
        "test_A": {
            "p_touch_by_bucket": {
                BUCKET_LABELS[b]: {"p_touch": rate(tA_bucket_touch[b]),
                                   "n_bars": tA_bucket_touch[b][1]}
                for b in range(6)},
            "in_range": {"p_touch": rate(tA_inrange), "n_bars": tA_inrange[1]},
            "stretched": {"p_touch": rate(tA_stretched), "n_bars": tA_stretched[1]},
            "stretched_minus_inrange": (
                (rate(tA_stretched) - rate(tA_inrange))
                if rate(tA_stretched) is not None and rate(tA_inrange) is not None
                else None),
            "per_ticker_spread": {
                "p_touch_in_range": _spread(perT_A_in),
                "p_touch_stretched": _spread(perT_A_st)},
        },
        "test_B": {
            "in_range": bcell(tB["in_range"]),
            "stretched": bcell(tB["stretched"]),
            "success_in_minus_stretched": (
                (sr_in - sr_st) if sr_in is not None and sr_st is not None else None),
            "by_bucket": {BUCKET_LABELS[b]: bcell(tB_bucket[b]) for b in range(6)},
            "per_ticker_spread": {
                "success_in_range": _spread(perT_B_in),
                "success_stretched": _spread(perT_B_st)},
        },
        "per_ticker": per_ticker_detail,
    }


def main():
    results = {
        "meta": {
            "phase": "PHASE 1 conditioning study (DEV-ONLY, promotion-closed)",
            "lookback": LOOKBACK, "k": K, "stop_z": STOP_Z, "horizon": HORIZON,
            "holdout": "excluded (load_ohlcv default, < 2025-01-09)",
            "note": ("descriptive study, not a variant selection; 4 TF-pair "
                     "descriptive passes"),
        },
        "pairs": {},
    }
    for name, lk, hk, tks in PAIRS:
        print(f"[pair] {name} lower={lk} higher={hk} n_tickers={len(tks)}")
        results["pairs"][name] = study_pair(name, lk, hk, tks)

    # ---- VERDICT ----
    seps_A, seps_B = [], []
    lines = []
    for name in results["pairs"]:
        A = results["pairs"][name]["test_A"]
        B = results["pairs"][name]["test_B"]
        dA = A["stretched_minus_inrange"]
        dB = B["success_in_minus_stretched"]
        seps_A.append(dA); seps_B.append(dB)
        lines.append(
            f"{name}: TestA P(touch) stretched={A['stretched']['p_touch']:.3f} "
            f"vs in-range={A['in_range']['p_touch']:.3f} (Δ={dA:+.3f}); "
            f"TestB P(revert) in-range={B['in_range']['success_rate']} "
            f"vs stretched={B['stretched']['success_rate']} "
            f"(Δ={dB if dB is None else round(dB,3)}, "
            f"N_in={B['in_range']['n_events']}, N_st={B['stretched']['n_events']})")

    # separation judged materially (>= 0.10 abs) AND consistent in sign
    def consistent(vals, thresh=0.10):
        v = [x for x in vals if x is not None]
        if not v:
            return False, 0.0
        signs = set(np.sign([x for x in v]))
        material = np.median([abs(x) for x in v]) >= thresh
        return (material and len(signs) == 1), float(np.median(v))

    consB, medB = consistent(seps_B)
    verdict = (
        "MECHANISM SEPARATES (dev, promotion-closed): reversion success is "
        "materially and consistently higher when the higher TF is in-range."
        if consB else
        "NULL / NO MATERIAL SEPARATION (dev, promotion-closed): the conditional "
        "reversion-success probabilities do NOT separate materially/consistently "
        "across TF pairs. Under this design the MTF conditioning has no tradeable "
        "foundation; a positive grid result would be suspect.")
    results["verdict"] = {
        "test_B_median_success_delta_in_minus_stretched": medB,
        "separates": bool(consB),
        "line": verdict,
        "per_pair": lines,
    }

    out = REPO / "scratchpad" / "mtf_conditioning_results.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(results, indent=2))

    # human table
    print("\n" + "=" * 78)
    print("PHASE 1 CONDITIONING STUDY - HUMAN TABLE (dev-only, promotion-closed)")
    print("=" * 78)
    for name in results["pairs"]:
        P = results["pairs"][name]
        A, B = P["test_A"], P["test_B"]
        print(f"\n### {name}  (lower={P['lower_kind']}, higher={P['higher_kind']}, "
              f"n_tickers={P['n_tickers']})")
        print("  Test A  P(lower-band touch | higher-TF z_H bucket):")
        for lab in BUCKET_LABELS:
            c = A["p_touch_by_bucket"][lab]
            p = c["p_touch"]
            print(f"    {lab:>10}: P(touch)={p if p is None else round(p,4)}  "
                  f"(n_bars={c['n_bars']})")
        sA = A["per_ticker_spread"]
        print(f"    in-range P(touch)={A['in_range']['p_touch']:.4f}  "
              f"stretched P(touch)={A['stretched']['p_touch']:.4f}  "
              f"Δ(st-in)={A['stretched_minus_inrange']:+.4f}")
        print(f"    per-ticker P(touch|in-range) spread: {sA['p_touch_in_range']}")
        print(f"    per-ticker P(touch|stretched) spread: {sA['p_touch_stretched']}")
        print("  Test B  P(reversion success) | regime:")
        print(f"    in-range : success={B['in_range']['success_rate']}  "
              f"N={B['in_range']['n_events']}  "
              f"fwd_mean_ret={B['in_range']['fwd_mean_ret']}")
        print(f"    stretched: success={B['stretched']['success_rate']}  "
              f"N={B['stretched']['n_events']}  "
              f"fwd_mean_ret={B['stretched']['fwd_mean_ret']}")
        print(f"    Δ(in-stretched)={B['success_in_minus_stretched']}")
        sB = B["per_ticker_spread"]
        print(f"    per-ticker success(in-range) spread: {sB['success_in_range']}")
        print(f"    per-ticker success(stretched) spread: {sB['success_stretched']}")
    print("\n" + "=" * 78)
    print("VERDICT:", verdict)
    print("=" * 78)
    print("wrote", out)


if __name__ == "__main__":
    main()
