from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import date
from bs4 import BeautifulSoup
from time import sleep
import logging
logger = logging.getLogger('django')
from django.conf import settings


def goldpoint(year, month):
    # prepare
    try:
        options = Options()
        options.binary_location = '/usr/bin/google-chrome'
        options.add_argument('--headless')
        options.add_argument('--window-size=1280,1024')
        driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
    except Exception as e:
        logger.error(e)
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome('/usr/local/bin/chromedriver', chrome_options=options)
    res = dict()

    try:
        # login処理
        url = "https://secure.goldpoint.co.jp/gpm/authentication/index.html"
        driver.get(url)
        logger.debug("before sign-in: {0}".format(driver.current_url))
        driver.find_element_by_id('authenticateDO.authKey').send_keys(settings.GOLDPOINT_ID)
        driver.find_element_by_id('authenticateDO.password').send_keys(settings.GOLDPOINT_PASSWORD)
        driver.find_element_by_class_name("sideSbmBtn").find_element_by_tag_name('input').click()
        logger.debug("after sign-in: {0}".format(driver.current_url))

        # 月毎の明細ページ
        month = "0{0}".format(month) if month < 10 else str(month)
        params = "?p01={0}{1}".format(year, month)
        url = "https://secure.goldpoint.co.jp/memx/web_meisai/top/index.html" + params
        driver.get(url)
        logger.debug("detail-page: {0}".format(driver.current_url))

        # 取得
        for i in range(10):
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            bb = soup.find('tbody')
            if bb:
                break
            else:
                # javascriptが完了するまでスリープ
                sleep(1)

        # 解析
        trs = bb.findChildren('tr')
        total = 0
        res['data'] = list()
        for n, tr in enumerate(trs):
            tds = tr.findChildren('td')
            tmp = {
                "no": n,
                "date": "",
                "debit_date": "",
                "fee": 0,
                "credit_item": "",
            }
            for i, k in enumerate(tds):
                # 利用日、項目、引落月、金額
                v = k.text.replace("\n", "").replace(",", "")
                if i == 17:
                    tmp['fee'] = int(v)
                    total += tmp['fee']
                elif i == 16:
                    tmp['debit_date'] = date(int("20" + v[0:2]), int(v[3:5]), 1)
                elif i == 1:
                    tmp['credit_item'] = v
                elif i == 0:
                    tmp['date'] = date(int("20" + v[0:2]), int(v[3:5]), int(v[6:8]))
            res['data'].append(tmp)
        res['total'] = total
        res['average'] = total / len(trs)
        logger.info("sum: {0}".format(total))
        logger.info("ave: {0}".format(total / len(trs)))
    except Exception as e:
        logger.erro(e)
    finally:
        driver.quit()
        return res
