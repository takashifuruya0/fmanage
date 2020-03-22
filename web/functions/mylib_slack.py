from google.cloud import datastore
from django.conf import settings
import requests
from datetime import datetime
from pytz import timezone
from web.models import Entry
import json
import logging
logger = logging.getLogger("django")


def post_message(text):
    url = settings.URL_SLACK_NAMS
    headers = {'Content-Type': 'application/json'}
    params = {"text": text, }
    json_data = json.dumps(params)
    r = requests.post(url, json_data, headers=headers)
    return r.text == "ok"


def post_open_entries():
    url = settings.URL_SLACK_NAMS
    headers = {'Content-Type': 'application/json'}
    # entries
    entries = Entry.objects.filter(is_closed=False, stock__is_trust=False)
    for e in entries:
        try:
            # params設定
            params = {
                "channel": "#asset_management",
                "username": "fk-management.com",
                "text": "last updated at {}".format(datetime.now(timezone('Asia/Tokyo')).ctime()),
                "attachments": [],
            }
            # 買付価格と現在価格、利益等の情報も送信
            title = "【{}】{}".format(e.stock.code, e.stock.name)
            text = "保有数: {}\n 現在値: {:,}".format(e.remaining(), e.stock.current_val())
            profit = e.profit()
            if profit > 0:
                text += "\n利益: +{:,}".format(profit)
            else:
                text += "\n損失: {:,}".format(profit)
            # color
            if e.is_plan:
                color = "#ffff00;"
            else:
                color = "#ff9960" if profit < 0 else "good"
            # attachment追加
            button = {
                "short": True,
                "fallback": "fallback string",
                "callback_id": "callback_id value",
                "title": title,
                "text": text,
                "color": color,
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "order",
                        "text": "成行注文",
                        "type": "button",
                        "style": "primary",
                        "value": e.stock.code,
                        "confirm": {
                            "title": "成行注文を実行します。よろしいですか？",
                            "text": "{}_{}".format(title, text),
                            "ok_text": "Order",
                            "dismiss_text": "Cancel"
                        },
                    },
                    {
                        "name": "current_price",
                        "text": "現在値取得",
                        "type": "button",
                        "style": "default",
                        "value": e.stock.code,
                    },
                ]
            }
            params['attachments'].append(button)
            # json
            json_data = json.dumps(params)
            requests.post(url, json_data, headers=headers)
        except Exception as ee:
            logger.error("Failed to post for {}".format(e))
            logger.error(ee)