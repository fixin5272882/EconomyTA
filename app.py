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
    # 設定資料夾路徑
    folder_path = './Json/'

    # 讀取資料夾中的所有檔案名稱
    file_names = os.listdir(folder_path)

    # 過濾出檔案名稱（排除子資料夾），並加上完整路徑
    file_paths = [os.path.join(folder_path, f) for f in file_names if os.path.isfile(os.path.join(folder_path, f))]
    print(file_paths)
    
    all_data = []

    for file_path in file_paths:
        all_data.extend(read_json_file(file_path))

    user_message = event.message.text
    reply_messages = search_and_extract_anser(all_data,user_message)
    messages_to_reply = []
    for message in reply_messages:
        if determine_content_type(message) == "Image":
            messages_to_reply.append(ImageSendMessage(original_content_url=message, preview_image_url=message))
        else:
            messages_to_reply.append(TextSendMessage(text=message))
    
    # 一次性回覆所有訊息
    if messages_to_reply:
        line_bot_api.reply_message(event.reply_token, messages_to_reply)

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
            print(item_key,end=': ')
            if item_key in message:
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
        # print(f"Error checking URL: {e}")
        return "Text"

if __name__ == "__main__":
    app.run()