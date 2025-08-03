📈 Algo-Trading System with ML & Automation
An end-to-end automated trading system that combines rule-based strategies and machine learning to make informed buy/sell decisions on NIFTY 50 stocks. It fetches stock data, generates trade signals, backtests strategies, logs trades to Google Sheets, and sends alerts via Telegram.

🚀 Features
✅ Fetch historical stock data using yfinance

✅ Rule-based strategy using RSI and moving average crossover

✅ ML-based prediction using Logistic Regression & Random Forest (with GridSearch)

✅ Trade logging and backtesting over 6 months

✅ Auto-logging trades and P&L to Google Sheets

✅ Optional Telegram alerts for new trades

✅ Modular, reusable, and well-documented code

🧠 Strategy Overview
📊 Rule-Based Buy Signal
RSI < 30

20-DMA > 50-DMA (Golden crossover)

🤖 ML Models
Inputs: RSI, MACD, Volume, etc.

Algorithms: Logistic Regression & Random Forest (with GridSearchCV)

Output: Next-day movement (UP or DOWN)

Saved with: joblib

🔁 Combined Logic
If rule-based signal is triggered or ML predicts UP, a buy signal is generated.

📂 Folder Structure
bash
Copy
Edit
algo_trading_project/
│
├── data/                   # Contains downloaded stock data CSVs
│   ├── RELIANCE.csv
│   └── ...
├── models/                 # Saved ML models (.joblib)
├── trade_logs.csv          # All trade actions
├── backtest_summary.csv    # P&L summary
├── credentials.json        # Google Sheets service account creds
├── .env                    # Stores Telegram token, chat_id
│
├── fetch_data.py           # Fetches data via yfinance
├── indicators.py           # RSI, MA, MACD functions
├── strategy.py             # Rule + ML logic
├── ml_models.py            # Training & prediction
├── backtester.py           # Backtesting engine
├── googlesheet.py          # Google Sheets push functions
├── telegram_bot.py         # Telegram alert handler
├── bots.py                 # Master script to run the full pipeline
└── README.md
📋 Requirements
Install via requirements.txt:

bash
Copy
Edit
pip install -r requirements.txt
Dependencies include:

pandas

yfinance

scikit-learn

joblib

gspread

oauth2client

python-dotenv

requests

🔐 Environment Setup
Create a .env file:

ini
Copy
Edit
AcessToken=your_telegram_bot_token
ChatID=your_telegram_chat_id
Download and place your credentials.json for Google Sheets API in the root directory.

📊 Outputs
✅ Google Sheet
Trade_Log: Every trade with reason and model info

P&L_Summary: Stock-wise trade count, return %, and win ratio

Ticker sheets: Daily indicators for each stock

✅ Telegram Alert
You’ll receive trade alerts like:

vbnet
Copy
Edit
🔔 New Trade Executed:
Ticker: RELIANCE
Signal: BUY
Model: LogisticRegression (Accuracy: 54%)
Reason: ML Only
Price: ₹1393.70