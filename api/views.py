from django.shortcuts import render
from kakeibo.models import Kakeibos, Usages, Resources, SharedKakeibos
from asset.models import BuyOrders, SellOrders, Stocks, HoldingStocks
import json
from datetime import date, datetime
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


@csrf_exempt
def kakeibo(request):
    # add data to DB
    if request.method == "POST":
        val = json.loads(request.body.decode())
        try:

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
            memo = "Successfully completed"

        except Exception as e:
            memo = e

    else:
        memo = "you should use POST"

    # json
    data = {"memo": memo, }
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

        except Exception as e:
            memo = e

    else:
        memo = "you should use POST"

    # json
    data = {"memo": memo, }
    json_str = json.dumps(data, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=None)
    return response


@csrf_exempt
def buy_order(request, target_id=0):
    status = None
    # POST --> save it to DB
    if request.method == "POST":
        data = json.loads(request.body.decode())
        # Buying order
        bo = BuyOrders()
        bo.datetime = datetime.today()
        bo.num = data['num']
        bo.price = data['price']
        bo.account = data['account'] # Difficult to determine NISA or not based on mails from SBI
        bo.commission = data['fee']
        # Stock_records
        sr = Stocks.objects.filter(code=data['code'])
        if sr.__len__ is 1:
            bo = sr[0]
        else:
            sr = Stocks()
            sr.code = data['code']
            sr.name = data['name']
            sr.save()
            bo.stock = sr
        # Save
        bo.save()
        # Holding Stocks
        ho = HoldingStocks.objects.filter(stock=bo.stock)
        # 所有済み
        if ho.__len__ is 1:
            ho.date = date.today()
            ho.average_price = (ho.average_price * ho.num + bo.price * bo.num) / (ho.num + bo.num)
            ho.num = ho.num+bo.num
        # 所有していない
        else:
            ho.date = date.today()
            ho.stock = bo.stock
            ho.average_price = bo.price
            ho.num = bo.num
        ho.save()

        # res
        memo = "success: " + str(bo.pk)
        res = {
          "memo": memo,
        }
    # GET --> select * from DB
    elif request.method == "GET":
        if target_id is 0:
            bo = BuyOrders().objects.all()
        else:
            bo = BuyOrders().objects.filter(pk=target_id)
        res = {}
        for i in bo:
            res[i.pk] = {}
            res[i.pk]['datetime'] = i.datetime
            res[i.pk]['name'] = i.stock.name
            res[i.pk]['code'] = i.stock.code
            res[i.pk]['num'] = i.num
            res[i.pk]['price'] = i.price
    # json_str: json形式に整形
    json_str = json.dumps(res, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
    return response


@csrf_exempt
def sell_order(request, target_id=0):
    status = None
    # POST --> save it to DB
    if request.method == "POST":
        data = json.loads(request.body.decode())
        # Selling order
        so = SellOrders()
        so.datetime = datetime.today()
        so.num = data['num']
        so.price = data['price']
        so.fee = data['fee']
        so.stock = Stocks.objects.get(code=data['code'])
        so.commission = data['commission']
        so.account = data['account']

        # Save
        so.save()

        # Holding Stocks
        # 0になる→result
        # その他
        memo = "success: " + str(so.pk)
        res = {
          "memo": memo,
        }
    # GET --> select * from DB
    elif request.method == "GET":
        if target_id is 0:
            so = SellOrders().objects.all()
        else:
            so = SellOrders().objects.filter(pk=target_id)
        res = {}
        for i in so:
            res[i.pk] = {}
            res[i.pk]['datetime'] = i.datetime
            res[i.pk]['name'] = i.stock.name
            res[i.pk]['code'] = i.stock.code
            res[i.pk]['num'] = i.num
            res[i.pk]['price'] = i.price
    # json_str: json形式に整形
    json_str = json.dumps(res, ensure_ascii=False, indent=2)
    response = HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
    return response
