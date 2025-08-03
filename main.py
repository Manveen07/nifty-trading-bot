import os
import pandas as pd
from strategies.indicators import add_indicators
from utils.fetch_data import get_stock_data


tickers = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']
os.makedirs("data", exist_ok=True)

for ticker in tickers:
    try:
        df = get_stock_data(ticker, period='1y')
        if not df.empty and 'Close' in df.columns:
            print("[DEBUG] Before indicators: ", type(df['Close']), df['Close'].shape)
            df = add_indicators(df)
            path = f"data/{ticker.replace('.NS', '')}.csv"
            df.to_csv(path, index=False)
            print(f"[INFO] Saved with indicators: {path}")
        else:
            print(f"[WARN] No valid data for {ticker}")
    except Exception as e:
        print(f"[ERROR] Error processing {ticker}: {e}")

