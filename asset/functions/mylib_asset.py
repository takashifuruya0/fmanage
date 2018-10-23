# coding:utf-8
from asset.models import Stocks, HoldingStocks, AssetStatus
from asset.functions import get_info
from datetime import date
import logging
logger = logging.getLogger("django")


# hs_idのHoldingStocksについて、含み損益を計算する
def benefit(hs_id):
    hs = HoldingStocks.objects.get(id=hs_id)
    code = hs.stock.code
    data = get_info.stock_overview(code)
    if data['status']:
        cval = data['price']
        val = (data['price'] - hs.price) * hs.num
        total = hs.num * data['price']
    else:
        cval = "-"
        val = "-"
        total = "-"
    holding_time = date.today() - hs.date
    res = {
        "data": {
            "id": hs_id,
            "date": hs.date,
            "code": code,
            "name": hs.stock.name,
            "num": hs.num,
            "price": hs.price,
        },
        "current_price": cval,
        "total": total,
        "benefit": val,
        "holding_time": holding_time.days,
    }
    return res


# すべてのHoldingStocksについて、含み損益を計算する
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


# 現在の資産運用状況を記録
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


# 円表示に変更
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


# 負の値にはred, それ以外にはBlackを返す
def val_color(val):
    if type(val) is str:
        return "black"
    elif val > 0:
        return "black"
    else:
        return "red"


# 証券コードcodeの株式をStocksに保存
def register_stocks(code):
    try:
        data = get_info.stock_overview(code)
        stock = Stocks()
        stock.code = code
        stock.name = data['name']
        status = True
        msg = "Code " + str(code) + " was successfully registered"
    except Exception as e:
        status = False
        msg = "Code " + str(code) + " was failed to register"
    res = {"status": status, "message": msg,}
    return res


# これまでの資産運用状況を引き継ぎ
def inherit_asset_status():
    dates = [
        [2018, 8, 10],
        [2018, 8, 3],
        [2018, 7, 27],
        [2018, 7, 20],
        [2018, 7, 13],
        [2018, 7, 6],
        [2018, 6, 29],
        [2018, 6, 22],
        [2018, 6, 15],
        [2018, 6, 8],
        [2018, 6, 1],
        [2018, 5, 25],
        [2018, 5, 18],
        [2018, 5, 11],
        [2018, 5, 4],
        [2018, 4, 27],
        [2018, 4, 20],
        [2018, 4, 13],
        [2018, 4, 6],
        [2018, 4, 3],
        [2018, 3, 23],
        [2018, 3, 2],
        [2018, 2, 1],
        [2017, 10, 15],
        [2017, 9, 24],
        [2017, 7, 23],
        [2017, 7, 8],
        [2017, 6, 24],
        [2017, 6, 16],
        [2017, 6, 3],
        [2017, 5, 27],
        [2017, 5, 22],
        [2017, 5, 15],
        [2017, 5, 13],
        [2017, 4, 29],
        [2017, 4, 22],
        [2017, 4, 15],
        [2017, 4, 8],
        [2017, 4, 1],
        [2017, 3, 21],
        [2017, 3, 3],
        [2017, 2, 24],
        [2017, 2, 10],
    ]
    sums = [
        842040,
        830040,
        821240,
        821640,
        827440,
        877040,
        847640,
        841840,
        819840,
        830240,
        861840,
        844640,
        819040,
        827840,
        845240,
        845640,
        864240,
        888440,
        902240,
        931040,
        976840,
        948894,
        867554,
        966846,
        964058,
        957144,
        967628,
        948910,
        944611,
        959797,
        940696,
        945695,
        951998,
        961123,
        980784,
        942797,
        922794,
        938142,
        958342,
        981843,
        968768,
        961128,
        928848,
    ]
    for d, v in zip(dates, sums):
        ass = AssetStatus()
        ass.date = date(d[0], d[1], d[2])
        ass.total = v
        ass.stocks_value = v
        ass.investment = 960640
        ass.buying_power = 0
        ass.other_value = 0
        ass.save()


