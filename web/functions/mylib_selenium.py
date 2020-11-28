from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
from django.conf import settings
import logging
logger = logging.getLogger("django")


# login
class SeleniumSBI:
    def __init__(self):
        if settings.ENVIRONMENT == 'metabase':
            # linux
            options = Options()
            options.binary_location = '/usr/bin/google-chrome'
            options.add_argument('--headless')
            options.add_argument('--window-size=1280,1024')
            self.driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
        elif settings.ENVIRONMENT == 'develop':
            # mac
            self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        logger.info("the driver has started")
        self.driver.get("https://www.sbisec.co.jp/ETGate/")
        self.driver.find_element_by_name('user_password').send_keys(settings.SBI_PASSWORD_LOGIN)
        self.driver.find_element_by_name('user_id').send_keys(settings.SBI_USER_ID)
        self.driver.find_element_by_name('ACT_login').click()
        logger.info("login SBI")
        self.driver.get("https://site2.sbisec.co.jp/ETGate")

    def __del__(self):
        self.driver.close()
        logger.info("closed the driver")

    def close(self):
        self.driver.close()
        logger.info("closed the driver")

    def buy(self, stock_code, num):
        url_buy = "https://site2.sbisec.co.jp/ETGate/?_ControlID=WPLETstT002Control&_DataStoreID=DSWPLETstT002Control&stock_sec_code={}".format(stock_code)
        self.driver.get(url_buy)
        # 買い口数
        a = self. driver.find_element_by_name('input_quantity')
        a.send_keys(num)
        # 成行
        b = self.driver.find_element_by_id('nariyuki')
        b.click()
        # 確認省略
        c = self.driver.find_element_by_id('shouryaku')
        c.click()
        # PASSWORD
        d = self.driver.find_element_by_id('pwd3')
        d.send_keys(settings.SBI_PASSWORD_ORDER)
        # Order
        e = self.driver.find_element_by_id('botton2')
        e.click()
        # check
        if not self.driver.current_url == url_buy:
            try:
                a = self.driver.find_element_by_xpath('//*[@id="MAINAREA02_780"]/form/div[1]/p/b')
                if a.text == 'ご注文を受け付けました。':
                    logger.info("Completed buy-order. Code: {}, Num: {}".format(stock_code, num))
                    return True
                else:
                    logger.error("Failed buy order")
                    return False
            except Exception as e:
                logger.error(e)
                return False
        else:
            logger.error("Failed buy order")
            return False

    def sell(self, stock_code, num):
        url_sell = "https://site2.sbisec.co.jp/ETGate/?_ControlID=WPLETstT004Control&_DataStoreID=DSWPLETstT004Control&stock_sec_code={}".format(stock_code)
        self.driver.get(url_sell)
        # 売り口数
        a = self.driver.find_element_by_name('input_quantity')
        a.send_keys(num)
        # 成行
        b = self.driver.find_element_by_id('nariyuki')
        b.click()
        # 確認省略
        c = self.driver.find_element_by_id('shouryaku')
        c.click()
        # PASSWORD
        d = self.driver.find_element_by_id('pwd3')
        d.send_keys(settings.SBI_PASSWORD_ORDER)
        # Order
        e = self.driver.find_element_by_id('botton2')
        e.click()
        # check
        if not self.driver.current_url == url_sell:
            try:
                a = self.driver.find_element_by_xpath('//*[@id="MAINAREA02_780"]/form/div[1]/p/b')
                if a.text == 'ご注文を受け付けました。':
                    logger.info("Completed sell-order. Code: {}, Num: {}".format(stock_code, num))
                    return True
                else:
                    logger.error("Failed buy order")
                    return False
            except Exception as e:
                logger.error(e)
                return False

        else:
            logger.error("Failed buy order")
            return False

    def alert(self, stock_code, val, alert_type):
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
        self.driver.get(url_alert)
        # alert_type: 0.現在値（円以上）, 1.現在値（円以下）, 2.前日比（％以上）, 3.前日比（％以下）
        a = self.driver.find_element_by_name('smartAlertRegDtl[0].aarAlertId')
        a.send_keys(alert_type)
        # 目標値
        b = self.driver.find_element_by_name('smartAlertRegDtl[0].aarAlertValue')
        b.send_keys(int(val))
        # 通知短文
        c = self.driver.find_element_by_xpath('//*[@id="smartAlertForm"]/table[1]/tbody/tr[1]/td[4]/label[3]/input')
        c.click()
        #
        d = self.driver.find_element_by_name('smartAlertRegDtl[0].aarAlertId')
        d = Select(d)
        d.select_by_value(str(alert_type))
        # Set Alert
        e = self.driver.find_element_by_xpath("//img[@title='設定']")
        e.click()
        # check
        if not self.driver.current_url == url_alert:
            logger.info("Completed process")
            return True
        else:
            logger.error("Failed process")
            return False

    def delete_all_alerts(self):
        url = "https://site0.sbisec.co.jp/marble/domestic/top.do?"
        self.driver.get(url)
        url = "https://www.sbisec.co.jp/ETGate/WPLETmgR001Control?OutSide=on&getFlg=on&burl=search_home&cat1=home&cat2=service&dir=service&file=home_mail_alert.html"
        self.driver.get(url)
        self.driver.find_element_by_xpath("//img[@alt='スマートアラート（株価通知）のご登録はこちら']").click()
        self.driver.find_element_by_id("regListPage").click()
        # 登録数
        num_registered = int(self.driver.find_element_by_id("regListPage").text.split("(")[1].split("/")[0])
        cnt = 0
        for i in range(num_registered):
            id = "copyTD3_{}".format(i)
            if self.driver.find_elements_by_id(id).__len__() == 0:
                id = "nextTd3_{}".format(i)
            if self.driver.find_element_by_id(id).text == "送信済":
                cnt += 1
                self.driver.find_element_by_id(id).click()
        # click
        if cnt > 0:
            self.driver.find_element_by_xpath("//img[@title='設定']").click()
            for i in range(10):
                if not self.driver.current_url == url:
                    logger.info("Completed process. Deleted {}".format(cnt))
                    return True
                else:
                    logger.info("In process {}".format(i))
                    time.sleep(2)
            logger.error("Failed process")
            return False
        else:
            logger.info("Not deleted")
            return True

