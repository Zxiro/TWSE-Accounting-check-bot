import os
import pyimgur
import scrapy
import time
import datetime as dt
import matplotlib.pyplot as plt
import requests as req
import pandas as pd
import dataframe_image as dfi
from bs4 import BeautifulSoup
from django.conf import settings
from pandas.plotting import table 
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextMessage, TextSendMessage


channel_access_token = settings.LINE_CHANNEL_ACCESS_TOKEN


def search_stock(s_type, index):
    if(s_type == 0):
        res = req.get(
            'https://www.tej.com.tw/webtej/doc/uid.htm'
        )
        res.encoding = 'big5'
        soup = BeautifulSoup(res.text, 'html.parser')
        soup.encode('UTF-8')
        stock_list = soup.find_all('font')
        for s in stock_list:
            if(index in s.text):
                stock_name = s.text[:5]
                stock_name = stock_name.replace(" ", "")
                return stock_name
        if (stock_name == ''):
            return '無此公司!'
        return stock_name
    if(s_type == 1):
        payload = {
                'encodeURIComponent': 1,
                'step': 1,
                'firstin': 1,
                'off': 1,
                'queryName': 'co_id',
                'inpuType': 'co_id',
                'TYPEK': 'all',
                'isnew': 'true',
                'season':"",
                'co_id':index,
        }
        res = req.post('https://mops.twse.com.tw/mops/web/t163sb03', data = payload)
        soup = BeautifulSoup(res.content, 'html.parser')
        txt = soup.find('td', {'style':'text-align:left !important;', 'class':'odd'})
        if(txt is None):
            return "查無此報告"
        else:
            return txt.text
        
        
def send_flex_message(reply_token, msg_to_rep):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, 
        msg_to_rep
    ) 

def send_text_message(reply_token, text):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, 
        TextSendMessage(text = text)
    )
