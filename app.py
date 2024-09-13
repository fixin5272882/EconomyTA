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

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    chapters =  read_json_file("./Json/keyword.json")
    similar_chapterPath = "./Json/"+similarity_chapter(chapters, user_message)+".json"
    all_data = read_json_file(similar_chapterPath)
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

# 多執行緒的比對函數
def find_similarities_across_chapters(chapters, target_message):
    similarities = []

    # 定義執行緒池
    with ThreadPoolExecutor() as executor:
        # 將每個章節及關鍵字的相似度計算任務提交到執行緒池
        future_to_chapter = {
            executor.submit(calculate_string_similarity, target_message, keyword): (chapter, keyword)
            for chapter, keywords in chapters.items()
            for keyword in keywords
        }

        # 收集結果
        for future in as_completed(future_to_chapter):
            chapter, keyword = future_to_chapter[future]
            similarity = future.result()
            similarities.append((chapter, keyword, similarity))

    # 根據相似度排序，從高到低
    similarities.sort(key=lambda x: x[2], reverse=True)

    return similarities

# 獲得最相近的關鍵字
def similarity_chapter(keywordData, target_message):
    similarity_results = find_similarities_across_chapters(keywordData, target_message)

    if not similarity_results or similarity_results[0][2] < 0.5:
        return "抱歉、找不到相關資訊，請換種方式詢問"
    else:
        for chapter, keyword, similarity in similarity_results[:1]:  # 顯示前三名
            return chapter

# 定義函數來計算兩個字串之間的相似度
def calculate_string_similarity(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).ratio()

# 定義一個函數來搜尋最接近的關鍵詞並提取 'answer' 中的資料
def search_and_extract_anser(data, message):
    results = []
    Best_similarity = 0
    for item in data:
        for item_key in item['keyword']:
            similarity = calculate_string_similarity(item_key, message)
            if similarity>Best_similarity:
                Best_similarity=similarity
                results=item['answer']
                    
    return results

#判斷回應問題的類型
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
        return e

if __name__ == "__main__":
    app.run()