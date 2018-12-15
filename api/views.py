from kakeibo.models import Kakeibos, Usages, Resources, SharedKakeibos
import json
from datetime import date
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Avg, Count
from kakeibo.functions import mylib
from asset.functions import mylib_asset, get_info
from asset.models import Orders, Stocks
# Create your views here.
import logging
logger = logging.getLogger("django")


@csrf_exempt
def kakeibo(request):
    # add data to DB
    if request.method == "POST":
        try:
            val = json.loads(request.body.decode())
            logger.info(val)

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
            logger.info(memo)

        except Exception as e:
            status = False
            memo = e
            logger.error(str(e))

    else:
        status = False
        memo = "you should use POST"
        logger.error("POST is not acceptable")

    # json
    data = {"message": memo, "status": status,}
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def shared(request):
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

        except Exception as e:
            memo = e
            status = False
            logger.error(str(e))

    else:
        memo = "you should use POST"
        status = False
        logger.error("POST is not acceptable")

    # json
    data = {"message": memo, "status": status,}
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
    if request.method != "POST":
        # GET以外はFalse
        data = {
            "message": "POST request is only acceptable",
            "status": False,
        }
    elif request.method == "POST":
        try:
            val = json.loads(request.body.decode())
            stockinfo = get_info.stock_overview(val["code"])
            bo = Orders()
            bo.datetime = val["datetime"]
            bo.order_type = val["kind"]
            if Stocks.objects.filter(code=val["code"]).__len__() == 0:
                stock = Stocks()
                stock.code = val["code"]
                stock.name = stockinfo['name']
                stock.save()
            else:
                stock = Stocks.objects.get(code=val["code"])
            bo.stock = stock
            bo.num = val["num"]
            bo.price = val["price"]
            bo.is_nisa = False
            bo.commission = mylib_asset.get_commission(bo.num*bo.price)
            bo.save()
            logger.info("New Order is created")

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
            # message
            data = {
                "message": msg,
                "status": status,
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
        print(e)
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
def test2(request):
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
            startDate = date(today.year, today.month, 1)
            endDate = startDate + relativedelta(months=1, days=-1)
        # log
        logger.info("query_type: " + query_type)
        logger.info("startDate: " + str(startDate))
        logger.info("endDate: " + str(endDate))
        # calculation
        if query_type == "individual":
            usage_name = val['queryResult']['parameters']['usage_name']
            logger.info("usage_name: " + usage_name)
            shared = SharedKakeibos.objects.filter(date__range=[startDate, endDate], usage__name=usage_name)
            # text
            text = str(startDate) + "から" + str(endDate) + "までの" + usage_name + "の合計は、"
            text = text + shared.aggregate(sum=Sum('fee'))['sum'] + "円です。"
        elif query_type == "overview":
            seisan = mylib.seisan(startDate.year, startDate.month)
            paid_by_t = seisan['payment']['taka']
            paid_by_h = seisan['payment']['hoko']
            shared_grouped_by_usage = SharedKakeibos.objects.filter(date__range=[startDate, endDate])\
                .values('usage__name').annotate(sum=Sum('fee')).order_by("-sum")
            # text
            text = str(startDate.year)+"年"+str(startDate.month)+"月の支出合計は"
            text = text + str(paid_by_t + paid_by_h) + "円です。"
            text = text + "たかしの支出は、" + str(paid_by_t) + "円、"
            text = text + "ほうこの支出は、" + str(paid_by_h) + "円です。"
            text = text + "内訳は"
            for sgbu in shared_grouped_by_usage:
                text = "、" + text + sgbu['usage__name'] + sgbu['sum'] + "円"
            text = text + "です。"
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


