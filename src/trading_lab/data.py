"""Data layer: fetch, cache, and load OHLCV bars.

Fetch path (network, used only when refreshing the cache):
  1. ``yfinance`` with ``auto_adjust=True`` (a plain, non-impersonating
     curl_cffi session is used so corporate egress proxies don't reset the
     TLS handshake).
  2. Fallback: Yahoo's v8 chart API directly via ``requests``, with the
     same adjustment yfinance applies (scale O/H/L/C by adjclose/close).
  3. Daily-only fallback: stooq.com CSV download (unadjusted; flagged when
     used).

Cache format: ``data/{timeframe}/{ticker}.csv.gz`` with columns
``timestamp,open,high,low,close,volume``. Daily timestamps are exchange-local
calendar dates (tz-naive). Hourly timestamps are UTC, stored tz-naive.

HOLDOUT ENFORCEMENT: ``load_ohlcv`` drops every bar with
``timestamp >= config.HOLDOUT_START`` unless ``unlock_holdout=True`` is
passed explicitly. That flag exists ONLY for the roadmap-P5 final review and
emits a loud warning so accidental peeking is visible in logs and pytest.
The raw cache files may contain holdout bars; no analysis code reads them.
"""

from __future__ import annotations

import gzip
import io
import logging
import time
import warnings
from pathlib import Path

import pandas as pd

from . import config

logger = logging.getLogger(__name__)

OHLCV_COLUMNS = ["open", "high", "low", "close", "volume"]

_CHART_API = "https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
_UA = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) trading-lab-research"}

_YF_INTERVAL = {"daily": "1d", "hourly": "1h"}


class DataIntegrityError(ValueError):
    """Raised when a cached dataset fails basic integrity checks."""


class HoldoutViolationWarning(UserWarning):
    """Emitted when the locked holdout is explicitly unlocked."""


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def cache_path(ticker: str, timeframe: str, data_dir: Path | None = None) -> Path:
    if timeframe not in config.TIMEFRAMES:
        raise ValueError(f"unknown timeframe {timeframe!r}; expected one of {config.TIMEFRAMES}")
    base = Path(data_dir) if data_dir is not None else config.DATA_DIR
    return base / timeframe / f"{ticker.upper()}.csv.gz"


# ---------------------------------------------------------------------------
# Normalization + integrity
# ---------------------------------------------------------------------------

