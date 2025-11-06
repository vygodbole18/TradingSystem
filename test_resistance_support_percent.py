

from fetch import fetch_ohlc_data
from resistance_support_percent_bilateral import (
    all_bilateral_resistance_support, _fmt_date
)

def show(symbol: str, lookback: int = 250, left_pct: float = 0.02, right_pct: float = 0.03):
    print(f"\n=== {symbol} | DAILY | last {lookback} | wick-based L={left_pct*100:.1f}%  R={right_pct*100:.1f}% ===")
    candles = fetch_ohlc_data(symbol, "day", lookback)

    out = all_bilateral_resistance_support(candles, pct_left=left_pct, pct_right=right_pct)
    R, S = out["resistances"], out["supports"]

    if R:
        print("\nResistances (idx, date, price, L-confirm date, R-confirm date):")
        for r in R:
            i = r["index"]; kL = r["left_confirm_idx"]; kR = r["right_confirm_idx"]
            print(f"  {i:>4}  {_fmt_date(candles[i].get('date'))}  "
                  f"{r['price']:.2f}  "
                  f"{_fmt_date(candles[kL].get('date')) if kL is not None else '-'}  "
                  f"{_fmt_date(candles[kR].get('date')) if kR is not None else '-'}")
    else:
        print("\nResistances: NONE")

    if S:
        print("\nSupports (idx, date, price, L-confirm date, R-confirm date):")
        for s in S:
            i = s["index"]; kL = s["left_confirm_idx"]; kR = s["right_confirm_idx"]
            print(f"  {i:>4}  {_fmt_date(candles[i].get('date'))}  "
                  f"{s['price']:.2f}  "
                  f"{_fmt_date(candles[kL].get('date')) if kL is not None else '-'}  "
                  f"{_fmt_date(candles[kR].get('date')) if kR is not None else '-'}")
    else:
        print("\nSupports: NONE")

if __name__ == "__main__":
    symbols = ["ADANIPORTS"]  # edit as needed
    for sym in symbols:
        # Daily, last 100 bars, LEFT=2%, RIGHT=3%
        show(sym, lookback=250, left_pct=0.02, right_pct=0.03)
