import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone, timedelta
import os

# 建立 Google Sheets 連接
def connect_google_sheets():
    # Google Sheets 連接設定
    #給憑證
    SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # 加載憑證
    creds = Credentials.from_service_account_file("./phrasal-truck-426318-a6-1afe736b2cee.json", scopes=SCOPES)
    # 連接到 Google Sheets
    gc = gspread.authorize(creds)
    sh  = gc.open_by_url(os.getenv('SHEET_URL'))
    return sh

# 新增無法回答的問題進入google sheet
def add_question_insheet(line_bot_api,event,chapter,question,worksheet):
    user_Id  = event.source.user_id
    profile = line_bot_api.get_profile(user_Id)
    user_name = profile.display_name
    questions = worksheet.col_values(5)
    if question not in questions:
        time = datetime.now().astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")
        new_row = [time,user_Id,user_name,chapter,question]
        worksheet.append_row(new_row)