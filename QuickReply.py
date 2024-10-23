from linebot.models import TextSendMessage, QuickReply, QuickReplyButton, MessageAction

def QReply_Start():
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
    return quick_reply_buttons

def QReply_Chapter():
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
                        action=MessageAction(label="Ch4", text="Ch4")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="期中(ch1-ch4)", text="期中複習")
                    ),
                    QuickReplyButton(
                        action=MessageAction(label="停止測試", text="測試結束")
                    )
                ]
            )
    message_text = "請先選擇想要練習的章節："
    current_state = "choose_section"
    return quick_reply_buttons,message_text,current_state

def QReply_QuestionNumber():
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
    message_text = "請先選擇想要練習的題數："
    current_state = "choose_question_count"
    return quick_reply_buttons,message_text,current_state

def QReply_AnserButton():
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
    message_text = "請選擇答案:"
    current_state = "testing"
    return quick_reply_buttons,message_text,current_state
