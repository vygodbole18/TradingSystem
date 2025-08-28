# test_support_resistance.py
from resistance_and_support import trend_based_levels
from fetch import fetch_ohlc_data

def test_symbol(symbol, interval="day", lookback=150):
    print(f"\n=== Testing {symbol} ({interval}, last {lookback}) ===")
    candles = fetch_ohlc_data(symbol, interval, lookback)
    result = trend_based_levels(candles, swing_left=2, swing_right=2, threshold_pct=0.03)

    print(f"Trend: {result['trend']}")
    if not result['levels']:
        print("No levels detected.")
    else:
        for lvl in result['levels']:
            if result['trend'] == "Uptrend":
                print(f"[RESIST] {lvl['date']} | high={lvl['price']} | drop={lvl['drop_pct']}%")
            elif result['trend'] == "Downtrend":
                print(f"[SUPPORT] {lvl['date']} | low={lvl['price']} | rise={lvl['rise_pct']}%")

if __name__ == "__main__":
    # Test a few symbols (add/remove as you like)
    test_symbol("RELIANCE", "day", 200)