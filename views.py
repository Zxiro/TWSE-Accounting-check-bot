import requests
import logging
from bs4 import BeautifulSoup
from django.shortcuts import render
from django.http.request import HttpRequest
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from sendfile import sendfile
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextSendMessage, TextMessage
from .fsm import TocMachine

# Create your views here.
logging.basicConfig(level=logging.DEBUG)
line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

def index(req):
    return HttpResponse('My first line bot app build on Django')
machine = {}

@csrf_exempt
def callback(req : HttpRequest):

    if req.method =='POST':#data in the msg-body
        signature = req.META['HTTP_X_LINE_SIGNATURE']
        body = req.body.decode('utf-8')
        try:
            events = parser.parse(body, signature) #The event get by the HTTP method POST
            #print(events)
        except InvaildSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()
        
        for event in events:
            if event.source.user_id not in machine:
                machine[event.source.user_id] = TocMachine(
                    states = ['start','all_stock', 'single_stock'], 
                    transitions =[
                        { #options and fsm go back to start
                            "trigger" : "advance",
                            "source" : "start",
                            "dest" : "all_stock",
                            "conditions" : "going_all"
                        },
                        { #options and fsm go back to start
                            "trigger" : "advance",
                            "source" : "start",
                            "dest" : "single_stock",
                            "conditions" : "going_single"
                        },
                        { #options and fsm go back to start
                            "trigger" : "advance",
                            "source" : "single_stock",
                            "dest" : "single_stock",
                            "conditions" : "back_single"
                        },
                        { #options and fsm go back to start
                            "trigger" : "advance",
                            "source" : "all_stock",
                            "dest" : "all_stock",
                            "conditions" : "back_all"
                        },
                        { #options and fsm go back to start
                            "trigger" : "advance",
                            "source" : ["start", "all_stock", "single_stock"],
                            "dest" : "start",
                            "conditions" : "back_start"
                        },
                    ],
                    initial="start", #init needs to be start can use this para to debug
                    auto_transitions = False,
                    show_conditions = True,
                )
            machine[event.source.user_id].get_graph().draw("fsm.png", prog="dot", format="png")
            #Wait for the input
            if not isinstance(event, MessageEvent):
                continue
            if not isinstance(event.message, TextMessage):
                continue
            if not isinstance(event.message.text, str):
                continue
            response = machine[event.source.user_id].advance(event)
            if response == False:
                line_bot_api.reply_message(  # 回復傳入的訊息文字
                    event.reply_token,
                    TextSendMessage(text= "Invalid command, try again")
                )
            #machine.get_graph().draw("fsm.png", prog="dot", format="png")
        return HttpResponse()
    else:
        return HttpResponseBadRequest()