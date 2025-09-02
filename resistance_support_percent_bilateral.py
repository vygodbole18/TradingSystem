# resistance_support_percent_bilateral.py
# Bilateral wick-based Resistance/Support detection (collect ALL levels).
# Supports DIFFERENT left/right thresholds:
#   - Resistance @ i (candidate = HIGH[i]):
#       LEFT:  nearest k<i with LOW[k] <= HIGH[i]*(1 - pct_left)
#              AND no bar in [k..i] has HIGH > HIGH[i]
#       RIGHT: before any HIGH > HIGH[i], exists k>i with LOW[k] <= HIGH[i]*(1 - pct_right)
#   - Support @ i (candidate = LOW[i]):
#       LEFT:  nearest k<i with HIGH[k] >= LOW[i]*(1 + pct_left)
#              AND no bar in [k..i] has LOW < LOW[i]
#       RIGHT: before any LOW < LOW[i], exists k>i with HIGH[k] >= LOW[i]*(1 + pct_right)

from typing import List, Dict, Optional

Candle = Dict[str, float]  # must include: 'open','high','low','close'; optional: 'date'

def _fmt_date(val):
    try:
        return val.strftime("%Y-%m-%d")
    except Exception:
        return str(val)

# -------------------- Resistance (from HIGH down to LOW) --------------------

def _left_confirm_drop_from_high(candles: List[Candle], i: int, pct_left: float) -> Optional[int]:
    """Nearest k<i with LOW[k] <= HIGH[i] * (1 - pct_left)."""
    Hi = candles[i]['high']
    target = Hi * (1.0 - pct_left)
    for k in range(i - 1, -1, -1):  # nearest first
        if candles[k]['low'] <= target:
            return k
    return None

def _left_no_higher_high_between(candles: List[Candle], i: int, k: int) -> bool:
    """No HIGH > HIGH[i] in [k..i]."""
    Hi = candles[i]['high']
    for t in range(k, i + 1):
        if candles[t]['high'] > Hi:
            return False
    return True

def _right_confirm_drop_from_high(candles: List[Candle], i: int, pct_right: float) -> Optional[int]:
    """
    Scan forward; if any HIGH > HIGH[i] before LOW<=target (with pct_right), invalidate.
    Else return first k>i where LOW<=target.
    """
    Hi = candles[i]['high']
    target = Hi * (1.0 - pct_right)
    for k in range(i + 1, len(candles)):
        if candles[k]['high'] > Hi:
            return None
        if candles[k]['low'] <= target:
            return k
    return None

def is_bilateral_resistance(
    candles: List[Candle],
    i: int,
    pct_left: float = 0.02,   # 2% on the left
    pct_right: float = 0.03,  # 3% on the right
) -> Optional[Dict]:
    """Return details if index i is a confirmed resistance; else None."""
    if i <= 0 or i >= len(candles) - 1:
        return None
    k_left = _left_confirm_drop_from_high(candles, i, pct_left)
    if k_left is None:
        return None
    if not _left_no_higher_high_between(candles, i, k_left):
        return None
    k_right = _right_confirm_drop_from_high(candles, i, pct_right)
    if k_right is None:
        return None
    return {
        "type": "resistance",
        "index": i,
        "date": candles[i].get("date"),
        "price": candles[i]["high"],
        "left_confirm_idx": k_left,
        "right_confirm_idx": k_right,
        "pct_left": pct_left,
        "pct_right": pct_right,
    }

def all_bilateral_resistances(
    candles: List[Candle],
    pct_left: float = 0.02,
    pct_right: float = 0.03,
) -> List[Dict]:
    """Collect ALL resistances across the series."""
    out = []
    n = len(candles)
    for i in range(1, n - 1):
        r = is_bilateral_resistance(candles, i, pct_left=pct_left, pct_right=pct_right)
        if r:
            out.append(r)
    return out

# -------------------- Support (from LOW up to HIGH) --------------------

def _left_confirm_rise_from_low(candles: List[Candle], i: int, pct_left: float) -> Optional[int]:
    """Nearest k<i with HIGH[k] >= LOW[i] * (1 + pct_left)."""
    Li = candles[i]['low']
    target = Li * (1.0 + pct_left)
    for k in range(i - 1, -1, -1):
        if candles[k]['high'] >= target:
            return k
    return None

def _left_no_lower_low_between(candles: List[Candle], i: int, k: int) -> bool:
    """No LOW < LOW[i] in [k..i]."""
    Li = candles[i]['low']
    for t in range(k, i + 1):
        if candles[t]['low'] < Li:
            return False
    return True

def _right_confirm_rise_from_low(candles: List[Candle], i: int, pct_right: float) -> Optional[int]:
    """
    Scan forward; if any LOW < LOW[i] before HIGH>=target (with pct_right), invalidate.
    Else return first k>i where HIGH>=target.
    """
    Li = candles[i]['low']
    target = Li * (1.0 + pct_right)
    for k in range(i + 1, len(candles)):
        if candles[k]['low'] < Li:
            return None
        if candles[k]['high'] >= target:
            return k
    return None

def is_bilateral_support(
    candles: List[Candle],
    i: int,
    pct_left: float = 0.02,
    pct_right: float = 0.03,
) -> Optional[Dict]:
    """Return details if index i is a confirmed support; else None."""
    if i <= 0 or i >= len(candles) - 1:
        return None
    k_left = _left_confirm_rise_from_low(candles, i, pct_left)
    if k_left is None:
        return None
    if not _left_no_lower_low_between(candles, i, k_left):
        return None
    k_right = _right_confirm_rise_from_low(candles, i, pct_right)
    if k_right is None:
        return None
    return {
        "type": "support",
        "index": i,
        "date": candles[i].get("date"),
        "price": candles[i]["low"],
        "left_confirm_idx": k_left,
        "right_confirm_idx": k_right,
        "pct_left": pct_left,
        "pct_right": pct_right,
    }

def all_bilateral_supports(
    candles: List[Candle],
    pct_left: float = 0.02,
    pct_right: float = 0.03,
) -> List[Dict]:
    """Collect ALL supports across the series."""
    out = []
    n = len(candles)
    for i in range(1, n - 1):
        s = is_bilateral_support(candles, i, pct_left=pct_left, pct_right=pct_right)
        if s:
            out.append(s)
    return out

# -------------------- Convenience: both at once --------------------

def all_bilateral_resistance_support(
    candles: List[Candle],
    pct_left: float = 0.02,
    pct_right: float = 0.03,
) -> Dict[str, List[Dict]]:
    """
    Return both lists:
      - 'resistances': all confirmed resistances (wick-based bilateral with split thresholds)
      - 'supports':    all confirmed supports (wick-based bilateral with split thresholds)
    """
    return {
        "resistances": all_bilateral_resistances(candles, pct_left=pct_left, pct_right=pct_right),
        "supports":    all_bilateral_supports(candles, pct_left=pct_left,  pct_right=pct_right),
    }
