from kakeibo.models import Kakeibos, Usages, Resources, SharedKakeibos
import json
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Avg, Count
from kakeibo.functions import mylib
from asset.functions import mylib_asset, get_info, slack_asset, sbi_asset
from asset.models import Orders, Stocks, StockDataByDate, AssetStatus, HoldingStocks
from fmanage import tasks
# Create your views here.
import logging
logger = logging.getLogger("django")
from pytz import timezone


@csrf_exempt
def kakeibo(request):
    data_list = list()
    # add data to DB
    if request.method == "POST":
        try:
            val = json.loads(request.body.decode())
            logger.info(val)
            # record
            kakeibo = Kakeibos()
            kakeibo.date = date.today()
            kakeibo.fee = (val['金額'])
            kakeibo.way = val['項目']
            kakeibo.memo = val['メモ']
            kakeibo.tag = val['タグ']
            if kakeibo.way == "引き落とし":
                kakeibo.move_from = Resources.objects.get(name=val['引き落とし対象'])
                kakeibo.usage = Usages.objects.get(name=val['引き落とし項目'])
            elif kakeibo.way == "振替":
                kakeibo.move_from = Resources.objects.get(name=val['From'])
                kakeibo.move_to = Resources.objects.get(name=val['To'])
            elif kakeibo.way == "収入":
                kakeibo.move_to = Resources.objects.get(name=val['振込先'])
                if val['収入源'] == 'その他':
                    val['収入源'] = 'その他収入'
                kakeibo.usage = Usages.objects.get(name=val['収入源'])
            elif kakeibo.way == "支出（現金）":
                kakeibo.move_from = Resources.objects.get(name='財布')
                kakeibo.usage = Usages.objects.get(name=val['支出項目'])
            elif kakeibo.way == "支出（クレジット）":
                kakeibo.usage = Usages.objects.get(name=val['支出項目'])
            elif kakeibo.way == "共通支出":
                kakeibo.usage = Usages.objects.get(name="共通支出")
                kakeibo.move_from = Resources.objects.get(name="財布")
            # save
            kakeibo.save()
            status = True
            memo = "Successfully completed"
            d = {
                "fee": kakeibo.fee,
                "date": {
                    "year": kakeibo.date.year,
                    "month": kakeibo.date.month,
                    "day": kakeibo.date.day,
                },
                "way": kakeibo.way,
                "memo": kakeibo.memo,
                "usage": kakeibo.usage.name if kakeibo.usage else None,
                "move_from": kakeibo.move_from.name if kakeibo.move_from else None,
                "move_to": kakeibo.move_to.name if kakeibo.move_to else None,
            }
            data_list.append(d)
            logger.info(memo)
        except Exception as e:
            status = False
            memo = e
            logger.error(str(e))
        finally:
            data = {
                "message": memo,
                "status": status,
                "data_list": data_list,
                "length": data_list.__len__()
            }

    elif request.method == "GET":
        status = True
        kakeibos = Kakeibos.objects.all().select_related()
        for k in kakeibos:
            d = {
                "fee": k.fee,
                "date": {
                    "year": k.date.year,
                    "month": k.date.month,
                    "day": k.date.day,
                },
                "way": k.way,
                "memo": k.memo,
                "usage": k.usage.name if k.usage else None,
                "move_from": k.move_from.name if k.move_from else None,
                "move_to": k.move_to.name if k.move_to else None,
            }
            data_list.append(d)
        # data
        data = {
            "message": "",
            "status": status,
            "data_list": data_list,
            "length": data_list.__len__()
        }
    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def shared(request):
    data_list = list()
    # add data to DB
    if request.method == "POST":
        val = json.loads(request.body.decode())
        logger.info(val)
        try:
            kakeibo = SharedKakeibos()
            kakeibo.date = date.today()
            kakeibo.fee = (val['金額'])
            kakeibo.way = val['項目']
            kakeibo.memo = val['メモ']
            kakeibo.paid_by = val['支払者']
            kakeibo.is_settled = False
            if kakeibo.way == "引き落とし":
                kakeibo.move_from = Resources.objects.get(name=val['引き落とし対象'])
                kakeibo.usage = Usages.objects.get(name=val['引き落とし項目'])
            elif kakeibo.way == "現金":
                kakeibo.move_from = Resources.objects.get(name='財布')
                kakeibo.usage = Usages.objects.get(name=val['支出項目'])
            elif kakeibo.way == "クレジット":
                kakeibo.usage = Usages.objects.get(name=val['支出項目'])
            # save
            kakeibo.save()
            memo = "Successfully completed"
            status = True
            d = {
                "fee": kakeibo.fee,
                "date": {
                    "year": kakeibo.date.year,
                    "month": kakeibo.date.month,
                    "day": kakeibo.date.day,
                },
                "memo": kakeibo.memo,
                "usage": kakeibo.usage.name if kakeibo.usage else None,
                "move_from": kakeibo.move_from.name if kakeibo.move_from else None,
                "paid_by": kakeibo.paid_by
            }
            data_list.append(d)
        except Exception as e:
            memo = e
            status = False
            logger.error(str(e))
        finally:
            data = {
                "message": memo,
                "status": status,
                "data_list": data_list,
                "length": data_list.__len__()
            }

    elif request.method == "GET":
        status = True
        skakeibos = SharedKakeibos.objects.all().select_related()
        for sk in skakeibos:
            d = {
                "fee": sk.fee,
                "date": {
                    "year": sk.date.year,
                    "month": sk.date.month,
                    "day": sk.date.day,
                },
                "memo": sk.memo,
                "usage": sk.usage.name if sk.usage else None,
                "move_from": sk.move_from.name if sk.move_from else None,
                "paid_by": sk.paid_by
            }
            data_list.append(d)
        memo = ""
        data = {
            "message": memo,
            "status": status,
            "data_list": data_list,
            "length": data_list.__len__()
        }
    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def seisan(request):
    if request.method != "GET":
        data = {
            "status": False,
            "message": "GET request is only acceptable",
            }
    else:
        # 指定月の一ヶ月前の月末日を取得
        year = request.GET.get(key="year")
        month = request.GET.get(key="month")
        if year is None or month is None:
            today = date.today()
            last = date(int(today.year), int(today.month), 1) - relativedelta(days=1)
            year = last.year
            month = last.month
        seisan = mylib.seisan(year, month)
        data = {
            "status": True,
            "message": "Got response successfully",
            "data": seisan,
            }
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def kakeibo_month(request):
    if request.method != "GET":
        # GET以外はFalse
        data = {
            "message": "GET request is only acceptable",
            "status": False,
        }
        logger.error(data)
    elif request.method == "GET":
        # jsonに変換するデータを準備
        data = {
            "expense": list(),
            "income": list(),
        }
        # yearかmonthが指定されていない→全件取得
        year = request.GET.get(key="year")
        month = request.GET.get(key="month")
        if year is None or month is None:
            data['date'] = {"year": None, "month": None, }
            ks = Kakeibos.objects.exclude(usage=None)
        else:
            data['date'] = {"year": year, "month": month, }
            ks = Kakeibos.objects.exclude(usage=None).filter(date__year=year, date__month=month)
        # usage=None（振替）を除外
        ks = ks.values("usage") \
            .annotate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        # dataがない場合
        if ks.__len__() == 0:
            data['message'] = "No data"
            data['status'] = False
        else:
            for k in ks:
                d = {
                    "usage": Usages.objects.get(pk=k['usage']).name,
                    "sum": k['sum'],
                    "ave": k['avg'],
                    "count": k['count'],
                }
                if Usages.objects.get(pk=k['usage']).is_expense is True:
                    data["expense"].append(d)
                else:
                    data["income"].append(d)
            data["message"] = "Success"
            data['status'] = True
        data['date'] = {"year": year, "month": month, }
    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def shared_month(request):
    if request.method != "GET":
        # GET以外はFalse
        data = {
            "message": "GET request is only acceptable",
            "status": False,
        }
        logger.error(data)
    elif request.method == "GET":
        # jsonに変換するデータを準備
        data = {
            "expense": list(),
            "income": list(),
        }
        # yearかmonthが指定されていない→全件取得
        year = request.GET.get(key="year")
        month = request.GET.get(key="month")
        if year is None or month is None:
            data['date'] = {"year": None, "month": None, }
            ks = SharedKakeibos.objects.exclude(usage=None)
        else:
            data['date'] = {"year": year, "month": month, }
            ks = SharedKakeibos.objects.exclude(usage=None).filter(date__year=year, date__month=month)
        # usage=None（振替）を除外
        ks = ks.values("usage", "paid_by").order_by("paid_by")\
            .annotate(sum=Sum('fee'), avg=Avg('fee'), count=Count('fee'))
        # dataがない場合
        if ks.__len__() == 0:
            data['message'] = "No data"
            data['status'] = False
        else:
            for k in ks:
                d = {
                    "usage": Usages.objects.get(pk=k['usage']).name,
                    "paid_by": k['paid_by'],
                    "sum": k['sum'],
                    "ave": k['avg'],
                    "count": k['count'],
                }
                if Usages.objects.get(pk=k['usage']).is_expense is True:
                    data["expense"].append(d)
                else:
                    data["income"].append(d)
            data["message"] = "Success"
            data['status'] = True
        data['date'] = {"year": year, "month": month, }
    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


