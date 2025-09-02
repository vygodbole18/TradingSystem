from fetch import fetch_ohlc_data
from datetime import datetime

GREEN = "green"
RED = 'red'
BASING = 'basing'

def classify(c):
    range_of_candle = c["high"] - c["low"]
    body = abs(c["close"] - c["open"])

    if range_of_candle == 0 or (body/range_of_candle) < 0.5:
        return BASING
    return GREEN if c["close"] > c["open"] else RED 


def find_demand_zones(candles, lookback=100):
    n = len(candles)
    if n == 0:
        return []

    zones = []
    # Start probe line at the latest candle's low
    line = candles[-1]["low"]

    start = n - 1
    stop  = max(n - 1 - lookback, 0)

    i = start
    while i >= stop:
        c = candles[i]

        if c["low"] > line:
            i -= 1
            continue

        # We touched/breached the line
        if classify(c) != GREEN:
            line = c["low"]
            i -= 1
            continue

        # Collect consecutive basing candles just before this leg-out
        base = []
        j = i - 1
        while j >= 0 and classify(candles[j]) == BASING:
            base.append(candles[j])
            j -= 1

        if not base:
            
            line = c["low"]
            i -= 1
            continue
        
        base_highs = [b["high"] for b in base]
        if not (c["high"] > max(base_highs)):
            line = c["low"]
            i = i - 1
            continue

        # Determine leg-in 
        leg_in = candles[j] if j >= 0 else None
        zone_type = None
        if leg_in:
            kin = classify(leg_in)
            if kin == RED:
                zone_type = "DBR"
            elif kin == GREEN:
                zone_type = "RBR"
            else:
                zone_type = "UNCLASSIFIED"
        else:
            zone_type = "UNCLASSIFIED"

      
        highs_base = [b["high"] for b in base]
        lows_base  = [b["low"]  for b in base]
        base_high  = max(highs_base)
        base_low   = min(lows_base)

        if zone_type == "DBR":
            zone_top = base_high
            candidates = [base_low, c["low"]]
            if leg_in:
                candidates.append(leg_in["low"])
            zone_bottom = min(candidates)
        elif zone_type == "RBR":
            zone_top = base_high
            zone_bottom = base_low
        else:
            
            zone_top = base_high
            zone_bottom = base_low

        
        zones.append({
            "type": zone_type,
            "top": zone_top,
            "bottom": zone_bottom,
            "created_at": c.get("date"),
            "leg_out_idx": i,
            "leg_in_idx": j if j >= 0 else None,
            "base_start_idx": j + 1,   # left-most basing candle
            "base_end_idx": i - 1,     # right-most basing candle
            "base_count": len(base),
            "base_high": base_high,
            "base_low": base_low,
        })

        # Move the probe line to the bottom of the found zone and continue scanning left
        line = zone_bottom

        # Advance left from where we were (avoid re-detecting the same structure)
        i = j  # jump to the candle before the base; keeps scanning older bars

    return zones