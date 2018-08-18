from django.shortcuts import render

import logging
logger = logging.getLogger("django")
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
from asset.models import Stocks, HoldingStocks, AssetStatus
from asset.functions import get_info, mylib_asset
# Template-view
from django.views.generic.edit import CreateView


# 概要
def dashboard(request):

    # 保有株リスト
    hstocks = list()
    hss = HoldingStocks.objects.all()
    for hs in hss:
        name = hs.stock.name
        code = hs.stock.code
        num = hs.num
        date = hs.date
        aprice = hs.average_price
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
    # 買付余力
    astatus = AssetStatus.objects.all().order_by('date')
    investment = astatus.last().investment
    buying_power = astatus.last().buying_power
    total_b = total + buying_power

    # return
    output = {
        "today": date.today(),
        "hstocks": hstocks,
        "total": total,
        "benefit": benefit,
        "buying_power": buying_power,
        "total_color": mylib_asset.val_color(benefit),
        "total_b": total_b,
        "investment": investment,
        "astatus": astatus,
    }
    return render(request, 'asset/dashboard.html', output)


class StocksCreateView(CreateView):
    model = Stocks
    fields = ("code", "name")  # リストもしくはタプル


class HoldingStocksCreateView(CreateView):
    model = HoldingStocks
    fields = ("stock", "date", "average_price", "num")  # リストもしくはタプル