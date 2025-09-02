# test_swings_percent.py

from fetch import fetch_ohlc_data
from swings_percent_bilateral import latest_bilateral_swings, _fmt_date

def test_symbol(symbol: str, lookback: int = 100, pct: float = 0.03):
    print(f"\n=== {symbol} | DAILY | last {lookback} | 7% from CLOSE (pct={pct*100:.2f}%) ===")
    candles = fetch_ohlc_data(symbol, "day", lookback)

    out = latest_bilateral_swings(candles, pct=pct)
    sh, sl = out["swing_high"], out["swing_low"]

    if sh:
        print(f"Swing High @ idx={sh['index']}  date={_fmt_date(sh['date'])}  "
              f"high={sh['high']:.2f}  close={sh['close']:.2f}")
    else:
        print("Swing High: NOT FOUND")

    if sl:
        print(f"Swing Low  @ idx={sl['index']}  date={_fmt_date(sl['date'])}  "
              f"low={sl['low']:.2f}   close={sl['close']:.2f}")
    else:
        print("Swing Low: NOT FOUND")

if __name__ == "__main__":
    symbols = ["RELIANCE", "HDFCBANK", "TCS"]  
    for s in symbols:
        test_symbol(s, lookback=100, pct=0.03)