def _normalize(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Standardize columns/index; daily -> naive dates, hourly -> naive UTC."""
    out = df.copy()
    out.columns = [str(c).lower() for c in out.columns]
    out = out[OHLCV_COLUMNS]
    idx = pd.DatetimeIndex(out.index)
    if timeframe == "hourly":
        if idx.tz is not None:
            idx = idx.tz_convert("UTC").tz_localize(None)
    else:
        if idx.tz is not None:
            # daily bars: keep the exchange-local calendar date
            idx = idx.tz_localize(None)
        idx = idx.normalize()
    out.index = idx
    out.index.name = "timestamp"
    # Yahoo hourly data occasionally contains all-NaN rows; drop them.
    out = out.dropna(subset=["open", "high", "low", "close"])
    out = out[~out.index.duplicated(keep="first")].sort_index()
    return out


def check_integrity(df: pd.DataFrame, ticker: str = "?") -> None:
    """Basic sanity checks; raises DataIntegrityError on failure."""
    if df.empty:
        raise DataIntegrityError(f"{ticker}: empty dataset")
    if not isinstance(df.index, pd.DatetimeIndex):
        raise DataIntegrityError(f"{ticker}: index is not a DatetimeIndex")
    if df.index.has_duplicates:
        raise DataIntegrityError(f"{ticker}: duplicate timestamps")
    if not df.index.is_monotonic_increasing:
        raise DataIntegrityError(f"{ticker}: timestamps not monotonically increasing")
    for col in ("open", "high", "low", "close"):
        if df[col].isna().any():
            raise DataIntegrityError(f"{ticker}: NaN values in {col}")
        if (df[col] <= 0).any():
            raise DataIntegrityError(f"{ticker}: non-positive prices in {col}")
    if (df["high"] < df["low"]).any():
        raise DataIntegrityError(f"{ticker}: high < low")


# ---------------------------------------------------------------------------
# Fetchers (network)
# ---------------------------------------------------------------------------

def _fetch_yfinance(ticker: str, timeframe: str, start: str | None, end: str | None) -> pd.DataFrame:
    import yfinance as yf

    session = None
    try:  # plain curl_cffi session: no browser impersonation (proxy-safe)
        import os

        from curl_cffi import requests as curl_requests

        verify = os.environ.get("REQUESTS_CA_BUNDLE") or True
        session = curl_requests.Session(verify=verify)
        session.headers["User-Agent"] = _UA["User-Agent"]
    except Exception:  # pragma: no cover - curl_cffi always ships with yfinance
        pass

    kwargs: dict = dict(interval=_YF_INTERVAL[timeframe], auto_adjust=True,
                        progress=False, threads=False, session=session)
    if timeframe == "hourly" and start is None:
        kwargs["period"] = "730d"  # yfinance/Yahoo max for 1h bars
    else:
        kwargs["start"] = start
        kwargs["end"] = end
    df = yf.download(ticker, **kwargs)
    if df is None or df.empty:
        raise RuntimeError(f"yfinance returned no data for {ticker} {timeframe}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return _normalize(df, timeframe)


def _fetch_chart_api(ticker: str, timeframe: str, start: str | None, end: str | None) -> pd.DataFrame:
    """Yahoo v8 chart API via plain requests, auto-adjusted like yfinance."""
    import requests

    params: dict = {"interval": _YF_INTERVAL[timeframe], "events": "div,splits"}
    if timeframe == "hourly" and start is None:
        params["range"] = "730d"
    else:
        start_ts = pd.Timestamp(start or config.DAILY_START)
        end_ts = pd.Timestamp(end) if end else pd.Timestamp.utcnow().tz_localize(None)
        params["period1"] = int(start_ts.timestamp())
        params["period2"] = int(end_ts.timestamp())
    resp = requests.get(_CHART_API.format(ticker=ticker), params=params,
                        headers=_UA, timeout=30)
    resp.raise_for_status()
    payload = resp.json()["chart"]
    if payload.get("error"):
        raise RuntimeError(f"chart API error for {ticker}: {payload['error']}")
    result = payload["result"][0]
    ts = result.get("timestamp")
    if not ts:
        raise RuntimeError(f"chart API returned no bars for {ticker} {timeframe}")
    quote = result["indicators"]["quote"][0]
    tz = result["meta"].get("exchangeTimezoneName", "UTC")
    idx = pd.to_datetime(ts, unit="s", utc=True).tz_convert(tz)
    df = pd.DataFrame({k: quote[k] for k in OHLCV_COLUMNS}, index=idx)
    adj = result["indicators"].get("adjclose")
    if adj and adj[0].get("adjclose"):
        factor = pd.Series(adj[0]["adjclose"], index=idx) / df["close"]
        for col in ("open", "high", "low", "close"):
            df[col] = df[col] * factor
    return _normalize(df, timeframe)


def _fetch_stooq(ticker: str, timeframe: str, start: str | None, end: str | None) -> pd.DataFrame:
    """Daily-only fallback. Unadjusted for dividends — flag when used."""
    import requests

    if timeframe != "daily":
        raise RuntimeError("stooq fallback supports daily bars only")
    url = f"https://stooq.com/q/d/l/?s={ticker.lower()}.us&i=d"
    resp = requests.get(url, headers=_UA, timeout=30)
    resp.raise_for_status()
    df = pd.read_csv(io.StringIO(resp.text), parse_dates=["Date"], index_col="Date")
    df.columns = [c.lower() for c in df.columns]
    if "volume" not in df.columns:
        df["volume"] = 0
    logger.warning("stooq fallback used for %s: prices are NOT dividend-adjusted", ticker)
    df = df.loc[str(start or config.DAILY_START):str(end) if end else None]
    return _normalize(df, timeframe)


_FETCHERS = {
    "yfinance": _fetch_yfinance,
    "chart": _fetch_chart_api,
    "stooq": _fetch_stooq,
}


def fetch_ohlcv(ticker: str, timeframe: str, start: str | None = None,
                end: str | None = None,
                sources: tuple[str, ...] = ("yfinance", "chart", "stooq")) -> pd.DataFrame:
    """Fetch bars from the network, trying each source in order.

    Fetches EVERYTHING available (including holdout bars). The holdout rail
    is enforced at load time, not fetch time.
    """
    if timeframe == "daily" and start is None:
        start = config.DAILY_START
    errors = []
    for name in sources:
        try:
            df = _FETCHERS[name](ticker, timeframe, start, end)
            check_integrity(df, ticker)
            logger.info("fetched %s %s via %s: %d bars", ticker, timeframe, name, len(df))
            return df
        except Exception as exc:  # try next source
            errors.append(f"{name}: {exc}")
            time.sleep(1)
    raise RuntimeError(f"all sources failed for {ticker} {timeframe}: {errors}")


# ---------------------------------------------------------------------------
# Cache I/O
# ---------------------------------------------------------------------------

def save_cache(df: pd.DataFrame, ticker: str, timeframe: str,
               data_dir: Path | None = None) -> Path:
    path = cache_path(ticker, timeframe, data_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    out = df.copy()
    out.index.name = "timestamp"
    # mtime=0 keeps the gzip byte-for-byte reproducible for identical data.
    with gzip.GzipFile(path, "wb", mtime=0) as fh:
        fh.write(out.to_csv(float_format="%.6f").encode())
    return path


def load_ohlcv(ticker: str, timeframe: str = "daily", *,
               start: str | None = None, end: str | None = None,
               unlock_holdout: bool = False,
               data_dir: Path | None = None) -> pd.DataFrame:
    """Load bars from the local cache, enforcing the locked holdout.

    By default every bar with ``timestamp >= config.HOLDOUT_START`` is
    excluded. ``unlock_holdout=True`` is reserved for the P5 final review.
    """
    path = cache_path(ticker, timeframe, data_dir)
    if not path.exists():
        raise FileNotFoundError(
            f"no cached data for {ticker} {timeframe} at {path}; "
            "run scripts/fetch_data.py first")
    df = pd.read_csv(path, parse_dates=["timestamp"], index_col="timestamp")
    check_integrity(df, ticker)

    holdout = pd.Timestamp(config.HOLDOUT_START)
    if unlock_holdout:
        msg = (f"HOLDOUT UNLOCKED for {ticker} {timeframe}: bars >= "
               f"{config.HOLDOUT_START} are included. This is permitted ONLY "
               "for the P5 final review (docs/founding-plan.md).")
        logger.warning(msg)
        warnings.warn(msg, HoldoutViolationWarning, stacklevel=2)
    else:
        df = df[df.index < holdout]

    if start is not None:
        df = df[df.index >= pd.Timestamp(start)]
    if end is not None:
        df = df[df.index < pd.Timestamp(end)]
    return df


def refresh_cache(tickers: list[str] | None = None,
                  timeframes: tuple[str, ...] = config.TIMEFRAMES,
                  data_dir: Path | None = None) -> dict[str, int]:
    """Fetch + cache all tickers/timeframes. Returns {ticker/timeframe: rows}."""
    counts: dict[str, int] = {}
    for timeframe in timeframes:
        for ticker in (tickers or config.UNIVERSE):
            df = fetch_ohlcv(ticker, timeframe)
            save_cache(df, ticker, timeframe, data_dir)
            counts[f"{ticker}/{timeframe}"] = len(df)
    return counts
