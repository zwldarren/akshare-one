from typing import Any

import pandas as pd


def parse_kline_data(data: dict[str, Any]) -> pd.DataFrame:
    """
    Parses K-line data from the API response into a pandas DataFrame.
    """
    klines = data.get("data", {}).get("klines", [])
    if not klines:
        return pd.DataFrame(
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

    records = []
    for kline in klines:
        parts = kline.split(",")
        if len(parts) >= 6:
            records.append(
                {
                    "timestamp": parts[0],
                    "open": float(parts[1]),
                    "close": float(parts[2]),
                    "high": float(parts[3]),
                    "low": float(parts[4]),
                    "volume": int(parts[5]),
                }
            )

    df = pd.DataFrame(records)
    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["timestamp"] = df["timestamp"].dt.tz_localize("Asia/Shanghai")
        df = df[["timestamp", "open", "high", "low", "close", "volume"]]
    return df


def parse_realtime_data(data: dict[str, Any]) -> pd.DataFrame:
    """
    Parses real-time quote data from the API response into a pandas DataFrame.
    """
    stock_data = data.get("data")
    if not stock_data:
        return pd.DataFrame()

    df = pd.DataFrame(
        [
            {
                "symbol": stock_data.get("f57"),
                "price": stock_data.get("f43"),
                "change": stock_data.get("f169"),
                "pct_change": stock_data.get("f170"),
                "volume": stock_data.get("f47"),
                "amount": stock_data.get("f48"),
                "open": stock_data.get("f46"),
                "high": stock_data.get("f44"),
                "low": stock_data.get("f45"),
                "prev_close": stock_data.get("f60"),
            }
        ]
    )
    df["timestamp"] = pd.Timestamp.now(tz="Asia/Shanghai")
    return df


def resample_historical_data(
    df: pd.DataFrame, interval: str, multiplier: int
) -> pd.DataFrame:
    """
    Resamples historical data to a specified frequency.
    """
    if df.empty or multiplier <= 1:
        return df

    df = df.set_index("timestamp")

    freq_map = {
        "day": f"{multiplier}D",
        "week": f"{multiplier}W-MON",
        "month": f"{multiplier}MS",
        "year": f"{multiplier * 12}MS",
    }
    freq = freq_map.get(interval)

    if not freq:
        return df.reset_index()

    resampled = (
        df.resample(freq)
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        .dropna()
    )

    return resampled.reset_index()
