from google.cloud import datastore
from django.conf import settings
from django.urls import reverse
import requests
from datetime import datetime
from pytz import timezone
from web.models import Entry, Ipo
import json
import logging
logger = logging.getLogger("django")


def post_message(text, url=None):
    if url is None:
        url = settings.URL_SLACK_NAMS
    headers = {'Content-Type': 'application/json'}
    params = {"text": text, }
    json_data = json.dumps(params)
    r = requests.post(url, json_data, headers=headers)
    return r.text == "ok"

def post_rich_message(data, url=None):
    if url is None:
        url = settings.URL_SLACK_LOG
    headers = {'Content-Type': 'application/json'}
    json_data = json.dumps(data)
    r = requests.post(url, json_data, headers=headers)
    return r.text == "ok"


def post_open_entries(is_excluding_plan=True):
    url = settings.URL_SLACK_NAMS
    headers = {'Content-Type': 'application/json'}
    # entries
    entries = Entry.objects.filter(is_closed=False, stock__is_trust=False)
    if is_excluding_plan:
        entries = entries.exclude(is_plan=True)
    for e in entries:
        try:
            json_data = json.dumps(param_entry(e))
            requests.post(url, json_data, headers=headers)
        except Exception as ee:
            logger.error("Failed to post for {}".format(e))
            logger.error(ee)


def param_entry(e):
    # params設定
    params = {
        "text": "last updated at {}".format(datetime.now(timezone('Asia/Tokyo')).ctime()),
        "attachments": [],
    }
    # 買付価格と現在価格、利益等の情報も送信
    profit = e.profit()
    current_val = e.stock.current_val()
    remaining = e.remaining()
    date_open = e.date_open()
    title = "【{}】{}".format(e.stock.code, e.stock.name)
    # color
    if e.is_plan:
        color = "#ffff00"
    else:
        color = "#ff9960" if profit < 0 else "good"
    # attachment追加
    button = {
        "short": True,
        "fallback": "fallback string",
        "callback_id": "callback_id value",
        "title": title,
        "text": "https://www.fk-management.com{}".format(reverse('web:entry_detail', kwargs={'pk': e.pk})),
        "fields": [
            {
                "title": "予定株価" if e.is_plan else "Open Date",
                "value": "¥{:,}".format(e.val_plan) if e.is_plan else str(date_open),
                "short": True,
            },
            {
                "title": "保有数/予定数",
                "value": "{:,}/{:,}".format(remaining, e.num_plan),
                "short": True,
            },
            {
                "title": "現在株価",
                "value": "¥{:,}".format(current_val),
                "short": True,
            },
            {
                "title": "損益",
                "value": "¥{:,}".format(profit),
                "short": True,
            },
            {
                "title": "利確",
                "value": "¥{:,}".format(e.border_profit_determination) if e.border_profit_determination else "-",
                "short": True,
            },
            {
                "title": "損切",
                "value": "¥{:,}".format(e.border_loss_cut) if e.border_loss_cut else "-",
                "short": True,
            },
        ],
        "color": color,
        "attachment_type": "default",
        "actions": [
            {
                "name": "{}_order".format("buy" if e.is_plan else "sell"),
                "text": "成行{}注文".format("買" if e.is_plan else "売"),
                "type": "button",
                "style": "primary",
                "value": e.pk,
                "confirm": {
                    "title": "成行{}注文を実行しますか？".format("買" if e.is_plan else "売"),
                    "text": "{}: {}円/{}株".format(title, current_val, e.num_plan if e.is_plan else remaining),
                    "ok_text": "Order",
                    "dismiss_text": "Cancel"
                },
            },
            {
                "name": "current_price",
                "text": "現在値取得",
                "type": "button",
                "style": "default",
                "value": e.pk,
            },
        ]
    }
    params['attachments'].append(button)
    return params


def param_ipo_selected(ipo: Ipo):
    param =  {
        "short": True,
        "fallback": "fallback string",
        "callback_id": "callback_id value",
        "title": "IPO当選！",
        "text": "https://www.fk-management.com/web",
        "fields": [
            {
                "title": "当選数",
                "value": f"{ipo.num_select}株",
                "short": True,
            },
            {
                "title": "単価",
                "value": f"¥{ipo.val_list:,}",
                "short": True,
            },
        ],
        "color": "good",
        "attachment_type": "default",
    }
    d = {
        "text": "IPO当選",
        "attachments": [param],
    }
    return d