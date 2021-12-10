from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime, date
from django.conf import settings
from bs4 import BeautifulSoup
from pprint import pprint
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
        self.login()
        self.driver.get("https://site2.sbisec.co.jp/ETGate")

    def __del__(self):
        self.driver.close()
        logger.info("closed the driver")

    def login(self):
        self.driver.get("https://www.sbisec.co.jp/ETGate/")
        self.driver.find_element_by_name('user_password').send_keys(settings.SBI_PASSWORD_LOGIN)
        self.driver.find_element_by_name('user_id').send_keys(settings.SBI_USER_ID)
        time.sleep(1)
        self.driver.find_element_by_name('ACT_login').click()
        logger.info("login SBI")

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

    def get_ipos(self):
        # prepate
        self.driver.get("https://site2.sbisec.co.jp/ETGate")
        year = datetime.today().year
        # 国内
        path0 = '/html/body/div[2]/div/div/ul/li[3]/a/img'
        time.sleep(1)
        self.driver.find_element_by_xpath(path0).click()
        # IPO
        path1 = '/html/body/div[4]/div/div/ul/li[5]/div/a'
        time.sleep(1)
        self.driver.find_element_by_xpath(path1).click()
        # 購入意思表示
        path2 = '/html/body/div[4]/div/table/tbody/tr/td[1]/div/div[10]/div/div/a/img'
        time.sleep(1)
        self.driver.find_element_by_xpath(path2).click()
        # table
        # path3 = '/html/body/table/tbody/tr/td/table[1]/tbody/tr/td/table[1]/tbody/tr[1]/td/table[9]'
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        tbls = soup.find_all("table", width=780, cellspacing="1")
        data_list = list()
        error_list = list()
        for tbl in tbls:
            logger.info("===========================")
            # data
            data = {
                "name": None,
                "market": None,
                "code": None,
                "unit": None,
                "datetime_open": None,
                "datetime_close": None,
                "status": None,
                "val_list": None,
                "is_applied": False,
                "num_applied": None,
                "point": None,
                "date_list": None,
                "datetime_select": None,
                'result_select': None,
                "datetime_purchase_close": None,
                "datetime_purchase_open": None,
                "result_buy": None,
            }
            try:
                tds = tbl.find_all('td', attrs={"bgcolor": ["#ffffff", '#ffffcc']})
                # 銘柄
                company = tbl.find("td", width="701").text.replace(u'\xa0', ' ').split(" ")
                data['name'] = company[1]
                data['market'] = company[4].strip().split("）")[1]
                data['code'] = company[4].strip().split("）")[0].replace("（", "")
                if len(tds) < 11:
                    logger.info("Skipped because {} has only {} length".format(data['name'], len(tds)))
                    # 11要素取得できない場合はスキップ
                    continue
                # 1: ブックビル期間: '7/12\xa00:00〜7/16\xa011:00'
                logger.info("1: ブックビル期間:")
                if "〜" in tds[1].text:
                    data['datetime_open'] = datetime.strptime(
                        "{}/{}".format(year, tds[1].text.split("〜")[0].replace(u'\xa0', ' ')), "%Y/%m/%d %H:%M")
                    data['datetime_close'] = datetime.strptime(
                        "{}/{}".format(year, tds[1].text.split("〜")[1].replace(u'\xa0', ' ')), "%Y/%m/%d %H:%M")
                else:
                    data['datetime_open'] = None
                    data['datetime_close'] = None
                # 2: ブックビル申込: '受付終了'
                logger.info("2: ブックビル申込:")
                data['status'] = tds[2].text
                # 3: 発行価格又は売出価格: '決定日 7/19'
                #                      '仮条件1700〜1940'
                logger.info("3: 発行価格又は売出価格:")
                if "決定日" in tds[3].text:
                    data['val_list'] = None
                elif "仮条件" in tds[3].text:
                    data["val_list"] = int(tds[3].text.replace(",", "").replace("円", "").split("〜")[1])
                else:
                    # 1,780円
                    data['val_list'] = int(tds[3].text.replace("円", "").replace(",", ""))
                # 4: 申込単位: '100株単位'
                logger.info("4: 申込単位:")
                data['unit'] = int(tds[4].text.replace("株単位", "").replace("口単位", ""))
                # 5: ブックビル申込内容: '-'
                logger.info("5: ブックビル申込内容:")
                if "IPOポイント" in tds[5].text:
                    # 200株
                    # ストライクプライス
                    # (使用IPOポイント -)
                    data['is_applied'] = True
                    data['num_applied'] = int(tds[5].contents[0].replace("株", "").replace("口", "").replace(",", ""))
                    tmp = tds[5].contents[4].replace(
                        u'\xa0', ' ').replace("株", "").replace("口", "").replace(",", "").replace("P)", "").split(" ")[1]
                    data['point'] = None if tmp == "-)" else int(tmp)
                else:
                    # 申し込み前
                    data['is_applied'] = False
                    data['point'] = None
                    data['num_applied'] = None
                # 6: 上場日: '7/30'
                logger.info("6: 上場日: ")
                data['date_list'] = datetime.strptime("{}/{}".format(year, tds[6].text), "%Y/%m/%d").date()
                # 7: 抽選結果: '7/19 18:00〜'
                logger.info("7: 抽選結果: ")
                if tds[7].text == "-":
                    data['datetime_select'] = None
                elif "〜" in tds[7].text:
                    data['datetime_select'] = datetime.strptime(
                        "{}/{}".format(year, tds[7].text.replace("〜", "")), "%Y/%m/%d %H:%M")
                else:
                    # 落選
                    data['result_select'] = tds[7].text
                # 8: 購入意思表示期限: '7/26 12:00'
                logger.info("8: 購入意思表示期限: ")
                if tds[8].text == "-":
                    data['datetime_purchase_close'] = None
                elif tds[8].text == "締切":
                    data['datetime_purchase_close'] = None
                else:
                    data['datetime_purchase_close'] = datetime.strptime(
                        "{}/{}".format(year, tds[8].text), "%Y/%m/%d %H:%M")
                # 9: 購入意思表示: '7/20 0:00〜'
                logger.info("9: 購入意思表示: ")
                if tds[9].text == "-" or "／" in tds[7].text:
                    data['datetime_purchase_open'] = None
                else:
                    data['datetime_purchase_open'] = datetime.strptime(
                        "{}/{}".format(year, tds[9].text.replace("〜", "")), "%Y/%m/%d %H:%M")
                # 10: 購入結果: '-'
                logger.info("10: 購入結果:")
                data['result_buy'] = tds[10].text
                # pprint(data)
                logger.info(data)
                logger.info("Successfully extracted information of {}".format(data['name']))
                data_list.append(data)
            except Exception as e:
                error_list.append({data['name']: e})
                logger.error("Failed to extract information of {}".format(data['name']))
                logger.error(e)
                logger.error(data)
                continue
        # return
        res = {
            "data": data_list,
            "errors": error_list
        }
        return res

    def apply_ipo(self, code, num):
        res = {}
        url = "https://m.sbisec.co.jp/oeapw011?type=21&p_cd={}".format(code)
        try:
            # 国内
            path0 = '/html/body/div[2]/div/div/ul/li[3]/a/img'
            time.sleep(1)
            self.driver.find_element_by_xpath(path0).click()
            # IPO
            path1 = '/html/body/div[4]/div/div/ul/li[5]/div/a'
            time.sleep(1)
            self.driver.find_element_by_xpath(path1).click()
            # 購入意思表示
            path2 = '/html/body/div[4]/div/table/tbody/tr/td[1]/div/div[10]/div/div/a/img'
            time.sleep(1)
            self.driver.find_element_by_xpath(path2).click()
            time.sleep(1)
            self.driver.get(url)
            # page遷移
            time.sleep(2)
            self.driver.find_element_by_name('suryo').send_keys(num)
            self.driver.find_element_by_name('tr_pass').send_keys(settings.SBI_PASSWORD_ORDER)
            self.driver.find_element_by_id('strPriceRadio').click()
            self.driver.find_element_by_name('order_kakunin').click()
            # page遷移
            time.sleep(2)
            self.driver.find_element_by_name('order_btn').click()
            res['status'] = True
            res['msg'] = 'Orderd {} units for Stock code {}'.format(num, code)
        except Exception as e:
            res['status'] = False
            res['msg'] = e
        finally:
            # res
            return res


