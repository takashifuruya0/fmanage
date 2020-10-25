from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime
from django.conf import settings
import logging
logger = logging.getLogger("django")


# login
class Lancers:
    def __init__(self):
        if settings.ENVIRONMENT == 'metabase':
            # linux
            options = Options()
            options.binary_location = '/usr/bin/google-chrome'
            options.add_argument('--headless')
            options.add_argument('--window-size=1280,1024')
            self.driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=options)
            self.driver.implicitly_wait(10)  # seconds
        elif settings.ENVIRONMENT == 'develop':
            # mac
            self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')
            self.driver.implicitly_wait(10)  # seconds
            self.driver.set_page_load_timeout(10)
        logger.info("the driver has started")
        self.driver.get("https://www.lancers.jp/user/login")
        time.sleep(3)
        if self.driver.title == "404 Not Found":
            self.close()
            print("Failed to launch")
        self.driver.find_element_by_name('data[User][password]').send_keys(settings.LANCERS_PASSWORD)
        self.driver.find_element_by_name('data[User][email]').send_keys(settings.LANCERS_USER_ID)
        self.driver.find_element_by_id('form_submit').click()
        logger.info("login Lancers")
        self.driver.get("https://www.lancers.jp/mypage")
        time.sleep(3)
        if self.driver.title == "404 Not Found":
            self.close()
            print("Failed to launch")

    def __del__(self):
        self.driver.close()
        logger.info("closed the driver")

    def close(self):
        self.driver.close()
        logger.info("closed the driver")

    def get_proposal(self, proposal_id):
        """
        提案
        """
        url = "https://www.lancers.jp/work/proposal/{}".format(proposal_id)
        for i in range(3):
            self.driver.get(url)
            time.sleep(3)
            if self.driver.title == "404 Not Found":
                print("Retry {}".format(i))
                if i == 2:
                    raise Exception("Failed to access {}".format(url))
            else:
                break
        # proposal
        description_proposal = self.driver.find_element_by_class_name('comment').text
        val_payment_str = self.driver.find_element_by_class_name('proposal_amount_value').text
        val_payment = int(val_payment_str.replace(",", "").replace(" 円", ""))
        date_proposed_delivery_str = self.driver.find_element_by_class_name('proposal_amount_deadline').text
        date_proposed_delivery = datetime.strptime(date_proposed_delivery_str.replace(' ', ''), "%Y年%m月%d日")
        val_str = self.driver.find_elements_by_class_name('p-proposal-fee-calculators__number')[6].text
        val = int(val_str.replace(",", "").replace(" 円", ""))
        budget = self.driver.find_element_by_class_name('work-proposal-budget').text.replace("\n", "")
        num_proposal_str = self.driver.find_element_by_xpath(
            "/html/body/div[4]/div[2]/table/tbody/tr/td[2]/div/div[3]/table/tbody/tr[3]/td"
        ).text
        num_proposal = int(num_proposal_str[:-1])
        client = self.driver.find_element_by_class_name('client').find_element_by_tag_name('a')
        client_name = client.text
        client_url = client.get_property('href')
        client_id = client_url.split("/")[-1]
        opportunity_url = self.driver.find_elements_by_class_name('naviTabs__item__anchor')
        date_proposal = datetime.strptime(self.driver.find_element_by_id("suggestion").text[:-3], "%Y-%m-%d %H:%M").date()
        if opportunity_url.__len__() > 5:
            opportunity_url = opportunity_url[5].get_property('href')
            opportunity_id = opportunity_url.split("/")[-1]
            res_opportunity = self.get_opportunity(opportunity_id)
        elif opportunity_url.__len__() == 2:
            opportunity_url = opportunity_url[0].get_property('href')
            opportunity_id = opportunity_url.split("/")[-1]
            res_opportunity = self.get_opportunity(opportunity_id)
        else:
            opportunity_url = None
            opportunity_id = ""
        # res
        res = {
            "description_proposal": description_proposal,
            "val_payment": val_payment,
            "date_proposed_delivery": date_proposed_delivery,
            "val": val,
            "budget": budget,
            "num_proposal": num_proposal,
            "client_name": client_name,
            "client_url": client_url,
            "client_id": client_id,
            "opportunity_url": opportunity_url,
            "opportunity_id": opportunity_id,
            "date_proposal": date_proposal,
            "proposal_id": proposal_id,
            "type": "提案受注",
        }
        if opportunity_url:
            res.update(res_opportunity)
        return res

    def get_direct_opportunity(self, direct_opportunity_id):
        """
        直接依頼
        """
        url = "https://www.lancers.jp/work_offer/{}".format(direct_opportunity_id)
        for i in range(3):
            self.driver.get(url)
            time.sleep(3)
            if self.driver.title == "404 Not Found":
                print("Retry {}".format(i))
                if i == 2:
                    raise Exception("Failed to access {}".format(url))
            else:
                break
        self.driver.find_element_by_id("topHiddenDetail").click()
        self.driver.find_element_by_id("bottomHiddenDetail").click()
        vals = self.driver.find_elements_by_class_name("p-work-create-private-start-calculator__col-number")
        val_payment = int(vals[2].text.replace(",", ""))
        val = int(vals[7].text.replace(",", ""))
        date_desired_delivery = datetime.strptime(
            self.driver.find_elements_by_class_name("worksummary__text")[2].text, "%Y年%m月%d日"
        )
        opportunity_id = self.driver.find_element_by_class_name("naviTabs__item__anchor").get_property("href").split("/")[-2]
        # client
        clients = self.driver.find_elements_by_class_name('c-link')
        if clients.__len__() == 10:
            client = clients[0]
        elif clients.__len__() == 11:
            client = clients[1]
        client_url = client.get_property('href')
        client_name = client.text
        client_id = client_url.split("/")[-1]
        # opportunity
        res_opportunity = self.get_opportunity(opportunity_id)
        # res
        res = {
            "val_payment": val_payment,
            "val": val,
            "date_desired_delivery": date_desired_delivery,
            "opportunity_id": opportunity_id,
            "type": "直接受注",
            "direct_opportunity_id": direct_opportunity_id,
            "client_url": client_url,
            "client_name": client_name,
            "client_id": client_id,
        }
        res.update(res_opportunity)
        return res

    def get_opportunity(self, opportunity_id):
        """
        依頼情報（提案、直接依頼で共通）
        """
        opportunity_url = "https://www.lancers.jp/work/detail/{}".format(opportunity_id)
        for i in range(3):
            self.driver.get(opportunity_url)
            time.sleep(3)
            if self.driver.title == "404 Not Found":
                print("Retry {}".format(i))
                if i == 2:
                    raise Exception("Failed to access {}".format(opportunity_url))
            else:
                break
        dd = self.driver.find_elements_by_class_name('workdetail-schedule__item__text')
        datetime_open_opportunity = datetime.strptime(dd[0].text, "%Y年%m月%d日 %H:%M")
        datetime_close_opportunity = datetime.strptime(dd[1].text, "%Y年%m月%d日 %H:%M")
        date_desired_delivery = datetime.strptime(dd[2].text, "%Y年%m月%d日")
        if dd.__len__() > 3:
            datetime_updated_opportunity = datetime.strptime(dd[3].text, "%Y年%m月%d日 %H:%M")
        else:
            datetime_updated_opportunity = datetime_open_opportunity
        dd = self.driver.find_elements_by_class_name('definitionList__description')
        dt = self.driver.find_elements_by_class_name('definitionList__term')
        description_opportunity = dd[0].text
        detail_opportunity = {
            k.text: v.text for k, v in zip(dt, dd)
        }
        name = self.driver.title.split("の依頼")[0]
        res = {
            "datetime_open_opportunity": datetime_open_opportunity,
            "datetime_close_opportunity": datetime_close_opportunity,
            "date_desired_delivery": date_desired_delivery,
            "datetime_updated_opportunity": datetime_updated_opportunity,
            "description_opportunity": description_opportunity,
            "detail_opportunity": detail_opportunity,
            "name": name,
        }
        return res

    def get_client(self, client_id):
        """
        クライアント
        """
        url = "https://www.lancers.jp/client/{}".format(client_id)
        self.driver.get(url)
        time.sleep(3)
        res = {}
        return res
