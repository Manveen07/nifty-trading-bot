import pandas as pd
import ta

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds RSI (14), MACD, MACD Signal, 20-day and 50-day moving averages to given OHLCV DataFrame.
    :param df: pandas DataFrame containing at least 'Close' column.
    :return: DataFrame with new indicator columns.
    """
    df = df.copy()
    
    if 'Close' not in df.columns:
        raise ValueError("'Close' column is required in the DataFrame")
    
    close_series = df['Close']
    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.squeeze()
    
    df['RSI'] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
    macd = ta.trend.MACD(close=close_series)
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    
    df['MA20'] = close_series.rolling(window=20).mean()
    df['MA50'] = close_series.rolling(window=50).mean()
    
    df = df.dropna() # Remove rows with NaNs — only if needed.
    return df

