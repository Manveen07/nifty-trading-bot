import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os
import requests
from dotenv import load_dotenv

load_dotenv()
def send_telegram_message(message, token, chat_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"  # or "HTML"
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("[INFO] Telegram message sent")
    else:
        print(f"[ERROR] Telegram message failed: {response.text}")



def push_to_google_sheets_all(trade_df, pnl_df, data_folder="data"):
    # Setup
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    sheet = client.open_by_key("1WiDmH1QdJu8QC4aXcTA1Gkvw8lncOa8t3tYJqaQDpTw")

    # --- Trade_Log tab ---
    try:
        trade_ws = sheet.worksheet("Trade_Log")
        sheet.del_worksheet(trade_ws)
    except:
        pass
    trade_ws = sheet.add_worksheet(title="Trade_Log", rows=1000, cols=20)
    trade_ws.update([trade_df.columns.values.tolist()] + trade_df.values.tolist())

    # --- P&L_Summary tab ---
    try:
        pnl_ws = sheet.worksheet("P&L_Summary")
        sheet.del_worksheet(pnl_ws)
    except:
        pass
    pnl_ws = sheet.add_worksheet(title="P&L_Summary", rows=1000, cols=10)
    pnl_ws.update([pnl_df.columns.values.tolist()] + pnl_df.values.tolist())

    # --- Upload all data/*.csv as individual sheets ---
    for file in os.listdir(data_folder):
        if file.endswith(".csv"):
            ticker_name = file.replace(".csv", "")
            df = pd.read_csv(os.path.join(data_folder, file))

            # Clean invalid float values
            df_cleaned = df.replace([float('inf'), float('-inf')], pd.NA).fillna("")

            # Delete existing sheet if exists
            try:
                ws = sheet.worksheet(ticker_name)
                sheet.del_worksheet(ws)
            except:
                pass

            # Add and update
            ws = sheet.add_worksheet(title=ticker_name, rows=1000, cols=20)
            ws.update([df_cleaned.columns.values.tolist()] + df_cleaned.values.tolist())
            print(f"[INFO] Uploaded {file} to sheet: {ticker_name}")

    print("[INFO] All data uploaded to Google Sheets.")



# Sample data
trade_df = pd.read_csv("trade_logs.csv")
pnl_df = pd.read_csv("backtest_summary.csv")

message = "📈 *Latest Trade Logs:*\n\n"
for _, row in trade_df.tail(3).iterrows():
    message += (
        f"📅 {row['Date']}, 🏦 {row['Ticker']}\n"
        f"Signal: {'BUY' if row['Signal'] == 1 else 'SELL' if row['Signal'] == -1 else 'HOLD'} at ₹{row['Close']:.2f}\n"
        f"RSI: {row['RSI']:.2f}, MA20: {row['MA20']:.2f}, MA50: {row['MA50']:.2f}\n"
        f"📊 Prediction: {row['ML_Prediction']} ({row['Model']}, {row['Model_Accuracy']}%)\n"
        f"Reason: {row['Reason']}\n\n"
    )
print(os.getenv("AcessToken"), os.getenv("ChatID"))
send_telegram_message(message, os.getenv("AcessToken"), os.getenv("ChatID"))   
push_to_google_sheets_all(trade_df, pnl_df)
print("Done")