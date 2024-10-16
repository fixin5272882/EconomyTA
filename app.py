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
asner_mode = False
set_mode = False
test_mode = False

# 處理訊息的事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global asner_mode # 使用全域變數來追蹤狀態
    global set_mode
    global test_mode
    user_message = event.message.text
    time =0

    if user_message == "測試設定":
        asner_mode = False
        set_mode = True
        test_mode = False
        QuickReply.QReply_Chapter(event,line_bot_api)
    
    # elif user_message == "開始測試":
    #     asner_mode = False
    #     set_mode = False
    #     test_mode = True
    #     QuickReply.QReply_AnserButton(event,line_bot_api)

    elif user_message == "測試結束":
        asner_mode = False
        set_mode = False
        test_mode = False 
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="測試結束，按鈕已隱藏。")
        )

    else:
        if set_mode:
            # pattern_chp = r'^ch\w*\d$'
            # test_chp = re.fullmatch(pattern_chp, user_message)
            if time ==0:
                QuickReply.QReply_Chapter(event,line_bot_api)
            elif time ==1:
                QuickReply.QReply_QuestionNumber(event,line_bot_api)
            else:
                set_mode = False
                test_mode = True
                QuickReply.QReply_AnserButton(event,line_bot_api)
            # if test_chp == False:
            #     line_bot_api.reply_message(
            #     event.reply_token,
            #     TextSendMessage(text="輸入錯誤，請重新輸入")
            # )
            #     QuickReply.QReply_Chapter((event,line_bot_api))
            # else:
            #     QuickReply.QReply_QuestionNumber(event,line_bot_api)
            #     if user_message==10 or user_message==20 or user_message==30:
            #         test_num = int(user_message)
            #         line_bot_api.reply_message(
            #     event.reply_token,
            #     TextSendMessage(text=test_num)
            # )
            #     else:
            #         line_bot_api.reply_message(
            #     event.reply_token,
            #     TextSendMessage(text="輸入錯誤，請重新輸入")
            # )

        # 如果在測試模式中，則每次訊息都顯示 Quick Reply 按鈕
        if test_mode:
            QuickReply.QReply_AnserButton(event,line_bot_api)
        else:
            QuickReply.QReply_Start(event,line_bot_api)
            # 如果不在測試模式中，則只是回覆訊息
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=f"你傳送了：{user_message}")
            )


