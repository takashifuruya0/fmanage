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
    try:
        tmp = AssetStatus.objects.filter(date=date.today())
        if tmp.__len__() == 1:
            astatus = tmp[0]
            memo = "updated AssetStatus for today"
        else:
            astatus = AssetStatus()
            memo = "create AssetStatus for today"
        # 保有株式を計算
        data = benefit_all()
        astatus.date = date.today()
        astatus.stocks_value = data['total_all']
        # 一つ前のデータからother_value, buying_power, investment,を引き継ぎ
        current = AssetStatus.objects.all().latest('id')
        astatus.other_value = current.other_value
        astatus.buying_power = current.buying_power
        astatus.investment = current.investment
        # total を update
        astatus.total = astatus.stocks_value + astatus.other_value + astatus.buying_power
        astatus.save()
        logger.info(astatus.total)
        #
        status = True
    except Exception as e:
        status = False
        memo = e
    res = {"status": status, "memo": memo,}
    return res


def convert_yen(v):
    v = int(v)
    try:
        if v >= 0:
            new_val = '¥{:,}'.format(v)
        elif v < 0:
            new_val = '-¥{:,}'.format(-v)
    except Exception as e:
            new_val = "-"
    return new_val


def val_color(val):
    if type(val) is str:
        return "black"
    elif val > 0:
        return "black"
    else:
        return "red"
