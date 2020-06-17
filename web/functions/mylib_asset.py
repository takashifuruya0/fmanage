from web.functions import mylib_scraping, mylib_analysis
from web.models import StockFinancialData, Stock, Entry, AssetStatus, StockValueData
from django.contrib.auth.models import User
import requests
from io import BytesIO
import csv
from django.core import files
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import logging
logger = logging.getLogger('django')


def register_stock(code):
    result = {
        "code": code,
        "stock": None,
        "status": False
    }
    if Stock.objects.filter(code=code).exists():
        raise Exception('Already existing')
    try:
        yf_detail = mylib_scraping.yf_detail(code)
        if yf_detail['status']:
            data = yf_detail['data']
            data.pop('financial_data')
            stock = Stock.objects.create(**data)
            result['stock'] = stock
            result['status'] = True
            logger.info("New stock object of {}".format(stock))
    except Exception as e:
        print(e)
        logger.error(e)
        result['status'] = False
    finally:
        return result


def register_stock_value_data(code):
    '''
    record_stock_value_data
    :desc: kabuoji3からHLOCTを取得し、StockValueDataに格納
    :param code: 銘柄コード
    :return: StockValueDataの追加数等
    '''
    # for result
    counter = 0
    list_added = list()
    # main process
    data = mylib_scraping.kabuoji3(code)
    stock = Stock.objects.get(code=code)
    if data['status']:
        for d in data['data']:
            if StockValueData.objects.filter(stock=stock, date=d[0]).__len__() == 0:
                counter += 1
                s = StockValueData.objects.create(
                    stock=stock,
                    date=d[0],
                    val_open=d[1],
                    val_high=d[2],
                    val_low=d[3],
                    val_close=d[4],
                    turnover=d[5],
                )
                list_added.append(s.date.__str__())
        logger.info('StockValueData of {} are updated'.format(stock))
    result = {
        "counter": counter,
        "stock": {
            "name": stock.name,
            "code": stock.code,
        },
        "list": list_added,
    }
    return result


def register_stock_financial_data(code):
    result = {
        'code': code,
        'StockFinancialData': [],
        'status': False,
    }
    try:
        # 情報取得
        detail = mylib_scraping.yf_detail(code)
        profiles = mylib_scraping.yf_settlement(code, is_consolidated=True)
        if profiles['status'] and profiles['data'][0]['決算期'] is None:
            # 単体の情報を取得
            profiles = mylib_scraping.yf_settlement(code, is_consolidated=False)
        # stock情報
        stock = Stock.objects.get(code=code)
        # 今年度を含めて３年分
        for i in range(3):
            profile = profiles['data'][i]
            if not StockFinancialData.objects.filter(date=profile["決算発表日"], stock__code=code).exists():
                data = {
                    "stock": stock,
                    # profile
                    "date": profile["決算発表日"],
                    'equity': profile['自己資本'],
                    'equity_ratio': profile["自己資本比率"],
                    'capital': profile["資本金"],
                    'operating_income': profile["営業利益"],
                    'assets': profile["総資産"],
                    'recurring_profit': profile["経常利益"],
                    'net_income': profile["当期利益"],
                    'interest_bearing_debt': profile["有利子負債"],
                    'eps': profile["EPS（一株当たり利益）"],
                    'bps': profile["BPS（一株当たり純資産）"],
                    'sales': profile["売上高"],
                    'roa': profile["ROA（総資産利益率）"],
                    'roa_2': profile["総資産経常利益率"],
                    'roe': profile["ROE（自己資本利益率）"],
                }
                # 今年度分はdetail情報を利用
                if i == 0 and detail['status']:
                    data['market_value'] = detail['data']['financial_data']["時価総額"]
                    data['dividend_yield'] = detail['data']['financial_data']["配当利回り（会社予想）"]
                    data['bps_f'] = detail['data']['financial_data']["BPS（実績）"]
                    data['eps_f'] = detail['data']['financial_data']["EPS（会社予想）"]
                    data['pbr_f'] = detail['data']['financial_data']["PBR（実績）"]
                    data['per_f'] = detail['data']['financial_data']["PER（会社予想）"]
                # 保存
                logger.debug(data)
                sfd = StockFinancialData.objects.create(**data)
                result['StockFinancialData'].append(sfd)
        # status=Trueに設定
        result['status'] = True
    except Exception as e:
        print(e)
        logger.error(e)
        # status=Falseに設定
        result['status'] = False
    finally:
        return result


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


