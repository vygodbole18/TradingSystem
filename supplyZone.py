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

def find_supply_zones(candles, lookback=100):
    n = len(candles)
    if n == 0:
        return []

    zones = []
    line = candles[-1]["high"]   # start probe line at latest high

    start = n - 1
    stop = max(n - 1 - lookback, 0)

    i = start
    while i >= stop:
        c = candles[i]

        # If candle high < line, keep scanning left
        if c["high"] < line:
            i -= 1
            continue

        # We touched/breached the line
        if classify(c) != RED:
            # Not decisive red: move probe line to this high
            line = c["high"]
            i -= 1
            continue

        # Collect basing candles before this leg-out
        base = []
        j = i - 1
        while j >= 0 and classify(candles[j]) == BASING:
            base.append(candles[j])
            j -= 1

        if not base:
            line = c["high"]
            i -= 1
            continue

        base_lows = [b["low"] for b in base]
        if not (c["low"] < min(base_lows)):
            line = c["high"]
            i = i - 1
            continue

        # Leg-in candle (before base cluster)
        leg_in = candles[j] if j >= 0 else None
        zone_type = None
        if leg_in:
            kin = classify(leg_in)
            if kin == GREEN:
                zone_type = "RBD" 
            elif kin == RED:
                zone_type = "DBD"  
            else:
                zone_type = "UNCLASSIFIED"
        else:
            zone_type = "UNCLASSIFIED"

        body_highs = [b["high"] for b in base]
        body_lows  = [b["low"] for b in base]
        base_body_high = max(body_highs)
        base_body_low  = min(body_lows)

        if zone_type == "RBD":
          
            proximal = base_body_low
           
            highs = [c["high"]] + [b["high"] for b in base]
            if leg_in:
                highs.append(leg_in["high"])
            distal = max(highs)

        elif zone_type == "DBD":
            
            proximal = base_body_low
           
            highs = [c["high"]] + [b["high"] for b in base]
            distal = max(highs)

        else:
            
            proximal = base_body_low
            distal = max([c["high"]] + [b["high"] for b in base])

        zones.append({
            "type": zone_type,
            "proximal": proximal,
            "distal": distal,
            "created_at": c.get("date"),
            "leg_out_idx": i,
            "leg_in_idx": j if j >= 0 else None,
            "base_start_idx": j + 1,
            "base_end_idx": i - 1,
            "base_count": len(base),
        })

        
        line = distal
        i = j

    return zones