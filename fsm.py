import requests as req
import pandas as pd
from transitions.extensions import GraphMachine
from django.conf import settings
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextSendMessage, TextMessage, FlexSendMessage, ImageSendMessage
from pandas.plotting import table 
from .utils import send_text_message, send_flex_message, search_stock
from .msg_temp import choose_game_type, choose_stock_type
class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
    def back_start(self, event):
        text = event.message.text
        print('back_start', text)
        return text.lower() == 'start'
    
    def back_single(self, event):
        text = event.message.text
        print('back_start', text)
        if(text.lower() != 'start'):
            return True

    def back_all(self, event):
        text = event.message.text
        print('back_all', text)
        if(text.lower() != 'start'):
            return True

    def going_all(self, event):
        text = event.message.text
        return text.lower() == 'going_all'
    
    def going_single(self, event):
        text = event.message.text
        return text.lower() == 'going_single'

    def on_enter_all_stock(self, event):
        text = event.message.text
        if(text == 'going_all'):
            send_text_message(event.reply_token, '請輸入公司名')
            return True
        if (text.isdigit()==True):
            send_text_message(event.reply_token, '請輸入正確公司名')
            return True
        if (text.isdigit()==False):
            stat = search_stock(0, text)
            but = [
                 {
                "type":"text",
                "text": stat, 
                "size":'lg',
                'margin':'sm',
            },
            {
            "type": "button",
            "action": {
                "type": "message",
                "label": "查詢其他公司",
                "text": "going_all"
            },
            "height": "sm",
            "color": "#00cc66",
            "style": "primary"
            },
            {
            "type": "button",
            "action": {
                "type": "message",
                "label": "返回首頁",
                "text": "start"
            },
            "height": "sm",
            "color": "#00cc66",
            "style": "primary"
            }
            ]
            ret = choose_stock_type()
            for i in range(len(but)):
                ret['body']['contents'].append(but[i])
            msg_to_rep = FlexSendMessage('test', ret)
            send_flex_message(event.reply_token, msg_to_rep)
            return True
            return True
        return text.lower() == 'test'

    def on_enter_single_stock(self, event):
        print('enter_single')
        text = event.message.text
        if(text == 'going_single'):
            send_text_message(event.reply_token, '請輸入股票代碼')
            return True
        if (text.isdigit()==False):
            send_text_message(event.reply_token, '請輸入數字!')
            return True
        if (text.isdigit()==True):
            stat = search_stock(1, text)
            #send_text_message(event.reply_token, stat)
            but = [
                 {
                "type":"text",
                "text": stat, 
                "size":'lg',
                'margin':'sm',
            },
            {
            "type": "button",
            "action": {
                "type": "message",
                "label": "查詢其他股票",
                "text": "going_single"
            },
            "height": "sm",
            "color": "#00cc66",
            "style": "primary"
            },
            {
            "type": "button",
            "action": {
                "type": "message",
                "label": "返回首頁",
                "text": "start"
            },
            "height": "sm",
            "color": "#00cc66",
            "style": "primary"
            }
            ]
            ret = choose_stock_type()
            for i in range(len(but)):
                ret['body']['contents'].append(but[i])
            msg_to_rep = FlexSendMessage('test', ret)
            send_flex_message(event.reply_token, msg_to_rep)
            return True
            

    def on_enter_start(self, event):
        reply_token = event.reply_token
        msg = choose_game_type()
        msg_to_rep = FlexSendMessage('開啟主選單', msg)
        send_flex_message(reply_token, msg_to_rep)
        return True