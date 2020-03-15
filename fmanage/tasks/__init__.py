# fmanage/tasks/__init__.py
from ..celery import app
from asset.functions import sbi_asset, slack_asset
from asset.models import HoldingStocks
from web.functions import selenium_sbi
import logging
logger = logging.getLogger('django')
# celery -A fmanage worker -c 2 -l info


@app.task()
def minus_numbers(a, b):
    print('Request: {}-{}={}'.format(a, b, a - b))
    return a - b


@app.task()
def add_numbers(a, b):
    print('Request: {}+{}={}'.format(a, b, a + b))
    return a + b


@app.task()
def set_buy(response_url, replyMessage, code, num):
    # order
    res = sbi_asset.set_buy(code, num)
    # slack
    if res:
        # order成功
        title = replyMessage['attachments'][0]['title']
        text = "✅成行注文完了"
        content = {
            "title": title,
            "text": text,
            "color": "#428bfa",
        }
        replyMessage['attachments'] = []
        replyMessage['attachments'].append(content)
        pass
    else:
        # order失敗→現在値更新
        # 取得
        holding = HoldingStocks.objects.get(stock__code=code)
        # 買付価格と現在価格、利益等の情報も送信
        current_price = holding.get_current_price()
        benefit = (current_price - holding.price) * holding.num
        text = "保有数: {}\n現在値: {:,}".format(holding.num, current_price)
        if benefit > 0:
            text += "\n利益: +{:,}".format(benefit)
        else:
            text += "\n損失: {:,}".format(benefit)
        # update
        replyMessage['attachments'][0]["title"] = replyMessage['attachments'][0]["title"] + "（注文失敗）"
        replyMessage['attachments'][0]["text"] = text
        replyMessage['attachments'][0]['color'] = "#FF9960" if benefit < 0 else "good"
        pass
    r = slack_asset.post_slack(response_url, replyMessage)
    # return
    res = {
        "state_code": r.status_code,
        "json": r.json(),
        "response_url": r.url,
    }
    return res


@app.task()
def set_sell(response_url, replyMessage, code):
    # order
    holding = HoldingStocks.objects.get(stock__code=code)
    res = sbi_asset.set_sell(code, holding.num)
    # order結果の判定
    if res:
        # order成功
        title = replyMessage['attachments'][0]['title']
        text = "✅成行注文完了"
        content = {
            "title": title,
            "text": text,
            "color": "#428bfa",
        }
        replyMessage['attachments'] = []
        replyMessage['attachments'].append(content)
    else:
        # order失敗→現在値更新
        # 買付価格と現在価格、利益等の情報も送信
        current_price = holding.get_current_price()
        benefit = (current_price - holding.price) * holding.num
        text = "保有数: {}\n現在値: {:,}".format(holding.num, current_price)
        if benefit > 0:
            text += "\n利益: +{:,}".format(benefit)
        else:
            text += "\n損失: {:,}".format(benefit)
        # update
        replyMessage['attachments'][0]["title"] = replyMessage['attachments'][0]["title"] + "（注文失敗）"
        replyMessage['attachments'][0]["text"] = text
        replyMessage['attachments'][0]['color'] = "#FF9960" if benefit < 0 else "good"
    # update slack message
    r = slack_asset.post_slack(response_url, replyMessage)
    # return
    res = {
        "state_code": r.status_code,
        "json": r.json(),
        "response_url": r.url,
    }
    return res


@app.task()
def set_alert(stock_code, val, type):
    SBI = selenium_sbi.SeleniumSBI()
    try:
        res = SBI.alert(stock_code=stock_code, val=val, alert_type=type)
    except Exception as e:
        logger.error(e)
        res = False
    finally:
        SBI.close()
        return res
