from django.shortcuts import render
from kakeibo.models import Kakeibos, Usages, Resources, SharedKakeibos
import json
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, Avg, Count
from kakeibo.functions import mylib, calc_val
from asset.functions import mylib_asset, get_info
from asset.models import BuyOrders, Stocks
# Create your views here.
import logging
logger = logging.getLogger("django")


@csrf_exempt
def kakeibo(request):
    # add data to DB
    if request.method == "POST":
        try:
            logger.info("kakeibo api is called by POST")
            val = json.loads(request.body.decode())

            kakeibo = Kakeibos()
            kakeibo.date = date.today()
            kakeibo.fee = (val['金額'])
            kakeibo.way = val['項目']
            kakeibo.memo = val['メモ']
            kakeibo.tag = val['タグ']
            if kakeibo.way == "引き落とし":
                kakeibo.move_from = Resources.objects.get(name=val['引き落とし対象'])
                kakeibo.usage = Usages.objects.get(name=val['引き落とし項目'])
                # update current_val
                # calc_val.resource_current_val(val['引き落とし対象'], -kakeibo.fee)

            elif kakeibo.way == "振替":
                kakeibo.move_from = Resources.objects.get(name=val['From'])
                kakeibo.move_to = Resources.objects.get(name=val['To'])
                # update current_val
                # calc_val.resource_current_val(val['From'], -kakeibo.fee)
                # calc_val.resource_current_val(val['To'], kakeibo.fee)

            elif kakeibo.way == "収入":
                kakeibo.move_to = Resources.objects.get(name=val['振込先'])
                if val['収入源'] == 'その他':
                    val['収入源'] = 'その他収入'
                kakeibo.usage = Usages.objects.get(name=val['収入源'])
                # update current_val
                # calc_val.resource_current_val(val['振込先'], kakeibo.fee)

            elif kakeibo.way == "支出（現金）":
                kakeibo.move_from = Resources.objects.get(name='財布')
                kakeibo.usage = Usages.objects.get(name=val['支出項目'])
                # update current_val
                # calc_val.resource_current_val('財布', -kakeibo.fee)

            elif kakeibo.way == "支出（クレジット）":
                kakeibo.usage = Usages.objects.get(name=val['支出項目'])

            elif kakeibo.way == "共通支出":
                kakeibo.usage = Usages.objects.get(name="共通支出")
                kakeibo.move_from = Resources.objects.get(name="財布")
                # update current_val
                # calc_val.resource_current_val('財布', -kakeibo.fee)

            # save
            kakeibo.save()
            name = [i.name for i in Resources.objects.all()]
            for i in name:
                calc_val.resource_current_val(i, 0)

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

    else:
        memo = "you should use POST"
        status = False

    # json
    data = {"message": memo, "status": status,}
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


# @csrf_exempt
# def buy_order(request, target_id=0):
#     status = None
#     # POST --> save it to DB
#     if request.method == "POST":
#         data = json.loads(request.body.decode())
#         # Buying order
#         bo = BuyOrders()
#         bo.datetime = datetime.today()
#         bo.num = data['num']
#         bo.price = data['price']
#         bo.account = data['account'] # Difficult to determine NISA or not based on mails from SBI
#         bo.commission = data['fee']
#         # Stock_records
#         sr = Stocks.objects.filter(code=data['code'])
#         if sr.__len__ is 1:
#             bo = sr[0]
#         else:
#             sr = Stocks()
#             sr.code = data['code']
#             sr.name = data['name']
#             sr.save()
#             bo.stock = sr
#         # Save
#         bo.save()
#         # Holding Stocks
#         ho = HoldingStocks.objects.filter(stock=bo.stock)
#         # 所有済み
#         if ho.__len__ is 1:
#             ho.date = date.today()
#             ho.average_price = (ho.average_price * ho.num + bo.price * bo.num) / (ho.num + bo.num)
#             ho.num = ho.num+bo.num
#         # 所有していない
#         else:
#             ho.date = date.today()
#             ho.stock = bo.stock
#             ho.average_price = bo.price
#             ho.num = bo.num
#         ho.save()
#
#         # res
#         memo = "success: " + str(bo.pk)
#         res = {
#           "memo": memo,
#         }
#     # GET --> select * from DB
#     elif request.method == "GET":
#         if target_id is 0:
#             bo = BuyOrders().objects.all()
#         else:
#             bo = BuyOrders().objects.filter(pk=target_id)
#         res = {}
#         for i in bo:
#             res[i.pk] = {}
#             res[i.pk]['datetime'] = i.datetime
#             res[i.pk]['name'] = i.stock.name
#             res[i.pk]['code'] = i.stock.code
#             res[i.pk]['num'] = i.num
#             res[i.pk]['price'] = i.price
#     # json_str: json形式に整形
#     json_str = json.dumps(res, ensure_ascii=False, indent=2)
#     response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
#     return response
#
#
# @csrf_exempt
# def sell_order(request, target_id=0):
#     status = None
#     # POST --> save it to DB
#     if request.method == "POST":
#         data = json.loads(request.body.decode())
#         # Selling order
#         so = SellOrders()
#         so.datetime = datetime.today()
#         so.num = data['num']
#         so.price = data['price']
#         so.fee = data['fee']
#         so.stock = Stocks.objects.get(code=data['code'])
#         so.commission = data['commission']
#         so.account = data['account']
#
#         # Save
#         so.save()
#
#         # Holding Stocks
#         # 0になる→result
#         # その他
#         memo = "success: " + str(so.pk)
#         res = {
#           "memo": memo,
#         }
#     # GET --> select * from DB
#     elif request.method == "GET":
#         if target_id is 0:
#             so = SellOrders().objects.all()
#         else:
#             so = SellOrders().objects.filter(pk=target_id)
#         res = {}
#         for i in so:
#             res[i.pk] = {}
#             res[i.pk]['datetime'] = i.datetime
#             res[i.pk]['name'] = i.stock.name
#             res[i.pk]['code'] = i.stock.code
#             res[i.pk]['num'] = i.num
#             res[i.pk]['price'] = i.price
#     # json_str: json形式に整形
#     json_str = json.dumps(res, ensure_ascii=False, indent=2)
#     response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
#     return response
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
    data = mylib_asset.benefit_all()
    # json
    print(data)
    for d in data['data_all']:
        d['data']['date'] = str(d['data']['date'].year) + "/" \
                            + str(d['data']['date'].month) + "/" \
                            + str(d['data']['date'].day)
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


def asset_order(request):
    if request.method != "POST":
        # GET以外はFalse
        data = {
            "message": "POST request is only acceptable",
            "status": False,
        }
    elif request.method == "POST":
        if request.POST["kind"] == "buy_order":
            # jsonに変換するデータを準備
            bo = BuyOrders()
            bo.datetime = request.POST["datetime"]
            # request.POST["order_id"]
            if Stocks.objects.filter(code=request.POST["code"]) == 0:
                stock = Stocks()
                stock.code = request.POST["code"]
                stock.name = get_info.stock_overview(request.POST["code"])['name']
                stock.save()
            else:
                stock = Stocks.objects.get(code=request.POST["code"])
            bo.stock = stock
            bo.num = request.POST["num"]
            bo.price = request.POST["price"]
            bo.is_nisa = False
            bo.commission = 0
            bo.save()
        data = {
            "message": "Successfully recorded",
            "status": True,
        }

    # json
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response
