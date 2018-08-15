# coding:utf-8
import requests
from bs4 import BeautifulSoup


def stock_overview(code):
    base_url = "https://stocks.finance.yahoo.co.jp/stocks/detail/"
    query = {}
    query["code"] = str(code) + ".T"
    ret = requests.get(base_url, params=query)
    try:
        soup = BeautifulSoup(ret.content, "lxml")
        stocktable = soup.find('table', {'class': 'stocksTable'})
        symbol = stocktable.findAll('th', {'class': 'symbol'})[0].text
        stockprice = stocktable.findAll('td', {'class': 'stoksPrice'})[1].text
        stockprice = float(stockprice.replace(",", ""))
        memo = "Success"
    except Exception as e:
        symbol = "-"
        stockprice = e
        memo = ret.text
    res = {
        "code": code,
        "name": symbol,
        "price": stockprice,
        "status": memo,
    }
    return res
