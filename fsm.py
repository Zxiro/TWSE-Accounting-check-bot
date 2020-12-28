import datetime as dt
import requests as req
import pandas as pd
import matplotlib.pyplot as plt
from abc import ABC, abstractmethod
from transitions.extensions import GraphMachine
from django.conf import settings
from linebot import LineBotApi, WebhookParser
from linebot.models import MessageEvent, TextSendMessage, TextMessage, FlexSendMessage, ImageSendMessage
from pandas.plotting import table 
from .utils import send_text_message, send_image_url, send_flex_message, search_stock
from .msg_temp import show_pic, main_menu, table, show_team, choose_game_type, return_button, intro, show_score
class TocMachine(GraphMachine):
    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.name = ''
        self.year = ''
        self.game_year = ''
        self.game_month = ''
        self.game_day = ''
    def back_league(self, event):
        text = event.message.text
        print('back_league', text)
        return text.lower() == 'league'

    def back_team_year(self, event):
        text = event.message.text
        print('back_team', text)
        if(text.lower() != 'start'):
            return True

    def back_team(self, event):
        text = event.message.text
        print('back_team', text)
        return text.lower() == 'team'

    def back_start(self, event):
        text = event.message.text
        print('back_start', text)
        return text.lower() == 'start'

    def back_player(self, event):
        text = event.message.text
        print('back_player', text)
        return True

    def back_player_name(self, event):
        text = event.message.text
        print('back_player_name', text)
        return True
    
    def back_player_year(self, event):
        text = event.message.text
        print('back_player_year', text)
        if(text.lower() != 'start'):
            return True

    def going_intro(self, event):
        text = event.message.text
        return text.lower() == 'intro'
    
    def going_test(self, event):
        text = event.message.text
        #send_text_message(event.reply_token, 'test')
        return text.lower() == 'test'

    def on_enter_test(self, event):
        text = event.message.text
        send_text_message(event.reply_token, 'test')
        return text.lower() == 'test'

    def on_enter_intro(self, event):
        send_text_message(event.reply_token, '歡迎使用CPBL - Stat bot! \n 你可以藉由輸入不同指令來獲得資訊 \n 在主選單輸入以下資訊: \n player : 獲取球員資料 \n league : 獲取對戰資料 \n team : 獲取球季資料 \n intro : 再看一次指令集 \n fsm : 獲取有限狀態機圖 \n 輸入start來開始使用!' )
        return event.message.text.lower() == 'intro'
        
    def on_enter_start(self, event):
        reply_token = event.reply_token
        msg = main_menu()
        msg_to_rep = FlexSendMessage('開啟主選單', msg)
        send_flex_message(reply_token, msg_to_rep)
        return True

    def going_fsm(self, event):
        text = event.message.text
        print('going_fsm', text)
        return text.lower() == 'fsm'

    def on_enter_fsm(self, event):
        reply_token = event.reply_token
        msg = show_pic()
        msg_to_rep = FlexSendMessage('fsm', msg)
        send_image_url(reply_token, msg_to_rep)
        return True
    
    def going_player(self, event):
        text = event.message.text
        print('going_player', text)
        return text.lower() == 'player'or text.lower() == 'change_player' #如果input是 player 就 return True 代表可以進入

    def on_enter_player(self, event): #Input the player name
        send_text_message(event.reply_token, '請輸入球員名稱')
        self.name = ''
        return True

    def going_player_name(self, event):
        text = event.message.text
        print('going_player_name', text)
        if(self.name == ''):
            return True
        if(self.name != '' and self.year == ''):
            return text.lower() == 'change_year'

    def on_enter_player_name(self, event): #Input the player name
        text = event.message.text
        print('name: ', text)
        if(self.name != ''):
            send_text_message(event.reply_token, '請輸入球季年份')
            return True
        name = search_player(text)
        if(type(name)== int):
            send_text_message(event.reply_token, '查無此人, 請輸入正確名稱!')
        else:
            self.name = text
            send_text_message(event.reply_token, '請輸入球季年份')
            return True

    def going_player_year(self, event):
        text = event.message.text
        print('going_player_year', text)
        if(self.name != '' and self.year == ''):
            return True

    def on_enter_player_year(self, event): #Input the player name
        name = self.name
        year = event.message.text
        if(year.isdigit() == False or len(year)<4 ):
            send_text_message(event.reply_token, '年份錯誤, 請重新輸入!')
            return True
        else:
            ddd = (name, year) 
            print(ddd)
            stat_ = get_player_stat(name, year)
            message = table()
            out_box = {
                "type":"box",
                "layout": "horizontal",
                "margin": "md",
                "spacing": "sm",
                "contents": [],
                "flex" : 1
            }
            box = {
                "type": "box",
                "layout": "vertical",
                "margin": "sm",
                "contents": [],
                "flex" : 1
            }
            for col in range(1, len(stat_.columns)):
                data = {
                    "type": "text",
                    "text": stat_.columns[col],
                    "size": "md",
                    "color": "#555555",
                    "flex" : 1
                }
                box['contents'].append(data)
            out_box['contents'].append(box)
            for i in range(len(stat_.index)): # Iter row number time
                tmp_list = stat_.loc[i].tolist()
                box = {
                "type": "box",
                "layout": "vertical",
                "margin": "sm",
                "spacing": "sm",
                "contents": [],
                "flex" : 1
                }
                for j in range(1, len(tmp_list)):
                    data = {
                        "type": "text",
                        "text": tmp_list[j],
                        "size": "md",
                        "color": "#111111",
                        "flex" : 1
                    }
                    box['contents'].append(data)
                out_box['contents'].append(box)
            message["body"]["contents"][2]["contents"].append(out_box)
            msg_to_rep = FlexSendMessage(self.name + "數據", message)
            self.year = ''
            send_flex_message(event.reply_token, msg_to_rep)
            
    def going_team(self, event):
        text = event.message.text
        print('enter_team', text)
        return text.lower() =='team'

    def on_enter_team(self, event): #Choose which year's stat
        send_text_message(event.reply_token, '請輸入球季年份')

    def going_team_year(self, event):
        text = event.message.text
        print('going_team_year', text)
        return True

    def on_enter_team_year(self, event): #Show team stat
        text = event.message.text
        print('enter_team_year', text)
        stat_ = get_team_stat(text) #Imgur Link
        if(type(stat_)==int and stat_ == 1):
            send_text_message(event.reply_token, '請輸入正確年份')
            return True
        if(type(stat_)==int and stat_ == 2):
            send_text_message(event.reply_token, '查無資料, 請重新輸入!')
            return True
        else:
            stat_.drop(['RKS', 'PCT', 'GB', 'HOME', 'AWAY'], inplace = True,  axis=1)
            print(stat_)
            message = show_team()
            data_ = {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": []
                }
            for i in range(0, len(stat_.columns)):
                print('col', stat_.columns[i])
                text = {
                  "type": "text",
                  "text": stat_.columns[i],
                  "size": "sm",
                  'margin':'sm',
                  "color": "#555555",
                  "flex": 1,
                }
                data_['contents'].append(text)
            print("_", data_)
            message["body"]["contents"][2]["contents"].append(data_)
            for i in range(len(stat_.columns)-3):
                tmp_list = stat_.loc[i].tolist()
                #print(tmp_list)
                data = {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": []
                }
                for j in range(len(tmp_list)):
                    #print(tmp_list[j])
                    detail_data = {
                        "type": "text",
                        "text": tmp_list[j],
                        "size": "sm",
                        "color": "#555555",
                        "flex": 1,
                        "margin": "md"
                    } 
                    data['contents'].append(detail_data)
                message["body"]["contents"][4]["contents"].append(data)
            msg_to_rep = FlexSendMessage("球隊戰績", message)
            send_flex_message(event.reply_token, msg_to_rep)

    def going_league(self, event):
        text = event.message.text
        print('enter_league', text)
        return text.lower() == 'league' 

    def on_enter_league(self, event): #
        message = choose_game_type()
        msg_to_rep = FlexSendMessage("戰績選擇", message)
        send_flex_message(event.reply_token, msg_to_rep)    
    
    def going_league_ordinary(self, event):
        text = event.message.text
        print('going_ordinary', text)
        return text.lower() == 'league_ordinary'

    def on_enter_league_ordinary(self, event):
        text = event.message.text
        print('enter_ordinary', text)
        send_text_message(event.reply_token, '請輸入年份')
    
    def going_league_year(self, event):
        text = event.message.text
        print('going_year', text)
        return True

    def back_league_year(self, event):
        text = event.message.text
        print('back_year')
        if(self.game_year == ''):
            return True  #Depend on the line input

    def on_enter_league_year(self, event):
        text = event.message.text
        print('enter_year', text)
        self.game_year = text
        if(self.game_year.isdigit() == False or len(self.game_year) != 4):
            send_text_message(event.reply_token, '請重新輸入年份')
            self.game_year = ''
        else:
            send_text_message(event.reply_token, '請輸入月份')
            return True
    
    def going_league_month(self, event):
        text = event.message.text
        print('going_month', text)
        if (self.game_year != ''):
            return True
        
    def back_league_month(self, event):
        print('back_month')
        if(self.game_month == ''):
            return True   

    def on_enter_league_month(self, event):
        text = event.message.text
        print('enter_month', text)
        self.game_month = text
        if(self.game_month.isdigit() == False or int(self.game_month) > 12 or int(self.game_month) < 1):
            send_text_message(event.reply_token, '請重新輸入月份')
            self.game_month = ''
        else:
            send_text_message(event.reply_token, '請輸入日期')
            return True
        
    def going_league_day(self, event):
        text = event.message.text
        print('going_day', text)
        if(self.game_month != ''):
            return True

    def back_league_day(self, event):
        print('back_day')
        if(event.message.text == 'start'):
            return False
        if(self.game_day == ''):
            return True    

    def on_enter_league_day(self, event):
        text = event.message.text
        print('enter_day', text)
        self.game_day = text
        if(self.game_day.isdigit() == False or int(self.game_day) > 31 or int(self.game_day) < 1):
            send_text_message(event.reply_token, '請重新輸入日期')
            self.game_day = ''
        else:
            stat = get_game_stat(self.game_year, self.game_month, self.game_day)
            if(type(stat)==int):
                print('None')
                #send_text_message(event.reply_token, '此日期無比賽, 請重新輸入!')
                message = return_button()
                msg_to_rep = FlexSendMessage("結果", message)
                send_flex_message(event.reply_token, msg_to_rep)
                self.game_year =''
                self.game_month = ''
                self.game_day = ''
                return True
            else:
                message = show_score()
                out_box = {
                    'type':'box',
                    "layout": "vertical",
                    'contents':[
                    ]
                }
                for i in range(len(stat['t1'])):
                    for k in range(2):
                        in_box = {
                        'type':'box',
                        "layout": "horizontal",
                        'contents':[
                        ]
                        }
                        if(k==0):
                            if(stat['t1'][i] == ''):
                                stat['t1'][i] = 'NaN'
                            text = {
                                "type": "text",
                                "text": stat['t1'][i],
                                "align": "center",
                                "weight": "bold",
                                "size": "md",
                                "color": "#555555",
                                "flex" : 1
                            }
                            in_box['contents'].append(text)
                            if(stat['t2'][i] == ''):
                                stat['t2'][i] = 'NaN'
                            text = {
                                "type": "text",
                                "text": stat['t2'][i],
                                "align": "center",
                                "weight": "bold",
                                "size": "md",
                                "color": "#555555",
                                "flex" : 1
                            }
                            in_box['contents'].append(text)
                        if(k==1):
                            if(stat['t1_s'][i] == ''):
                                stat['t1_s'][i] = 'NaN'
                            text = {
                                "type": "text",
                                "text": stat['t1_s'][i],
                                "align": "center",
                                "size": "xl",
                                "color": "#111111",
                                "flex" : 1
                            }
                            in_box['contents'].append(text)
                            if(stat['t2_s'][i] == ''):
                                stat['t2_s'][i] = 'NaN'
                            text = {
                                "type": "text",
                                "text": stat['t2_s'][i],
                                "align": "center",
                                "size": "xl",
                                "color": "#111111",
                                "flex" : 1
                            }
                            in_box['contents'].append(text)
                        out_box['contents'].append(in_box)
                message['body']['contents'][2]['contents'].append(out_box)
                msg_to_rep = FlexSendMessage("結果", message)
                send_flex_message(event.reply_token, msg_to_rep)
                return True
                
                
    def going_league_yt(self, event):
        text = event.message.text
        print('enter_yt', text)
        return text.lower() == 'league_yt'
    
    def on_enter_league_yt(self, event):
        message = intro()
        msg_to_rep = FlexSendMessage("回覆", message)
        send_flex_message(event.reply_token, msg_to_rep)
        return text.lower() == 'league_yt'
    
    