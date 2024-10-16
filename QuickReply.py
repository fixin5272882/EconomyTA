from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction

def QReply_Start(event,line_bot_api):
    quick_reply_buttons = QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="操作介紹", text="操作介紹")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="練習模式", text="練習模式")
                    )
                ]
            )
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(quick_reply=quick_reply_buttons)
    )

def QReply_Chapter(event,line_bot_api):
    quick_reply_buttons = QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="Ch1", text="Ch1")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="Ch2", text="Ch2")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="Ch3", text="Ch3")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="停止測試", text="測試結束")
                    )
                ]
            )
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="請先選擇想要練習的章節:", quick_reply=quick_reply_buttons)
    )

def QReply_QuestionNumber(event,line_bot_api):
    quick_reply_buttons = QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="10題", text="10")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="20題", text="20")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="30題", text="30")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="停止測試", text="測試結束")
                    )
                ]
            )
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="請選擇想要練習題目數量:", quick_reply=quick_reply_buttons)
    )

def QReply_AnserButton(event,line_bot_api):
    quick_reply_buttons = QuickReply(
                items=[
                    QuickReplyButton(
                        action=MessageAction(label="(A)", text="(A)")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="(B)", text="(B)")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="(C)", text="(C)")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="(D)", text="(D)")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="停止測試", text="測試結束")
                    )
                ]
            )
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="請選擇答案:", quick_reply=quick_reply_buttons)
    )