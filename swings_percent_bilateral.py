# PSH base:  OPEN if RED, else CLOSE (GREEN or BASING)
# PSL base:  OPEN if GREEN, else CLOSE (RED or BASING)
# Confirmation is bilateral and accepts either a close hit or a wick touch.


from typing import List, Dict, Optional

GREEN = "green"
RED = "red"
BASING = "basing"

def classify(c: Dict[str, float]) -> str:
    range_of_candle = c["high"] - c["low"]
    body = abs(c["close"] - c["open"])
    if range_of_candle == 0 or (body / range_of_candle) < 0.5:
        return BASING
    return GREEN if c["close"] > c["open"] else RED

Candle = Dict[str, float] 

def _fmt_date(val):
    try:
        return val.strftime("%Y-%m-%d")
    except Exception:
        return str(val)



def _psh_base(c: Candle) -> float:
    """For PSH: base = OPEN if RED, else CLOSE (GREEN or BASING)."""
    color = classify(c)
    return c["open"] if color == RED else c["close"]

def _left_confirm_drop_any_hit_psh(candles: List[Candle], i: int, pct: float) -> Optional[int]:
    """
    LEFT side for PSH @ i:
      target = base * (1 - pct), where base = OPEN if RED else CLOSE.
      Return nearest k < i where (close[k] <= target) OR (low[k] <= target).
    """
    base = _psh_base(candles[i])
    target = base * (1.0 - pct)
    for k in range(i - 1, -1, -1):  # nearest first
        ck = candles[k]
        if ck["close"] <= target or ck["low"] <= target:
            return k
    return None

def _right_confirm_drop_any_hit_psh(candles: List[Candle], i: int, pct: float) -> Optional[int]:
    """
    RIGHT side for PSH @ i:
      target = base * (1 - pct)
      If we hit target first, return that index.
    """
    Hi = candles[i]["high"]
    base = _psh_base(candles[i])
    target = base * (1.0 - pct)
    for k in range(i + 1, len(candles)):
        ck = candles[k]
        if ck["high"] > Hi:
            return None  # invalidated to the right
        if ck["close"] <= target or ck["low"] <= target:
            return k      # confirmed on the right
    return None

def _left_no_higher_high_between(candles: List[Candle], i: int, k: int) -> bool:
    """Ensure no bar in [k..i] has high > high[i]."""
    Hi = candles[i]["high"]
    for t in range(k, i + 1):
        if candles[t]["high"] > Hi:
            return False
    return True

def is_bilateral_swing_high(candles: List[Candle], i: int, pct: float = 0.07) -> Optional[Dict]:
    """
    Bilateral swing high at index i if BOTH:
      LEFT:  exists nearest k<i with (close<=target OR low<=target) AND no high>Hi in [k..i]
      RIGHT: before any higher-high, exists k>i with (close<=target OR low<=target)
    """
    # Left side
    k_left = _left_confirm_drop_any_hit_psh(candles, i, pct)
    if k_left is None:
        return None
    if not _left_no_higher_high_between(candles, i, k_left):
        return None

    # Right side
    k_right = _right_confirm_drop_any_hit_psh(candles, i, pct)
    if k_right is None:
        return None

    return {
        "index": i,
        "date": candles[i].get("date"),
        "high": candles[i]["high"],
        "close": candles[i]["close"],
        "left_confirm_idx": k_left,
        "right_confirm_idx": k_right,
    }


def _psl_base(c: Candle) -> float:
    """For PSL: base = OPEN if GREEN, else CLOSE (RED or BASING)."""
    color = classify(c)
    return c["open"] if color == GREEN else c["close"]

def _left_confirm_rise_any_hit_psl(candles: List[Candle], i: int, pct: float) -> Optional[int]:
    """
    LEFT side for PSL @ i:
      target = base * (1 + pct), where base = OPEN if GREEN else CLOSE.
      Return nearest k < i where (close[k] >= target) OR (high[k] >= target).
    """
    base = _psl_base(candles[i])
    target = base * (1.0 + pct)
    for k in range(i - 1, -1, -1):
        ck = candles[k]
        if ck["close"] >= target or ck["high"] >= target:
            return k
    return None

def _right_confirm_rise_any_hit_psl(candles: List[Candle], i: int, pct: float) -> Optional[int]:
    """
    RIGHT side for PSL @ i:
      target = base * (1 + pct)
      Scan forward; if any low < low[i] BEFORE we hit (close>=target or high>=target), invalidate (None).
      If we hit target first, return that index.
    """
    Li = candles[i]["low"]
    base = _psl_base(candles[i])
    target = base * (1.0 + pct)
    for k in range(i + 1, len(candles)):
        ck = candles[k]
        if ck["low"] < Li:
            return None  # invalidated to the right
        if ck["close"] >= target or ck["high"] >= target:
            return k      # confirmed on the right
    return None

def _left_no_lower_low_between(candles: List[Candle], i: int, k: int) -> bool:
    """Ensure no bar in [k..i] has low < low[i]."""
    Li = candles[i]["low"]
    for t in range(k, i + 1):
        if candles[t]["low"] < Li:
            return False
    return True

def is_bilateral_swing_low(candles: List[Candle], i: int, pct: float = 0.07) -> Optional[Dict]:
    """
    Bilateral swing low at index i if BOTH:
      LEFT:  exists nearest k<i with (close>=target OR high>=target) AND no low<Li in [k..i]
      RIGHT: before any lower-low, exists k>i with (close>=target OR high>=target)
    """
    # Left side
    k_left = _left_confirm_rise_any_hit_psl(candles, i, pct)
    if k_left is None:
        return None
    if not _left_no_lower_low_between(candles, i, k_left):
        return None

    # Right side
    k_right = _right_confirm_rise_any_hit_psl(candles, i, pct)
    if k_right is None:
        return None

    return {
        "index": i,
        "date": candles[i].get("date"),
        "low": candles[i]["low"],
        "close": candles[i]["close"],
        "left_confirm_idx": k_left,
        "right_confirm_idx": k_right,
    }


def latest_bilateral_swings(candles: List[Candle], pct: float = 0.07) -> Dict[str, Optional[Dict]]:
    
    n = len(candles)
    sh = None
    for i in range(n - 2, 0, -1):  # avoid endpoints
        got = is_bilateral_swing_high(candles, i, pct)
        if got:
            sh = got
            break

    sl = None
    for i in range(n - 2, 0, -1):
        got = is_bilateral_swing_low(candles, i, pct)
        if got:
            sl = got
            break

    return {"swing_high": sh, "swing_low": sl}
