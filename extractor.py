"""Load CSV / Excel / JSON files into a pandas DataFrame."""
import pandas as pd
import json


def load_file(filepath):
    if filepath.endswith(".csv"):
        return pd.read_csv(filepath)
    if filepath.endswith(".xlsx") or filepath.endswith(".xls"):
        return pd.read_excel(filepath)
    if filepath.endswith(".json"):
        with open(filepath) as f:
            data = json.load(f)
        if isinstance(data, list):
            return pd.DataFrame(data)
        return pd.json_normalize(data)
    raise ValueError(f"Unsupported file type: {filepath}")


def get_summary(df):
    return {
        "rows": int(len(df)),
        "columns": df.columns.tolist(),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing_values": {c: int(v) for c, v in df.isnull().sum().items()},
    }
