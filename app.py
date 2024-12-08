from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage, QuickReply, QuickReplyButton, MessageAction
from linebot.exceptions import InvalidSignatureError
import os,json
import QuickReply as QR
import CRU_googlesheet as Gsheet
import ReplyMessage as RM

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

user_mode = {}
user_TNum = {}

# 處理訊息的事件
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id  # 用戶的ID
    user_message = event.message.text  # 用戶發送的訊息
    reply_token = event.reply_token
    messages_to_reply = []
    # 檢查用戶是否有測試模式狀態
    if user_id not in user_mode:
        user_mode[user_id] = '問答模式'  # 初始為問答模式
    
    current_mode = user_mode[user_id]
    
    if user_message == "開始測試" or any(keyword in user_message for keyword in ["題目練習", "練習題目", "練習題"]):
        global questions
        questions = Gsheet.read_question()
        user_mode[user_id] = '測試模式'
        user_TNum[user_id] = int(0)
        print(questions[0]['題目'])
        messages_to_reply.append(TextSendMessage(text=f"歡迎！此為期末範圍題目\n第 1 題：\n{str(questions[0]['題目'])}"))
        if questions[0]['題目圖片']:
            messages_to_reply.append(ImageSendMessage(original_content_url=str(questions[0]['題目圖片']), preview_image_url=str(questions[0]['題目圖片'])))
        quick_reply_buttons = QR.QReply_AnserButton()
        messages_to_reply[-1].quick_reply = quick_reply_buttons
        line_bot_api.reply_message(reply_token, messages_to_reply)
        
    # 如果處於測試模式
    if current_mode == '測試模式':
        if user_message == '結束測試':
            user_mode[user_id] = '問答模式'  # 退出測試模式
            quick_reply_buttons = QR.QReply_Start()
            line_bot_api.reply_message(
                        reply_token,
                        TextSendMessage(text="已結束測試模式，回到問答模式。", quick_reply=quick_reply_buttons)
                    )
            return
        else:
            if user_message in ['A','B','C','D']:
                if user_message == questions[user_TNum[user_id]]['答案是']:
                    messages_to_reply.append(TextSendMessage(text="答對了!"))
                else:
                    messages_to_reply.append(TextSendMessage(text=f"答錯了!答案是{questions[user_TNum[user_id]]['答案是']}"))
                    for i in range(1,3):
                        anser = '解答'+str(i)
                        if questions[user_TNum[user_id]][anser]:
                            if RM.determine_content_type(questions[user_TNum[user_id]][anser]) == "Image":
                                messages_to_reply.append(ImageSendMessage(original_content_url=questions[user_TNum[user_id]][anser], preview_image_url=questions[user_TNum[user_id]][anser]))
                            else:
                                messages_to_reply.append(TextSendMessage(text=questions[user_TNum[user_id]][anser]))
                
                if user_TNum[user_id] == len(questions)-1:
                    user_mode[user_id] = '問答模式'  # 退出測試模式
                    messages_to_reply.append(TextSendMessage(text="已完成測試，回到問答模式。"))
                    quick_reply_buttons = QR.QReply_Start()
                    messages_to_reply[-1].quick_reply = quick_reply_buttons
                    line_bot_api.reply_message(reply_token, messages_to_reply)
                    return
                else:
                    user_TNum[user_id] +=1
                    messages_to_reply.append(TextSendMessage(text=f"第 {user_TNum[user_id]+1} 題：\n{questions[user_TNum[user_id]]['題目']}"))
                    if questions[user_TNum[user_id]]['題目圖片']:
                        messages_to_reply.append(ImageSendMessage(original_content_url=questions[user_TNum[user_id]]['題目圖片'], preview_image_url=questions[user_TNum[user_id]]['題目圖片']))
            else:
                messages_to_reply.append(TextSendMessage(text=f"請回答第{user_TNum[user_id]+1}題的答案，或是輸入'結束測試'離開測試模式"))
        
            quick_reply_buttons = QR.QReply_AnserButton()
            messages_to_reply[-1].quick_reply = quick_reply_buttons
            line_bot_api.reply_message(reply_token, messages_to_reply)
    else:
        keywords =  read_json_file("./Json/keyword.json")
        matched_chapter = RM.find_keywords_in_message(keywords, user_message)
        cnatreply_sheet = Gsheet.connect_google_sheets(os.getenv('QSHEET_URL')).sheet1
        if matched_chapter != "None":
            chapterPath = "./Json/"+matched_chapter+".json"
            chapterData = read_json_file(chapterPath)
            reply_messages = RM.find_answer_with_similarity(chapterData, user_message, threshold=0.5)
            if reply_messages == "None":
                Gsheet.add_question_insheet(line_bot_api,event,matched_chapter,user_message,cnatreply_sheet)
                messages_to_reply.append(TextSendMessage(text="抱歉、找不到相關資訊，請換種方式詢問或問其他問題～後續會再持續更新"))
            else:
                for message in reply_messages[0][2]:
                    if RM.determine_content_type(message) == "Image":
                        messages_to_reply.append(ImageSendMessage(original_content_url=message, preview_image_url=message))
                    else:
                        messages_to_reply.append(TextSendMessage(text=message))
        else:
            Gsheet.add_question_insheet(line_bot_api,event,matched_chapter,user_message,cnatreply_sheet)
            messages_to_reply.append(TextSendMessage(text="抱歉、找不到相關資訊，請換種方式詢問或問其他問題～後續會再持續更新"))

        quick_reply_buttons = QR.QReply_Start()
        messages_to_reply[-1].quick_reply = quick_reply_buttons
        line_bot_api.reply_message(reply_token, messages_to_reply)
        
# 定義一個函數來讀取JSON文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)