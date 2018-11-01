from django.shortcuts import render

import logging
logger = logging.getLogger("django")
import requests

from bs4 import BeautifulSoup
from datetime import date, datetime
from kakeibo.functions.mylib import time_measure
from asset.models import Stocks, HoldingStocks, AssetStatus, Orders
from asset.functions import get_info, mylib_asset
from asset.forms import AddInvestmentForm, OrdersForm, StocksForm
# Template-view
from django.views.generic.edit import CreateView
# login
from django.contrib.auth.decorators import login_required


# 概要
@login_required
@time_measure
def dashboard(request):
    # FormのPost処理
    if request.method == "POST":
        logger.debug(request.POST)
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
                logger.info("Additional investment was registered")
            except Exception as e:
                logger.error(e)
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
                logger.info("New stock was registered")
            except Exception as e:
                logger.error(e)
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
                order.commission = post_data.get('commission')
                order.is_nisa = post_data.get('is_nisa')
                order.save()
                logger.info("New oreder was registered")
                
                # Status
                astatus = AssetStatus.objects.all().order_by('date').last()
                # 買い
                if order.order_type == "現物買い":
                    astatus.buying_power = astatus.buying_power - order.num * order.price - order.commission
                    astatus.stocks_value = astatus.stocks_value + order.num * order.price
                    astatus.total = astatus.buying_power + astatus.stocks_value + astatus.other_value
                    # holding stock に追加
                    hos = HoldingStocks.objects.filter(stock=order.stock)
                    if hos:
                        ho = hos[0]
                        ho.price = (ho.price * ho.num + order.price * order.num) / (ho.num + order.num)
                        ho.num = ho.num + order.num
                        ho.save()
                    else:
                        ho = HoldingStocks()
                        ho.stock = order.stock
                        ho.num = order.num
                        ho.price = order.price
                        ho.date = order.datetime.date()
                        ho.save()
                # 売り
                elif order.order_type == "現物売り":
                    if order.is_nisa:
                        # NISA: TAX=0%
                        astatus.buying_power = astatus.buying_power + order.num * order.price
                    else:
                        # NISA以外: TAX=20%
                        astatus.buying_power = astatus.buying_power + (order.num * order.price)*0.8 - order.commission
                    astatus.stocks_value = astatus.stocks_value - order.num * order.price
                    astatus.total = astatus.buying_power + astatus.stocks_value + astatus.other_value
                    # holding stock から削除
                    ho = HoldingStocks.objects.get(stock=order.stock)
                    ho.price = (ho.num * ho.price - order.num * order.price)/(ho.num - order.num)
                    ho.num = ho.num - order.num
                    if ho.num == 0:
                        ho.remove()
                    else:
                        ho.save()

            except Exception as e:
                logger.error(e)
                print(post_data)

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
        date = hs.date
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
            "date": date,
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

    # return
    output = {
        "today": date.today(),
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
    }
    return render(request, 'asset/dashboard.html', output)


class StocksCreateView(CreateView):
    model = Stocks
    fields = ("code", "name")  # リストもしくはタプル


class HoldingStocksCreateView(CreateView):
    model = HoldingStocks
    fields = ("stock", "date", "price", "num")  # リストもしくはタプル


class OrdersCreateView(CreateView):
    model = Orders
    fields = ("datetime", "order_type", "stock", "num", "price", "commission", "is_nisa")