from fetch import fetch_ohlc_data, fetch_ltp
from resistance_support_percent_bilateral import all_bilateral_resistance_support
from demandZone import find_demand_zones
from supplyZone import find_supply_zones
from momentum_zones import detect_momentum_zones
import time

def _fmt_date(d):
    try:
        return d.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return str(d)

def _normalize_demand_zones(raw):
    out = []
    for z in raw:
        if z.get("type") != "RBR":
            continue
        out.append({
            "zone_low": float(z["bottom"]),
            "zone_high": float(z["top"]),
            "base_start": int(z["base_start_idx"]),
            "base_end": int(z["base_end_idx"]),
            "leg_in": int(z["leg_in_idx"]) if z.get("leg_in_idx") is not None else int(z["base_start_idx"]),
            "start_date": z.get("created_at"),
            "end_date": z.get("created_at"),  # use leg-out candle date as RBR date
        })
    return out

def _normalize_supply_zones(raw):
    out = []
    for z in raw:
        if z.get("type") != "DBD":
            continue
        out.append({
            "zone_low": float(z["proximal"]),
            "zone_high": float(z["distal"]),
            "base_start": int(z["base_start_idx"]),
            "base_end": int(z["base_end_idx"]),
            "leg_in": int(z["leg_in_idx"]) if z.get("leg_in_idx") is not None else int(z["base_start_idx"]),
            "start_date": z.get("created_at"),
            "end_date": z.get("created_at"),  # use leg-out candle date as DBD date
        })
    return out

def show(symbol: str, lookback: int = 400, left_pct: float = 0.01, right_pct: float = 0.015):
    print(f"\n=== {symbol} | HOURLY | last {lookback} | wick-based L={left_pct*100:.1f}%  R={right_pct*100:.1f}% ===")
    candles = fetch_ohlc_data(symbol, "60minute", lookback)

    rs = all_bilateral_resistance_support(candles, pct_left=left_pct, pct_right=right_pct)
    resistances, supports = rs["resistances"], rs["supports"]

    rbr_raw = find_demand_zones(candles, lookback=lookback)  # only RBR used
    dbd_raw = find_supply_zones(candles, lookback=lookback)  # only DBD used
    rbr_zones = _normalize_demand_zones(rbr_raw)
    dbd_zones = _normalize_supply_zones(dbd_raw)

    out = detect_momentum_zones(
        candles=candles,
        resistances=resistances,
        supports=supports,
        rbr_zones=rbr_zones,
        dbd_zones=dbd_zones,
    )

    mds = out["momentum_demand"]
    mss = out["momentum_supply"]

    printed = False

    if mds:
        printed = True
        print("\nMomentum Demand Zones (MDZ):")
        print(" RBR_date | R1_price (R1_date) -> R2_price (R2_date) -> Breach_date")
        for z in mds:
            print(f" {_fmt_date(z['base_end_date'])} | "
                  f"{z['seed_price']:.2f} ({_fmt_date(z['seed_date'])}) -> "
                  f"{z['confirm_price']:.2f} ({_fmt_date(z['confirm_date'])}) -> "
                  f"{_fmt_date(z['breach_date'])}")
    else:
        print("\nMomentum Demand Zones (MDZ): NONE")

    if mss:
        printed = True
        print("\nMomentum Supply Zones (MSZ):")
        print(" DBD_date | S1_price (S1_date) -> S2_price (S2_date) -> Breach_date")
        for z in mss:
            print(f" {_fmt_date(z['base_end_date'])} | "
                  f"{z['seed_price']:.2f} ({_fmt_date(z['seed_date'])}) -> "
                  f"{z['confirm_price']:.2f} ({_fmt_date(z['confirm_date'])}) -> "
                  f"{_fmt_date(z['breach_date'])}")
    else:
        print("\nMomentum Supply Zones (MSZ): NONE")

    if printed:
        ltp = fetch_ltp(symbol)
        if ltp:
            print(f"\nCurrent LTP for {symbol}: {ltp:.2f}")    

