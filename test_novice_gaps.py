from fetch import fetch_ohlc_data
from novice_gaps import detect_novice_gaps

def _fmt_date(d):
    try:
        return d.strftime("%Y-%m-%d")
    except Exception:
        return str(d)

def test_symbol(symbol: str, lookback: int = 100, N: int = 3, pct: float = 0.02):
    print(f"\n=== {symbol} | DAILY | last {lookback} | Novice Gaps (N={N}, pct={pct*100:.1f}%) ===")
    candles = fetch_ohlc_data(symbol, "day", lookback)

    out = detect_novice_gaps(candles, N=N, pct=pct)
    dlist, ulist = out["novice_gap_downs"], out["novice_gap_ups"]

    if dlist:
        print("\nNovice Gap Downs:")
        print(" idx | prior -> current | prev_close | curr_open | curr_close | prior_low")
        for g in dlist:
            print(f"{g['index']:>4} | {_fmt_date(g['prior_date'])} -> {_fmt_date(g['current_date'])} | "
                  f"{g['prev_close']:.2f} | {g['curr_open']:.2f} | {g['curr_close']:.2f} | {g['prior_low']:.2f}")
    else:
        print("\nNovice Gap Downs: NONE")

    if ulist:
        print("\nNovice Gap Ups:")
        print(" idx | prior -> current | prev_close | curr_open | curr_close | prior_high")
        for g in ulist:
            print(f"{g['index']:>4} | {_fmt_date(g['prior_date'])} -> {_fmt_date(g['current_date'])} | "
                  f"{g['prev_close']:.2f} | {g['curr_open']:.2f} | {g['curr_close']:.2f} | {g['prior_high']:.2f}")
    else:
        print("\nNovice Gap Ups: NONE")

if __name__ == "__main__":
    symbols = ["RELIANCE" , "HDFCBANK", "TCS"]
    for s in symbols:
        test_symbol(s, lookback=100, N=3, pct=0.02)
