
from typing import List, Dict, Optional

Candle = Dict[str, float]  

GREEN = "green"
RED = "red"
BASING = "basing"

def classify(c: Candle) -> str:
    """Simple color classifier consistent with your earlier logic."""
    rng = float(c["high"]) - float(c["low"])
    body = abs(float(c["close"]) - float(c["open"]))
    if rng == 0 or (rng > 0 and body / rng < 0.5):
        return BASING
    return GREEN if float(c["close"]) > float(c["open"]) else RED

def _fmt_date(d):
    try:
        return d.strftime("%Y-%m-%d")
    except Exception:
        return str(d)

def _has_downmove(candles: List[Candle], prior_idx: int, min_bars: int, min_pct: float) -> bool:
    """
    Downmove into the gap:
      Look back at least `min_bars` candles before the PRIOR bar.
      Let Cmax = max(close[j]) over j in [prior_idx - min_bars, prior_idx - 1]
      Condition: (Cmax - close_prior) / Cmax >= min_pct
    """
    start = prior_idx - min_bars
    end = prior_idx - 1
    if start < 0 or end < 0 or start > end:
        return False
    closes = [float(candles[j]["close"]) for j in range(start, end + 1)]
    if not closes:
        return False
    cmax = max(closes)
    c_prior = float(candles[prior_idx]["close"])
    if cmax <= 0:
        return False
    return (cmax - c_prior) / cmax >= min_pct

def _has_upmove(candles: List[Candle], prior_idx: int, min_bars: int, min_pct: float) -> bool:
    """
    Upmove into the gap:
      Look back at least `min_bars` candles before the PRIOR bar.
      Let Cmin = min(close[j]) over j in [prior_idx - min_bars, prior_idx - 1]
      Condition: (close_prior - Cmin) / Cmin >= min_pct
    """
    start = prior_idx - min_bars
    end = prior_idx - 1
    if start < 0 or end < 0 or start > end:
        return False
    closes = [float(candles[j]["close"]) for j in range(start, end + 1)]
    if not closes:
        return False
    cmin = min(closes)
    c_prior = float(candles[prior_idx]["close"])
    if cmin <= 0:
        return False
    return (c_prior - cmin) / cmin >= min_pct

def detect_pro_gaps(
    candles: List[Candle],
    min_bars: int = 3,
    min_pct: float = 0.02,  
) -> Dict[str, List[Dict]]:
    """
    Detect Pro Gap Ups and Pro Gap Downs across the series.
    Returns:
      {
        "pro_gap_ups":   [ { index, prior_date, current_date, prev_close, curr_low,  zone_low, zone_high } ... ],
        "pro_gap_downs": [ { index, prior_date, current_date, prev_close, curr_high, zone_low, zone_high } ... ],
      }
    """
    n = len(candles)
    ups, downs = [], []

    for i in range(1, n):  # compare prior (i-1) and current (i)
        prior = candles[i - 1]
        curr = candles[i]

        color_prior = classify(prior)
        color_curr = classify(curr)

        prev_close = float(prior["close"])
        curr_low = float(curr["low"])
        curr_high = float(curr["high"])

        # -------- Pro Gap Up: prior RED, current GREEN, strict low>prev_close, downmove context --------
        if color_prior == RED and color_curr == GREEN and curr_low > prev_close:
            if _has_downmove(candles, prior_idx=i - 1, min_bars=min_bars, min_pct=min_pct):
                ups.append({
                    "index": i,
                    "prior_date": prior.get("date"),
                    "current_date": curr.get("date"),
                    "type": "pro_gap_up",
                    "prev_close": prev_close,
                    "curr_low": curr_low,
                    # Zone: from low of red (prior) to open of green (current)
                    "zone_low": float(prior["low"]),
                    "zone_high": float(curr["open"]),
                })

        # -------- Pro Gap Down: prior GREEN, current RED, strict high<prev_close, upmove context --------
        if color_prior == GREEN and color_curr == RED and curr_high < prev_close:
            if _has_upmove(candles, prior_idx=i - 1, min_bars=min_bars, min_pct=min_pct):
                downs.append({
                    "index": i,
                    "prior_date": prior.get("date"),
                    "current_date": curr.get("date"),
                    "type": "pro_gap_down",
                    "prev_close": prev_close,
                    "curr_high": curr_high,
                    # Zone: from open of red (current) to high of green (prior)
                    "zone_low": float(curr["open"]),
                    "zone_high": float(prior["high"]),
                })

    return {"pro_gap_ups": ups, "pro_gap_downs": downs}