class SeleniumIPO:
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
        self.driver.get("https://96ut.com/ipo/yoso.php")

    def __del__(self):
        self.driver.close()
        logger.info("closed the driver")

    def get_list(self):
        res = []
        self.driver.get("https://96ut.com/ipo/yoso.php")
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        table = soup.find("table")
        trs = table.find_all("tr")
        for tr in trs:
            tds = tr.find_all("td")
            if len(tds) > 0:
                #? '=========================='
                #?0 'サーキュレーション\n(みずほ\n)'
                #?1 '07/27\n(火)'
                #?2 '東M\n[7379]'
                #?3 '1,610-1,810\n1,610⇒1,810'
                #?4 '2,300\n2,800'
                #?5 'B(7)⇒B (7)\n2,479 (66件)'
                #?5 '\n'
                #?6 '3,205'
                #?7 '締切\n'
                #? '=========================='
                val = {}
                try:
                    # 0
                    td0 = tds[0].text.replace("(", "").replace(")", "").split("\n")
                    val["name"] = td0[0]
                    val["managing_underwriter"] = td0[1]
                    # 1
                    td1 = tds[1].text.split("\n")[0].split("/")
                    month = int(td1[0])
                    day = int(td1[1])
                    this_year = date.today().year
                    year =  this_year if date.today() <= date(this_year, month, day) else this_year+1
                    val["date_list"] = date(year, month, day)
                    # 2
                    val["code"] = tds[2].text.replace("]", "").split("[")[1]
                    # 3
                    td3 = tds[3].text.split("\n")[1].split("⇒")
                    val["val_list"] = int((td3[0] if td3[1] == "未" else td3[1]).replace(",", ""))
                    # 4
                    # 5
                    td5 = tds[5].text.split("\n")
                    val["rank"] = td5[0][0]
                    val["val_predicted"] = int(tds[5].text.split("\n")[1].split(" ")[0].replace(",", ""))
                    val["url"] = tds[5].a.get_attribute_list("href")[0]
                    res.append(val)
                except Exception as e:
                    logger.error(e)
                finally:
                    logger.info(val)
                    logger.info("======================")
        return res