def asset(request):
    data = mylib_asset.get_benefit_all()
    # json
    logger.info(data)
    for d in data['data_all']:
        d['data']['date'] = str(d['data']['date'].year) + "/" \
                            + str(d['data']['date'].month) + "/" \
                            + str(d['data']['date'].day)
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def asset_order(request):
    if request.method == "GET":
        data_list = list()
        asset_orders = Orders.objects.all().select_related()
        for ao in asset_orders:
            d = {
                "is_nisa": ao.is_nisa,
                "commission": ao.commission,
                "price": ao.price,
                "num": ao.num,
                "datetime": {
                    "year": ao.datetime.year,
                    "month": ao.datetime.month,
                    "day": ao.datetime.day,
                    "hour": ao.datetime.hour,
                    "minute": ao.datetime.minute,
                },
                "order_type": ao.order_type,
                "stock": {
                    "code": ao.stock.code,
                    "name": ao.stock.name,
                }
            }
            data_list.append(d)
        # data
        data = {
            "message": "Data list of orders",
            "status": True,
            "data_list": data_list,
            "length": data_list.__len__()
        }
    elif request.method == "POST":
        try:
            val = json.loads(request.body.decode())
            logger.info("request_json: {}".format(val))
            stockinfo = get_info.stock_overview(val["code"])
            bo = Orders()
            bo.datetime = val["datetime"]
            bo.order_type = val["kind"]
            if bo.order_type == "現物買":
                # SBIの通知を設定
                sbi_asset.set_alert(val['code'])
            if Stocks.objects.filter(code=val["code"]).__len__() == 0:
                # Stocksにデータがない→登録
                stock = Stocks()
                stock.code = val["code"]
                stock.name = stockinfo['name']
                stock.industry = stockinfo['industry']
                stock.market = stockinfo['market']
                stock.save()
                # kabuoji3よりデータ取得
                if len(str(stock.code)) > 4:
                    # 投資信託→スキップ
                    pass
                else:
                    # 株→登録
                    data = get_info.kabuoji3(stock.code)
                    if data['status']:
                        # 取得成功時
                        for d in data['data']:
                            # (date, stock)の組み合わせでデータがなければ追加
                            if StockDataByDate.objects.filter(stock=stock, date=d[0]).__len__() == 0:
                                sdbd = StockDataByDate()
                                sdbd.stock = stock
                                sdbd.date = d[0]
                                sdbd.val_start = d[1]
                                sdbd.val_high = d[2]
                                sdbd.val_low = d[3]
                                sdbd.val_end = d[4]
                                sdbd.turnover = d[5]
                                sdbd.save()
                        logger.info('StockDataByDate of "%s" are updated' % stock.code)
                    else:
                        # 取得失敗時
                        logger.error(data['msg'])
                smsg = "New stock was registered:{}".format(stock.code)
            else:
                stock = Stocks.objects.get(code=val["code"])
                smsg = "This stock has been already registered:{}".format(stock.code)
            logger.info(smsg)
            bo.stock = stock
            bo.num = val["num"]
            bo.price = val["price"]
            bo.is_nisa = False
            bo.commission = mylib_asset.get_commission(bo.num*bo.price)
            bo.save()
            logger.info("New Order is created: {}".format(bo))

            # order時のholding stocks, asset status の変更
            smsg, emsg = mylib_asset.order_process(bo)

            # res
            if smsg:
                msg = smsg
                status = True
                logger.info(smsg)
            else:
                msg = emsg
                status = False
                logger.error(emsg)
                logger.error(val)
            # message
            d = {
                "is_nisa": bo.is_nisa,
                "commission": bo.commission,
                "price": bo.price,
                "num": bo.num,
                "datetime": str(bo.datetime),
                "order_type": bo.order_type,
                "stock": {
                    "code": bo.stock.code,
                    "name": bo.stock.name,
                }
            }
            data = {
                "message": msg,
                "status": status,
                "data_list": [d,],
                "length": 1,
            }
        except Exception as e:
            logger.error(e)
    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def test(request):
    # json
    try:
        val = json.loads(request.body.decode())
        logger.info(val)
    except Exception as e:
        logger.error(e)
    data = {
        "speech": "hello hello",
        "displayText": "hello hello",
        "fulfillmentText": "hello hello"
    }
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def googlehome_shared(request):
    today = date.today()
    # json purse
    try:
        val = json.loads(request.body.decode())
        keys = val['queryResult']['parameters'].keys()
        query_type = val['queryResult']['parameters']['query_type']
        if 'date-period' in keys and val['queryResult']['parameters']['date-period']:
            startDate = date(
                int(val['queryResult']['parameters']['date-period']["startDate"][0:4]),
                int(val['queryResult']['parameters']['date-period']["startDate"][5:7]),
                int(val['queryResult']['parameters']['date-period']["startDate"][8:10])
            )
            endDate = date(
                int(val['queryResult']['parameters']['date-period']["endDate"][0:4]),
                int(val['queryResult']['parameters']['date-period']["endDate"][5:7]),
                int(val['queryResult']['parameters']['date-period']["endDate"][8:10])
            )
        else:
            # 指定がない場合は、今月1ヶ月間を指定
            startDate = date(today.year, today.month, 1)
            endDate = startDate + relativedelta(months=1, days=-1)

        # log
        logger.debug("query_type: {0}".format(query_type))
        logger.debug("startDate: {0}".format(startDate))
        logger.debug("endDate: {0}".format(endDate))

        # カテゴリ別の合計
        if query_type == "individual":
            usage_name = val['queryResult']['parameters']['usage_name']
            logger.debug("usage_name: {0}".format(usage_name))
            shared = SharedKakeibos.objects.filter(date__range=[startDate, endDate], usage__name=usage_name)
            # text
            if shared:
                data = shared.aggregate(sum=Sum('fee'), count=Count('fee'))
                text = "{0}から{1}までの{2}の合計は、".format(startDate, endDate, usage_name)
                text += "{0}円です。".format(data['sum'])
                text += "レコード数は、{0}件です。".format(data['count'])
            else:
                # usage_nameがヒットしない場合
                text = "{0}から{1}までの{2}の記録はありません。".format(startDate, endDate, usage_name)
        # 詳細
        elif query_type == "breakdown":
            seisan = mylib.seisan(startDate.year, startDate.month)
            paid_by_t = seisan['payment']['taka']
            paid_by_h = seisan['payment']['hoko']
            shared_grouped_by_usage = SharedKakeibos.objects.filter(date__range=[startDate, endDate]) \
                .values('usage__name').annotate(sum=Sum('fee')).order_by("-sum")
            # text
            text = "{0.year}年{0.month}月の支出合計は".format(startDate)
            text += "{0}円です。".format(paid_by_t + paid_by_h)
            text += "たかしの支出は、{0}円、".format(paid_by_t)
            text += "ほうこの支出は、{0}円です。".format(paid_by_h)
            text += "内訳は"
            for sgbu in shared_grouped_by_usage:
                text += "、{0}{1}円".format(sgbu['usage__name'], sgbu['sum'])
            text = text + "です。"
        # 概要
        elif query_type == "overview":
            seisan = mylib.seisan(startDate.year, startDate.month)
            total = seisan['payment']['sum']
            # text
            text = "{0.year}年{0.month}月の支出合計は".format(startDate)
            text += "{0}円です。".format(total)
            text += "{0}額は、{1}円、".format(seisan['status'], seisan['inout'])
            text += "現金精算額は、{0}円です。".format(seisan['seisan'])
        # 登録
        elif query_type == "create":
            pay_date = date(
                int(val['queryResult']['parameters']['date'][0:4]),
                int(val['queryResult']['parameters']['date'][5:7]),
                int(val['queryResult']['parameters']['date'][8:10])
            )
            shared = SharedKakeibos.objects.create(
                usage=Usages.objects.get(name=val['queryResult']['parameters']['usage_name']),
                date=pay_date,
                fee=val['queryResult']['parameters']['fee'],
                paid_by=val['queryResult']['parameters']['paid_by'],
                is_settled=False
            )
            # text
            text = "新しい共通家計簿レコードを追加しました。"
            text += "{0.date}の{0.usage.name}、{0.fee}円、支払い者は{0.paid_by}です。".format(shared)
        # 登録（mine）
        elif query_type == "create_mine":
            pay_date = date(
                int(val['queryResult']['parameters']['date'][0:4]),
                int(val['queryResult']['parameters']['date'][5:7]),
                int(val['queryResult']['parameters']['date'][8:10])
            )
            data = {
                "usage": Usages.objects.get(name=val['queryResult']['parameters']['usage_name']),
                "date": pay_date,
                "fee": val['queryResult']['parameters']['fee'],
                "way": val['queryResult']['parameters']['way'],
            }
            # move_to, move_fromがあったら追加
            if not val['queryResult']['parameters']['move_from'] == "None":
                data["move_from"] = Resources.objects.get(name=val['queryResult']['parameters']['move_from'])
            if not val['queryResult']['parameters']['move_to'] == "None":
                data["move_from"] = Resources.objects.get(name=val['queryResult']['parameters']['move_to'])
            kakeibo = Kakeibos.objects.create(**data)
            # text
            text = "新しいマイ家計簿レコードを追加しました。"
            text += "{0.date}の{0.way}、{0.usage.name}、{0.fee}円です。".format(kakeibo)
        logger.info(text)
    # Error処理
    except Exception as e:
        logger.error(e)
        text = "エラーがありました。エラー文は次のとおりです。"
        text = text + str(e)

    # data
    data = {
        "fulfillmentText": text
    }
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def asset_status(request):
    if request.method == "GET":
        astatus = AssetStatus.objects.all().order_by('date')
        data = {
            "length": len(astatus),
            "data_list": [
                {
                    "pk": a.pk,
                    "date": {
                        "year": a.date.year,
                        "month": a.date.month,
                        "day": a.date.day,
                    },
                    "total": a.total,
                    "stocks_value": a.stocks_value,
                    "other_value": a.other_value,
                    "buying_power": a.buying_power,
                    "investment": a.investment,
                } for a in astatus
            ]
        }
    elif request.method == "POST":
        logger.error("POST is not allowed. {}".format(request.POST))
        raise Http404
    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def asset_holding(request):
    if request.method == "GET":
        holdings = HoldingStocks.objects.all()
        data = {
            "length": len(holdings),
            "data_list": [
                {
                    "stock": {
                        "code": h.stock.code,
                        "name": h.stock.name,
                    },
                    "num": h.num,
                    "price": h.price,
                    "date": {
                        "year": h.date.year,
                        "month": h.date.month,
                        "day": h.date.day,
                    }
                } for h in holdings
            ]
        }
    elif request.method == "POST":
        raise Http404
    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def asset_stock_all(request):
    if request.method == "GET":
        stocks = Stocks.objects.all()
        data = {
            "length": len(stocks),
            "data_list": [
                {
                    "name": s.name,
                    "code": s.code,
                    "time_buy": s.orders_set.filter(order_type="現物買").count(),
                    "time_sell": s.orders_set.filter(order_type="現物売").count(),
                    "is_holding": True if s.holdingstocks_set.count() > 0 else False,
                    "current_price": s.holdingstocks_set.first().get_current_price() if s.holdingstocks_set.count() > 0 else None,
                    "buy_price": s.holdingstocks_set.first().price if s.holdingstocks_set.count() > 0 else None,
                    "num_holding": s.holdingstocks_set.first().num if s.holdingstocks_set.count() > 0 else 0,
                } for s in stocks
            ]
        }
    elif request.method == "POST":
        raise Http404
    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def asset_stock(request, code):
    if request.method == "GET":
        try:
            s = Stocks.objects.get(code=code)
            data = {
                "name": s.name,
                "code": s.code,
                "time_buy": s.orders_set.filter(order_type="現物買").count(),
                "time_sell": s.orders_set.filter(order_type="現物売").count(),
                "is_holding": True if s.holdingstocks_set.count() > 0 else False,
                "current_price": s.holdingstocks_set.first().get_current_price() if s.holdingstocks_set.count() > 0 else None,
                "buy_price": s.holdingstocks_set.first().price if s.holdingstocks_set.count() > 0 else None,
                "num_holding": s.holdingstocks_set.first().num if s.holdingstocks_set.count() > 0 else 0,
            }
        except Exception as e:
            logger.error(e)
            data = {
                "name": None,
                "code": None,
                "message": "No data of {}".format(code)
            }
    elif request.method == "POST":
        raise Http404
    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def asset_slack_interactive(request):
    if request.method == "POST":
        # payload受け取り
        request_json = json.loads(request.POST["payload"])
        logger.info(request_json)
        # original message の転用
        replyMessage = request_json['original_message']
        replyMessage.pop('type')
        replyMessage.pop('subtype')
        replyMessage.pop('ts')
        replyMessage.pop('bot_id')
        replyMessage["replace_original"] = True
        replyMessage["response_type"] = "in_channel"
        replyMessage["text"] = "Last updated at {}".format(datetime.now(timezone('Asia/Tokyo')).ctime())

        if request_json['actions'][0]['name'] == "order":
            """ 成行注文 """
            # response_url
            code = request_json['actions'][0]['value']
            response_url = request_json['response_url']
            logger.info("成行注文 {}".format(code))
            logger.info("response_url: {}".format(response_url))
            # task
            tasks.set_sell.delay(response_url, replyMessage, code)
            # reply
            title = request_json['original_message']['attachments'][0]['title']
            text = "📲成行注文中..."
            content = {
                "fallback": "fallback string",
                "callback_id": "callback_id value",
                "title": title,
                "text": text,
                "color": "#88abfe",
            }
            replyMessage['attachments'] = []
            replyMessage['attachments'].append(content)

        elif request_json['actions'][0]['name'] == "current_price":
            """ 現在値確認 """
            logger.info("現在値確認 {}".format(request_json['actions'][0]['value']))
            # 取得
            holding = HoldingStocks.objects.get(stock__code=request_json['actions'][0]['value'])
            # 買付価格と現在価格、利益等の情報も送信
            current_price = holding.get_current_price()
            benefit = (current_price - holding.price) * holding.num
            text = "保有数: {}\n現在値: {:,}".format(holding.num, current_price)
            if benefit > 0:
                text += "\n利益: +{:,}".format(benefit)
            else:
                text += "\n損失: {:,}".format(benefit)
            # update
            replyMessage['attachments'][0]["text"] = text
            replyMessage['attachments'][0]['color'] = "#FF9960" if benefit < 0 else "good"

    elif request.method == "GET":
        logger.info("Got request for posting message to slack")
        slack_asset.post_holdings_to_slack()
        replyMessage = {
            "message": "Posted message to slack"
        }

    # return
    logger.info("replyMessage {}".format(replyMessage))
    json_str = json.dumps(replyMessage, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response
