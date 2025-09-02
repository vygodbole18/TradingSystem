# Gap Up   : low[i]  > close[i-1]
# Gap Down : high[i] < close[i-1]
#
# Output (per gap):
#   {
#     "index": i,                       # index in the candles list
#     "date": candles[i].get("date"),   # date of the current candle
#     "type": "gap_up" | "gap_down",
#     "prev_close": candles[i-1]["close"],
#     "current_low_or_high": candles[i]["low"]  (if gap_up)
#                           | candles[i]["high"] (if gap_down)
#   }

from typing import List, Dict

Candle = Dict[str, float]  

def _is_chronological(candles: List[Candle]) -> bool:

    dates = [c.get("date") for c in candles]
    return all(dates[i] <= dates[i+1] for i in range(len(dates)-1) if dates[i] is not None and dates[i+1] is not None)

def detect_simple_gaps(candles: List[Candle]) -> List[Dict]:

    n = len(candles)
    if n < 2:
        return []

    
    if not _is_chronological(candles):
        candles = list(sorted(candles, key=lambda c: c.get("date")))

    gaps = []
    for i in range(1, n):
        prev = candles[i-1]
        curr = candles[i]
        try:
            prev_close = float(prev["close"])
            low_i  = float(curr["low"])
            high_i = float(curr["high"])
        except (KeyError, TypeError, ValueError):
            continue  

        if low_i > prev_close:
            gaps.append({
                "index": i,
                "date": curr.get("date"),
                "type": "gap_up",
                "prev_close": prev_close,
                "current_low_or_high": low_i,
            })
        elif high_i < prev_close:
            gaps.append({
                "index": i,
                "date": curr.get("date"),
                "type": "gap_down",
                "prev_close": prev_close,
                "current_low_or_high": high_i,
            })

    return gaps
