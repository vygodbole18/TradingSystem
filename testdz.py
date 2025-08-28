from fetch import fetch_ohlc_data
from demandZone import find_demand_zones

# Example: Reliance daily candles, last 200 days
candles = fetch_ohlc_data("HAL", "day", 200)

# Find zones in the last 100 bars
zones = find_demand_zones(candles, lookback=100)

for z in zones:
    print(f"{z['type']} | Top={z['top']} | Bottom={z['bottom']} | Created={z['created_at']}")