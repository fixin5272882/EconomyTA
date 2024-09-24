from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
import json
import requests
import os
import difflib

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
# Channel Secret
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 定義一個全域變數來追蹤測試狀態
test_mode = False

# 處理訊息的事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global test_mode  # 使用全域變數來追蹤狀態
    user_message = event.message.text

    if user_message == "測試開始":
        test_mode = True  # 開始測試，設置為 True
        Reply_Modle(event)
        
    elif user_message == "測試結束":
        test_mode = False  # 結束測試，設置為 False
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="測試結束，按鈕已隱藏。")
        )

    else:
        # 如果在測試模式中，則每次訊息都顯示 Quick Reply 按鈕
        if test_mode:
            Reply_Modle(event)
        else:
            # 如果不在測試模式中，則只是回覆訊息
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"你傳送了：{user_message}")
            )

def Reply_Modle(event):
    quick_reply_buttons = QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="選項 1", text="你選擇了選項 1")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="選項 2", text="你選擇了選項 2")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="選項 3", text="你選擇了選項 3")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="測試結束", text="測試結束")
                    )
                ]
            )
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="測試開始，請選擇一個選項:", quick_reply=quick_reply_buttons)
    )