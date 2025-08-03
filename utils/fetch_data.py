import yfinance as yf
import pandas as pd

def get_stock_data(ticker, period='1y', interval='1d'):
    import yfinance as yf
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty or 'Close' not in df.columns:
        print(f"[ERROR] Failed to fetch valid data for {ticker}")
        return pd.DataFrame()  # Empty frame, so main script will skip
    return df.reset_index()

