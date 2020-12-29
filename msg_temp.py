def choose_game_type():
  game_type = {
      "type": "bubble",
      "body":{
      "type":"box",
      "layout": "vertical",
      "contents": [
        {
          "type": "button",
          "action": {
            "type": "message",
            "label": "查詢查核意見",
            "text": "going_single"
          },
          "height": "md",
          "color": "#00cc66",
          "style": "primary"
        },
        {
          "type": "button",
          "action": {
            "type": "message",
            "label": "查詢股號",
            "text": "going_all"
          },
          "height": "md",
          "color": "#00cc66",
          "style": "primary"
        }
      ],
      "spacing": "lg"
      }
  }
  return game_type

def choose_stock_type():
  game_type = {
      "type": "bubble",
      "body":{
      "type":"box",
      "layout": "vertical",
      "contents": [
      ],
      "spacing": "lg"
      }
  }
  return game_type


