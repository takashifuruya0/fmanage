from django.shortcuts import render

import logging
logger = logging.getLogger("django")
import requests
from bs4 import BeautifulSoup
from datetime import date, datetime
from asset.models import Stocks, HoldingStocks
from asset.functions import get_info, asset_calculation


# 概要
def dashboard(request):

    def val_color(val):
        if type(val) is str:
            return "black"
        elif val > 0:
            return "black"
        else:
            return "red"

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
            "color": val_color(benefit),
        }
        hstocks.append(res)

    # 総資産
    total = asset_calculation.benefit_all()['total_all']
    benefit = asset_calculation.benefit_all()['benefit_all']

    # return
    output = {
        "today": date.today(),
        "hstocks": hstocks,
        "total": total,
        "benefit": benefit,
        "total_color": val_color(benefit),
    }
    return render(request, 'asset/dashboard.html', output)


