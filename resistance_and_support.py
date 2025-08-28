
def detect_swings(candles, left=2, right=2):
    """Pivot swings using wick highs/lows."""
    sh, sl = [], []
    for i in range(left, len(candles)-right):
        hi = candles[i]['high']; lo = candles[i]['low']
        if all(hi > candles[j]['high'] for j in range(i-left, i)) and \
           all(hi > candles[j]['high'] for j in range(i+1, i+1+right)):
            sh.append(i)
        if all(lo < candles[j]['low']  for j in range(i-left, i)) and \
           all(lo < candles[j]['low']  for j in range(i+1, i+1+right)):
            sl.append(i)
    return sh, sl

def detect_trend(candles, left=2, right=2):
    """Uptrend if HH+HL, Downtrend if LH+LL, else Sideways."""
    sh, sl = detect_swings(candles, left, right)
    if len(sh) < 2 or len(sl) < 2:
        return "Sideways", sh, sl
    h1, h2 = sh[-2], sh[-1]
    l1, l2 = sl[-2], sl[-1]
    hh = candles[h2]['high'] > candles[h1]['high']
    hl = candles[l2]['low']  > candles[l1]['low']
    lh = candles[h2]['high'] < candles[h1]['high']
    ll = candles[l2]['low']  < candles[l1]['low']
    if hh and hl: return "Uptrend", sh, sl
    if lh and ll: return "Downtrend", sh, sl
    return "Sideways", sh, sl

def detect_resistances(candles, threshold_pct=0.03, dedup_pct=0.004):
    """Resistance: a candle's HIGH where price drops >= threshold BEFORE any higher-high."""
    out = []
    n = len(candles); i = 0
    while i < n:
        H = candles[i]['high']
        j = i + 1; confirmed = None
        while j < n:
            if candles[j]['high'] > H:      # invalidated
                confirmed = None; break
            drop = (H - candles[j]['low']) / H
            if drop >= threshold_pct:
                confirmed = {'price': H, 'index': i, 'date': candles[i].get('date'),
                             'drop_pct': round(drop*100, 2)}
                break
            j += 1
        if confirmed:
            if not out or abs(confirmed['price']-out[-1]['price'])/confirmed['price'] > dedup_pct:
                out.append(confirmed)
            else:
                if confirmed['drop_pct'] > out[-1]['drop_pct']:
                    out[-1] = confirmed
            i = j
        else:
            i += 1
    return out

def detect_supports(candles, threshold_pct=0.03, dedup_pct=0.004):
    """Support: a candle's LOW where price rises >= threshold BEFORE any lower-low."""
    out = []
    n = len(candles); i = 0
    while i < n:
        L = candles[i]['low']
        j = i + 1; confirmed = None
        while j < n:
            if candles[j]['low'] < L:       # invalidated
                confirmed = None; break
            rise = (candles[j]['high'] - L) / L
            if rise >= threshold_pct:
                confirmed = {'price': L, 'index': i, 'date': candles[i].get('date'),
                             'rise_pct': round(rise*100, 2)}
                break
            j += 1
        if confirmed:
            if not out or abs(confirmed['price']-out[-1]['price'])/confirmed['price'] > dedup_pct:
                out.append(confirmed)
            else:
                if confirmed['rise_pct'] > out[-1]['rise_pct']:
                    out[-1] = confirmed
            i = j
        else:
            i += 1
    return out

def trend_based_levels(candles, swing_left=2, swing_right=2, threshold_pct=0.03):
    """
    STRICT: 
      - Uptrend -> ONLY resistances (3% drop from a high)
      - Downtrend -> ONLY supports (3% rise from a low)
      - Sideways -> no levels
    """
    trend, _, _ = detect_trend(candles, swing_left, swing_right)
    if trend == "Uptrend":
        return {'trend': trend, 'levels': detect_resistances(candles, threshold_pct)}
    if trend == "Downtrend":
        return {'trend': trend, 'levels': detect_supports(candles, threshold_pct)}
    return {'trend': "Sideways", 'levels': []}