# coding:utf-8
import requests
from bs4 import BeautifulSoup
import logging
logger = logging.getLogger("django")


def stock_overview(code):
    base_url = "https://stocks.finance.yahoo.co.jp/stocks/detail/"
    query = {}
    query["code"] = str(code)
    ret = requests.get(base_url, params=query)
    try:
        soup = BeautifulSoup(ret.content, "lxml")
        stocktable = soup.find('table', {'class': 'stocksTable'})
        symbol = stocktable.findAll('th', {'class': 'symbol'})[0].text
        stockprice = float(stocktable.findAll('td', {'class': 'stoksPrice'})[1].text.replace(",", ""))
        # 投資信託は10000口単位
        if len(code) > 4:
            stockprice = float(stockprice)/10000
        memo = "Success"
        status = True
    except Exception as e:
        symbol = "-"
        stockprice = e
        status = False
        memo = ret.text
    res = {
        "code": code,
        "name": symbol,
        "price": stockprice,
        "status": status,
        "memo": memo,
    }
    return res


def kabuoji3(code):
    base_url = "https://kabuoji3.com/stock/" + str(code) + "/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    ret = requests.get(base_url, headers=headers)
    try:
        soup = BeautifulSoup(ret.content, "lxml")
        stocktable = soup.find('table', {'class': 'stock_table stock_data_table'})
        records = stocktable.find_all('tr')
        records.pop(0)
        data = list()
        for r in records:
            tmp = list()
            for i in range(7):
                tmp.append(r.select('td:nth-of-type(' + str(i+1) + ')')[0].text)
            data.append(tmp)
        msg = "Done"
        status = True
    except Exception as e:
        msg = "code" + str(code) + ":" + e
        data = None
        status = False
    res = {
        "msg": msg,
        "status": status,
        "data": data,
    }
    return res
