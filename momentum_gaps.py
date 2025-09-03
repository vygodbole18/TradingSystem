from typing import List, Dict, Tuple

Candle = Dict[str, float]

def _body_low(c: Candle) -> float:
    return min(float(c["open"]), float(c["close"]))

def _body_high(c: Candle) -> float:
    return max(float(c["open"]), float(c["close"]))

def _zone_for_gap_up(prior: Candle, current: Candle) -> Tuple[float, float]:
    # Gap up: 'upper candle' = current, 'lower candle' = prior
    upper_level = _body_low(current)
    lower_level = _body_high(prior)
    lo, hi = (lower_level, upper_level) if lower_level <= upper_level else (upper_level, lower_level)
    return lo, hi

def _zone_for_gap_down(prior: Candle, current: Candle) -> Tuple[float, float]:
    # Gap down: 'upper candle' = prior, 'lower candle' = current
    upper_level = _body_low(prior)
    lower_level = _body_high(current)
    lo, hi = (lower_level, upper_level) if lower_level <= upper_level else (upper_level, lower_level)
    return lo, hi

def _inside_zone(price: float, lo: float, hi: float) -> bool:
    return lo <= price <= hi  # inclusive

def _no_obstruction_between(candles: List[Candle], start_idx: int, end_idx: int, level_price: float) -> bool:
    """
    Ensure no candle in [start_idx .. end_idx] straddles the level (strict):
      NOT (low < level < high) for any bar in the range.
    If start_idx > end_idx (empty range), return True.
    """
    if start_idx > end_idx:
        return True
    for t in range(start_idx, end_idx + 1):
        lo = float(candles[t]["low"])
        hi = float(candles[t]["high"])
        if lo < level_price < hi:  # strict crossing; touches are allowed
            return False
    return True

def detect_momentum_gaps(
    candles: List[Candle],
    gaps: List[Dict],
    resistances: List[Dict],
    supports: List[Dict],
) -> Dict[str, List[Dict]]:
    """
    Identify momentum gaps with prior-only levels and no-obstruction rule.
    """
    m_up: List[Dict] = []
    m_dn: List[Dict] = []

    # Prepack levels as (price, index) for speed
    res_levels = [(float(r["price"]), int(r["index"])) for r in resistances]
    sup_levels = [(float(s["price"]), int(s["index"])) for s in supports]

    n = len(candles)
    for g in gaps:
        i = int(g["index"])  # current (right) bar of the gap
        if i <= 0 or i >= n:
            continue
        prior_idx = i - 1
        prior = candles[prior_idx]
        current = candles[i]

        if g["type"] == "gap_up":
            zl, zh = _zone_for_gap_up(prior, current)
            # Consider PRIOR resistances only; check nearest first
            res_prior = [(p, idx) for (p, idx) in res_levels if idx < i]
            res_prior.sort(key=lambda t: t[1], reverse=True)
            for price, lvl_idx in res_prior:
                if _inside_zone(price, zl, zh):
                    # No obstruction between resistance bar (lvl_idx) and prior candle (prior_idx)
                    if _no_obstruction_between(candles, lvl_idx + 1, prior_idx - 1, price):
                        m_up.append({
                            "index": i,
                            "current_date": current.get("date"),
                            "prior_date": prior.get("date"),
                            "level_date": candles[lvl_idx].get("date"),
                            "zone_low": zl,
                            "zone_high": zh,
                            "level_type": "resistance",
                            "level_price": price,
                            "level_index": lvl_idx,
                        })
                        break  # one valid prior resistance is enough

        elif g["type"] == "gap_down":
            zl, zh = _zone_for_gap_down(prior, current)
            # Consider PRIOR supports only; check nearest first
            sup_prior = [(p, idx) for (p, idx) in sup_levels if idx < i]
            sup_prior.sort(key=lambda t: t[1], reverse=True)
            for price, lvl_idx in sup_prior:
                if _inside_zone(price, zl, zh):
                    # No obstruction between support bar (lvl_idx) and prior candle (prior_idx)
                    if _no_obstruction_between(candles, lvl_idx + 1, prior_idx - 1, price):
                        m_dn.append({
                            "index": i,
                            "current_date": current.get("date"),
                            "prior_date": prior.get("date"),
                            "level_date": candles[lvl_idx].get("date"),
                            "zone_low": zl,
                            "zone_high": zh,
                            "level_type": "support",
                            "level_price": price,
                            "level_index": lvl_idx,
                        })
                        break

    return {"momentum_gap_ups": m_up, "momentum_gap_downs": m_dn}
