import pandas as pd


tickers = ['RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS']

def generate_signals_with_rsi_lookback(df, rsi_threshold=30, lookback=2):
    df = df.copy()
    df['Signal'] = 0
    
    soft_crossover = (df['MA20'] > df['MA50'] * 0.98)
    crossover_days = soft_crossover & (df['MA20'].shift(1) <= df['MA50'].shift(1))
    print("Total crossovers:", crossover_days.sum())

    buy_signals = []
    for i in range(len(df)):
        if crossover_days.iloc[i]:
            start_idx = max(i - lookback, 0)
            end_idx = min(i + lookback, len(df) - 1)
            rsi_window = df.loc[start_idx:end_idx, 'RSI']
            print(f"Crossover at index {i}, RSI window values:\n{rsi_window}")

            if (rsi_window < rsi_threshold).any():
                buy_signals.append(i)
    
    df.loc[buy_signals, 'Signal'] = 1
    
    sell_condition = (df['RSI'] > 70) & (df['MA20'] < df['MA50']) & (df['MA20'].shift(1) >= df['MA50'].shift(1))
    df.loc[sell_condition, 'Signal'] = -1

    print(f"Buy signals generated: {len(buy_signals)}")
    return df



def backtest_signals(df, holding_period=10):
    df = df.copy()
    trades = []
    position = None  # 'long' or None
    entry_date, entry_price = None, None

    for i in range(len(df)):
        row = df.iloc[i]
        if row['Signal'] == 1 and position is None:
            # Enter long position
            position = 'long'
            entry_date = row['Date']
            entry_price = row['Close']
            entry_index = i

        elif position == 'long':
            exit_condition = row['Signal'] == -1 or (i - entry_index) >= holding_period
            if exit_condition:
                exit_date = row['Date']
                exit_price = row['Close']
                profit_pct = (exit_price - entry_price) / entry_price * 100

                trades.append({
                   "Ticker": df['Ticker'].iloc[0] if 'Ticker' in df.columns else "N/A",
                    "Entry_Date": entry_date,
                    "Exit_Date": exit_date,
                    "Entry_Price": entry_price,
                    "Exit_Price": exit_price,
                    "P&L (%)": round(profit_pct, 2),
                    "Holding_Days": i - entry_index
                })

                # Reset position
                position = None
                entry_date, entry_price = None, None

    # Final open trade exit (optional)
    if position == 'long':
        last_row = df.iloc[-1]
        profit_pct = (last_row['Close'] - entry_price) / entry_price * 100
        trades.append({
             "Ticker": df['Ticker'].iloc[0] if 'Ticker' in df.columns else "N/A",
            "Entry_Date": entry_date,
            "Exit_Date": last_row['Date'],
            "Entry_Price": entry_price,
            "Exit_Price": last_row['Close'],
            "P&L (%)": round(profit_pct, 2),
            "Holding_Days": len(df) - entry_index
        })

    # Convert to DataFrame and calculate metrics
    trade_df = pd.DataFrame(trades)
    trade_df["Win"] = trade_df["P&L (%)"] > 0
    total_return = trade_df["P&L (%)"].sum()
    win_ratio = trade_df["Win"].mean() * 100 if not trade_df.empty else 0

    print(f"Total Trades: {len(trade_df)}")
    print(f"Total Return: {round(total_return, 2)}%")
    print(f"Win Ratio: {round(win_ratio, 2)}%")

    return trade_df

summary_rows = []
# Usage:
for ticker in tickers:
    csv_path = f"data/{ticker.replace('.NS', '')}.csv"
    df = pd.read_csv(csv_path)
    df = df.sort_values('Date').reset_index(drop=True)
    df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
    df["Ticker"] = ticker.replace(".NS", "")
   # Generate signals
    df = generate_signals_with_rsi_lookback(df, rsi_threshold=45, lookback=2)

    # Backtest
    results = backtest_signals(df)
    results.to_csv(f"backtest_{ticker.replace('.NS', '')}.csv", index=False)

    df.to_csv(csv_path, index=False)

    # Append summary
    total_return = results["P&L (%)"].sum()
    win_ratio = results["Win"].mean() * 100 if not results.empty else 0
    total_trades = len(results)

    summary_rows.append({
        "Ticker": ticker.replace(".NS", ""),
        "Total_Trades": total_trades,
        "Total_Return (%)": round(total_return, 2),
        "Win_Ratio (%)": round(win_ratio, 2)
    })

    print(f"[{ticker}] Buy signals: {(df['Signal'] == 1).sum()}")
    print(f"[{ticker}] Backtest saved. Total trades: {total_trades}\n")


# Save backtest summary
summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv("backtest_summary.csv", index=False)
print("[INFO] Backtest summary saved to backtest_summary.csv")