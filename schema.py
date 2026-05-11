"""Auto-detect column roles (price, volume, timestamp, etc.) for ANY data file.

Strategy:
  1. Normalize column names (lowercase, strip non-alphanumeric) and match
     against a synonym table — handles "LTP_Price", "exec_px", "Last Trade Px"
     etc. without a code change.
  2. If a critical role is still unknown, ask a local Ollama model to look at
     the column names + a few sample rows and identify which column plays
     which role. This catches weird names like "p", "X1", or non-English.
  3. Always return a dict that callers can override (the UI exposes this).
"""
import re
import json
import requests


SYNONYMS = {
    "price": [
        "ltpprice", "ltp", "lasttradedprice", "tradeprice", "tradedprice",
        "executionprice", "executionpx", "fillprice", "fillpx", "lastpx",
        "px", "close", "closingprice", "closeprice", "settlementprice",
        "mid", "midprice", "tprice", "price", "p",
    ],
    "volume": [
        "ltqprice", "ltq", "lasttradedquantity", "tradedquantity",
        "quantity", "qty", "size", "volume", "vol", "ttq",
        "shares", "contracts", "lots", "q",
    ],
    "timestamp": [
        "timestamp", "datetime", "tradetime", "executiontime",
        "tradedate", "time", "date", "ts", "epoch", "exectime",
    ],
    "ticker": [
        "tradingsymbol", "ticker", "symbol", "instrument", "scrip",
        "stock", "security", "isin", "tkr",
    ],
    "bid": ["bidprice", "bid", "bestbid", "bid1"],
    "ask": ["askprice", "ask", "offer", "offerprice", "bestask", "ask1"],
    "side": ["sidevalue", "side", "buysell", "tradeside", "direction", "bs"],
    "open": ["openprice", "open"],
    "high": ["highprice", "high", "dayhigh"],
    "low": ["lowprice", "low", "daylow"],
}

CRITICAL_ROLES = ["price", "volume"]
OLLAMA_URL = "http://localhost:11434"
PREFERRED_MODELS = ["qwen3:30b", "qwen3", "llama3", "qwen2.5", "mistral"]


def normalize(name):
    return re.sub(r"[^a-z0-9]", "", str(name).lower())


def match_by_synonyms(columns):
    """Map roles -> column names using exact + substring matches on normalized names."""
    norm_map = {normalize(c): c for c in columns}
    schema = {}
    used = set()

    # Pass 1: exact matches (highest priority)
    for role, syns in SYNONYMS.items():
        for syn in syns:
            if syn in norm_map and norm_map[syn] not in used:
                schema[role] = norm_map[syn]
                used.add(norm_map[syn])
                break

    # Pass 2: substring matches for roles not yet found
    for role, syns in SYNONYMS.items():
        if role in schema:
            continue
        for norm_col, orig in norm_map.items():
            if orig in used:
                continue
            if any(syn in norm_col for syn in syns):
                schema[role] = orig
                used.add(orig)
                break

    return schema


def _pick_ollama_model():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        if r.status_code != 200:
            return None
        installed = [m["name"] for m in r.json().get("models", [])]
        for pref in PREFERRED_MODELS:
            for name in installed:
                if pref in name:
                    return name
        return installed[0] if installed else None
    except Exception:
        return None


def infer_with_llm(df, missing_roles):
    """Ask local Ollama to map columns based on names + sample values."""
    model = _pick_ollama_model()
    if not model:
        return {}

    sample = df.head(3).to_dict(orient="records")
    prompt = (
        "You map columns of a tabular financial file to semantic roles.\n\n"
        f"Available columns: {df.columns.tolist()}\n"
        f"Sample rows: {json.dumps(sample, default=str)}\n\n"
        f"For each role in this list, identify the matching column name "
        f"(or null if no column fits): {missing_roles}\n\n"
        "Reply with ONLY a JSON object, no commentary. "
        'Example: {"price": "exec_px", "volume": null}'
    )

    try:
        r = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "format": "json",
            },
            timeout=120,
        )
        if r.status_code != 200:
            return {}
        text = r.json().get("response", "{}")
        result = json.loads(text)
        # Validate — only keep columns that actually exist in df
        return {k: v for k, v in result.items() if v in df.columns}
    except Exception as e:
        print(f"LLM schema inference failed: {e}")
        return {}


def infer_schema(df, use_llm=True):
    """Detect roles -> column names. Returns dict like {'price': 'LTP_Price'}."""
    schema = match_by_synonyms(df.columns)

    if use_llm:
        missing = [r for r in CRITICAL_ROLES if r not in schema]
        if missing:
            llm_result = infer_with_llm(df, missing)
            for role, col in llm_result.items():
                if role not in schema and col:
                    schema[role] = col

    return schema


def describe_schema(schema):
    """Human-readable summary of detected roles."""
    if not schema:
        return "No roles detected."
    return ", ".join(f"{role}={col}" for role, col in sorted(schema.items()))
