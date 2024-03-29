# coding:utf-8
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from datetime import datetime
import logging
logger = logging.getLogger("django")

'''
data形式
{
    "msg": "Success",
    "status": True,
    "data": res,
}
'''


def kabuoji3(code):
    """kabuoji3からHLOCTを取得"""
    base_url = "https://kabuoji3.com/stock/" + str(code) + "/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    ret = requests.get(base_url, headers=headers)
    try:
        if settings.ENVIRONMENT == "develop":
            soup = BeautifulSoup(ret.content, "html5lib")
        else:
            soup = BeautifulSoup(ret.content, "lxml")
        stocktable = soup.find('table', {'class': 'stock_table stock_data_table'})
        records = stocktable.find_all('tr')
        records.pop(0)
        data = list()
        for r in records:
            tmp = list()
            for i in range(7):
                # date, open, high, low, close, turnover, ?
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


def yf_settlement(code, is_consolidated=True):
    """銘柄の決算情報を取得"""
    if is_consolidated:
        # 連結
        url = "https://profile.yahoo.co.jp/consolidate/{}".format(code)
    else:
        # 単体
        url = "https://profile.yahoo.co.jp/independent/{}".format(code)
    ret = requests.get(url)
    res = list()
    # table取得
    try:
        if settings.ENVIRONMENT == "develop":
            soup = BeautifulSoup(ret.content, "html5lib")
        else:
            soup = BeautifulSoup(ret.content, "lxml")
        table = soup.find('table', {'class': 'yjMt'})
        trs = table.findAll('tr')
    except Exception as e:
        logger.error(e)
        res = {
            "msg": "{}".format(e),
            "status": False,
            "data": None,
        }
        return res
    # 最終更新日
    try:
        d = soup.find('div', {'class': 'yjSt info'}).text.split("：")[1]
        last_update = datetime.strptime(d, '%Y年%m月%d日').date()
    except Exception as e:
        logger.error(e)

    # tableから
    for i in range(3):
        data = dict()
        data['最終更新日'] = last_update
        for tr in trs:
            try:
                tds = tr.findAll('td')
                text = tds[i+1].text.replace("%", "").replace(",", "").replace("円", "")
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
        # return用のresに追加
        res.append(data)
    # return
    res = {
        "msg": "Success",
        "status": True,
        "data": res,
    }
    return res


def yf_detail_old_v1(code):
    """銘柄詳細を取得"""
    base_url = "https://stocks.finance.yahoo.co.jp/stocks/detail/"
    res = {
        "msg": None,
        "status": None,
        "data": None,
    }
    data = {
        key: None
        for key in ("code", "name", "val", "market", "industry", "financial_data", "is_trust")
    }
    data['code'] = code
    data['is_trust'] = False if len(str(code)) == 4 else True
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    ret = requests.get(base_url, params={"code": str(code), }, headers=headers)
    try:
        if settings.ENVIRONMENT == "develop":
            soup = BeautifulSoup(ret.content, "html5lib")
        else:
            soup = BeautifulSoup(ret.content, "lxml")
        if not data['is_trust']:
            # 株
            stocktable = soup.find('table', {'class': 'stocksTable'})
            data['name'] = stocktable.findAll('th', {'class': 'symbol'})[0].text
            data['industry'] = soup.find('dd', {'class': 'category'}).text
            data['market'] = soup.findAll('span', {'class': 'stockMainTabName'})[0].text
            # finance情報
            chartfinance = soup.findAll('div', {'class': 'chartFinance'})[1]
            # 値の取得
            vals = [
                dd.text.replace(",", "").replace("\n", "").replace("(連) ", "").replace("(単) ", "")
                for dd in chartfinance.findAll('strong')
            ]
            # current val and hloct
            detail = soup.find('div', {"class": "innerDate"})
            strongs = detail.findAll('strong')
            val = stocktable.findAll('td', {'class': 'stoksPrice'})[1].text.replace(",", "")
            data['val'] = float(strongs[0].text.replace(',', '')) if val == "---" else float(val)
            data['val_close'] = data['val']
            data['val_open'] = None if val == "---" else float(strongs[1].text.replace(',', ''))
            data['val_high'] = None if val == "---" else float(strongs[2].text.replace(',', ''))
            data['val_low'] = None if val == "---" else float(strongs[3].text.replace(',', ''))
            data['turnover'] = None if strongs[4].text.replace(',', '') == "---" else float(strongs[4].text.replace(',', ''))
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
            # res['financial_data']に格納
            data['financial_data'] = {
                k: None if v == "---" else v
                for k, v in zip(keys, vals)
            }
            if not data['industry'] == "ETF":
                data['financial_data']['時価総額'] = int(data['financial_data']['時価総額']) * 1000000
            res['data'] = data
            # 完了
            res['msg'] = "Success"
            res['status'] = True
        else:
            # 投資信託
            data['name'] = soup.find('span', {'class': "cj4y2d7f"}).text
            data['industry'] = "投資信託"
            d = soup.find('span', {"class": "_284RTWj9"})
            # spans
            spans = soup.findAll('span', {'class': "_3BGK5SVf"})
            data['val'] = float(spans[0].text.replace(',', ''))/10000
            data['diff'] = float(spans[1].text.replace(',', ''))
            data['diff_pct'] = float(spans[2].text.replace(',', ''))
            data['balance'] = float(spans[3].text.replace(',', ''))*1000000
            data['資金流出入'] = float(spans[4].text.replace(',', '')) * 1000000
            data['トータルリターン (%)'] = float(spans[5].text.replace(',', ''))
            data['信託報酬 (%)'] = float(spans[6].text.replace(',', ''))
            data['リスク'] = float(spans[7].text.replace(',', ''))
            # table
            # table = soup.find('table', {"class": "_2NDVpt4L"})
            # tds = table.findAll('td')
            # data['カテゴリ-'] = None
            # data['運用会社'] = None
            # data['運用方針'] = None
            # data['設定日'] = None
            # data['償還日'] = None
            res['data'] = data
            # 完了
            res['msg'] = "Success"
            res['status'] = True
    except Exception as e:
        logger.error("スクレイピング失敗＠{}".format(code))
        logger.error("data: {}".format(data))
        logger.error(e)
        res['msg'] = e
        res['status'] = False
    return res


