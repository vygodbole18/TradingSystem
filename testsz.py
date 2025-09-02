from fetch import fetch_ohlc_data
from supplyZone import find_supply_zones   

if __name__ == "__main__":
    # Pick any symbol you like; here using RELIANCE as example
    symbol = "HAL"
    interval = "day"      # 1-minute, 5-minute, 15-minute, day, etc.
    count = 200           # how many candles to fetch       

    # Fetch OHLC candles
    candles = fetch_ohlc_data(symbol, interval, count)

    # Find supply zones in last 100 bars
    zones = find_supply_zones(candles, lookback=100)

    if not zones:
        print("No supply zones found in the last 100 bars.")
    else:
        for z in zones:
            print(
                f"{z['type']} | "
                f"Proximal={z['proximal']} | "
                f"Distal={z['distal']} | "
                f"Created={z['created_at']}"
            )