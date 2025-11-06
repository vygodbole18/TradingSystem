from typing import List, Dict, Optional

Candle = Dict[str, float]
Level  = Dict[str, float]
Zone   = Dict[str, float]

def _first_wick_breach_up(candles: List[Candle], start_idx: int, level_price: float) -> Optional[int]:
    n = len(candles)
    for j in range(start_idx + 1, n):
        if float(candles[j]["high"]) > level_price:
            return j
    return None

def _first_wick_breach_down(candles: List[Candle], start_idx: int, level_price: float) -> Optional[int]:
    n = len(candles)
    for j in range(start_idx + 1, n):
        if float(candles[j]["low"]) < level_price:
            return j
    return None

def _origin_low_between(candles: List[Candle], i1: int, b1: int) -> Optional[float]:
    if b1 - i1 <= 1:
        return None
    lows = [float(candles[k]["low"]) for k in range(i1 + 1, b1)]
    return min(lows) if lows else None

def _origin_high_between(candles: List[Candle], i1: int, b1: int) -> Optional[float]:
    if b1 - i1 <= 1:
        return None
    highs = [float(candles[k]["high"]) for k in range(i1 + 1, b1)]
    return max(highs) if highs else None

def _first_level_after(levels: List[Level], after_idx: int) -> Optional[Level]:
    cands = [L for L in levels if int(L["index"]) > after_idx]
    if not cands:
        return None
    cands.sort(key=lambda L: int(L["index"]))
    return cands[0]

def _first_zone_after(zones: List[Zone], after_idx: int) -> Optional[Zone]:
    cands = [Z for Z in zones if int(Z["base_start"]) >= after_idx]
    if not cands:
        return None
    cands.sort(key=lambda Z: int(Z["base_start"]))
    return cands[0]

def detect_momentum_continuation_zones(
    candles: List[Candle],
    resistances: List[Level],
    supports: List[Level],
    dbr_zones: List[Zone],
    rbd_zones: List[Zone],
) -> Dict[str, List[Dict]]:
    out_demand: List[Dict] = []
    out_supply: List[Dict] = []

    res_sorted = sorted(resistances, key=lambda L: int(L["index"]))
    sup_sorted = sorted(supports,    key=lambda L: int(L["index"]))

    for R1 in res_sorted:
        i1 = int(R1["index"]); p1 = float(R1["price"])
        b1 = _first_wick_breach_up(candles, start_idx=i1, level_price=p1)
        if b1 is None:
            continue
        origin_low = _origin_low_between(candles, i1, b1)
        if origin_low is None:
            continue
        R2 = _first_level_after(res_sorted, after_idx=b1)
        if R2 is None:
            continue
        i2 = int(R2["index"]); p2 = float(R2["price"])
        first_breach_r2 = _first_wick_breach_up(candles, start_idx=i2, level_price=p2)
        if first_breach_r2 is None:
            continue
        Z = _first_zone_after(dbr_zones, after_idx=i2)
        if Z is None:
            continue
        zl = float(Z["zone_low"]); zh = float(Z["zone_high"])
        base_end = int(Z["base_end"])
        if base_end > first_breach_r2:
            continue
        if not (zl > origin_low):
            continue
        out_demand.append({
            "zone_type": "MCDZ",
            "dbr_date": Z.get("zone_date"),
            "r1_price": p1, "r1_date": R1.get("date"),
            "r2_price": p2, "r2_date": R2.get("date"),
            "origin": origin_low,
            "breach_date": candles[first_breach_r2].get("date"),
            "zone_low": zl, "zone_high": zh,
        })

    for S1 in sup_sorted:
        i1 = int(S1["index"]); p1 = float(S1["price"])
        b1 = _first_wick_breach_down(candles, start_idx=i1, level_price=p1)
        if b1 is None:
            continue
        origin_high = _origin_high_between(candles, i1, b1)
        if origin_high is None:
            continue
        S2 = _first_level_after(sup_sorted, after_idx=b1)
        if S2 is None:
            continue
        i2 = int(S2["index"]); p2 = float(S2["price"])
        first_breach_s2 = _first_wick_breach_down(candles, start_idx=i2, level_price=p2)
        if first_breach_s2 is None:
            continue
        Z = _first_zone_after(rbd_zones, after_idx=i2)
        if Z is None:
            continue
        zl = float(Z["zone_low"]); zh = float(Z["zone_high"])
        base_end = int(Z["base_end"])
        if base_end > first_breach_s2:
            continue
        if not (zh < origin_high):
            continue
        out_supply.append({
            "zone_type": "MCSZ",
            "rbd_date": Z.get("zone_date"),
            "s1_price": p1, "s1_date": S1.get("date"),
            "s2_price": p2, "s2_date": S2.get("date"),
            "origin": origin_high,
            "breach_date": candles[first_breach_s2].get("date"),
            "zone_low": zl, "zone_high": zh,
        })

    return {"continuation_demand": out_demand, "continuation_supply": out_supply}
