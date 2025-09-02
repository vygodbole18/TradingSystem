# Trading System (Kite Connect + Python)

This project uses **Zerodha Kite Connect API** to fetch daily OHLC candles and detect:

- **Swings** (swing highs & lows using % rules)  
- **Support & Resistance** (bilateral, wick-based, configurable left/right %)  
- **Simple Gaps** (gap up / gap down between consecutive days)

## Files
- `generate_token.py` → create daily access token  
- `fetch.py` → fetch OHLC data as list of dictionaries  
- `swings_percent_bilateral.py` → swing detection  
- `resistance_support_percent_bilateral.py` → support/resistance levels  
- `gaps_simple.py` → simple gap detection  
- `test_*.py` → tester scripts for each module  

##  Setup Instructions

1. Install dependencies:

```bash
pip install kiteconnect python-dotenv
```
2. **Create a `.env` file** (Do NOT commit this to Git)  
Inside your project folder, create a file named `.env` and add:
```
API_KEY=your_api_key
API_SECRET=your_api_secret
REQUEST_TOKEN=your_request_token
ACCESS_TOKEN=your_access_token
```

3. Generate your access token daily using
```
python generate_token.py
```

4. Run scripts based on your need
 ```
python test*.py
```


##  Output 

When you run a tester script, you will get results showing the index, date, type, previous close, and current high/low (depending on the file you run).

## Safety Notes

- This project is for **educational purposes only**.  
- You are responsible for **all trades placed** using your API credentials.  
- Always test in paper/mock mode before using real funds.


## License

This project is licensed under MIT.

## Built with ❤️ for 🇮🇳
©️Vedant Godbole
