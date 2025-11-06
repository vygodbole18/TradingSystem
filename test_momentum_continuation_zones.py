from fetch import fetch_ohlc_data
from resistance_support_percent_bilateral import all_bilateral_resistance_support
from demandZone import find_demand_zones
from supplyZone import find_supply_zones
from momentum_continuation_zones import detect_momentum_continuation_zones

def _fmt_date(d):
    try:
        return d.strftime("%Y-%m-%d")
    except Exception:
        return str(d)

def _normalize_dbr_zones(raw):
    out = []
    for z in raw:
        if z.get("type") != "DBR":
            continue
        out.append({
            "zone_low": float(z["bottom"]),
            "zone_high": float(z["top"]),
            "base_start": int(z["base_start_idx"]),
            "base_end": int(z["base_end_idx"]),
            "zone_date": z.get("created_at"),
        })
    return out

def _normalize_rbd_zones(raw):
    out = []
    for z in raw:
        if z.get("type") != "RBD":
            continue
        out.append({
            "zone_low": float(z["proximal"]),
            "zone_high": float(z["distal"]),
            "base_start": int(z["base_start_idx"]),
            "base_end": int(z["base_end_idx"]),
            "zone_date": z.get("created_at"),
        })
    return out

def show(symbol: str, lookback: int = 100, left_pct: float = 0.02, right_pct: float = 0.03):
    print(f"\n=== {symbol} | DAILY | last {lookback} | M-Continuation (L={left_pct*100:.1f}%, R={right_pct*100:.1f}%) ===")
    candles = fetch_ohlc_data(symbol, "day", lookback)

    rs = all_bilateral_resistance_support(candles, pct_left=left_pct, pct_right=right_pct)
    resistances, supports = rs["resistances"], rs["supports"]

    dz_raw = find_demand_zones(candles, lookback=lookback)
    sz_raw = find_supply_zones(candles, lookback=lookback)
    dbr_zones = _normalize_dbr_zones(dz_raw)
    rbd_zones = _normalize_rbd_zones(sz_raw)

    out = detect_momentum_continuation_zones(
        candles=candles,
        resistances=resistances,
        supports=supports,
        dbr_zones=dbr_zones,
        rbd_zones=rbd_zones,
    )

    cds = out["continuation_demand"]
    css = out["continuation_supply"]

    if cds:
        print("\nMomentum Continuation Demand (MCDZ):")
        print(" DBR_date | R1_price (R1_date) -> R2_price (R2_date) -> Breach_date | origin -> zone_low..zone_high")
        for z in cds:
            print(f" {_fmt_date(z['dbr_date'])} | "
                  f"{z['r1_price']:.2f} ({_fmt_date(z['r1_date'])}) -> "
                  f"{z['r2_price']:.2f} ({_fmt_date(z['r2_date'])}) -> "
                  f"{_fmt_date(z['breach_date'])} | "
                  f"{z['origin']:.2f} -> {z['zone_low']:.2f}..{z['zone_high']:.2f}")
    else:
        print("\nMomentum Continuation Demand (MCDZ): NONE")

    if css:
        print("\nMomentum Continuation Supply (MCSZ):")
        print(" RBD_date | S1_price (S1_date) -> S2_price (S2_date) -> Breach_date | origin -> zone_low..zone_high")
        for z in css:
            print(f" {_fmt_date(z['rbd_date'])} | "
                  f"{z['s1_price']:.2f} ({_fmt_date(z['s1_date'])}) -> "
                  f"{z['s2_price']:.2f} ({_fmt_date(z['s2_date'])}) -> "
                  f"{_fmt_date(z['breach_date'])} | "
                  f"{z['origin']:.2f} -> {z['zone_low']:.2f}..{z['zone_high']:.2f}")
    else:
        print("\nMomentum Continuation Supply (MCSZ): NONE")

if __name__ == "__main__":
    symbols = ["ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL", "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT", "ETERNAL", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY", "ITC", "JIOFIN", "JSWSTEEL", "KOTAKBANK", "LT", "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM", "TITAN", "TRENT", "ULTRACEMCO"," WIPRO"]
    for s in symbols:
        show(s, lookback=100, left_pct=0.02, right_pct=0.03)