def order_process(order, user=None):
    res = {
        "status": False,
        "msg": None,
    }
    try:
        '''chart保存'''
        url_chart = "https://chart.yahoo.co.jp/?code={}.T&tm=6m&type=c&log=off&size=m&over=m25,m75&add=m,r,vm&comp=".format(order.stock.code)
        r = requests.get(url_chart)
        if r.status_code == 200 and not order.stock.is_trust:
            # file
            filename = "{}_{}.png".format(date.today(), order.stock.code)
            fp = BytesIO()
            fp.write(r.content)
            order.chart.save(filename, files.File(fp))
            logger.info("A current chart is added to {}".format(order))
        '''Status更新'''
        astatus_today = AssetStatus.objects.filter(date=date.today())
        if astatus_today:
            astatus = astatus_today[0]
        else:
            astatus = AssetStatus.objects.latest('date')
            astatus.pk = None
            astatus.date = date.today()
        '''買い注文処理'''
        if order.is_buy:
            # status更新
            astatus.buying_power = astatus.buying_power - order.num * order.val - order.commission
            # 買付余力以上は買えません
            if astatus.buying_power < 0:
                logger.error("====== buying_power < 0 ! =====")
                logger.error("order {}".format(order))
                logger.error("buying_power " + str(astatus.buying_power))
                logger.error("order.num " + str(order.num))
                logger.error("order.val " + str(order.val))
                logger.error("order.commision " + str(order.commission))
                raise ValueError("buying_power < 0 !")
            # Entry紐付け
            existing_entries = Entry.objects.filter(stock=order.stock, is_closed=False)
            if existing_entries.count() == 1:
                # 既存Entry(is_plan=True)に紐付け
                entry = existing_entries[0]
                entry.is_in_order = False
                order.entry = entry
            else:
                # Entry作成
                entry = Entry()
                entry.user = User.objects.first() if user is None else user
                entry.stock = order.stock
                entry.border_profit_determination = int(order.val * 1.05)
                entry.border_loss_cut = int(order.val * 0.90)
                entry.save()
                order.entry = entry
            order.save()
            logger.info("{} is linked to {}".format(order, entry))
            # Entry(is_close=False)に基づいて、sum_stock, sum_trustの更新
            astatus.update_status()
            astatus.save()
            # log
            logger.info("AssetStatus is updated")
            logger.info(astatus)
            # res
            res['status'] = True
            res['msg'] = "Buy Order Process was done"
        # 売り
        elif order.is_buy is False:
            entry = Entry.objects.prefetch_related('order_set').filter(is_closed=False, stock=order.stock).last()
            # entry紐付け
            if entry.remaining() >= order.num:
                order.entry = entry
                order.save()
                logger.info("{} is linked to {}".format(order, entry))
            else:
                logger.error("===== entry.remaining - order.num < 0! =====")
                logger.error("order {}".format(order))
                logger.error("entry {}".format(entry))
                logger.error("entry.remaining " + str(entry.remaining()))
                logger.error("order.num " + str(order.num))
                raise ValueError("entry.remaining - order.num < 0!")
            if order.is_nisa:
                # NISA: TAX=0%
                astatus.buying_power = astatus.buying_power + order.num * order.val
                logger.info("TAX 0%:NISA")
            elif order.val - entry.val_buy() > 0:
                # 利益あり＋NISA以外: TAX=20%
                tax = (order.val - entry.val_buy()) * order.num * 0.2
                astatus.buying_power = astatus.buying_power + order.num * order.val - order.commission - tax
                logger.info("TAX 20%:Has benefit and not NISA")
            else:
                # 利益なし＋NISA以外: TAX=0%
                astatus.buying_power = astatus.buying_power + order.num * order.val - order.commission
                logger.info("TAX 0%: Has not benefit and not NISA")
            # Entry(is_close=False)に基づいて、sum_stock, sum_trustの更新
            astatus.update_status()
            astatus.save()
            # log
            logger.info("AssetStatus is updated")
            logger.info(astatus)
            # res
            res['status'] = True
            res['msg'] = "Sell Order Process was done"
    except Exception as e:
        logger.error(e)
        logger.error(order.__dict__)
        res['status'] = False
        res['msg'] = "Process was failed"
    finally:
        return res


