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
            "datetime_open_offer": datetime_open_offer,
            "datetime_close_offer": datetime_close_offer,
            "date_desired_delivery": date_desired_delivery,
            "datetime_updated_offer": datetime_updated_offer,
            "description_offer": description_offer,
            "detail_offer": detail_offer,
        }
        return res

    def get_offer(self, client_id):
        url = "https://www.lancers.jp/work_offer/{}".format(client_id)
        self.driver.get(url)

    def get_client(self, client_id):
        url = "https://www.lancers.jp/client/{}".format(client_id)
        self.driver.get(url)

"""
a = lancers.driver.find_element_by_class_name('comment')
b = lancers.driver.find_element_by_class_name('work-proposal-budget')
>>> b.text
'20,000円\n~\n50,000円'


xpath = "/html/body/div[4]/div[2]/table/tbody/tr/td[2]/div/div[3]/table/tbody/tr[3]/td"
c = lancers.driver.find_element_by_xpath(xpath)
>>> c.text
'10件'

 d = lancers.driver.find_element_by_class_name('client').find_element_by_tag_name('a')
>>> d.text
'株式会社SYD'
>>> d.get_property('href')
'https://www.lancers.jp/client/sydmatsuda'

e = lancers.driver.find_element_by_class_name('proposal_amount_value')
>>> e.text
'41,250 円'

f = lancers.driver.find_element_by_class_name('proposal_amount_deadline')
>>> f.text
'2020 年 10 月 07 日'
>>> f.text.replace(' ', '')
'2020年10月07日'

g = lancers.driver.find_element_by_class_name('p-proposal-fee-calculators__number')
>>> g.text
'37,500'
>>> 


h = lancers.driver.find_elements_by_class_name('naviTabs__item__anchor')[5]
>>> h.get_property('href')
'https://www.lancers.jp/work/detail/3236157'

ii = lancers.driver.find_elements_by_class_name('workdetail-schedule__item__text')
>>> for i in ii:
...     i.text
... 
'2020年10月08日 23:46'
'2020年10月13日 23:46'
'2020年10月15日'
'2020年10月09日 11:44'

jj = lancers.driver.find_elements_by_class_name('definitionList__description')
>>> for j in jj:
...     j.text
... 
'Django3にてスクレイピングを使用したサイトを作成しています。\nある程度実装はできたのですが、本番環境だと処理が色々と試していますが、中々上手くいかないので、本番環境でも問題なく動く、非同期処理の実装をお願いしたいです。\いします。\nあるウェブサイトで自動で様々な処理をするものですが、その処理を非同期で実施したいです。\n\n\n詳しいを使用しています。\n\n\nあくまで本番の同じAWSEC２で動くことを前提としています。\n\n\nいまいちわかっていない部あるかと思いますが、宜しくお願いします。'
'分からないので、相談して決めさせていただければと思います。'
'Python'
'Django'
'設定なし'
'設定なし'
'その他'
'設計\nバックエンド開発'
'サーバー'

"""