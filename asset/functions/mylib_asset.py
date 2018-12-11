# coding:utf-8
from asset.models import Stocks, HoldingStocks, AssetStatus
from asset.functions import get_info
from datetime import date
import logging
logger = logging.getLogger("django")


# hs_idのHoldingStocksについて、含み損益を計算する
def get_benefit(hs_id):
    hs = HoldingStocks.objects.get(id=hs_id)
    code = hs.stock.code
    current_price = hs.get_current_price()
    benefit = (current_price - hs.price) * hs.num
    total = current_price * hs.num
    holding_time = hs.get_holding_time()
    res = {
        "data": {
            "id": hs_id,
            "date": hs.date,
            "code": code,
            "name": hs.stock.name,
            "num": hs.num,
            "price": hs.price,
        },
        "current_price": current_price,
        "total": total,
        "benefit": benefit,
        "holding_time": holding_time,
    }
    return res


# すべてのHoldingStocksについて、含み損益を計算する
def get_benefit_all():
    benefit_stock = 0
    benefit_trust = 0
    total_stock = 0
    total_trust = 0
    res = {
        "data_all": [],
    }
    hsa = HoldingStocks.objects.all()
    for hs in hsa:
        tmp = get_benefit(hs.id)
        res["data_all"].append(tmp)
        if len(hs.stock.code) == 4:
            total_stock += tmp['total']
            benefit_stock += tmp["benefit"]
        else:
            total_trust += tmp['total']
            benefit_trust += tmp["benefit"]
    # return
    res['total_all'] = total_stock + total_trust
    res['total_stock'] = total_stock
    res['total_trust'] = total_trust
    res['benefit_all'] = benefit_stock + benefit_trust
    res['benefit_stock'] = benefit_stock
    res['benefit_trust'] = benefit_trust
    return res


# 現在の資産運用状況を記録
def record_status():
    try:
        tmp = AssetStatus.objects.filter(date=date.today())
        if tmp:
            astatus = tmp[0]
            memo = "updated AssetStatus for today"
        else:
            astatus = AssetStatus.objects.all().order_by('date').last()
            astatus.pk = None
            astatus.date = date.today()
            astatus.save()
            memo = "create AssetStatus for today"
        logger.info(memo)
        # 保有株式・投資信託・の現在価値と合計値を計算
        data = get_benefit_all()
        astatus.stocks_value = data['total_stock']
        astatus.other_value = data['total_trust']
        astatus.total = data['total_all'] + astatus.buying_power
        # save
        astatus.save()
        logger.info("Total: "+str(astatus.total))
        status = True
    except Exception as e:
        memo = e
        logger.error(e)
        status = False
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
        logger.error(e)
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
        logger.info(msg)
    except Exception as e:
        status = False
        msg = "Code " + str(code) + " was failed to register"
        logger.error(msg)
    res = {"status": status, "message": msg,}
    return res


def order_process(order):
    smsg = emsg = ""
    try:
        # Status
        astatus_today = AssetStatus.objects.filter(date=date.today())
        if astatus_today:
            astatus = astatus_today[0]
        else:
            astatus = AssetStatus.objects.last()
            astatus.pk = None
            astatus.date = date.today()
        # 買い
        logger.info(order.order_type)
        if order.order_type == "現物買":
            # status更新
            astatus.buying_power = astatus.buying_power - order.num * order.price - order.commission
            # 買付余力以上は買えません
            if astatus.buying_power < 0:
                logger.error("buying_power " + str(astatus.buying_power))
                logger.error("order.num " + str(order.num))
                logger.error("order.price " + str(order.price))
                logger.error("order.commision " + str(order.commission))
                raise ValueError("buying_power < 0 !")
            if len(order.stock.code) == 4:
                astatus.stocks_value += order.num * order.price
            else:
                astatus.other_value += order.num * order.price
            astatus.total = astatus.buying_power + astatus.stocks_value + astatus.other_value
            astatus.save()
            logger.info("AssetStatus is updated")
            logger.info(astatus)
            # holding stock に追加
            hos = HoldingStocks.objects.filter(stock=order.stock)
            if hos:
                ho = hos[0]
                ho.price = (ho.price * ho.num + order.price * order.num) / (ho.num + order.num)
                ho.num = ho.num + order.num
                ho.save()
                logger.info("HoldingStock is updated")
                logger.info(ho)
            else:
                ho = HoldingStocks()
                ho.stock = order.stock
                ho.num = order.num
                ho.price = order.price
                ho.date = date.today()
                ho.save()
                logger.info("New HoldingStock is created")
                logger.info(ho)
            smsg = "Buy-order process was completed"
        # 売り
        elif order.order_type == "現物売":
            price = HoldingStocks.objects.get(stock=order.stock).price
            # status更新
            if order.is_nisa:
                # NISA: TAX=0%
                astatus.buying_power = astatus.buying_power + order.num * order.price
                logger.info("TAX 0%:NISA")
            elif order.price - price > 0:
                # 利益あり＋NISA以外: TAX=20%
                tax = (order.price - price) * order.num * 0.2
                astatus.buying_power = astatus.buying_power + order.num * order.price - order.commission -tax
                logger.info("TAX 20%:Has benefit and not NISA")
            else:
                # 利益なし＋NISA以外: TAX=0%
                astatus.buying_power = astatus.buying_power + order.num * order.price - order.commission
                logger.info("TAX 0%: Has not benefit and not NISA")
            if len(order.stock.code) == 4:
                astatus.stocks_value -= order.num * order.price
            else:
                astatus.other_value -= order.num * order.price
            astatus.total = astatus.buying_power + astatus.stocks_value + astatus.other_value
            astatus.save()
            logger.info("AssetStatus is updated")
            logger.info(astatus)
            # holding stock から削除
            ho = HoldingStocks.objects.get(stock=order.stock)
            if ho.num - order.num == 0:
                ho.delete()
                logger.info("This entry is exited")
            elif ho.num - order.num > 0:
                # ho.price = round((ho.num * ho.price - order.num * order.price) / (ho.num - order.num), 0)
                ho.num = ho.num - order.num
                ho.save()
                logger.info("This entry is still on")
            else:
                # 保有数以上は売れません
                logger.error("ho.num " + str(ho.num))
                logger.error("order.num " + str(order.num))
                raise ValueError("ho.num - order.num < 0!")
            smsg = "Sell-order process was completed"
    except Exception as e:
        emsg = e
    return smsg, emsg


def get_commission(fee):
    if fee < 50000:
        return 54
    elif fee < 100000:
        return 97
    elif fee < 200000:
        return 113
    elif fee < 500000:
        return 270
    elif fee < 1000000:
        return 525
    elif fee < 1500000:
        return 628
    elif fee < 30000000:
        return 994
    else:
        return 1050


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