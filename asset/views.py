from django.shortcuts import render

import requests
from bs4 import BeautifulSoup

# Create your views here.


# 株価取得
def get_stockprice(code):
    base_url = "https://stocks.finance.yahoo.co.jp/stocks/detail/"
    query = {}
    query["code"] = str(code) + ".T"
    ret = requests.get(base_url, params=query)
    try:
        soup = BeautifulSoup(ret.content,"lxml")
        stocktable = soup.find('table', {'class': 'stocksTable'})
        symbol = stocktable.findAll('th', {'class': 'symbol'})[0].text
        stockprice = stocktable.findAll('td', {'class': 'stoksPrice'})[1].text
        stockprice = float(stockprice.replace(",", ""))
        status = "Success"
    except Exception as e:
        symbol = "-"
        stockprice = e
        status = ret.text
    res = {
        "status": status,
        "symbol": symbol,
        "stockprice": stockprice,
        }
    return res

