import os
from datetime import datetime, timedelta
from kiteconnect import KiteConnect
from auth import get_kite

# Initialize KiteConnect client once using your auth.py helper
kite = get_kite()


def get_instrument_token(symbol, exchange="NSE"):
    """
    Fetch the instrument_token for a given symbol via kite.ltp(),
    avoiding the rate-limited instruments() endpoint.

    Args:
        symbol (str): Trading symbol, e.g. "RELIANCE"
        exchange (str): Exchange code, e.g. "NSE"

    Returns:
        int: instrument_token

    Raises:
        ValueError: if token not found in LTP response
    """
    key = f"{exchange}:{symbol}"
    # Call LTP endpoint, returns dict with last_price and instrument_token
    resp = kite.ltp(key)
    info = resp.get(key)
    if not info or "instrument_token" not in info:
        raise ValueError(f"Could not get instrument_token for {symbol} via LTP")
    return info["instrument_token"]


def fetch_ohlc_data(symbol, interval="day", days_back=300):
    """
    Fetch historical OHLC data for a symbol.

    Args:
        symbol (str): Trading symbol
        interval (str): "day", "week", "60minute", etc.
        days_back (int): Number of days (or weeks if interval="week") back to fetch

    Returns:
        List[dict]: Each dict has keys date (datetime), open, high, low, close (floats)
    """
    # Lookup token via LTP (no instruments() call)
    token = get_instrument_token(symbol)

    # Calculate time range
    to_dt = datetime.now()
    from_dt = to_dt - timedelta(days=days_back)
    fmt = "%Y-%m-%d %H:%M:%S"
    from_str = from_dt.strftime(fmt)
    to_str = to_dt.strftime(fmt)

    # Fetch bars using correct method name
    bars = kite.historical_data(
        instrument_token=token,
        from_date=from_str,
        to_date=to_str,
        interval=interval
    )

    # Normalize output
    data = []
    for b in bars:
        # handle date which may be str or datetime
        date_val = b.get("date")
        if isinstance(date_val, str):
            dt = datetime.fromisoformat(date_val)
        else:
            dt = date_val

        data.append({
            "date": dt,
            "open": float(b.get("open", 0)),
            "high": float(b.get("high", 0)),
            "low": float(b.get("low", 0)),
            "close": float(b.get("close", 0))
        })
    return data

def fetch_ltp(symbol: str, exchange: str = "NSE"):
    key = f"{exchange}:{symbol}"
    try:
        data = kite.ltp(key)
        return float(data[key]["last_price"])
    except Exception as e:
        print(f"Error fetching LTP for {symbol}: {e}")
        return None