def yf_profile(code):
    """会社の特色や事業情報を取得"""
    base_url = "https://stocks.finance.yahoo.co.jp/stocks/profile/"
    res = {
        "msg": None,
        "status": None,
        "data": None,
    }
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    ret = requests.get(base_url, params={"code": str(code), }, headers=headers)
    try:
        soup = BeautifulSoup(ret.content, "lxml")
        table = soup.find("table", {'class': "boardFinCom marB6"})
        if not table:
            msg = "{}と一致する銘柄は見つかりませんでした".format(code)
            logger.info(msg)
            res['msg'] = msg
            res['status'] = False
            return res
        ths = table.find_all('th')
        tds = table.find_all('td')
        res['data'] = {
            th.text: td.text
            for th, td in zip(ths, tds)
        }
        res['status'] = True
        res['msg'] = "Success"
    except Exception as e:
        logger.error(e)
        res['msg'] = e
        res['status'] = False
    return res


def yf_detail(code):
    """銘柄詳細を取得：2021/03/23 YahooFinance Updateに対応"""
    base_url = "https://stocks.finance.yahoo.co.jp/stocks/detail/"
    res = {
        "msg": None,
        "status": None,
        "data": None,
    }
    data = {
        key: None
        for key in ("code", "name", "val", "market", "industry", "financial_data", "is_trust")
    }
    data['code'] = code
    data['is_trust'] = False if len(str(code)) == 4 else True
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36"
    }
    ret = requests.get(base_url, params={"code": str(code), }, headers=headers)
    try:
        if settings.ENVIRONMENT == "develop":
            soup = BeautifulSoup(ret.content, "html5lib")
        else:
            soup = BeautifulSoup(ret.content, "lxml")
        if not soup.find('a', {'class': '_1unyWCX0 _2jbOvvHc'}) and not data['is_trust']:
            # ETF
            logger.info('ETF')
            # 値の取得
            data['name'] = soup.find('h1', {"class": "_6uDhA-ZV"}).text
            data['industry'] = 'ETF'
            data['market'] = "東証"
            # 値
            class_info = "_3rXWJKZF"
            spans = soup.findAll("span", {"class": class_info})
            if len(spans) > 8:
                val = spans[0].text.replace(",", "")
                data['val'] = float(0) if val == "---" else float(val)
                data['val_close'] = data['val']
                data['val_open'] = data['val'] if val == "---" else float(spans[4].text.replace(',', ''))
                data['val_high'] = data['val'] if val == "---" else float(spans[5].text.replace(',', ''))
                data['val_low'] = data['val'] if val == "---" else float(spans[6].text.replace(',', ''))
                data['turnover'] = data['val'] if spans[7].text.replace(',', '') == "---" else float(spans[7].text.replace(',', ''))
            else:
                data['val'] = None
                data['val_close'] = None
                data['val_open'] = None
                data['val_high'] = None
                data['val_low'] = None
                data['turnover'] = None
            # finance
            data['financial_data'] = {}
            keys = soup.findAll('span', {'class': '_3RQJDhPQ'})
            vals = soup.findAll('span', {'class': '_3rXWJKZF _11kV6f2G'})
            if len(keys) == len(vals):
                for k, v in zip(keys, vals):
                    if v == "---":
                        val = None
                    else:
                        val = v.text.replace(",", "").replace("\n", "").replace("(連) ", "").replace("(単) ", "")
                    data['financial_data'][k.text] = val
            res['data'] = data
            # 完了
            res['msg'] = "Success"
            res['status'] = True
        elif not data['is_trust']:
            # 株
            class_name = "_6uDhA-ZV"
            data['name'] = soup.find('h1', {"class": class_name}).text
            class_industry = "_1unyWCX0 _2jbOvvHc"
            data['industry'] = soup.find('a', {"class": class_industry}).text
            class_market = "_4C2X3X7J"
            data['market'] = soup.find('button', {"class": class_market})
            if data['market'] is None:
                class_market = "_3sg2Atie"
                data['market'] = soup.find('span', {"class": class_market}).text
            else:
                data['market'] = data['market'].text
            # 値
            class_info = "_3rXWJKZF"
            spans = soup.findAll("span", {"class": class_info})
            if len(spans) > 8:
                val = spans[0].text.replace(",", "")
                data['val'] = float(0) if val == "---" else float(val)
                data['val_close'] = data['val']
                data['val_open'] = data['val'] if val == "---" else float(spans[4].text.replace(',', ''))
                data['val_high'] = data['val'] if val == "---" else float(spans[5].text.replace(',', ''))
                data['val_low'] = data['val'] if val == "---" else float(spans[6].text.replace(',', ''))
                data['turnover'] = data['val'] if spans[7].text.replace(',', '') == "---" else float(spans[7].text.replace(',', ''))
            else:
                data['val'] = None
                data['val_close'] = None
                data['val_open'] = None
                data['val_high'] = None
                data['val_low'] = None
                data['turnover'] = None
            # finance
            data['financial_data'] = {}
            keys = soup.findAll('span', {'class': '_3RQJDhPQ'})
            vals = soup.findAll('span', {'class': '_3rXWJKZF _11kV6f2G'})
            if len(keys) == len(vals):
                for k, v in zip(keys, vals):
                    if v == "---":
                        val = None
                    else:
                        val = v.text.replace(",", "").replace("\n", "").replace("(連) ", "").replace("(単) ", "")
                    data['financial_data'][k.text] = val
            # 完了
            res['data'] = data
            res['msg'] = "Success"
            res['status'] = True
            """
            現在値
            ?
            ?
            前日終値
            始値
            高値
            安値
            出来高
            売買代金
            値幅制限
            時価総額
            発行済株式数
            配当利回り
            1株配当
            PER（会社予想）
            PBR（実績）
            EPS（会社予想）
            BPS（実績）
            最低購入代金
            単元株数
            年初来高値
            年初来安値
            """
        else:
            # 投資信託
            data['name'] = soup.find('span', {'class': "cj4y2d7f"}).text
            data['industry'] = "投資信託"
            d = soup.find('span', {"class": "_284RTWj9"})
            # spans
            spans = soup.findAll('span', {'class': "_3BGK5SVf"})
            data['val'] = float(spans[0].text.replace(',', '')) / 10000
            data['diff'] = float(spans[1].text.replace(',', ''))
            data['diff_pct'] = float(spans[2].text.replace(',', ''))
            data['balance'] = float(spans[3].text.replace(',', '')) * 1000000
            data['資金流出入'] = float(spans[4].text.replace(',', '')) * 1000000
            data['トータルリターン (%)'] = float(spans[5].text.replace(',', ''))
            data['信託報酬 (%)'] = float(spans[6].text.replace(',', ''))
            data['リスク'] = float(spans[7].text.replace(',', ''))
            # table
            # table = soup.find('table', {"class": "_2NDVpt4L"})
            # tds = table.findAll('td')
            # data['カテゴリ-'] = None
            # data['運用会社'] = None
            # data['運用方針'] = None
            # data['設定日'] = None
            # data['償還日'] = None
            res['data'] = data
            # 完了
            res['msg'] = "Success"
            res['status'] = True
    except Exception as e:
        logger.error("スクレイピング失敗＠{}".format(code))
        logger.error("data: {}".format(data))
        logger.error(e)
        res['msg'] = e
        res['status'] = False
    return res
