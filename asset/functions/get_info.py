# coding:utf-8
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import logging
logger = logging.getLogger("django")


def stock_overview(code):
    base_url = "https://stocks.finance.yahoo.co.jp/stocks/detail/"
    res = {
        key: None
        for key in ("code", "name", "price", "status", "market", "industry", "memo",)
    }
    res['code'] = code
    query = {}
    query["code"] = str(code)
    ret = requests.get(base_url, params=query)
    try:
        soup = BeautifulSoup(ret.content, "lxml")
        stocktable = soup.find('table', {'class': 'stocksTable'})
        res['name'] = stocktable.findAll('th', {'class': 'symbol'})[0].text
        # 投資信託は10000口単位
        price = float(stocktable.findAll('td', {'class': 'stoksPrice'})[1].text.replace(",", ""))
        res['price'] = float(price)/10000 if len(str(code)) > 4 else price
        # 業界 or 投資信託
        res['industry'] = soup.find('dd', {'class': 'category'}).text
        # 市場：株のみ
        if len(code) == 4:
            res['market'] = soup.findAll('span', {'class': 'stockMainTabName'})[0].text
        # memo
        res['memo'] = "Success"
        res['status'] = True
    except Exception as e:
        logger.error(e)
        res['memo'] = e
        res['status'] = False
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
                tmp.append(r.select('td:nth-of-type({0})'.format(i+1))[0].text)
            data.append(tmp)
        msg = "Done"
        status = True
    except Exception as e:
        msg = "code {0} : {1}".format(code, e)
        data = None
        status = False
    res = {
        "msg": msg,
        "status": status,
        "data": data,
    }
    return res


def stock_finance_info(code):
    base_url = "https://stocks.finance.yahoo.co.jp/stocks/detail/"
    query = {}
    query["code"] = str(code)
    ret = requests.get(base_url, params=query)
    try:
        soup = BeautifulSoup(ret.content, "lxml")
        chartfinance = soup.findAll('div', {'class': 'chartFinance'})[1]
        # 値の取得
        vals = [
            dd.text.replace(",", "").replace("\n", "").replace("(連) ", "")
            for dd in chartfinance.findAll('strong')
        ]
        # タイトルの取得
        dts = chartfinance.findAll('dt')
        keys = list()
        for dt in dts:
            # 補足が付いているので、前処理でタイトルのみ抽出
            splited = dt.text.split("\n")
            if splited[0] == "":
                keys.append(splited[1])
            else:
                keys.append(splited[0])
        # data設定
        data = {
            k: None if v == "---" else v
            for k, v in zip(keys, vals)
        }
        data['時価総額'] = int(data['時価総額'])*1000000

    except Exception as e:
        logger.error(e)
        data = dict()
    finally:
        return data


def stock_settlement_info(code):
    url = "https://profile.yahoo.co.jp/consolidate/{}".format(code)
    ret = requests.get(url)
    data = dict()
    try:
        soup = BeautifulSoup(ret.content, "lxml")
        table = soup.find('table', {'class': 'yjMt'})
        trs = table.findAll('tr')
        for tr in trs:
            tds = tr.findAll('td')
            data[tds[0].text] = tds[1].text.replace("%", "")
    except Exception as e:
        logger.error(e)
    finally:
        return data

    # 'BPS（一株当たり純資産）'
    # '178.37円'
    # '経常利益'
    # '40,714百万円'
    # '営業利益'
    # '‥百万円'
    # '総資産'
    # '1,141,926百万円'
    # '総資産経常利益率'
    # '3.76%'
    # '自己資本'
    # '212,559百万円'
    # '自己資本比率'
    # '18.6%'
    # 'EPS（一株当たり利益）'
    # '11.11円'
    # '資本金'
    # '30,679百万円'
    # 'ROA（総資産利益率）'
    # '1.22%'
    # '決算期'
    # '2019年3月期'
    # 'ROE（自己資本利益率）'
    # '6.24%'
    # '当期利益'
    # '13,236百万円'
    # '売上高'
    # '147,288百万円'


def stock_settlement_info_rev(code):
    url = "https://profile.yahoo.co.jp/consolidate/{}".format(code)
    ret = requests.get(url)
    data = dict()
    # table取得
    try:
        soup = BeautifulSoup(ret.content, "lxml")
        table = soup.find('table', {'class': 'yjMt'})
        trs = table.findAll('tr')
    except Exception as e:
        logger.error(e)
        return False
    # 最終更新日
    try:
        d = soup.find('div', {'class': 'yjSt info'}).text.split("：")[1]
        data['最終更新日'] = datetime.strptime(d, '%Y年%m月%d日').date()
    except Exception as e:
        logger.warning(e)

    # tableから
    for tr in trs:
        try:
            tds = tr.findAll('td')
            text = tds[1].text.replace("%", "").replace(",", "").replace("円", "")
            if "百万" in text:
                text = int(text.replace("百万", "")) * 1000000
            elif "年" in text and "月" in text:
                if "日" in text:
                    # 決算発表日
                    text = datetime.strptime(text, "%Y年%m月%d日").date()
                else:
                    # 決算期
                    text = datetime.strptime(text.replace("期", "1日"), "%Y年%m月%d日").date()
            elif text == "---":
                text = None
            data[tds[0].text] = text
        except Exception as e:
            logger.warning(e)
            data[tds[0].text] = None
    return data
