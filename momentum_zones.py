# momentum_zones.py
# Wick-based Momentum Demand/Supply Zones with unobstructed seed levels

from typing import List, Dict, Optional

Candle = Dict[str, float]
Level  = Dict[str, float]
Zone   = Dict[str, float]

def _inside_zone(price: float, lo: float, hi: float) -> bool:
    return lo <= price <= hi  # inclusive

def _first_after(levels: List[Level], after_idx: int) -> Optional[Level]:
    cands = [L for L in levels if int(L["index"]) > after_idx]
    if not cands:
        return None
    cands.sort(key=lambda L: int(L["index"]))
    return cands[0]

def _first_breach_after(candles: List[Candle], start_idx: int, level_price: float, direction: str) -> Optional[int]:
    n = len(candles)
    j = start_idx + 1
    if j >= n:
        return None
    if direction == "up":
        for k in range(j, n):
            if float(candles[k]["high"]) > level_price:
                return k
    else:
        for k in range(j, n):
            if float(candles[k]["low"]) < level_price:
                return k
    return None

def _no_obstruction_between(candles: List[Candle], start_idx: int, end_idx: int, level_price: float) -> bool:
    if start_idx > end_idx:
        return True
    for k in range(start_idx, end_idx + 1):
        lo = float(candles[k]["low"])
        hi = float(candles[k]["high"])
        if lo < level_price < hi:  # strict crossing; touches allowed
            return False
    return True

def _nearest_prior_seed_unobstructed(
    candles: List[Candle],
    levels: List[Level],
    before_idx: int,
    zone_low: float,
    zone_high: float,
    end_exclusive_idx: int,
) -> Optional[Level]:
    cands = [L for L in levels if int(L["index"]) < end_exclusive_idx and _inside_zone(float(L["price"]), zone_low, zone_high)]
    if not cands:
        return None
    cands.sort(key=lambda L: int(L["index"]), reverse=True)  # nearest prior first
    for L in cands:
        idx = int(L["index"]); px = float(L["price"])
        if _no_obstruction_between(candles, idx + 1, end_exclusive_idx - 1, px):
            return L
    return None

def detect_momentum_zones(
    candles: List[Candle],
    resistances: List[Level],
    supports: List[Level],
    rbr_zones: List[Zone],
    dbd_zones: List[Zone],
) -> Dict[str, List[Dict]]:
    momentum_demand: List[Dict] = []
    momentum_supply: List[Dict] = []

    res_sorted = sorted(resistances, key=lambda L: int(L["index"]))
    sup_sorted = sorted(supports,    key=lambda L: int(L["index"]))

    # Momentum Demand (RBR + resistances)
    for Z in rbr_zones:
        zl = float(Z["zone_low"]); zh = float(Z["zone_high"])
        b0 = int(Z["base_start"]); b1 = int(Z["base_end"])
        leg_in = int(Z.get("leg_in", b0))

        seed = _nearest_prior_seed_unobstructed(candles, res_sorted, before_idx=b0, zone_low=zl, zone_high=zh, end_exclusive_idx=leg_in)
        if seed is None:
            continue
        confirm = _first_after(res_sorted, after_idx=b1)
        if confirm is None:
            continue
        breach_idx = _first_breach_after(candles, start_idx=int(confirm["index"]), level_price=float(confirm["price"]), direction="up")
        if breach_idx is None:
            continue
        momentum_demand.append({
            "zone_type": "MDZ",
            "zone_low": zl, "zone_high": zh,
            "base_start": b0, "base_end": b1,
            "base_start_date": Z.get("start_date"), "base_end_date": Z.get("end_date"),
            "seed_type": "resistance",
            "seed_price": float(seed["price"]), "seed_index": int(seed["index"]), "seed_date": seed.get("date"),
            "confirm_price": float(confirm["price"]), "confirm_index": int(confirm["index"]), "confirm_date": confirm.get("date"),
            "breach_index": breach_idx, "breach_date": candles[breach_idx].get("date"),
        })

    # Momentum Supply (DBD + supports)
    for Z in dbd_zones:
        zl = float(Z["zone_low"]); zh = float(Z["zone_high"])
        b0 = int(Z["base_start"]); b1 = int(Z["base_end"])
        leg_in = int(Z.get("leg_in", b0))

        seed = _nearest_prior_seed_unobstructed(candles, sup_sorted, before_idx=b0, zone_low=zl, zone_high=zh,end_exclusive_idx=leg_in)
        if seed is None:
            continue
        confirm = _first_after(sup_sorted, after_idx=b1)
        if confirm is None:
            continue
        breach_idx = _first_breach_after(candles, start_idx=int(confirm["index"]), level_price=float(confirm["price"]), direction="down")
        if breach_idx is None:
            continue
        momentum_supply.append({
            "zone_type": "MSZ",
            "zone_low": zl, "zone_high": zh,
            "base_start": b0, "base_end": b1,
            "base_start_date": Z.get("start_date"), "base_end_date": Z.get("end_date"),
            "seed_type": "support",
            "seed_price": float(seed["price"]), "seed_index": int(seed["index"]), "seed_date": seed.get("date"),
            "confirm_price": float(confirm["price"]), "confirm_index": int(confirm["index"]), "confirm_date": confirm.get("date"),
            "breach_index": breach_idx, "breach_date": candles[breach_idx].get("date"),
        })

    return {"momentum_demand": momentum_demand, "momentum_supply": momentum_supply}
