# coding:utf-8
from asset.models import Stocks, HoldingStocks
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
    aval = 0
    res = dict()
    res["data_all"] = []
    hsa = HoldingStocks.objects.all()
    for hs in hsa:
        tmp = benefit(hs.id)
        res["data"].append(tmp)
        aval += tmp["benefit"]
    res['benefit_all'] = aval
    return res