def record_asset_status():
    '''
    今日のAssetStatusがある場合：アップデート
    今日のAssetStatusがない場合：前のレコードに基づいて新規作成
    '''
    today = date.today()
    asset_status = AssetStatus.objects.latest('date')
    if asset_status.date == today:
        # 更新
        logger.info("Updating AssetStatus {}".format(asset_status))
        asset_status.update_status()
        logger.info("Completed updating AssetStatus {}".format(asset_status))
    else:
        # 新規作成
        logger.info("Creating AssetStatus {}".format(asset_status))
        asset_status.pk = None
        asset_status.date = today
        asset_status.save()
        logger.info("Completed creating AssetStatus {}".format(asset_status))
    # res
    res = {
        "status": True,
        "asset_status": asset_status,
    }
    return res


def import_trust_0(path, stock):
    '''
    (291113C) ニッセイ外国株式インデックスファンド　向け
    https://www.nam.co.jp/fundinfo/data/csv.php?fund_code=121332
    日付	ファンド名	基準価額	税引前分配金再投資基準価額	純資産総額	前日比
    '''
    datelist = [svd.date for svd in StockValueData.objects.filter(stock=stock)]
    try:
        with open(path, encoding="shift-jis") as f:
            csv_line = csv.reader(f)
            svds = list()
            header = next(csv_line)
            for d in csv_line:
                if not datetime.strptime(d[0], "%Y年%m月%d日").date() in datelist:
                    svd = StockValueData(
                        stock=stock,
                        date=datetime.strptime(d[0], "%Y年%m月%d日").date(),
                        val_high=d[2],
                        val_low=d[2],
                        val_open=d[2],
                        val_close=d[2],
                        turnover=d[4][1:]
                    )
                    svds.append(svd)
            StockValueData.objects.bulk_create(svds)
            logger.info("{}のsvdを{}件作成しました".format(stock.name, len(svds)))
    except Exception as e:
        print(e.args)


def import_trust_1(path, stock):
    '''
    (64317081) SMTJ-REITインデックス･オープン
    https://www.smtam.jp/chart_data/140837/140837.csv
    基準日	基準価額	分配金	純資産総額
    '''
    datelist = [svd.date for svd in StockValueData.objects.filter(stock=stock)]
    try:
        with open(path) as f:
            csv_line = csv.reader(f)
            svds = list()
            header = next(csv_line)
            for d in csv_line:
                if not datetime.strptime(d[0], "%Y/%m/%d").date() in datelist:
                    svd = StockValueData(
                        stock=stock,
                        date=datetime.strptime(d[0], "%Y/%m/%d").date(),
                        val_high=d[1],
                        val_low=d[1],
                        val_open=d[1],
                        val_close=d[1],
                        turnover=float(d[3])*100000000
                    )
                    svds.append(svd)
            StockValueData.objects.bulk_create(svds)
            logger.info("{}のsvdを{}件作成しました".format(stock.name, len(svds)))
    except Exception as e:
        print(e.args)


