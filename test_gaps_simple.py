# test_gaps_simple.py

from fetch import fetch_ohlc_data
from gaps_simple import detect_simple_gaps

def _fmt_date(d):
    try:
        return d.strftime("%Y-%m-%d")
    except Exception:
        return str(d)

def test_symbol(symbol: str, lookback: int = 25):
    print(f"\n=== {symbol} | DAILY | last {lookback} bars ===")
    candles = fetch_ohlc_data(symbol, "day", lookback)

    gaps = detect_simple_gaps(candles)
    if not gaps:
        print("No gaps found.")
        return

    print("index | date       | type     | prev_close | current_low_or_high")
    for g in gaps:
        print(f"{g['index']:>5} | {_fmt_date(g['date']):<10} | {g['type']:<8} | "
              f"{g['prev_close']:.2f}    | {g['current_low_or_high']:.2f}")

if __name__ == "__main__":
    symbols = ["RELIANCE", "HDFCBANK", "TCS"]  
    for s in symbols:
        test_symbol(s, lookback=25)
