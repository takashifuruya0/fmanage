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
        elif settings.ENVIRONMENT == 'develop':
            # mac
            self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')
        logger.info("the driver has started")
        self.driver.get("https://www.lancers.jp/user/login?ref=header_menu")
        self.driver.find_element_by_name('data[User][password]').send_keys(settings.LANCERS_PASSWORD)
        self.driver.find_element_by_name('data[User][email]').send_keys(settings.LANCERS_USER_ID)
        self.driver.find_element_by_id('form_submit').click()
        logger.info("login Lancers")
        self.driver.get("https://www.lancers.jp/mypage")

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
        self.driver.get(url)
        # proposal
        description_proposal = self.driver.find_element_by_class_name('comment').text
        val_payment_str = self.driver.find_element_by_class_name('proposal_amount_value').text
        val_payment = int(val_payment_str.replace(",", "").replace(" 円", ""))
        deadline_str = self.driver.find_element_by_class_name('proposal_amount_deadline').text
        deadline = datetime.strptime(deadline_str.replace(' ', ''), "%Y年%m月%d日")
        val_str = self.driver.find_element_by_class_name('p-proposal-fee-calculators__number').text
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
        offer_url = self.driver.find_elements_by_class_name('naviTabs__item__anchor')[5].get_property('href')
        offer_id = offer_url.split("/")[-1]
        # offer
        res_offer = self.get_offer(offer_id)
        # res
        res = {
            "description_proposal": description_proposal,
            "val_payment": val_payment,
            "deadline": deadline,
            "val": val,
            "budget": budget,
            "num_proposal": num_proposal,
            "client_name": client_name,
            "client_url": client_url,
            "client_id": client_id,
            "offer_url": offer_url,
            "offer_id": offer_id,
        }
        res.update(res_offer)
        return res

    def get_direct_offer(self, direct_offer_id):
        """
        直接依頼
        """
        url = "https://www.lancers.jp/work_offer/{}".format(direct_offer_id)
        self.driver.get(url)
        vals = self.driver.find_elements_by_class_name("p-proposal-fee-calculators__number")
        val_payment = int(vals[0].text.replace(",", ""))
        val = int(vals[1].text.replace(",", ""))
        date_desired_delivery = datetime.strptime(
            self.driver.find_elements_by_class_name("worksummary__text")[2].text, "%Y年%m月%d日"
        )
        offer_id = self.driver.find_element_by_class_name("naviTabs__item__anchor").get_property("href").split("/")[-2]
        # offer
        res_offer = self.get_offer(offer_id)
        # res
        res = {
            "val_payment": val_payment,
            "val": val,
            "date_desired_delivery": date_desired_delivery,
            "offer_id": offer_id,
        }
        res.update(res_offer)
        return res

    def get_offer(self, offer_id):
        """
        依頼情報（提案、直接依頼で共通）
        """
        offer_url = "https://www.lancers.jp/work/detail/{}".format(offer_id)
        self.driver.get(offer_url)
        dd = self.driver.find_elements_by_class_name('workdetail-schedule__item__text')
        datetime_open_offer = datetime.strptime(dd[0].text, "%Y年%m月%d日 %H:%M")
        datetime_close_offer = datetime.strptime(dd[1].text, "%Y年%m月%d日 %H:%M")
        date_desired_delivery = datetime.strptime(dd[2].text, "%Y年%m月%d日")
        if dd.__len__() > 3:
            datetime_updated_offer = datetime.strptime(dd[3].text, "%Y年%m月%d日 %H:%M")
        else:
            datetime_updated_offer = datetime_open_offer
        dd = self.driver.find_elements_by_class_name('definitionList__description')
        dt = self.driver.find_elements_by_class_name('definitionList__term')
        description_offer = dd[0].text
        detail_offer = {
            k.text: v.text for k, v in zip(dt, dd)
        }
        res = {
            "datetime_open_offer": datetime_open_offer,
            "datetime_close_offer": datetime_close_offer,
            "date_desired_delivery": date_desired_delivery,
            "datetime_updated_offer": datetime_updated_offer,
            "description_offer": description_offer,
            "detail_offer": detail_offer,
        }
        return res

    def get_client(self, client_id):
        """
        クライアント
        """
        url = "https://www.lancers.jp/client/{}".format(client_id)
        self.driver.get(url)
        res = {}
        return res