def register_stock_value_data_alt(code):
    '''
    record_stock_value_data_alt
    :desc: yahooファイナンスからHLOCTを取得し、StockValueDataに格納
    :param code: 銘柄コード
    :return: StockValueDataの追加数等
    '''
    # for result
    counter = 0
    list_added = list()
    list_updated = list()
    # main process
    data = mylib_scraping.yf_detail(code)
    stock = Stock.objects.get(code=code)
    if data['status']:
        today = date.today()
        if StockValueData.objects.filter(stock=stock, date=today).__len__() == 0:
            counter += 1
            if stock.is_trust:
                s = StockValueData.objects.create(
                    stock=stock,
                    date=today,
                    val_open=data['data']['val']*10000,
                    val_high=data['data']['val']*10000,
                    val_low=data['data']['val']*10000,
                    val_close=data['data']['val']*10000,
                    turnover=data['data']['balance'],
                )
            else:
                s = StockValueData.objects.create(
                    stock=stock,
                    date=today,
                    val_open=data['data']['val_open'],
                    val_high=data['data']['val_high'],
                    val_low=data['data']['val_low'],
                    val_close=data['data']['val_close'],
                    turnover=data['data']['turnover'],
                )
            list_added.append(s.date.__str__())
            logger.info('StockValueData of {} is created'.format(stock))
        elif StockValueData.objects.filter(stock=stock, date=today).__len__() == 1:
            counter += 1
            s = StockValueData.objects.filter(stock=stock, date=today)
            if stock.is_trust:
                s.update(
                    val_open=data['data']['val'] * 10000,
                    val_high=data['data']['val'] * 10000,
                    val_low=data['data']['val'] * 10000,
                    val_close=data['data']['val'] * 10000,
                    turnover=data['data']['balance']
                )
            else:
                s.update(
                    val_open=data['data']['val_open'],
                    val_high=data['data']['val_high'],
                    val_low=data['data']['val_low'],
                    val_close=data['data']['val_close'],
                    turnover=data['data']['turnover'],
                )
            list_updated.append(s.first().date.__str__())
            logger.info('StockValueData of {} is updated'.format(stock))
    result = {
        "counter": counter,
        "stock": {
            "name": stock.name,
            "code": stock.code,
        },
        "list_added": list_added,
        "list_updated": list_updated,
    }
    return result


def register_stock_value_data_kabuoji3(code):
    '''
    record_stock_value_data_kabuoji3
    :desc: kabuoji3からHLOCTを取得し、StockValueDataに格納
    :param code: 銘柄コード
    :return: StockValueDataの追加数等
    '''
    # for result
    counter = 0
    list_added = list()
    # main process
    data = mylib_scraping.kabuoji3(code)
    stock = Stock.objects.get(code=code)
    if data['status']:
        for d in data['data']:
            d[0] = datetime.strptime(d[0], "%Y-%m-%d").date()
            if StockValueData.objects.filter(stock=stock, date=d[0]).__len__() == 0:
                counter += 1
                s = StockValueData.objects.create(
                    stock=stock, date=d[0],
                    val_open=d[1],
                    val_high=d[2],
                    val_low=d[3],
                    val_close=d[4],
                    turnover=d[5],
                )
                list_added.append(s.date.__str__())
                logger.info('StockValueData of {} is created'.format(stock))
    result = {
        "counter": counter,
        "stock": {
            "name": stock.name,
            "code": stock.code,
        },
        "list": list_added,
    }
    return result


def analyse_all(days=14):
    stocks = Stock.objects.all()
    od = date.today() - relativedelta(days=days)
    cd = date.today()
    check = list()
    for s in stocks:
        svds = StockValueData.objects.filter(stock=s, date__gte=od, date__lte=cd).order_by('date')
        if svds.exists():
            df = mylib_analysis.prepare(svds)
            # df_trend = mylib_analysis.get_trend(df)
            df_check = mylib_analysis.check(df)
            check += df_check
    check_sorted = sorted(check, key=lambda x: x['date'])
    check_sorted.reverse()
    return check_sorted
