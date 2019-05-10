# coding:utf-8
from datetime import date
from asset.models import Stocks, EntryExit
from django.core import files
from io import BytesIO
import requests
from asset.functions.get_info import stock_overview


def make_testdata(code):
    url = "https://chart.yahoo.co.jp/?code={}.T&tm=6m&type=c&log=off&size=m&over=m25,m75&add=m,r,vm&comp=".format(code)
    r = requests.get(url)
    if r.status_code == 200:
        ee = EntryExit()
        # date
        ee.date_entry = date.today()
        # stock
        info = stock_overview(code)
        if Stocks.objects.filter(code=code).exists():
            stock = Stocks.objects.get(code=code)
        else:
            stock = Stocks.objects.create(
                name=info['name'],
                code=info['code']
            )
        ee.stock = stock
        # num
        ee.num_entry = 100
        # price
        ee.price_entry = info['price']
        ee.price_set_profit = round(info['price'] * 1.1, 1)
        ee.price_loss_cut = round(info['price'] * 0.9, 1)
        # file
        filename = "{}_{}.png".format(date.today(), code)
        fp = BytesIO()
        fp.write(r.content)
        ee.chart_entry.save(filename, files.File(fp))
        return ee
    else:
        print("Failed")
        return False