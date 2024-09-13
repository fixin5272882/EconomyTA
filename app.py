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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    data = read_json_file('./Json/keyword.json')
    user_message = event.message.text
    all_data = []
    related_chapters = find_related_chapters(user_message, data)
    messages_to_reply = []

    if related_chapters == "抱歉、找不到相關資訊，請換種方式詢問":
        messages_to_reply = related_chapters
    else :
        related_chapters = "./Json/"+related_chapters+".json"
        messages_to_reply.append(related_chapters)
        all_data.extend(read_json_file(related_chapters))
        reply_messages = search_and_extract_anser(all_data,user_message)

        for message in reply_messages:
            if determine_content_type(message) == "Image":
                messages_to_reply.append(ImageSendMessage(original_content_url=message, preview_image_url=message))
            else:
                messages_to_reply.append(TextSendMessage(text=message))
    
    # 一次性回覆所有訊息
    if messages_to_reply:
        line_bot_api.reply_message(event.reply_token, messages_to_reply)

# 搜尋內容在哪章節
def find_related_chapters(message, data):
    related_chapters = set()  # 使用 set 來避免重複
    for chapter, keywords in data.items():
        for keyword in keywords:
            if keyword in message:  # 檢查 message 是否包含關鍵字
                related_chapters.add(chapter)  # 加入相關章節名稱
    if related_chapters==set():
        related_chapters = ["抱歉、找不到相關資訊，請換種方式詢問"]
    return list(related_chapters)[0]

# 定義一個函數來讀取JSON文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 定義一個函數來搜尋最接近的關鍵詞並提取 'answer' 中的資料
def search_and_extract_anser(data, message):
    results = []
    Best_similarity = 0
    for item in data:
        for item_key in item['keyword']:
            similarity = difflib.SequenceMatcher(None, item_key, message).ratio()
            if similarity>Best_similarity:
                Best_similarity=similarity
                results=item['answer']
                    
    return results

def determine_content_type(url):
    try:
        # 發送HEAD請求獲取響應頭部
        response = requests.head(url, allow_redirects=True)
        # 獲取Content-Type
        content_type = response.headers.get('content-type')
        
        if content_type:
            # 判斷是否是圖片類型
            if content_type.startswith('image/'):
                return "Image"
            # 判斷是否是文字類型
            elif content_type.startswith('text/'):
                return "Text"
        
    except requests.RequestException as e:
        return "ERROR"

if __name__ == "__main__":
    app.run()