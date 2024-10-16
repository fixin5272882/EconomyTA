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
    global test_mode
    user_message = event.message.text
    if test_mode == False:
        QuickReply.QReply_Start(event,line_bot_api)
        if user_message == "練習模式":
            QuickReply.QReply_Chapter(event,line_bot_api)
            test_mode = True
            
    else:      
        # 第二步：選擇題數 (10、20、30)
        if user_message in ["Ch1", "Ch2", "Ch3"]:
            chapter = user_message  # 儲存選擇的章節
            QuickReply.QReply_QuestionNumber(event,line_bot_api)

        # 第三步：選擇 ABCD 答案
        elif user_message in ["10", "20", "30"]:
            question_count = user_message  # 儲存題數
            QuickReply.QReply_AnserButton(event,line_bot_api)

        # 最後一步：接收答案
        elif user_message in ["(A)", "(B)", "(C)", "(D)"]:
            answer = user_message  # 儲存選擇的答案
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f' {chapter} {question_count}。')
            )
            QuickReply.QReply_AnserButton(event,line_bot_api)

        elif user_message == "停止測試":
            test_mode = False
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='按鈕已隱藏')
            )
        
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='請輸入正確資訊')
            )


