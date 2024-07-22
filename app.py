from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
import json
import requests

app = Flask(__name__)

line_bot_api = LineBotApi('e0K5L5PfmBqS8cm4eZgTn4PWPGZz2mc97S8EwyPrJux4gpZcmfh6az83GAs4C04gzDI2Pc7xN6MjBysyMVZhsuZVjapY2ZBThddu6rbe4kbr/A58nW8vREVdtau2wjYIRgLYnCRxgsdgZnyS02unmgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('db3f5b159f43eb5f1526c1b43f835722')

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
    # 讀取三個JSON文件
    file_paths = ['./Json/Ch1.json', './Json/Ch2.json', './Json/Ch3.json', './Json/Ch4.json', './Json/Ch5.json'
                  , './Json/Ch6.json', './Json/Ch7.json', './Json/Ch8.json', './Json/Ch9.json', './Json/Ch10.json'
                  , './Json/Ch11.json', './Json/Ch12.json', './Json/Ch13.json', './Json/Ch14.json', './Json/Ch15.json'
                  , './Json/Ch16.json', './Json/Ch17.json', './Json/Ch18.json', './Json/Ch19.json', './Json/Ch20.json'
                  , './Json/Ch21.json', './Json/Ch22.json', './Json/Ch23.json', './Json/Ch24.json', 
                  , './Json/Other.json', './Json/OtherData.json']
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

# 定義一個函數來搜尋關鍵詞並提取 'answer' 中的資料
def search_and_extract_anser(data, message):
    results = []
    for item in data:
        for item_key in item['keyword']:
            if item_key in message:
                results.extend(item['answer'])

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