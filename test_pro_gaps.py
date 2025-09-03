
from fetch import fetch_ohlc_data
from pro_gaps import detect_pro_gaps

def _fmt_date(d):
    try:
        return d.strftime("%Y-%m-%d")
    except Exception:
        return str(d)

def test_symbol(symbol: str, lookback: int = 100, min_bars: int = 3, min_pct: float = 0.02):
    print(f"\n=== {symbol} | DAILY | last {lookback} | Pro Gaps (context: ≥{min_bars} bars & ≥{min_pct*100:.1f}%) ===")
    candles = fetch_ohlc_data(symbol, "day", lookback)

    out = detect_pro_gaps(candles, min_bars=min_bars, min_pct=min_pct)
    ups, downs = out["pro_gap_ups"], out["pro_gap_downs"]

    if ups:
        print("\nPro Gap Ups:")
        print(" idx | prior_date  -> current_date | prev_close | curr_low | zone_low .. zone_high")
        for g in ups:
            print(f"{g['index']:>4} | {_fmt_date(g['prior_date'])} -> {_fmt_date(g['current_date'])} | "
                  f"{g['prev_close']:.2f} | {g['curr_low']:.2f} | {g['zone_low']:.2f} .. {g['zone_high']:.2f}")
    else:
        print("\nPro Gap Ups: NONE")

    if downs:
        print("\nPro Gap Downs:")
        print(" idx | prior_date  -> current_date | prev_close | curr_high | zone_low .. zone_high")
        for g in downs:
            print(f"{g['index']:>4} | {_fmt_date(g['prior_date'])} -> {_fmt_date(g['current_date'])} | "
                  f"{g['prev_close']:.2f} | {g['curr_high']:.2f} | {g['zone_low']:.2f} .. {g['zone_high']:.2f}")
    else:
        print("\nPro Gap Downs: NONE")

if __name__ == "__main__":
    symbols = ["HEROMOTOCO"]
    for s in symbols:
        test_symbol(s, lookback=100, min_bars=3, min_pct=0.02)
