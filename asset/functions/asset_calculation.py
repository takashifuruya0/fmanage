# coding:utf-8
from asset.models import Stocks, HoldingStocks, AssetStatus
from asset.functions import get_info
from datetime import date


def benefit(hs_id):
    hs = HoldingStocks.objects.get(id=hs_id)
    code = hs.stock.code
    data = get_info.stock_overview(code)
    val = (data['price'] - hs.average_price) * hs.num
    holding_time = date.today() - hs.date
    res = {
        "data": {
            "id": id,
            "date": hs.date,
            "code": code,
            "name": hs.stock.name,
            "num": hs.num,
            "average_price": hs.average_price,
        },
        "current_price": data['price'],
        "total": hs.num * data['price'],
        "benefit": val,
        "holding_time": holding_time.days,
    }
    return res


def benefit_all():
    benefit_all = 0
    total_all = 0
    res = dict()
    res["data_all"] = []
    hsa = HoldingStocks.objects.all()
    for hs in hsa:
        tmp = benefit(hs.id)
        res["data"].append(tmp)
        benefit_all += tmp["benefit"]
        total_all += tmp['total']
    res['benefit_all'] = benefit_all
    res['total_all'] = total_all
    return res


def record_status():
    tmp = AssetStatus.objects.get(date=date.today())
    if tmp.__len__ is 1:
        astatus = tmp[0]
    else:
        astatus = AssetStatus()
    current = AssetStatus.objects.all().latest('id')
    data = benefit_all()
    astatus.date = date.today()
    astatus.stocks_value = data['total_all']

    # otherやbuying_power, investmentのアップデートもこの関数でやる？
    astatus.other_value = current.other_value
    astatus.buying_power = current.buying_power
    astatus.investment = current.investment

    astatus.total = astatus.stocks_value + astatus.other_value + astatus.buying_power

    return res

