import pandas as pd
from ml_predict import prepare_data_for_ml, train_and_evaluate

tickers = ['RELIANCE', 'TCS', 'HDFCBANK']
trade_logs = []

for ticker in tickers:
    filename = f"data/{ticker}.csv"
    df, features = prepare_data_for_ml(filename)
    
    result_df = train_and_evaluate(df, features, ticker)  # this is now a DataFrame
    # print(type(result_df))  # Should print: <class 'pandas.core.frame.DataFrame'>


    last_row = result_df.iloc[-1]  # use latest model-enhanced row

    trade_logs.append({
        "Date": last_row["Date"],
        "Ticker": ticker,
        "Signal": df.iloc[-1].get("Signal", 0),
        "Close": last_row["Close"],
        "RSI": last_row["RSI"],
        "MA20": last_row["MA20"],
        "MA50": last_row["MA50"],
        "ML_Prediction": "UP" if last_row["ML_Prediction"] == 1 else "DOWN",
        "Model": last_row["Model"],
        "Model_Accuracy": last_row["Model_Accuracy"],
        "Reason": "Strategy Signal + ML Confirmation" if df.iloc[-1].get("Signal", 0) != 0 else "ML Only"
    })

# Save to CSV
log_df = pd.DataFrame(trade_logs)
log_df.to_csv("trade_logs.csv", index=False)
print("[INFO] Trade log saved to trade_logs.csv")


