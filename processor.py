"""Calculate financial ratios, trends, and indicators from price data.

Column detection is delegated to schema.py so any naming convention works.
Callers can pass a pre-computed `schema` dict to avoid re-detecting.
"""
import pandas as pd
from schema import infer_schema


def _prices(df, schema):
    col = schema.get("price")
    if col is None or col not in df.columns:
        return None, None
    series = pd.to_numeric(df[col], errors="coerce").dropna()
    return col, (series if not series.empty else None)


def calculate_ratios(df, schema=None):
    if schema is None:
        schema = infer_schema(df)

    ratios = {}
    price_col, prices = _prices(df, schema)
    if prices is None:
        return ratios

    ratios["price_column"] = price_col
    ratios["current_price"] = round(float(prices.iloc[-1]), 4)
    ratios["start_price"] = round(float(prices.iloc[0]), 4)
    ratios["price_change_pct"] = round(
        (prices.iloc[-1] - prices.iloc[0]) / prices.iloc[0] * 100, 2
    )
    ratios["volatility"] = round(float(prices.std()), 4)
    ratios["max_price"] = round(float(prices.max()), 4)
    ratios["min_price"] = round(float(prices.min()), 4)
    ratios["avg_price"] = round(float(prices.mean()), 4)

    vol_col = schema.get("volume")
    if vol_col and vol_col in df.columns:
        vol = pd.to_numeric(df[vol_col], errors="coerce").dropna()
        if not vol.empty:
            ratios["volume_column"] = vol_col
            ratios["avg_volume"] = round(float(vol.mean()), 2)
            ratios["total_volume"] = round(float(vol.sum()), 2)

    return ratios


def detect_trend(df, schema=None):
    if schema is None:
        schema = infer_schema(df)
    _, prices = _prices(df, schema)
    if prices is None:
        return "NO PRICE COLUMN"
    if len(prices) < 20:
        return "INSUFFICIENT DATA"

    ma_short = prices.rolling(20).mean().iloc[-1]
    ma_long = prices.rolling(min(50, len(prices))).mean().iloc[-1]

    if ma_short > ma_long * 1.02:
        return "UPTREND"
    if ma_short < ma_long * 0.98:
        return "DOWNTREND"
    return "SIDEWAYS"


def calculate_rsi(df, period=14, schema=None):
    if schema is None:
        schema = infer_schema(df)
    _, prices = _prices(df, schema)
    if prices is None or len(prices) <= period:
        return None

    delta = prices.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, 1e-9)
    rsi = 100 - (100 / (1 + rs))
    last = rsi.dropna()
    return round(float(last.iloc[-1]), 2) if not last.empty else None
