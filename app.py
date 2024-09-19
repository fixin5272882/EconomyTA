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
    messages_to_reply = []
    user_message = event.message.text
    keywords =  read_json_file("./Json/keyword.json")
    matched_chapter = find_keywords_in_message(keywords, user_message)
    messages_to_reply.append(TextSendMessage(text="章節分類至:"+matched_chapter))

    if matched_chapter != "None":
        chapterPath = "./Json/"+matched_chapter+".json"
        chapterData = read_json_file(chapterPath)
        reply_messages = find_answer_with_similarity(chapterData, user_message, threshold=0.76)
        if reply_messages == "None":
            messages_to_reply.append(TextSendMessage(text="2_抱歉、找不到相關資訊，請先詢問其他問題～後續會再持續更新"))
        else:
            messages_to_reply.append(TextSendMessage(text="相似度:"+reply_messages[0][0]))
            for message in reply_messages[0][2]:
                if determine_content_type(message) == "Image":
                    messages_to_reply.append(ImageSendMessage(original_content_url=message, preview_image_url=message))
                else:
                    messages_to_reply.append(TextSendMessage(text=message))
    else:
        messages_to_reply.append(TextSendMessage(text="1_抱歉、找不到相關資訊，請先詢問其他問題～後續會再持續更新"))
    
    # 一次性回覆所有訊息
    if messages_to_reply:
        line_bot_api.reply_message(event.reply_token, messages_to_reply)

# 定義一個函數來讀取JSON文件
def read_json_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 檢查關鍵字是否存在於目標字串中的函數
def keyword_in_message(target_message, keyword):
    return keyword in target_message

# 多執行緒搜尋關鍵字是否存在於字串
def find_keywords_in_message(chapters, target_message):
    results = "None"
    # 定義執行緒池
    with ThreadPoolExecutor() as executor:
        # 提交每個關鍵字的存在檢查任務到執行緒池
        future_to_chapter = {
            executor.submit(keyword_in_message, target_message, keyword): (chapter, keyword)
            for chapter, keywords in chapters.items()
            for keyword in keywords
        }

        # 收集結果
        for future in as_completed(future_to_chapter):
            best_similarity = 0
            chapter, keyword = future_to_chapter[future]
            exists = future.result()  # 結果為 True 或 False

            # 如果關鍵字存在於目標訊息中，則將其添加到結果中
            if exists:
                similarity = calculate_similarity(target_message,keyword)
                if similarity > best_similarity:
                    results = chapter

    return results

# 定義函數來計算兩個字串之間的相似度
def calculate_similarity(str1, str2):
    return difflib.SequenceMatcher(None, str1, str2).ratio()

# 檢查目標訊息是否與關鍵字足夠相似的函數
def similar_keyword_in_message(target_message, keywords, threshold):
    for keyword in keywords:
        similarity = calculate_similarity(target_message, keyword)
        if similarity >= threshold:  # 如果相似度高於閾值，則返回該關鍵字
            return keyword, similarity
    return None, 0  # 如果沒有找到足夠相似的關鍵字，返回 None 和相似度 0

# 多執行緒搜尋並返回對應的 answer 回傳 (相似度, 關鍵字, 答案)
def find_answer_with_similarity(entries, target_message, threshold):
    results = []

    # 定義執行緒池
    with ThreadPoolExecutor() as executor:
        # 提交每個條目的關鍵詞檢查任務到執行緒池
        future_to_entry = {
            executor.submit(similar_keyword_in_message, target_message, entry["keyword"], threshold): entry
            for entry in entries
        }

        # 收集結果
        for future in as_completed(future_to_entry):
            entry = future_to_entry[future]
            found_keyword, similarity = future.result()  # 結果為找到的相似詞和相似度

            # 如果有找到相似詞，則將其對應的 answer 添加到結果中
            if found_keyword:
                results.append((similarity, found_keyword, entry["answer"]))

        if results == []: return "None"
        else : results = sorted(results, key=lambda x: x[0], reverse=True)
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