from django.shortcuts import render, HttpResponse, Http404
import json
import logging
logger = logging.getLogger("django")
import requests

from bs4 import BeautifulSoup
from datetime import date, datetime
from kakeibo.functions.mylib import time_measure
from asset.models import Stocks, HoldingStocks, AssetStatus, Orders, StockDataByDate
from asset.functions import get_info, mylib_asset
from asset.forms import AddInvestmentForm, OrdersForm, StocksForm
# Template-view
from django.views.generic.edit import CreateView
# login
from django.contrib.auth.decorators import login_required
# pandas
from django_pandas.io import read_frame


# 概要
@login_required
@time_measure
def asset_dashboard(request):
    # msg
    today = date.today()
    smsg = emsg = ""
    # FormのPost処理
    if request.method == "POST":
        logger.debug(request.POST)
        print(request.POST)
        # Add investment
        if request.POST['post_type'] == "add_investment":
            try:
                form = AddInvestmentForm(request.POST)
                form.is_valid()
                post_data = form.cleaned_data
                astatus = AssetStatus.objects.all().order_by('date').last()
                astatus.investment = astatus.investment + post_data.get('value')
                astatus.buying_power = astatus.buying_power + post_data.get('value')
                astatus.total = astatus.total + post_data.get('value')
                astatus.save()
                smsg = "Additional investment was registered"
                logger.info(smsg)
            except Exception as e:
                emsg = e
                logger.error(emsg)

        # Stock
        elif request.POST['post_type'] == "stock_form":
            try:
                form = StocksForm(request.POST)
                form.is_valid()
                post_data = form.cleaned_data
                stock = Stocks()
                stock.code = post_data.get('code')
                stock.name = get_info.stock_overview(stock.code)['name']
                stock.save()
                smsg = "New stock was registered"
                logger.info(smsg)
            except Exception as e:
                emsg = e
                logger.error(emsg)
        # Order
        elif request.POST['post_type'] == "order_form":
            try:
                form = OrdersForm(request.POST)
                form.is_valid()
                post_data = form.cleaned_data
                order = Orders()
                order.datetime = post_data.get('datetime')
                order.order_type = post_data.get('order_type')
                order.stock = post_data.get('stock')
                order.num = post_data.get('num')
                order.price = post_data.get('price')
                order.is_nisa = post_data.get('is_nisa')
                order.commission = mylib_asset.get_commission(order.num * order.price) if order.is_nisa else 0
                order.save()
                smsg = "New order was registered"
                logger.info(smsg)
                
                smsg, emsg = mylib_asset.order_process(order)
                if emsg:
                    raise ValueError(emsg)
                else:
                    logger.info(smsg)
            except Exception as e:
                emsg = e
                logger.error(emsg)

    # Form
    stock_form = StocksForm()
    order_form = OrdersForm()
    add_investment_form = AddInvestmentForm()

    # 保有株リスト：現在値で登録
    hstocks = list()
    hss = HoldingStocks.objects.all()
    for hs in hss:
        name = hs.stock.name
        code = hs.stock.code
        num = hs.num
        hsdate = hs.date
        aprice = hs.price
        # scraping
        data = get_info.stock_overview(code)
        if data['status']:
            cprice = data['price']
            ctotal = cprice * num
            benefit = (cprice - aprice) * num
        else:
            cprice = "-"
            ctotal = "-"
            benefit = "-"

        res = {
            "date": hsdate,
            "name": name,
            "code": code,
            "num": num,
            "aprice": aprice,
            "atotal": aprice * num,
            "cprice": cprice,
            "ctotal": ctotal,
            "benefit": benefit,
            "color": mylib_asset.val_color(benefit),
        }
        hstocks.append(res)

    # 総資産
    total = mylib_asset.benefit_all()['total_all']
    benefit = mylib_asset.benefit_all()['benefit_all']
    # ステータス
    astatus = AssetStatus.objects.all().order_by('date')
    alatest = astatus.last()
    try:
        astatus_recent = astatus[len(astatus) - 15:len(astatus)]
    except Exception as e:
        logger.error(e)
        astatus_recent = None
    # 現在のトータル
    total_b = total + alatest.buying_power + alatest.other_value
    # 最近のorder
    orders = Orders.objects.all().order_by('-datetime')[:10]

    # return
    output = {
        "today": today,
        "hstocks": hstocks,
        "total": total,
        "benefit": benefit,
        "alatest": alatest,
        "order_form": order_form,
        "stock_form": stock_form,
        "add_investment_form": add_investment_form,
        "total_color": mylib_asset.val_color(benefit),
        "total_b": total_b,
        "astatus": astatus,
        "astatus_recent": astatus_recent,
        "orders": orders,
        "smsg": smsg,
        "emsg": emsg,
    }
    return render(request, 'asset/adashboard.html', output)


