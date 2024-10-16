from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, QuickReply, QuickReplyButton, MessageAction
from linebot.exceptions import InvalidSignatureError
import os,re
import QuickReply

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
    global test_mode  # 引用全域變數
    
    if test_mode == False:
        QuickReply.QReply_Start(event,line_bot_api)
    else:
        QuickReply.QReply_Chapter(event,line_bot_api)


