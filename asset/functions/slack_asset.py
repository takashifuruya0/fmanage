import requests
from datetime import datetime
from pytz import timezone
import json
from django.conf import settings
from asset.models import HoldingStocks
import logging
logger = logging.getLogger("django")


def post_holdings_to_slack():
    # holdings
    data = HoldingStocks.objects.all()
    for d in data:
        if len(d.stock.code) > 4:
            # 投資信託はスキップ
            logger.debug("{} is skipped".format(d.stock.code))
            continue
        # params設定
        params = {
            "channel": "#log_gas",
            "username": "fk-management.com",
            "text": "last updated at {}".format(datetime.now(timezone('Asia/Tokyo')).ctime()),
            "attachments": [
            ]
        }
        # 各種値を取得
        current_price = d.get_current_price()
        benefit = d.num * (current_price - d.price)
        code = d.stock.code
        # 買付価格と現在価格、利益等の情報も送信
        logger.debug("{} is added".format(code))
        title = "【{}】{}".format(code, d.stock.name)
        text = "保有数: {}\n 現在値: {:,}".format(d.num, current_price)
        if benefit > 0:
            text += "\n利益: +{:,}".format(benefit)
        else:
            text += "\n損失: {:,}".format(benefit)
        # attachment追加
        button = {
            "short": True,
            "fallback": "fallback string",
            "callback_id": "callback_id value",
            "title": title,
            "text": text,
            "color": "#FF9960" if benefit < 0 else "good",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "order",
                    "text": "成行注文",
                    "type": "button",
                    "style": "primary",
                    "value": code,
                    "confirm": {
                        "title": "成行注文を実行します。よろしいですか？",
                        "text": "{}\n{}".format(title, text),
                        "ok_text": "Order",
                        "dismiss_text": "Cancel"
                    },
                },
                {
                    "name": "current_price",
                    "text": "現在値取得",
                    "type": "button",
                    "style": "default",
                    "value": code,
                },
            ]
        }
        params['attachments'].append(button)
        # post msg to slack
        post_slack(params)
    return True


def post_slack(params):
    url = settings.SECRET["URL_SLACK_ASSET"]
    json_data = json.dumps(params)
    headers = {
        'Content-Type': 'application/json'
    }
    r = requests.post(url, json_data, headers=headers)
    logger.info("request status: {}".format(r.status_code))
    return r
