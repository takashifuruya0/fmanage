# coding:utf-8
from asset.models import Stocks, HoldingStocks, AssetStatus
from asset.functions import get_info
from datetime import date
import logging
logger = logging.getLogger("django")


def benefit(hs_id):
    hs = HoldingStocks.objects.get(id=hs_id)
    code = hs.stock.code
    data = get_info.stock_overview(code)
    if data['status']:
        cval = data['price']
        val = (data['price'] - hs.average_price) * hs.num
        total = hs.num * data['price']
    else:
        cval = "-"
        val = "-"
        total = "-"
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
        "current_price": cval,
        "total": total,
        "benefit": val,
        "holding_time": holding_time.days,
    }
    return res


def benefit_all():
    benefits = 0
    totals = 0
    res = {
        "data_all": [],
    }
    hsa = HoldingStocks.objects.all()
    for hs in hsa:
        tmp = benefit(hs.id)
        res["data_all"].append(tmp)
        try:
            benefits += tmp["benefit"]
            totals += tmp['total']
        except Exception as e:
            logger.error("adding in benefit_all() was failed")
            logger.error(e)
            benefits = 0
            totals = 0

    res['benefit_all'] = benefits
    res['total_all'] = totals
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

