

from fetch import fetch_ohlc_data
from gaps_simple import detect_simple_gaps
from resistance_support_percent_bilateral import all_bilateral_resistance_support, _fmt_date
from momentum_gaps import detect_momentum_gaps

def test_symbol(symbol: str, lookback: int = 100, left_pct: float = 0.02, right_pct: float = 0.03):
    print(f"\n=== {symbol} | DAILY | last {lookback} | R/S(left={left_pct*100:.1f}%, right={right_pct*100:.1f}%) ===")
    candles = fetch_ohlc_data(symbol, "day", lookback)

    gaps = detect_simple_gaps(candles)
    rs = all_bilateral_resistance_support(candles, pct_left=left_pct, pct_right=right_pct)

    out = detect_momentum_gaps(
        candles=candles,
        gaps=gaps,
        resistances=rs["resistances"],
        supports=rs["supports"],
    )

    ups = out["momentum_gap_ups"]
    dns = out["momentum_gap_downs"]

    if ups:
        print("\nMomentum Gap Ups (idx, date, zone_low..zone_high, resistance@price):")
        for d in ups:
            print(f"  {d['index']:>4}  prior={_fmt_date(d['prior_date'])}  "
                  f"current={_fmt_date(d['current_date'])}  "
                  f"zone={d['zone_low']:.2f}..{d['zone_high']:.2f}  "
                  f"RES@{d['level_price']:.2f} ({_fmt_date(d['level_date'])})")

    else:
        print("\nMomentum Gap Ups: NONE")

    if dns:
        print("\nMomentum Gap Downs (idx, date, zone_low..zone_high, support@price):")
        for d in dns:
           print(f"  {d['index']:>4}  prior={_fmt_date(d['prior_date'])}  "
      f"current={_fmt_date(d['current_date'])}  "
      f"zone={d['zone_low']:.2f}..{d['zone_high']:.2f}  "
      f"SUP@{d['level_price']:.2f} ({_fmt_date(d['level_date'])})")

    else:
        print("\nMomentum Gap Downs: NONE")


if __name__ == "__main__":
    symbols = ["HEROMOTOCO"]  
    for s in symbols:
        test_symbol(s, lookback=100, left_pct=0.02, right_pct=0.03)
