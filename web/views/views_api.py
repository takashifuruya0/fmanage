# coding:utf-8
from django.template.response import HttpResponse
from django.conf import settings
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
import json
from django.db import transaction
from web.functions import asset_scraping, asset_lib
from web.models import Entry, Order, Stock
# logging
import logging
logger = logging.getLogger("django")


# Create your views here.
@transaction.atomic
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
                    val['commission'] = asset_lib.get_commission(val['num']*val['val'])
                    # Stocksにデータがない→登録
                    if not Stock.objects.filter(code=val["code"]).exists():
                        stockinfo = asset_scraping.yf_detail(val["code"])
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
                    res = asset_lib.order_process(o, user=o.user)
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