class StocksCreateView(CreateView):
    model = Stocks
    fields = ("code", "name")  # リストもしくはタプル


class HoldingStocksCreateView(CreateView):
    model = HoldingStocks
    fields = ("stock", "date", "price", "num")  # リストもしくはタプル


class OrdersCreateView(CreateView):
    model = Orders
    fields = ("datetime", "order_type", "stock", "num", "price", "commission", "is_nisa")


def ajax(request):
    if request.method == 'POST':
        # response = json.dumps({'your_surprise_txt': "surprise_txt" })  # JSON形式に直して・・
        # return HttpResponse(response, content_type="text/javascript")  # 返す。JSONはjavascript扱いなのか・・
        name = get_info.stock_overview(request.POST['code'])['name']
        return HttpResponse(name)
    else:
        raise Http404  # GETリクエストを404扱いにしているが、実際は別にしなくてもいいかも


def analysis(request):
    stocks = Stocks.objects.all()
    code = request.GET.get(key='code', default=None)
    length = request.GET.get(key='length', default=None)
    # GETパラメータcodeが指定無しの場合、Stocksの1番目を利用
    if not code:
        code = Stocks.objects.first().code
    stock = stocks.get(code=code)
    sdbds = StockDataByDate.objects.filter(stock__code=code).order_by('date')
    df = read_frame(sdbds)

    # 終値前日比, 出来高前日比
    df['val_end_diff'] = -(df['val_end'].shift() - df['val_end'])
    df['val_end_diff_percent'] = round(-(df['val_end'].shift() - df['val_end'])/df['val_end'].shift()*100, 1)
    df['turnover_diff'] = -(df['turnover'].shift() - df['turnover'])
    df['turnover_diff_percent'] = round(-(df['turnover'].shift() - df['turnover'])/df['turnover'].shift()*100, 1)
    # 終値-始値
    df['val_end-start'] = df['val_end'] - df['val_start']
    # 陽線/陰線
    df['is_positive'] = False
    df['is_positive'] = df['is_positive'].where(df['val_end-start'] < 0, True)
    # 下ひげ
    df['lower_mustache'] = (df['val_start'] - df['val_low']).where(df['is_positive'], df['val_end'] - df['val_low'])
    # 上ひげ
    df['upper_mustache'] = (df['val_high'] - df['val_end']).where(df['is_positive'], df['val_high'] - df['val_start'])
    # 移動平均
    df['ma25'] = df.val_end.rolling(window=25, min_periods=1).mean()
    df['ma75'] = df.val_end.rolling(window=75, min_periods=1).mean()
    df['madiff'] = df.ma25 - df.ma75

    # length指定ありの場合
    if length:
        df = df.tail(int(length))

    # GOLDEN CROSS / DEAD CROSS
    cross = {
        "golden": list(),
        "dead": list(),
        "date": list()
    }
    recent_golden = None
    recent_dead = None
    for i in range(1, len(df)):
        if df.iloc[i - 1]['madiff'] < 0 and df.iloc[i]['madiff'] > 0:
            print("{}:GGOLDEN CROSS".format(df.iloc[i]["date"]))
            cross['golden'].append(df.iloc[i]['ma25'])
            cross['dead'].append(None)
            recent_golden = df.iloc[i]["date"]
        elif df.iloc[i - 1]['madiff'] > 0 and df.iloc[i]['madiff'] < 0:
            print("{}:DEAD CROSS".format(df.iloc[i]["date"]))
            cross['golden'].append(None)
            cross['dead'].append(df.iloc[i]['ma25'])
            recent_dead = df.iloc[i]["date"]
        else:
            cross['golden'].append(None)
            cross['dead'].append(None)
        cross['date'].append(df.iloc[i]["date"])

    # NaN行を削除
    # df = df.dropna()

    # mark
    mark = list()
    # 0. たくり線・勢力線// 前日にカラカサか下影陰線→◯。3日前~2日前で陰線だったら◎
    if df.iloc[0]['lower_mustache'] > df.iloc[0]['upper_mustache']:
        mark.append("◯")
        if not df.iloc[1]['is_positive'] and not df.iloc[2]['is_positive']:
            mark.append("◎")
    else:
        mark.append("")
    # 1. 包線
    mark.append("")
    # 2. はらみ線
    mark.append("")
    # 3. 上げ三法
    mark.append("")
    # 4. 三空叩き込み
    mark.append("")
    # 5. 三手大陰線
    mark.append("")
    # 6. ゴールデンクロス
    mark.append(recent_golden)
    # 7. デッドクロス
    mark.append(recent_dead)

    # 降順
    df_descending = df.sort_values('date', ascending=False)


    output = {
        "stocks": stocks,
        "stock": stock,
        "df_ascending": df,
        "df_descending": df_descending,
        "mark": mark,
        "cross": cross,
        "length": length,
    }
    print(df_descending.iterrows())
    return render(request, 'asset/analysis.html', output)