if __name__ == "__main__":

   # symbols = ["ADANIENT", "ADANIPORTS", "APOLLOHOSP", "ASIANPAINT", "AXISBANK", "BAJAJ-AUTO", "BAJFINANCE", "BAJAJFINSV", "BEL", "BHARTIARTL", "CIPLA", "COALINDIA", "DRREDDY", "EICHERMOT", "ETERNAL", "GRASIM", "HCLTECH", "HDFCBANK", "HDFCLIFE", "HEROMOTOCO", "HINDALCO", "HINDUNILVR", "ICICIBANK", "INDUSINDBK", "INFY", "ITC", "JIOFIN", "JSWSTEEL", "KOTAKBANK", "LT", "M&M", "MARUTI", "NESTLEIND", "NTPC", "ONGC", "POWERGRID", "RELIANCE", "SBILIFE", "SBIN", "SUNPHARMA", "TATACONSUM", "TATAMOTORS", "TATASTEEL", "TECHM", "TITAN", "TRENT", "ULTRACEMCO"," WIPRO"]
   
    symbols = [
    "RELIANCE", "NIFTY",  "HDFCBANK", "TCS", "BHARTIARTL", "ICICIBANK", "SBIN", "HINDUNILVR", 
    "INFY", "BAJFINANCE", "LICI", "ITC", "LT", "MARUTI", "M&M", "KOTAKBANK", "HCLTECH", 
    "SUNPHARMA", "ULTRACEMCO", "AXISBANK", "TITAN", "BAJAJFINSV", "NTPC", "ETERNAL", 
    "DMART", "HAL", "ONGC", "ADANIPORTS", "BEL", "POWERGRID", "ADANIENT", "JSWSTEEL", 
    "WIPRO", "TATAMOTORS", "BAJAJ-AUTO", "ASIANPAINT", "COALINDIA", "NESTLEIND", "INDIGO", 
    "TATASTEEL", "IOC", "JIOFIN", "TRENT", "GRASIM", "DLF", "HINDZINC", "SBILIFE", 
    "EICHERMOT", "VEDL", "HINDALCO", "TVSMOTOR", "MARICO", "BSE", "ICICIGI", "ADANIENSOL", 
    "GMRAIRPORT", "INDIANB", "INDUSTOWER", "LUPIN", "JSWENERGY", "NAUKRI", "ICICIPRULI", 
    "SRF", "POLICYBZR", "HINDPETRO", "PERSISTENT", "PAYTM", "SUZLON", "IDEA", "NHPC", 
    "ASHOKLEY", "SBICARD", "UNOMINDA", "BHEL", "ABCAPITAL", "OFSS", "FORTIS", "RVNL", 
    "NYKAA", "COLPAL", "PRESTIGE", "NMDC", "PATANJALI", "OIL", "YESBANK", "ALKEM", 
    "TORNTPOWER", "AUROPHARMA", "OBEROIRLTY", "GODREJPROP", "INDUSINDBK", "SUPREMEIND", 
    "GLENMARK", "TIINDIA", "LTF", "IRCTC", "COFORGE", "PIIND", "MFSL", "BHARATFORG", 
    "PHOENIXLTD", "SAIL", "IDFCFIRSTB", "MPHASIS", "BDL", "KALYANKJIL", "AUBANK", "UPL", 
    "BANKINDIA", "PAGEIND", "BIOCON", "LAURUSLABS", "VOLTAS", "FEDERALBNK", "APLAPOLLO", 
    "DALBHARAT", "KAYNES", "JUBLFOOD", "CONCOR", "HUDCO", "PETRONET", "IREDA", "BLUESTARCO", 
    "NATIONALUM", "ASTRAL", "MCX", "KEI", "EXIDEIND", "DELHIVERY", "TATAELXSI", "KPITTECH", 
    "CDSL", "LICHSGFIN", "IGL", "NBCC", "SONACOMS", "TATATECH", "PPLPHARMA", "AMBER", 
    "BANDHANBNK", "SYNGENE", "INOXWIND", "TATACHEM", "MANAPPURAM", "NUVAMA", "CROMPTON", 
    "ANGELONE", "PNBHOUSING", "CAMS", "KFINTECH", "IIFL", "RBLBANK", "PGEL", "NCC", 
    "CYIENT", "IEX", "SAMMAANCAP", "TITAGARH"
]

    for s in symbols:
        show(s, lookback=400, left_pct=0.01, right_pct=0.015)
        time.sleep(0.5)
