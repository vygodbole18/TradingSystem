
from typing import List, Dict, Tuple

Candle = Dict[str, float] 

def _fmt_date(d):
    try:
        return d.strftime("%Y-%m-%d")
    except Exception:
        return str(d)

def _window_bounds(prior_idx: int, N: int) -> Tuple[int, int]:
    # Window is the N bars BEFORE the prior candle (i-1).
    # We'll search for gaps inside [start_k .. prior_idx], but min/max closes use [start .. prior_idx-1].
    start = max(1, prior_idx - N)  
    return start, prior_idx

def _has_rapid_upmove(candles: List[Candle], prior_idx: int, N: int, pct: float) -> bool:
    start, end = _window_bounds(prior_idx, N)
    if start > prior_idx - 1:
        return False
    closes = [float(candles[j]["close"]) for j in range(start, prior_idx)]
    if not closes:
        return False
    cmin = min(closes)
    c_prior = float(candles[prior_idx]["close"])
    if cmin <= 0:
        return False
    return (c_prior - cmin) / cmin >= pct

def _has_rapid_downmove(candles: List[Candle], prior_idx: int, N: int, pct: float) -> bool:
    start, end = _window_bounds(prior_idx, N)
    if start > prior_idx - 1:
        return False
    closes = [float(candles[j]["close"]) for j in range(start, prior_idx)]
    if not closes:
        return False
    cmax = max(closes)
    c_prior = float(candles[prior_idx]["close"])
    if cmax <= 0:
        return False
    return (cmax - c_prior) / cmax >= pct

def _has_simple_gap_up_in_window(candles: List[Candle], start_k: int, end_k: int) -> bool:
    # Check low[k] > close[k-1] for any k in [start_k .. end_k]
    for k in range(start_k, end_k + 1):
        if float(candles[k]["low"]) > float(candles[k-1]["close"]):
            return True
    return False

def _has_simple_gap_down_in_window(candles: List[Candle], start_k: int, end_k: int) -> bool:
    # Check high[k] < close[k-1] for any k in [start_k .. end_k]
    for k in range(start_k, end_k + 1):
        if float(candles[k]["high"]) < float(candles[k-1]["close"]):
            return True
    return False

def detect_novice_gaps(
    candles: List[Candle],
    N: int = 3,
    pct: float = 0.02,   # 2%
) -> Dict[str, List[Dict]]:
    """
    Scan series and return novice gap downs/ups.

    Output:
      {
        "novice_gap_downs": [
          { "index", "prior_date", "current_date",
            "prev_close", "curr_open", "curr_close", "prior_low" }
        ],
        "novice_gap_ups": [
          { "index", "prior_date", "current_date",
            "prev_close", "curr_open", "curr_close", "prior_high" }
        ]
      }
    """
    downs, ups = [], []
    n = len(candles)
    if n < 2:
        return {"novice_gap_downs": downs, "novice_gap_ups": ups}

    for i in range(1, n):
        prior = candles[i-1]
        curr  = candles[i]

        prev_close = float(prior["close"])
        prior_low  = float(prior["low"])
        prior_high = float(prior["high"])
        open_i     = float(curr["open"])
        close_i    = float(curr["close"])

        # ----- Novice Gap DOWN (exhaustion after rapid upmove) -----
        # Strict open gap UP at i, then bearish engulfing close through prior low:
        # open[i] > close[i-1]  AND  close[i] < low[i-1]
        if open_i > prev_close and close_i < prior_low:
            start_k, end_k = _window_bounds(i-1, N)
            if _has_rapid_upmove(candles, i-1, N, pct) and _has_simple_gap_up_in_window(candles, start_k, end_k):
                downs.append({
                    "index": i,
                    "prior_date": prior.get("date"),
                    "current_date": curr.get("date"),
                    "type": "novice_gap_down",
                    "prev_close": prev_close,
                    "curr_open": open_i,
                    "curr_close": close_i,
                    "prior_low": prior_low,
                })

        # ----- Novice Gap UP (exhaustion after rapid downmove) -----
        # Strict open gap DOWN at i, then bullish engulfing close through prior high:
        # open[i] < close[i-1]  AND  close[i] > high[i-1]
        if open_i < prev_close and close_i > prior_high:
            start_k, end_k = _window_bounds(i-1, N)
            if _has_rapid_downmove(candles, i-1, N, pct) and _has_simple_gap_down_in_window(candles, start_k, end_k):
                ups.append({
                    "index": i,
                    "prior_date": prior.get("date"),
                    "current_date": curr.get("date"),
                    "type": "novice_gap_up",
                    "prev_close": prev_close,
                    "curr_open": open_i,
                    "curr_close": close_i,
                    "prior_high": prior_high,
                })

    return {"novice_gap_downs": downs, "novice_gap_ups": ups}
