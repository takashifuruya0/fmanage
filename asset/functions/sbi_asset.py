from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
from django.conf import settings
import logging
logger = logging.getLogger("django")
from fmanage.celery import app
from asset.functions import get_info


# login
def login(driver, USER_ID, LOGIN_PASSWORD):
    url = "https://site2.sbisec.co.jp/ETGate/"
    driver.get(url)
    driver.find_element_by_name('user_password').send_keys(LOGIN_PASSWORD)
    driver.find_element_by_name('user_id').send_keys(USER_ID)
    bu = driver.find_element_by_name('ACT_login')
    bu.click()
    logger.info("login SBI")
    return True


@app.task()
def buy(driver, stock_code, num, PASSWORD):
    url_buy = "https://site2.sbisec.co.jp/ETGate/?_ControlID=WPLETstT002Control&_DataStoreID=DSWPLETstT002Control&stock_sec_code={}".format(stock_code)
    driver.get(url_buy)
    # 買い口数
    a = driver.find_element_by_name('input_quantity')
    a.send_keys(num)
    # 成行
    b = driver.find_element_by_id('nariyuki')
    b.click()
    # 確認省略
    c = driver.find_element_by_id('shouryaku')
    c.click()
    # PASSWORD
    d = driver.find_element_by_id('pwd3')
    d.send_keys(PASSWORD)
    # Order
    e = driver.find_element_by_id('botton2')
    e.click()
    # check
    for i in range(10):
        if not driver.current_url == url_buy:
            logger.info("Completed buy-order. Code: {}, Num: {}".format(stock_code, num))
            return True
        else:
            logger.info("In process")
            time.sleep(2)
    logger.error("Failed buy order")
    return False


def sell(driver, stock_code, num, PASSWORD):
    url_sell = "https://site2.sbisec.co.jp/ETGate/?_ControlID=WPLETstT004Control&_DataStoreID=DSWPLETstT004Control&stock_sec_code={}".format(stock_code)
    driver.get(url_sell)
    # 売り口数
    a = driver.find_element_by_name('input_quantity')
    a.send_keys(num)
    # 成行
    b = driver.find_element_by_id('nariyuki')
    b.click()
    # 確認省略
    c = driver.find_element_by_id('shouryaku')
    c.click()
    # PASSWORD
    d = driver.find_element_by_id('pwd3')
    d.send_keys(PASSWORD)
    # Order
    e = driver.find_element_by_id('botton2')
    e.click()
    # check
    for i in range(10):
        if not driver.current_url == url_sell:
            logger.info("Completed sell-order. Code: {}, Num: {}".format(stock_code, num))
            return True
        else:
            logger.info("In process")
            time.sleep(2)
    logger.error("Failed sell-order")
    return False


def alert(driver, stock_code, val, alert_type):
    alert_msg = [
        "0.現在値（円以上）",
        "1.現在値（円以下）",
        "2.前日比（％以上）",
        "3.前日比（％以下）",
    ]
    logger.info("Code: {}".format(stock_code))
    logger.info("Value: {}".format(val))
    logger.info("Alert Type: {}".format(alert_msg[alert_type]))
    url_alert = "https://site2.sbisec.co.jp/ETGate/?_ControlID=WPLETsmR001Control&_DataStoreID=DSWPLETsmR001Control&cat1=home&cat2=none&sw_page=AlertSet&sw_param1={}&sw_param2=TKY&getFlg=on".format(stock_code)
    driver.get(url_alert)
    # alert_type: 0.現在値（円以上）, 1.現在値（円以下）, 2.前日比（％以上）, 3.前日比（％以下）
    # ToDo xpathで取得して、clickに変更
    a = driver.find_element_by_name('smartAlertRegDtl[0].aarAlertId')
    a.send_keys(alert_type)
    # 目標値
    b = driver.find_element_by_name('smartAlertRegDtl[0].aarAlertValue')
    b.send_keys(val)
    # 通知短文
    c = driver.find_element_by_xpath('//*[@id="smartAlertForm"]/table[1]/tbody/tr[1]/td[4]/label[3]/input')
    c.click()
    #
    d = driver.find_element_by_name('smartAlertRegDtl[0].aarAlertId')
    d = Select(d)
    d.select_by_value(str(alert_type))
    # Set Alert
    e = driver.find_element_by_xpath("//img[@title='設定']")
    e.click()
    # check
    for i in range(10):
        if not driver.current_url == url_alert:
            logger.info("Completed process")
            return True
        else:
            logger.info("In process")
            time.sleep(2)
    logger.error("Failed process")
    return False


def set_alert(code):
    try:
        if settings.ENVIRONMENT == 'metabase':
            # linux
            options = Options()
            options.binary_location = '/usr/bin/google-chrome'
            options.add_argument('--headless')
            options.add_argument('--window-size=1280,1024')
            driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
        elif settings.ENVIRONMENT == 'develop':
            # mac
            driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        login(driver, settings.SBI_USER_ID, settings.SBI_PASSWORD_LOGIN)
        # 現在価格の±１％以上の変動で通知
        val = get_info.stock_overview(code)['price']
        alert(driver, code, int(val*1.01), 0)
        alert(driver, code, int(val*0.99), 1)
        # set_alert: 前日比±１％以上の変動で通知
        alert(driver, code, 1, 2)
        alert(driver, code, 1, 3)
        res = True
    except Exception as e:
        logger.error(e)
        res = False
    finally:
        driver.quit()
        logger.debug("closed driver")
        return res


def set_buy(code, num):
    try:
        if settings.ENVIRONMENT == 'metabase':
            # linux
            options = Options()
            options.binary_location = '/usr/bin/google-chrome'
            options.add_argument('--headless')
            options.add_argument('--window-size=1280,1024')
            driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
        elif settings.ENVIRONMENT == 'develop':
            # mac
            driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        login(driver, settings.SBI_USER_ID, settings.SBI_PASSWORD_LOGIN)
        # set_buy：成行
        buy(driver, code, num, settings.SSBI_PASSWORD_ORDER)
        res = True
    except Exception as e:
        logger.error(e)
        res = False
    finally:
        driver.quit()
        logger.debug("closed driver")
        return res


def set_sell(code, num):
    try:
        if settings.ENVIRONMENT == 'metabase':
            # linux
            options = Options()
            options.binary_location = '/usr/bin/google-chrome'
            options.add_argument('--headless')
            options.add_argument('--window-size=1280,1024')
            driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
        elif settings.ENVIRONMENT == 'develop':
            # mac
            driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        login(driver, settings.SBI_USER_ID, settings.SBI_PASSWORD_LOGIN)
        # set_sell：成行
        sell(driver, code, num, settings.SSBI_PASSWORD_ORDER)
        res = True
    except Exception as e:
        logger.error(e)
        res = False
    finally:
        driver.quit()
        logger.debug("closed driver")
        return res
