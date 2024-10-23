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

test_mode = False  # 控制是否處於測試模式
current_state = "default"  # 控制當前狀態，可能的狀態包括 "default", "choose_section", "choose_question_count", "testing"
selected_section = None  # 用於儲存選擇的章節
selected_question_count = None  # 用於儲存選擇的題數

# 處理訊息的事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 定義一個全域變數來追蹤測試狀態
    global test_mode, current_state, selected_section, selected_question_count

    correct_answers = {"Q1": "(A)", "Q2": "(B)", "Q3": "(C)"}  # 假設的正確答案

    user_message = event.message.text

    if user_message == "練習模式" :
        test_mode = True

    if test_mode == False:
        message_text = "請選擇"
        quick_reply_buttons,message_text = QuickReply.QReply_Start()
    
    elif test_mode == True :     
        # 測試模式
        if current_state == "default":
            quick_reply_buttons,message_text,current_state = QuickReply.QReply_Chapter()
        
        elif current_state == "choose_section" :
            # 等待選擇章節，如果用戶已經選擇章節，進入下一步
            if user_message in ["Ch1", "Ch2", "Ch3", "Ch4", "期中複習"]:
                selected_section = user_message
                quick_reply_buttons,message_text,current_state = QuickReply.QReply_QuestionNumber()
        
        elif current_state == "choose_question_count" :
            # 等待選擇題數
            if user_message in ["10", "20", "30"]:
                selected_question_count = int(user_message)
                quick_reply_buttons,message_text,current_state = QuickReply.QReply_AnserButton()
        
        elif current_state == "testing":
            # 測試進行中，等待用戶選擇 ABCD
            for i in range (1,4):
                quick_reply_buttons,message_text,current_state = QuickReply.QReply_AnserButton()
                correct_answer = correct_answers.get("Q"+str(i+1))  # 假設是第 1 題的正確答案
                if user_message in ["(A)", "(B)", "(C)", "(D)"]:
                    if user_message == correct_answer:
                        message_text = "回答正確！"
                    else:
                        message_text = "答案為"+correct_answer

        elif user_message == "測試結束":
            test_mode = False
            current_state = "default"
            selected_section = None
            selected_question_count = None
            # 發送退出測試的訊息
            message_text = "你已退出測試模式。"
    
        else:
            message_text = "請重新輸入"

    # 發送帶有 QuickReply 按鈕的訊息
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=message_text, quick_reply=quick_reply_buttons)
    )
# [測試]QR2