from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
import json, os
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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    messages_to_reply = []
    user_message = event.message.text
    keywords =  read_json_file("./Json/keyword.json")
    matched_chapter = RM.find_keywords_in_message(keywords, user_message)
    worksheet = Gsheet.connect_google_sheets().sheet1

    if matched_chapter != "None":
        chapterPath = "./Json/"+matched_chapter+".json"
        chapterData = read_json_file(chapterPath)
        reply_messages = RM.find_answer_with_similarity(chapterData, user_message, threshold=0.5)
        if reply_messages == "None":
            Gsheet.add_question_insheet(line_bot_api,event,matched_chapter,user_message,worksheet)
            messages_to_reply.append(TextSendMessage(text="抱歉、找不到相關資訊，請換種方式詢問或問其他問題～後續會再持續更新"))
        else:
            for message in reply_messages[0][2]:
                if RM.determine_content_type(message) == "Image":
                    messages_to_reply.append(ImageSendMessage(original_content_url=message, preview_image_url=message))
                else:
                    messages_to_reply.append(TextSendMessage(text=message))
    else:
        Gsheet.add_question_insheet(line_bot_api,event,matched_chapter,user_message,worksheet)
        messages_to_reply.append(TextSendMessage(text="抱歉、找不到相關資訊，請換種方式詢問或問其他問題～後續會再持續更新"))
    
    # 一次性回覆所有訊息
    if messages_to_reply:
        line_bot_api.reply_message(event.reply_token, messages_to_reply)

# 定義一個函數來讀取JSON文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)
