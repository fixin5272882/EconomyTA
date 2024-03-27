from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

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
    user_message = event.message.text
    reply_message = generate_reply(user_message)
    # reply_message = user_message
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))

def generate_reply(message):
    # 在这里根据关键字生成回复消息的逻辑
    if '教室' in message:
        return '教室在123'
    elif '考試' in message:
        return '考試123'
    else:
        return '默认回复内容'

if __name__ == "__main__":
    app.run()