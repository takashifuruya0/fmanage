from django.shortcuts import render, HttpResponse, Http404
import json
import logging
logger = logging.getLogger("django")
import requests

from bs4 import BeautifulSoup
from datetime import date, datetime
from kakeibo.functions.mylib import time_measure
from asset.models import Stocks, HoldingStocks, AssetStatus, Orders, StockDataByDate
from asset.functions import get_info, mylib_asset, analysis_asset
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


@login_required
@time_measure
def analysis_list(request):
    stocks = dict()
    for stock in Stocks.objects.all():
        sdbd = StockDataByDate.objects.filter(stock=stock).order_by('date')
        df = analysis_asset.analyse_stock_data(read_frame(sdbd))
        mark = analysis_asset.check_mark(df)
        # date降順に並び替えて、先頭を取得
        df = df.sort_values('date', ascending=False).head(1)
        stocks[stock.code] = {
            "name": stock.name,
            "val_end": df.val_end,
            "val_end_diff_percent": float(df.val_end_diff_percent),
            "turnover": df.turnover,
            "turnover_diff_percent": float(df.turnover_diff_percent),
            "mark": mark,
        }
    # for stock in stocks:
    output = {
        "stocks": stocks,
        "mark": mark,
    }
    return render(request, 'asset/analysis_list.html', output)


@login_required
@time_measure
def analysis_detail(request, code):
    stocks = Stocks.objects.all()
    length = request.GET.get(key='length', default=None)
    stock = stocks.get(code=code)
    sdbds = StockDataByDate.objects.filter(stock__code=code).order_by('date')
    df = analysis_asset.analyse_stock_data(read_frame(sdbds))

    # length指定ありの場合
    if length:
        df = df.tail(int(length))
        print(int(length))

    # GOLDEN CROSS / DEAD CROSS
    cross = analysis_asset.get_cross(df)

    # mark
    mark = analysis_asset.check_mark(df)

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
    return render(request, 'asset/analysis_detail.html', output)
