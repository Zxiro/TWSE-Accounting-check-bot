import os
import pyimgur
import scrapy
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


def search_stock(name):
    res = req.get(
        'http://moneydj.emega.com.tw/js/StockTable.htm'
    )
    soup = BeautifulSoup(res.content, 'html.parser')
    stock_list = soup.find_all('td')
    index_list = []
    for s in stock_list:
        num = s.text[:4]
        if(num.isdigit()==True):
            index_list.append(num)
    print(index_list)
    stock_stat = {}
    for co in index_list:
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
            'co_id':int(co),
        }
        res = req.post('https://mops.twse.com.tw/mops/web/t163sb03', data = payload)
        soup = BeautifulSoup(res.content, 'html.parser')
        txt = soup.find('td', {'style':'text-align:left !important;', 'class':'odd'})
        #print(type(txt))
        if(txt is None):
            #print('無查核報告!')
            sleep(0.5)
            continue
        name = soup.find('td', {'class':'compName'})
        print(name.text[4:16], ', ', int(co), ':', txt.text)
        stock_stat[name.text[4:16]] = txt.text
        sleep(0.5)
         

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

def send_image_url(reply_token, msg_to_rep):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.reply_message(reply_token, 
        msg_to_rep
    )

