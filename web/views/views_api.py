# coding:utf-8
from django.template.response import HttpResponse
from django.views.generic import View
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
import json
from pytz import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from web.functions import mylib_scraping, mylib_asset, mylib_slack
from web.models import Entry, Order, Stock, SBIAlert
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
@transaction.atomic
@csrf_exempt
def create_order(request):
    if request.method == "POST":
        try:
            with transaction.atomic():
                json_data = json.loads(request.body.decode())
                logger.info("request_json: {}".format(json_data))
                pk_orders = list()
                for val in json_data.values():
                    logger.info(val)
                    val['user'] = User.objects.first()
                    logger.info("User: {}".format(val['user']))
                    val['commission'] = mylib_asset.get_commission(val['num'] * val['val'])
                    # Stocksにデータがない→登録
                    if not Stock.objects.filter(code=val["code"]).exists():
                        stockinfo = mylib_scraping.yf_detail(val["code"])
                        if stockinfo['status']:
                            stock = Stock()
                            stock.code = val["code"]
                            stock.name = stockinfo['data']['name']
                            stock.industry = stockinfo['data']['industry']
                            stock.market = stockinfo['data']['market']
                            stock.is_trust = False if len(str(stock.code)) == 4 else True
                            stock.save()
                        val['stock'] = stock
                        smsg = "New stock was registered:{}".format(stock.code)
                        logger.info(smsg)
                    else:
                        smsg = "Stock {} is found".format(stock.code)
                        val['stock'] = Stock.objects.get(code=val['code'])
                        logger.info(smsg)
                    # Order作成
                    val.pop("code")
                    o = Order.objects.create(**val)
                    pk_orders.append(o.pk)
                    msg = "New Order is created: {}".format(o)
                    logger.info(msg)
                # OrderProcessの実行
                orders = Order.objects.filter(pk__in=pk_orders).order_by("datetime")
                data_list = list()
                for o in orders:
                    res = mylib_asset.order_process(o, user=o.user)
                    if res['status']:
                        data_list.append({
                            "commission": o.commission,
                            "val": o.val,
                            "num": o.num,
                            "datetime": str(o.datetime),
                            "is_buy": o.is_buy,
                            "stock__code": o.stock.code,
                            "stock__name": o.stock.name,
                        })
                    else:
                        raise Exception('OrderProcess of {} failed'.format(o))
                data = {
                    "status": True,
                    "message": msg,
                    "data": data_list,
                }
        except Exception as e:
            logger.error(e)
            data = {
                "status": False,
                "message": "{}".format(e),
                "data": {}
            }
        finally:
            logger.info(data)
            json_str = json.dumps(data, ensure_ascii=False, indent=2)
            response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
            return response
    elif request.method == "GET":
        data = {
            "status": False,
            "message": "Please use POST method",
            "data": {}
        }
        json_str = json.dumps(data, ensure_ascii=False, indent=2)
        response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
        return response


class GetCurrentVals(View):
    def get(self, request, *args, **kwargs):
        stocks = Stock.objects.all()
        res = list()
        for stock in stocks:
            res.append({
                "code": stock.code,
                "val": stock.current_val(),
            })
        return JsonResponse(res, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class ReceiveAlert(View):
    """
    {
        "message": "2020/03/03 13:22に\r\nアラート条件\r\n前日比1\r\n％以上\r\nに達しました。\r\n日経ダブルインバ\r\n1357 東証\r\n現在値:1,063\r\n現時刻:2020/03/03 13:22\r\n前日比:+11\r\n出来高:61,214,318\r\n始値  :1,022\r\n高値  :1,063\r\n安値  :1,015\r\n売気配:1,063\r\n買気配:1,061\r\n買残  :72,668,214\r\n前週比:-2,111,136\r\n売残  :2,301,459\r\n前週比:-494,396\r\n倍率 :+31.57\r\n\r\n-- \r\n古屋敬士\r\nTel  08054506740\r\nMail takashi.furuya.0@gmail.com\r\n",
        "code": "1357",
        "val": 1,
        "type": 2
    }
    """
    def post(self, request, *args, **kwargs):
        json_data = json.loads(request.body.decode())
        try:
            if Stock.objects.filter(code=json_data['code']).count() == 1:
                stock = Stock.objects.get(code=json_data['code'])
            else:
                stockinfo = mylib_scraping.yf_detail(json_data["code"])
                if stockinfo['status']:
                    stock = Stock()
                    stock.code = json_data["code"]
                    stock.name = stockinfo['data']['name']
                    stock.industry = stockinfo['data']['industry']
                    stock.market = stockinfo['data']['market']
                    stock.is_trust = False if len(str(stock.code)) == 4 else True
                    stock.save()
                else:
                    res = {"status": False, "message": "Failed to create Stock"}
                    return JsonResponse(res, safe=False)
            sbialerts = SBIAlert.objects.filter(
                stock=stock, is_active=True, val=json_data['val'], type=json_data['type']
            )
            for sbialert in sbialerts:
                text = "【({}) {}】{}{}".format(stock.code, stock.name, sbialert.val, sbialert.get_type_display())
                mylib_slack.post_message(text)
            # slack
            sbialerts.update(checked_at=datetime.now(), is_active=False, message=json_data['message'])
            # res
            res = {"status": True, "message": json_data['message']}
        except Exception as e:
            logger.error(e)
            res = {"status": False, "message": str(e)}
        finally:
            return JsonResponse(res, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class SlackInteractive(View):
    def post(self, request, *args, **kwargs):
        # payload受け取り
        json_data = json.loads(request.POST["payload"])
        logger.info(json_data)
        try:
            entry = Entry.objects.get(pk=json_data["actions"][0]["value"])
            # current_price
            if json_data["actions"][0]['name'] == "current_price":
                res = mylib_slack.param_entry(entry)
            # buy_order
            elif json_data["actions"][0]['name'] == "buy_order":
                pass
        except Exception as e:
            logger.error(e)
            res = {"status": False, "message": str(e)}
        finally:
            res["replace_original"] = True
            res["response_type"] = "in_channel"
            logger.info(res)
            return JsonResponse(res, safe=False)